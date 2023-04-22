import streamlit as st
import datetime
import pymysql
from turtle import title
import pandas as pd
from bs4 import BeautifulSoup


def view_listing(record):
    cols = ['Name', 'Price', 'Latitude', 'Longitude', 'Maximum nights', 'Minimum nights','Description', 'Occupancy','Bedrooms', 'Bathrooms','Amenities', 'Room type name', 'Property type name', 'Has availability']
    record = record[cols]
    record['Description'] = BeautifulSoup(record['Description'], 'html.parser').get_text()
    st.table(record)   

def view_user_listings(connection):
    with connection.cursor() as cursor:
        # Retrieve all neighborhoods from Neighbourhoods table
        sql = "SELECT neighbourhood_id, name FROM Neighbourhoods"
        cursor.execute(sql)
        neighborhoods = cursor.fetchall()
        
    # Create a list of neighborhood names to use for dropdown menu
    neighborhood_names = [neighborhood['name'] for neighborhood in neighborhoods]

    # Display dropdown menu of neighborhoods
    selected_neighborhood = st.selectbox("Select Neighborhood", neighborhood_names)

    # Get neighborhood_id based on selected neighborhood name
    neighborhood_id = next(item for item in neighborhoods if item["name"] == selected_neighborhood)['neighbourhood_id']

    # Retrieve all listings in the selected neighborhood
    with connection.cursor() as cursor:
        sql = "SELECT * FROM Listings WHERE neighbourhood_id = %s"
        # sql = "SELECT * FROM Listings WHERE neighbourhood_id = %s"
        cursor.execute(sql, (neighborhood_id,))
        listings = cursor.fetchall()

    if listings:
        st.markdown("<h3>Available Listings</h3>", unsafe_allow_html=True)
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
    
def book_listing(connection):
    with connection.cursor() as cursor:
        # Retrieve all neighborhoods from Neighbourhoods table
        sql = "SELECT neighbourhood_id, name FROM Neighbourhoods"
        cursor.execute(sql)
        neighborhoods = cursor.fetchall()

    st.markdown("<h3>Select Filters</h3>", unsafe_allow_html=True)
    # Create a list of neighborhood names to use for dropdown menu
    neighborhood_names = [neighborhood['name'] for neighborhood in neighborhoods]

    # Display dropdown menu of neighborhoods
    selected_neighborhood = st.selectbox("Select Neighborhood", neighborhood_names)

    # Get neighborhood_id based on selected neighborhood name
    neighborhood_id = next(item for item in neighborhoods if item["name"] == selected_neighborhood)['neighbourhood_id']

    # Get search criteria from user
    min_price = st.number_input("Minimum Price", min_value=0, max_value=10000, value=0)
    max_price = st.number_input("Maximum Price", min_value=0, max_value=10000, value=2000)
    checkin_date = st.date_input("Check-in Date")
    checkout_date = st.date_input("Check-out Date")

    # Search for available listings based on the search criteria
    with connection.cursor() as cursor:
        cursor.callproc('search_listings', (neighborhood_id, min_price, max_price, checkin_date, checkout_date))
        available_listings = cursor.fetchall()

    if available_listings:
        st.markdown("<h3>Available Listings</h3>", unsafe_allow_html=True)
        listings_df = pd.DataFrame(available_listings)
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


        # Select listing to book
        selected_listing = st.selectbox("Select Listing to Book", [listing['name'] for listing in available_listings])

        # Get listing_id based on selected listing name
        try:
            listing_id = next(item for item in available_listings if item["name"] == selected_listing)['listing_id']
        except StopIteration:
            st.error("Selected listing is not available during selected dates.")
            return

        # Check if listing is available during selected dates
        with connection.cursor() as cursor:
            sql = "SELECT * FROM Listings WHERE listing_id = %s AND has_availability = TRUE"
            cursor.execute(sql, (listing_id,))
            available_listing = cursor.fetchone()

        # Create booking in Bookings table if listing is available
        if available_listing is not None:
            # Get booking name from user
            booking_name = st.text_input("Booking Name")
            if st.button("Book Now"):
                if booking_name.strip() == "":
                    st.write("Listing name cannot be empty!")
                else:
                    try:
                        with connection.cursor() as cursor:
                            sql = "INSERT INTO Bookings (user_id, listing_id, checkin_date, checkout_date, booking_name) VALUES (%s, %s, %s, %s, %s)"
                            cursor.execute(sql, (st.session_state.user_id, listing_id, checkin_date, checkout_date, booking_name))
                            connection.commit()
                        
                        st.success("Booking created!")
                    except pymysql.err.IntegrityError as e:
                        if e.args[0] == 1062:
                            st.write("Booking with same name exists!.")
    else:
        st.markdown("<h2>No listings!</h2>", unsafe_allow_html=True)

