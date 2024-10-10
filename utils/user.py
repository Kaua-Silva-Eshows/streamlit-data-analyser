import streamlit as st
import requests

def logout():
    st.session_state.clear()
    st.session_state['page'] = 'login'