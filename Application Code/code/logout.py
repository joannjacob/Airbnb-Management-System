import streamlit as st

def logout():
    # Clear session state variables
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_id = None

    # Redirect to login page
    st.experimental_set_query_params(logged_in=False)
    st.experimental_rerun()