def view_user_bookings(connection):
    user_id = st.session_state.user_id
    with connection.cursor() as cursor:
        # Retrieve all bookings for the given user from Bookings table
        sql = "SELECT * FROM Bookings WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        bookings = cursor.fetchall()

    if bookings:
        st.markdown("<h3>My Bookings</h3>", unsafe_allow_html=True)
        bookings_df = pd.DataFrame(bookings)
        cols_rename = [' '.join(c.capitalize().split('_')) for c in bookings_df.columns]
        bookings_df.columns = cols_rename
        cols = st.columns((1, 3, 3, 3, 5))
        fields = ["No.","Booking Name","Check-in Date","Check out Date", ""]
        for col, field_name in zip(cols, fields):
            col.write(field_name)
        
        for idx in bookings_df.index:
            col1, col2, col3, col4, col5 = st.columns((1, 3, 3, 3, 5))
            col1.write(idx+1)
            col2.write(bookings_df['Booking name'][idx])
            col3.write(bookings_df['Checkin date'][idx])
            col4.write(bookings_df['Checkout date'][idx])
            view_button = col5.empty()
            action = view_button.button("View", key=idx)

            if action:
                with connection.cursor() as cursor:
                    sql = "SELECT b.booking_name, b.checkin_date, b.checkout_date, l.name, l.price, l.latitude, l.longitude, l.description, l.occupancy, l.bedrooms, l.bathrooms, l.amenities, l.property_type_name, l.room_type_name FROM Listings l JOIN Bookings b ON l.listing_id = b.listing_id WHERE b.listing_id = %s"
                    cursor.execute(sql, bookings_df.loc[idx]['Listing id'])
                    result = cursor.fetchall()

                # Call view_booking function outside of the "with" block
                st.table(result[0])

    else:
        st.markdown("<h2>You have no bookings!</h2>", unsafe_allow_html=True)

def cancel_booking(connection):
    user_id = st.session_state.user_id
    with connection.cursor() as cursor:
        # Retrieve all bookings for the given user from Bookings table
        sql = "SELECT * FROM Bookings WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        bookings = cursor.fetchall()


    # Display the guest's bookings and allow them to select one to cancel
    if bookings:
        options = {f"{booking['booking_name']}" : booking for booking in bookings}
        selected_option = st.selectbox("Select a booking to cancel:", list(options.keys()))

        # Confirm deletion before proceeding
        if st.button("Cancel Booking"):
            with connection.cursor() as cursor:
                sql = "DELETE FROM Bookings WHERE booking_id = %s"
                cursor.execute(sql, options[selected_option]["booking_id"])
                connection.commit()

            st.success("Booking Cancelled.")
    else:
        st.markdown("<h2>You have no bookings!</h2>", unsafe_allow_html=True)

def post_review(connection):
    with connection.cursor() as cursor:
        # Retrieve all bookings made by the user
        sql = "SELECT * FROM Bookings WHERE user_id = %s"
        cursor.execute(sql, (st.session_state.user_id,))
        bookings = cursor.fetchall()

    if bookings:
        # Display dropdown menu of bookings made by the user
        selected_booking = st.selectbox("Select Booking to Review", [f"{booking['booking_name']}" for booking in bookings])

        # Get booking_id based on selected booking date range
        booking_id = next(item for item in bookings if f"{item['booking_name']}" == selected_booking)['booking_id']

        # Get user's rating and review text
        rating = st.slider("Rating (out of 5)", min_value=1, max_value=5)
        review_text = st.text_input("Review Text")

        # Create review in Reviews table
        if st.button("Post"):
            with connection.cursor() as cursor:
                sql = "INSERT INTO Reviews (user_id, booking_id, rating, review_comment) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (st.session_state.user_id, booking_id, rating, review_text))
                connection.commit()

            st.success("Review posted!")
    else:
        st.markdown("<h2>You have no bookings!</h2>", unsafe_allow_html=True)


def view_reviews(connection):
    with connection.cursor() as cursor:
        # Retrieve all neighborhoods from Neighbourhoods table
        sql = "SELECT neighbourhood_id, name FROM Neighbourhoods"
        cursor.execute(sql)
        neighborhoods = cursor.fetchall()
        
    # Create a list of neighborhood names to use for dropdown menu
    neighborhood_names = [neighborhood['name'] for neighborhood in neighborhoods]

    # Display dropdown menu of neighborhoods
    selected_neighborhood = st.selectbox("Select Neighborhood", neighborhood_names)

    # Get neighborhood_id based on selected neighborhood name
    neighborhood_id = next(item for item in neighborhoods if item["name"] == selected_neighborhood)['neighbourhood_id']

    # Retrieve all listings in the selected neighborhood
    with connection.cursor() as cursor:
        sql = "SELECT * FROM Listings WHERE neighbourhood_id = %s"
        cursor.execute(sql, (neighborhood_id,))
        listings = cursor.fetchall()

    if listings:
        selected_listing = None
        if listings:
            selected_listing = st.selectbox("Select Listing", [listing['name'] for listing in listings])

        # Get listing_id based on selected listing name
        listing_id = None
        if selected_listing:
            listing_id = next(item for item in listings if item["name"] == selected_listing)['listing_id']

        with connection.cursor() as cursor:
            # Select all reviews for a given listing and calculate the average rating
            sql = """
                SELECT r.*, avg_listing_rating(l.listing_id) AS avg_rating 
                FROM Reviews r 
                INNER JOIN Bookings b ON r.booking_id = b.booking_id 
                INNER JOIN Listings l ON b.listing_id = l.listing_id 
                WHERE l.listing_id = %s
            """
            cursor.execute(sql, (listing_id,))
            reviews = cursor.fetchall()

        if reviews:
            # Display reviews in a table
            st.table(reviews)

        else:
            st.markdown("<h2>This listing has no reviews!</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2>No listings!</h2>", unsafe_allow_html=True)