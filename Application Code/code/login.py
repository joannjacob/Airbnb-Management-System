import streamlit as st
import hashlib
import os

def login(connection):
    # Define the login form
    st.write("# Login")
    email = st.text_input("Email", key=f"login-email")
    password = st.text_input("Password", type="password", key=f"login-password")
    submitted = st.button("Login", key=f"login-submit")

    # If the login form is submitted, authenticate the user
    if submitted:
        # Hash the password before querying the database
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Query the database for the user
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email=%s AND password_hash=%s"
            cursor.execute(sql, (email, password_hash))
            user = cursor.fetchone()

        # Check if the user exists
        if user is not None:
            st.session_state.logged_in = True
            st.session_state.user_email = user['email']
            st.session_state.user_id = user['user_id']
            st.success(f"Logged in as {user['email']}")
            # Redirect to another page
            query_params = {"logged_in": True}
            url = st.experimental_get_query_params()
            url["logged_in"] = True
            st.experimental_set_query_params(**url)
            st.experimental_rerun()
        else:
            st.error("Invalid email or password")
    
        cursor.close()
