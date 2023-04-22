import streamlit as st
import pandas as pd
from guest_crud import view_listing

def view_host_listings(connection):
    with connection.cursor() as cursor:
        # Retrieve the listings created by the current user from Listings table
        sql = "SELECT * FROM Listings WHERE host_id = %s"
        cursor.execute(sql, (st.session_state.user_id,))
        listings = cursor.fetchall()

    if listings:
        # # Define number of items to display per page
        # items_per_page = st.slider("Items per page", min_value=1, max_value=20, value=10)
        # # Determine number of pages
        # num_pages = len(listings) // items_per_page + (len(listings) % items_per_page > 0)
        # # Add pagination
        # page = st.number_input("Page", min_value=1, max_value=num_pages, value=1)
        # start_idx = (page - 1) * items_per_page
        # end_idx = start_idx + items_per_page
        # listings_page = listings[start_idx:end_idx]
        # # Display listings in a table
        # st.table(listings_page)
        if listings:
            st.markdown("<h3>Available Listings</h3>", unsafe_allow_html=True)
            # Add search bar for filtering listings by name, location, or other details
            search_term = st.text_input("Search listings:")
            if search_term:
                listings = [listing for listing in listings if search_term.lower() in str(listing).lower()]

            listings_df = pd.DataFrame(listings)
            cols_rename = [' '.join(c.capitalize().split('_')) for c in listings_df.columns]
            listings_df.columns = cols_rename

            cols = st.columns((1,4,2,3,3,2))
            fields = ["No.","Name","Price","Minimum Nights","Maximum Nights"," "]
            for col, field_name in zip(cols, fields):
                col.write(field_name)
            
            for idx in listings_df.index:
                col1, col2, col3, col4,col5,col6  = st.columns((1,4,2,3,3,2))
                col1.write(idx+1)
                col2.write(listings_df['Name'][idx])
                col3.write(listings_df['Price'][idx])
                col4.write(listings_df['Minimum nights'][idx])
                col5.write(listings_df['Maximum nights'][idx])
                view_button = col6.empty()
                action = view_button.button("View", key=idx)
                
                if action:
                    view_listing(listings_df.loc[idx])

    else:
        st.markdown("<h2>You have no listings!</h2>", unsafe_allow_html=True)

def create_host_listings(connection):
    listing_name = st.text_input("Listing Name", value="")
    listing_price = st.number_input("Price per night", value = 0.0)
    listing_latitude = st.number_input("Latitude", format="%.5f")
    listing_longitude = st.number_input("Longitude", format="%.5f")
    listing_min_nights = st.number_input("Minimum Nights", value=0)
    listing_max_nights = st.number_input("Maximum Nights", value=0)
    listing_desc = st.text_input("Description")
    listing_occupancy = st.number_input("Maximum Occupancy", value=0)
    listing_bedrooms = st.number_input("Bedrooms", value=0)
    listing_bathrooms = st.number_input("Bathrooms", value=0)
    listing_license = st.text_input("License")
    listing_has_availability = st.checkbox("Has Availability")
    with connection.cursor() as cursor:
        # Query all neighbourhood names from the database
        sql = "SELECT neighbourhood_id, name FROM Neighbourhoods"
        cursor.execute(sql)
        neighbourhoods = cursor.fetchall()
        neighbourhood_names = [neighbourhood['name'] for neighbourhood in neighbourhoods]

        # Retrieve all property type names from PropertyTypes table
        cursor.execute("SELECT property_type_name FROM PropertyTypes")
        property_types = cursor.fetchall()
        property_type_names = [pt['property_type_name'] for pt in property_types]

        # Retrieve all room type names from RoomTypes table
        cursor.execute("SELECT room_type_name FROM RoomTypes")
        room_type_names = [row["room_type_name"] for row in cursor.fetchall()]

        # Create the neighbourhood dropdown
        listing_neighbourhood_name = st.selectbox("Neighbourhood", neighbourhood_names)
        listing_neighbourhood_id = next(neighbourhood['neighbourhood_id'] for neighbourhood in neighbourhoods 
                                        if neighbourhood['name'] == listing_neighbourhood_name)
        listing_property_type_name = st.selectbox("Property Type", property_type_names)
        listing_room_type_name = st.selectbox("Room Type", room_type_names)

    listing_amenities = st.text_input("Amenities")

    if st.button("Create"):
        if listing_name.strip() == "":
            st.write("Listing name cannot be empty!")
        elif listing_license.strip() == "":
            st.write("License is needed!")
        else:
            with connection.cursor() as cursor:
                # Check if listing with same name already exists for this user
                sql = "SELECT COUNT(*) FROM Listings WHERE name = %s AND host_id = %s"
                cursor.execute(sql, (listing_name, st.session_state.user_id))
                result = cursor.fetchone()
                if result["COUNT(*)"] > 0:
                    st.write("A listing with the same name already exists for this user.")
                else:
                    sql = "INSERT INTO Listings (name, price, latitude, longitude, minimum_nights, maximum_nights, description, occupancy, bedrooms, bathrooms, license, has_availability, host_id, neighbourhood_id, property_type_name, room_type_name, amenities) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql, (listing_name, listing_price, listing_latitude, listing_longitude, listing_min_nights, listing_max_nights, listing_desc, listing_occupancy, listing_bedrooms, listing_bathrooms, 
                                        listing_license, listing_has_availability, st.session_state.user_id, 
                                        listing_neighbourhood_id, listing_property_type_name, listing_room_type_name, listing_amenities))
                    connection.commit()
                    st.write("Listing created!")

            

