import streamlit as st
from guest_crud import view_user_listings, book_listing, view_user_bookings, cancel_booking, post_review, view_reviews
from host_crud import view_host_listings, edit_host_listings, create_host_listings, delete_host_listings
from logout import logout

def welcome(connection):
    st.markdown(f"<h1>HELLO {st.session_state.user_email}!</h1>", unsafe_allow_html=True)
    if st.session_state.get("logged_in"):
        if st.button("Logout"):
            logout()

    with connection.cursor() as cursor:
        sql = "SELECT * FROM hosts WHERE user_id=%s"
        cursor.execute(sql, (st.session_state.user_id))
        host = cursor.fetchone()
        if host:
            choice = st.sidebar.radio("Please select an option", ("View Listings", "Create Listings", 
                                                                  "Edit Listings", "Delete Listings"))
            if choice == "View Listings":
                view_host_listings(connection)
            elif choice == "Create Listings":
                create_host_listings(connection)
            elif choice == "Edit Listings":
                edit_host_listings(connection)
            elif choice == "Delete Listings":
                delete_host_listings(connection)
            else:
                logout()
        else:
            choice = st.sidebar.radio("Please select an option", ("View All Listings", "Book Listings", 
                                                                  "View My Bookings", "Cancel Booking", 
                                                                  "Post Review", "View Reviews"))
            if choice == "View All Listings":
                view_user_listings(connection)
            elif choice == "Book Listings":
                book_listing(connection)
            elif choice == "View My Bookings":
                view_user_bookings(connection)
            elif choice == "Cancel Booking":
                cancel_booking(connection)
            elif choice == "Post Review":
                post_review(connection)
            elif choice == "View Reviews":
                view_reviews(connection)
            else:
                logout()
