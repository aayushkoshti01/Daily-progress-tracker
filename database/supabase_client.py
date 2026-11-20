
import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def get_config(key):
    # First try Streamlit Cloud secrets
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    # Fall back to local .env file
    return os.getenv(key)


SUPABASE_URL = get_config("SUPABASE_URL")
SUPABASE_KEY = get_config("SUPABASE_KEY")


def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase URL or publishable key is missing."
        )

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    session_data = st.session_state.get("auth_session")

    if session_data:
        client.auth.set_session(
            session_data["access_token"],
            session_data["refresh_token"]
        )

    return client
