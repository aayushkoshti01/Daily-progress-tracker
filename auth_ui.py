
import streamlit as st
from database.auth import sign_up, sign_in, sign_out, is_logged_in


def show_auth_page():

    # AK Branding
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="
                font-size: 42px;
                font-weight: 800;
                letter-spacing: 4px;
                color: #4F8BF9;
            ">
                AK
            </div>
            <div style="
                font-size: 14px;
                color: beige;
                margin-top: -5px;
            ">
                Made by Aayush Koshti
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.title("Daily Progress Tracker")
    st.subheader("Welcome! Please log in or create an account.")

    if is_logged_in():
        st.success(f"Logged in as {st.session_state['user']['email']}")

        if st.button("Logout"):
            sign_out()
            st.rerun()

        return True

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")

        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            if not login_email or not login_password:
                st.warning("Please enter your email and password.")

            else:
                try:
                    sign_in(login_email, login_password)
                    st.success("Login successful!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Login failed: {e}")

    with tab2:
        st.subheader("Create Account")

        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button("Sign Up", use_container_width=True):

            if not signup_email or not signup_password:
                st.warning("Please fill in all fields.")

            elif signup_password != confirm_password:
                st.error("Passwords do not match.")

            elif len(signup_password) < 6:
                st.warning("Password must contain at least 6 characters.")

            else:
                try:
                    response = sign_up(signup_email, signup_password)

                    if response.session:
                        sign_in(signup_email, signup_password)
                        st.success("Account created successfully!")
                        st.rerun()

                    else:
                        st.success(
                            "Account created! Please verify your email "
                            "before logging in."
                        )

                except Exception as e:
                    st.error(f"Sign up failed: {e}")

    return False
