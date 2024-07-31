import streamlit as st
import requests

def initialize_session_state():
    if 'jwt_token' not in st.session_state:
        st.session_state['jwt_token'] = None
        st.session_state['loggedIn'] = False
        st.session_state['user_data'] = None
        st.session_state['page'] = 'login'

def logout():
    st.cache_data.clear()
    st.session_state['loggedIn'] = False
    st.session_state['user_data'] = None