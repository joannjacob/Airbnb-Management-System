import hashlib
import re
import csv
import pymysql
import datetime
import pandas as pd

db_username = input("Input your DB username: ")
db_password = input("Input your DB password: ")

while True:
    # try to connect to the database with the given username and password
    try:
        connection = pymysql.connect(
            host='localhost',
            user=db_username,
            password=db_password,
            db='airbnb', 
            charset='utf8mb4', 
            cursorclass=pymysql.cursors.DictCursor)
    except pymysql.err.OperationalError as e:
        print("Could not connect to database. Please check your username and password.")
        break

    print("")
    print("OPTIONS")
    print("1. Add Country")
    print("2. Add State")
    print("3. Add City")
    print("4. Populate Neighbourhoods table from neighbourhoods CSV file")
    print("5. Populate Room Types, Property Types tables from listings CSV file")
    print("6. Populate host data into Users, Hosts and Listings tables from Listings csv file")
    option = input("Enter your option (or 'no' to stop): ")
    print("")

    if option == "no":
        break
    

    # Prepare a cursor object using cursor() method
    cursor = connection.cursor()

    if option == "1":
        # Ask user to input name of country
        country_name = input("Enter name of country: ")

        # Check if the country already exists in the table
        sql = "SELECT country_id FROM Countries WHERE name = %s"
        cursor.execute(sql, (country_name,))
        result = cursor.fetchone()

        if result:
            # Country already exists in table
            print(f"{country_name} already exists in table")
        else:
            # Country does not exist in table, insert a new row
            sql = "INSERT INTO Countries (name) VALUES (%s)"
            cursor.execute(sql, (country_name,))
            country_id = cursor.lastrowid
            print(f"{country_name} added to table")

    elif option == "2":
        cursor.execute("SELECT * FROM Countries ORDER BY name")
        country_list = [row["name"].lower() for row in cursor.fetchall()] 

        if country_list:
            # Display the list of countries to the user
            print("Available countries in the database")
            for country in country_list:
                print("- " + country)

            while True:
                user_country = input("Please select a country: ")
                if user_country.lower() in country_list:
                    # Check if the country already exists in the table
                    sql = "SELECT country_id FROM Countries WHERE name = %s"
                    cursor.execute(sql, (user_country,))
                    result = cursor.fetchone()
                    country_id = result['country_id']
                    break
                else:
                    print("Invalid country. Please choose from the list above.")

            # Ask user to input name of state
            state_name = input("Enter name of state: ")

            # Check if the country already exists in the table
            sql = "SELECT state_id FROM States WHERE name = %s"
            cursor.execute(sql, (state_name,))
            result = cursor.fetchone()

            if result:
                # State already exists in table
                print(f"{state_name} already exists in table")
            else:
                # State does not exist in table, insert a new row
                sql = "INSERT INTO States (name, country_id) VALUES (%s, %s)"
                cursor.execute(sql, (state_name, country_id,))
                state_id = cursor.lastrowid
                print(f"{state_name} added to table")
        else:
            print("No countries in the database. Populate countries using option 1")

    elif option == "3":
        cursor.execute("SELECT * FROM States ORDER BY name")
        states_list = [row["name"].lower() for row in cursor.fetchall()] 

        # Display the list of countries to the user
        if states_list:
            print("Available states in the database")
            for state in states_list:
                print("- " + state)

            while True:
                user_state = input("Please select a state: ")
                if user_state.lower() in states_list:
                    # Check if the country already exists in the table
                    sql = "SELECT state_id FROM States WHERE name = %s"
                    cursor.execute(sql, (user_state,))
                    result = cursor.fetchone()
                    state_id = result['state_id']
                    break
                else:
                    print("Invalid country. Please choose from the list above.")

            # Ask user to input name of city
            city_name = input("Enter name of city: ")

            # Check if the city already exists in the table
            sql = "SELECT city_id FROM Cities WHERE name = %s"
            cursor.execute(sql, (city_name,))
            result = cursor.fetchone()

            if result:
                # State already exists in table
                city_id = result['city_id']
                print(f"{city_name} already exists in table")
            else:
                # City does not exist in table, insert a new row
                sql = "INSERT INTO Cities (name, state_id) VALUES (%s, %s)"
                cursor.execute(sql, (city_name, state_id,))
                city_id = cursor.lastrowid
                print(f"{city_name} added to table")
        else:
            print("No states in the database. Populate states using option 2")

    elif option == "4":
        cursor.execute("SELECT * FROM Cities ORDER BY name")
        cities_list = [row["name"].lower() for row in cursor.fetchall()] 

        # Display the list of countries to the user
        if cities_list:
            print("Available cities in the database")
            for city in cities_list:
                print("- " + city)
        
            while True:
                user_city = input("Please select a city: ")
                if user_city.lower() in cities_list:
                    # Check if the country already exists in the table
                    sql = "SELECT city_id FROM Cities WHERE name = %s"
                    cursor.execute(sql, (user_city,))
                    result = cursor.fetchone()
                    city_id = result['city_id']
                    break
                else:
                    print("Invalid city. Please choose from the list above.")

            # Open the CSV file and read the data
            with open('inside_airbnb_data/neighbourhoods.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Insert the neighborhood record into the Neighborhoods table
                    neighbourhood_name = row['neighbourhood']
                    cursor = connection.cursor()
                    sql = "INSERT INTO Neighbourhoods (name, city_id) VALUES (%s, %s)"
                    try:
                        cursor.execute(sql, (neighbourhood_name, city_id,))
                        neighbourhood_id = cursor.lastrowid
                    except pymysql.err.IntegrityError as e:
                        if e.args[0] == 1062:
                            print(f"{neighbourhood_name} already exists in {user_city}.")
                        else:
                            print(f"{e}")
        else:
            print("No cities in the database. Populate cities using option 3")

    elif option == "5":
        # Read the CSV file
        df = pd.read_csv('inside_airbnb_data/listings_detailed.csv')

        # Get unique values of property_type column
        property_types = df['property_type'].unique()

        # Get unique values of room_type column
        room_types = df['room_type'].unique()

        # Insert unique property types into PropertyTypes table
        with connection.cursor() as cursor:
            for p in property_types:
                sql = "INSERT INTO PropertyTypes (property_type_name) VALUES (%s)"
                try:
                    cursor.execute(sql, p.strip())
                except pymysql.err.IntegrityError as e:
                    print(p.strip(), "already exists in PropertyTypes")
            connection.commit()

        # Insert unique room types into RoomTypes table
        with connection.cursor() as cursor:
            for r in room_types:
                sql = "INSERT INTO RoomTypes (room_type_name) VALUES (%s)"
                try:
                    cursor.execute(sql, r.strip())
                except pymysql.err.IntegrityError as e:
                    print(r.strip(), "already exists in RoomTypes")
            connection.commit()

    elif option == "6":
        default_city = "Boston"
        listings_data = pd.read_csv('inside_airbnb_data/listings_detailed.csv')

        # Iterate through each row of listings data.
        for index, row in listings_data.iterrows():
            # Extract the host information from the current row.
            host_id = row['host_id']
            host_name = row['host_name']
            if not host_id and not host_name:
                continue

            host_about = row['host_about'] if pd.notnull(row['host_about']) else 'Not Available'
            host_location = row['host_location'] if pd.notnull(row['host_location']) else 'Not Available'
            host_neighbourhood = row['host_neighbourhood'] if pd.notnull(row['host_neighbourhood']) else 'Not Available'
            host_is_superhost = True if row['host_is_superhost'] == 't' else False
            host_total_listings_count = row['host_total_listings_count'] if row['host_total_listings_count'] else 0

            if host_neighbourhood == 'Not Available':
                continue
            # Query the Neighbourhoods table to get the appropriate id.
            cursor = connection.cursor()
            cursor.execute("SELECT neighbourhood_id FROM Neighbourhoods WHERE name = %s", host_neighbourhood)
            result = cursor.fetchone()
            if not result:
                print(host_neighbourhood, "does not exist in table.")
                continue
            else:
                host_neighbourhood_id = result['neighbourhood_id']

            # Extract the listing information from the current row.
            name = row['name'] if row['name'] else 'Not Available'
            price = float(re.findall('\d+\.\d*', row['price'])[0]) if row['price'] else 0.0
            latitude = float(row['latitude']) if row['latitude'] else 0.0
            longitude = float(row['longitude']) if row['longitude'] else 0.0
            minimum_nights = int(row['minimum_nights']) if row['minimum_nights'] else 0
            maximum_nights = int(row['maximum_nights']) if row['maximum_nights'] else 0
            description = row['description'] if row['description'] else 'Not Available'
            occupancy = int(row['accommodates']) if row['accommodates'] else 0
            bedrooms = int(row['bedrooms']) if not pd.isnull(row['bedrooms']) else 0
            bathrooms = int(row['bathrooms']) if not pd.isnull(row['bathrooms']) else 0
            license = row['license'] if pd.notnull(row['license']) else 'Not Available'
            has_availability = True if row['has_availability'] == 't' else False
            amenities = row['amenities'][1:len(row['amenities'])-1] if pd.notnull(row['amenities']) else 'Not Available'
            neighbourhood = row['neighbourhood_cleansed']
            property_type = row['property_type']
            room_type = row['room_type']

            # Query the Neighbourhoods table to get the appropriate id.
            cursor = connection.cursor()
            cursor.execute("SELECT neighbourhood_id FROM Neighbourhoods WHERE name = %s", neighbourhood)
            result = cursor.fetchone()

            if not result:
                print(neighbourhood, "does not exist in table")
                continue
            
            listing_neighbourhood_id = result['neighbourhood_id']

            # Query the PropertyTypes table to get the appropriate name.
            cursor.execute("SELECT property_type_name FROM PropertyTypes WHERE property_type_name = %s", property_type)
            result = cursor.fetchone()

            if not result:
                print(property_type, "does not exist in table")
                continue

            property_type_name = result['property_type_name']

            # Query the RoomTypes table to get the appropriate name.
            cursor.execute("SELECT room_type_name FROM RoomTypes WHERE room_type_name = %s", room_type)
            result = cursor.fetchone()

            if not result:
                print(room_type,  "does not exist in table")
                continue

            room_type_name = result['room_type_name']

            # Create the user.
            user_name = re.sub(r"[^a-zA-Z0-9]+", " ", host_name.replace(" ","")).lower()
            password = user_name + "@123"
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            email = user_name + str(host_id) + "@airbnb.com"

            check_user = "SELECT user_id from Users where email = %s"
            cursor.execute(check_user, email)
            user_id_check = cursor.fetchone()
            if not user_id_check:
                try:
                    sql = "INSERT INTO Users(name, password_hash, email) VALUES (%s,%s,%s)"
                    cursor = connection.cursor()
                    cursor.execute(sql, (host_name, password_hash, email))
                    connection.commit()
                    # Get the user_id of the inserted user
                    user_id = cursor.lastrowid
                    print(f"Inserted user {user_id} into Users table successfully!")
                except pymysql.IntegrityError as e:
                    print(f"Tried to insert duplicate value into Users table: \n Reason: {e}")
                except pymysql.Error as e:
                    print(f"Error occurred while inserting user {host_id} into Users table: {e}")

                # Insert the host into the Hosts table.
                try:
                    sql = "INSERT INTO Hosts(user_id, host_about, host_location, host_neighbourhood, host_is_superhost, host_total_listings_count) VALUES(%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (user_id, host_about, host_location, host_neighbourhood_id, host_is_superhost, host_total_listings_count))
                    connection.commit()
                    print(f"Inserted host {user_id} into Hosts table successfully!")
                except pymysql.IntegrityError as e:
                    print(f"Tried to insert duplicate value into Hosts table : \n Reason: {e}")
                except pymysql.Error as e:
                    print(f"Error occurred while inserting host {host_id} into Hosts table: {e}")
            else:
                user_id = user_id_check['user_id']
            # Insert the listing into the Listings table.
            try:
                sql = "INSERT INTO Listings(name, price, latitude, longitude, minimum_nights, maximum_nights, description, occupancy, bedrooms, bathrooms, license, has_availability, host_id, amenities, neighbourhood_id, property_type_name, room_type_name) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (name, price, latitude, longitude, minimum_nights, maximum_nights, description, occupancy, bedrooms, bathrooms, license, has_availability, user_id, amenities, listing_neighbourhood_id, property_type_name, room_type_name))
                connection.commit()
                print(f"Inserted listing {name} into Listings table successfully!")
            except pymysql.IntegrityError as e:
                print(f"Tried to insert duplicate value into Listings table: \n Reason: {e}")
            except pymysql.Error as e:
                print(f"Error occurred while inserting listing {index} into Listings table: {e}")
      
    else:
        print("Invalid Option")

    # commit the transaction to the database
    connection.commit()
    cursor.close()

    # Close the database connection
    connection.close()