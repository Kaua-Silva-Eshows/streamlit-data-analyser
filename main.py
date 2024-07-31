import streamlit as st
from utils.components import hide_sidebar
import requests
from utils.jwt_utils import *
from utils.user import *

def initialize_session_state():
    if 'jwt_token' not in st.session_state:
        st.session_state['jwt_token'] = None
        st.session_state['loggedIn'] = False
        st.session_state['user_data'] = None
        st.session_state['page'] = 'login'

def authenticate(userName: str, userPassword: str):
    login_data = {
        "username": userName,
        "password": userPassword,
        "loginSource": 1,
    }
    response = requests.post('https://api.eshows.com.br/v1/Security/Login', json=login_data).json()
    if "error" in response:
        return None
    elif response["data"]["success"]:
        return response
    else:
        return None
    
def main():
    initialize_session_state()
    if st.session_state['jwt_token']:
        user_data = decode_jwt(st.session_state['jwt_token'])
        if user_data:
            st.session_state['user_data'] = user_data
            st.session_state['loggedIn'] = True
        else:
            st.session_state['jwt_token'] = None
            st.session_state['loggedIn'] = False

    if not st.session_state['loggedIn']:
        show_login_page()
        st.stop()
    else:
        st.switch_page("pages/Home.py")

def show_login_page():
    col1, col2 = st.columns([4,1])
    col2.image("./assets/imgs/eshows-logo.png", width=100)
    col1.write("## Dashboard de dados")
    userName = st.text_input(label="", value="", placeholder="Email")
    password = st.text_input(label="", value="", placeholder="Senha", type="password")
    if st.button("login"):
        user_data = authenticate(userName, password)
        if user_data:
            st.session_state['jwt_token'] = encode_jwt(user_data)
            st.session_state['user_data'] = user_data
            st.session_state['loggedIn'] = True
            st.switch_page("pages/home.py")
            st.experimental_rerun() #Força o carreganeto da pagina
        else:
            st.error("Email ou senha inválidos!")


if __name__ == '__main__':
    st.set_page_config(
    page_title="Relatórios Eshows",
    page_icon="./assets/imgs/eshows-logo100x100.png",
    layout="centered",
    )
    
    hide_sidebar()
    main()