import streamlit as st
import requests

def logout():
    st.cache_data.clear()
    st.session_state['loggedIn'] = False
    st.session_state['user_data'] = None