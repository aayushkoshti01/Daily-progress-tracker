
import streamlit as st
from database.auth import sign_up, sign_in, sign_out, is_logged_in


def show_auth_page():

    # Bottom branding styling
    st.markdown(
        """
        <style>
        .ak-footer {
            text-align: center;
            padding: 35px 10px 15px 10px;
            margin-top: 45px;
            border-top: 1px solid rgba(128, 128, 128, 0.25);
        }

        .ak-footer-logo {
            font-size: 30px;
            font-weight: 800;
            letter-spacing: 3px;
            color: #777777;
        }

        .ak-footer-text {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 2px;
            color: #888888;
            margin-top: 5px;
        }

        .ak-footer-small {
            font-size: 11px;
            color: #999999;
            margin-top: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Daily Progress Tracker")
    st.subheader("Welcome! Please log in or create an account.")

    logged_in = is_logged_in()

    if logged_in:

        st.success(
            f"Logged in as {st.session_state['user']['email']}"
        )

        if st.button("Logout"):
            sign_out()
            st.rerun()

    else:

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            st.subheader("Login")

            login_email = st.text_input(
                "Email",
                key="login_email"
            )

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

            signup_email = st.text_input(
                "Email",
                key="signup_email"
            )

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
                    st.warning(
                        "Password must contain at least 6 characters."
                    )

                else:
                    try:
                        response = sign_up(
                            signup_email,
                            signup_password
                        )

                        if response.session:
                            sign_in(signup_email, signup_password)
                            st.success("Account created successfully!")
                            st.rerun()

                        else:
                            st.success(
                                "Account created! Please verify your "
                                "email before logging in."
                            )

                    except Exception as e:
                        st.error(f"Sign up failed: {e}")

    # Bottom AK branding
    st.markdown(
        """
        <div class="ak-footer">
            <div class="ak-footer-logo">AK</div>
            <div class="ak-footer-text">
                MADE BY AAYUSH KOSHTI
            </div>
            <div class="ak-footer-small">
                Daily Progress Tracker · © 2026
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    return is_logged_in()
