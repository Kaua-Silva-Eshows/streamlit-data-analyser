import streamlit as st
import jwt
import datetime
import secrets

SECRET_KEY = st.secrets["general"]["SECRET_KEY"]

def encode_jwt(user_data):
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),  # Token expira em 1 dia
        "iat": datetime.datetime.utcnow(),
        "sub": user_data
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None