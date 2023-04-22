import pymysql
import streamlit as st
from login import login
from register import register
from welcome import welcome

def main():
    # Connect to the MySQL database
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="password",
        db="airbnb",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.get('logged_in', False):
        choice = st.sidebar.radio("Please select an option", ("Login", "Register"))

        if choice == "Login":
            login(connection)
        elif choice == "Register":
            register(connection)
    else:
        welcome(connection)

    connection.close()
        

if __name__ == "__main__":
    main()
