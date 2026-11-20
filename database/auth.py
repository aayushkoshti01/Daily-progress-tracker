
import streamlit as st
from database.supabase_client import get_supabase_client


def sign_up(email, password):
    supabase = get_supabase_client()

    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })

    return response


def sign_in(email, password):
    supabase = get_supabase_client()

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    session = response.session

    if session:
        st.session_state["auth_session"] = {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token
        }

        st.session_state["user"] = {
            "id": response.user.id,
            "email": response.user.email
        }

    return response


def sign_out():
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    finally:
        st.session_state.pop("auth_session", None)
        st.session_state.pop("user", None)


def get_current_user():
    return st.session_state.get("user")


def is_logged_in():
    return get_current_user() is not None