def edit_host_listings(connection):
    with connection.cursor() as cursor:
        # Retrieve all listings from Listings table for the current user
        sql = "SELECT * FROM Listings WHERE host_id = %s"
        cursor.execute(sql, st.session_state.user_id)
        listings = cursor.fetchall()

    if listings:
        # Create a list of listing names to display in the dropdown
        listing_names = [listing['name'] for listing in listings]

        # Create the listing dropdown
        st.markdown("<h5>Your Listings</h5>", unsafe_allow_html=True)
        selected_listing_name = st.selectbox("Select a listing to edit:", listing_names)

        # Get the selected listing's ID
        selected_listing_id = None
        for listing in listings:
            if listing['name'] == selected_listing_name:
                selected_listing_id = listing['listing_id']
                break

        # Get the current values of the selected listing
        selected_listing = None
        for listing in listings:
            if listing['listing_id'] == selected_listing_id:
                selected_listing = listing
                break
        st.markdown("<h5>Details</h5>", unsafe_allow_html=True)
        with connection.cursor() as cursor:
            # Query all neighbourhood names from the database
            sql = "SELECT neighbourhood_id, name FROM Neighbourhoods"
            cursor.execute(sql)
            neighbourhoods = cursor.fetchall()
            neighbourhood_names = [neighbourhood['name'] for neighbourhood in neighbourhoods]

            # Retrieve all property type names from PropertyTypes table
            cursor.execute("SELECT property_type_name FROM PropertyTypes")
            property_types = cursor.fetchall()
            property_type_names = [pt['property_type_name'] for pt in property_types]

            # Retrieve all room type names from RoomTypes table
            cursor.execute("SELECT room_type_name FROM RoomTypes")
            room_type_names = [row["room_type_name"] for row in cursor.fetchall()]

            # # Retrieve all listings from Listings table
            # cursor.execute("SELECT * FROM Listings")
            # listings = cursor.fetchall()


        # Find the selected listing and pre-fill the input fields with the existing data
        for listing in listings:
            if listing["name"] == selected_listing_name:
                listing_id = listing["listing_id"]
                listing_name = st.text_input("Listing Name", value=listing["name"])
                listing_price = st.number_input("Listing Price", value=listing["price"])
                listing_latitude = st.number_input("Listing Latitude", value=listing["latitude"])
                listing_longitude = st.number_input("Listing Longitude", value=listing["longitude"])
                listing_min_nights = st.number_input("Minimum Nights", value=listing["minimum_nights"])
                listing_max_nights = st.number_input("Maximum Nights", value=listing["maximum_nights"])
                listing_desc = st.text_input("Description", value=listing["description"])
                listing_occupancy = st.number_input("Occupancy", value=listing["occupancy"])
                listing_bedrooms = st.number_input("Bedrooms", value=listing["bedrooms"])
                listing_bathrooms = st.number_input("Bathrooms", value=listing["bathrooms"])
                listing_license = st.text_input("License", value=listing["license"])
                listing_has_availability = st.checkbox("Has Availability", value=listing["has_availability"])
                listing_neighbourhood_name = st.selectbox("Neighbourhood", neighbourhood_names)
                listing_neighbourhood_id = next(neighbourhood['neighbourhood_id'] for neighbourhood in neighbourhoods 
                                                if neighbourhood['name'] == listing_neighbourhood_name)
                listing_property_type_name = st.selectbox("Property Type", property_type_names, index=property_type_names.index(listing["property_type_name"]))
                listing_room_type_name = st.selectbox("Room Type", room_type_names, index=room_type_names.index(listing["room_type_name"]))
                listing_amenities = st.text_input("Amenities", value=listing["amenities"])

                # Update listing in the database if user clicks "Save Changes"
                if st.button("Save Changes"):
                    if listing_name.strip() == "":
                        st.write("Listing name cannot be empty!")
                    elif listing_license.strip() == "":
                        st.write("License is needed!")
                    else:
                        with connection.cursor() as cursor:
                            sql = "UPDATE Listings SET name=%s, price=%s, latitude=%s, longitude=%s, minimum_nights=%s, maximum_nights=%s, description=%s, occupancy=%s, bedrooms=%s, bathrooms=%s, license=%s, has_availability=%s, neighbourhood_id=%s, property_type_name=%s, room_type_name=%s, amenities=%s WHERE listing_id=%s"
                            cursor.execute(sql, (listing_name, listing_price, listing_latitude, listing_longitude, listing_min_nights, 
                                                listing_max_nights, listing_desc, listing_occupancy, listing_bedrooms, listing_bathrooms, 
                                                listing_license, listing_has_availability, listing_neighbourhood_id, listing_property_type_name, listing_room_type_name, listing_amenities, listing_id))
                            connection.commit()
                            st.write("Listing updated!")
    else:
        st.markdown("<h2>You have no listings!</h2>", unsafe_allow_html=True)

def delete_host_listings(connection):
    # Get the host's listings from the database
    with connection.cursor() as cursor:
        sql = "SELECT * FROM Listings WHERE host_id = %s"
        cursor.execute(sql, st.session_state.user_id)
        listings = cursor.fetchall()

    # Check if the host has any listings
    if listings:
        # Display the host's listings and allow them to select one to delete
        # st.write("Select a listing to delete:")
        options = {f"{listing['name']}" : listing for listing in listings}
        st.markdown("<h5>Your Listings</h5>", unsafe_allow_html=True)
        selected_option = st.selectbox("Select a listing to delete:", list(options.keys()))


        # Confirm deletion before proceeding
        if st.button("Delete"):
            try:
                with connection.cursor() as cursor:
                    sql = "DELETE FROM Listings WHERE listing_id = %s"
                    cursor.execute(sql, options[selected_option]["listing_id"])
                    connection.commit()
                st.success("Listing deleted.")
            except Exception as e:
                st.error(f"Error deleting listing: {e}")
    else:
        st.markdown("<h2>You have no listings!</h2>", unsafe_allow_html=True)
