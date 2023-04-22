import streamlit as st
import hashlib

def register(connection):
    # Define the registration form
    st.write("# Register")
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Password", type="password", key="password_input")
    name = st.text_input("Name", key="name_input")
    user_type = st.selectbox("Are you a host or a guest?", ("Host", "Guest"), key="user_type_input")
    
    if user_type == "Host":
        host_about = st.text_input("Tell us about yourself", key="host_about_input")
        host_location = st.text_input("Location", key="host_location_input")

        with connection.cursor() as cursor:
            # Query all neighbourhood names from the database
            sql = "SELECT neighbourhood_id, name FROM Neighbourhoods"
            cursor.execute(sql)
            neighbourhoods = cursor.fetchall()
            neighbourhood_names = [neighbourhood['name'] for neighbourhood in neighbourhoods]

        host_neighbourhood = st.selectbox("Neighbourhood", neighbourhood_names)
        # host_neighbourhood = st.text_input("Neighbourhood", key="host_neighbourhood_input")

    submitted = st.button("Register")

    # If the registration form is submitted, create a new user
    if submitted:

        # Check if the user with the same email already exists
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email=%s"
            cursor.execute(sql, (email,))
            existing_user = cursor.fetchone()

            if existing_user is not None:
                st.error("A user with this email already exists.")
            else:
                # Hash the password before storing in the database
                password_hash = hashlib.sha256(password.encode()).hexdigest()

                # Insert the new user into the database
                with connection.cursor() as cursor:
                    sql = "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (name, email, password_hash))
                    connection.commit()

                    # Get the user_id of the inserted user
                    user_id = cursor.lastrowid

                    # Insert the user into the appropriate table based on their user_type
                    if user_type == "Host":
                        # Query the Neighbourhoods table to get the appropriate id.
                        cursor = connection.cursor()
                        cursor.execute("SELECT neighbourhood_id FROM Neighbourhoods WHERE name = %s", host_neighbourhood)
                        result = cursor.fetchone()
                        host_neighbourhood_id = result['neighbourhood_id']

                        sql = "INSERT INTO Hosts (user_id, host_about, host_location, host_neighbourhood) VALUES (%s, %s, %s, %s)"
                        cursor.execute(sql, (user_id, host_about, host_location, host_neighbourhood_id))
                    elif user_type == "Guest":
                        sql = "INSERT INTO Guests (user_id) VALUES (%s)"
                        cursor.execute(sql, (user_id,))

                    connection.commit()

                # Show a success message
                st.success("You have successfully registered as a {} with email {}".format(user_type.lower(), email))
    
        cursor.close()

