# pages/auth.py
import streamlit as st
from database import ExpenseTrackerDB

def show_auth_page(db: ExpenseTrackerDB):
    # ... (Copy the entire show_auth_page function here)
    tab1, tab2 = st.tabs([
        "🔑 Login",
        "📝 Sign Up"
    ])

    with tab1:
        st.markdown(
            '<h3><i class="fas fa-sign-in-alt icon"></i>Welcome Back!</h3>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Your registered username"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Your account password"
            )

            col1, col2 = st.columns([1, 2])
            with col1:
                login_button = st.form_submit_button(
                    "Login",
                    use_container_width=True,
                    type="primary"
                )

            if login_button:
                if username and password:
                    user = db.authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.markdown(
                            '<div class="alert-success"><i class="fas fa-check-circle icon"></i>Login successful! Redirecting...</div>',
                            unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown(
                            '<div class="alert-error"><i class="fas fa-exclamation-triangle icon"></i>Invalid credentials. Please try again.</div>',
                            unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div class="alert-warning"><i class="fas fa-info-circle icon"></i>Please fill in all fields.</div>',
                        unsafe_allow_html=True)

    with tab2:
        st.markdown(
            '<h3><i class="fas fa-user-plus icon"></i>Create New Account</h3>', unsafe_allow_html=True)

        with st.form("signup_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_username = st.text_input(
                    "Username",
                    placeholder="Choose a username",
                    help="Must be unique"
                )
                new_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a password",
                    help="Choose a strong password"
                )

            with col2:
                new_email = st.text_input(
                    "Email Address",
                    placeholder="your.email@example.com",
                    help="Valid email address"
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Confirm your password",
                    help="Must match your password"
                )

            signup_button = st.form_submit_button(
                "Create Account",
                use_container_width=True,
                type="primary"
            )

            if signup_button:
                if new_username and new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            if db.create_user(new_username, new_email, new_password):
                                st.markdown(
                                    '<div class="alert-success"><i class="fas fa-check-circle icon"></i>Account created successfully! Please login with your credentials.</div>',
                                    unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    '<div class="alert-error"><i class="fas fa-exclamation-triangle icon"></i>Username or email already exists. Please try different credentials.</div>',
                                    unsafe_allow_html=True)
                        else:
                            st.markdown(
                                '<div class="alert-warning"><i class="fas fa-info-circle icon"></i>Password must be at least 6 characters long.</div>',
                                unsafe_allow_html=True)
                    else:
                        st.markdown(
                            '<div class="alert-error"><i class="fas fa-exclamation-triangle icon"></i>Passwords do not match.</div>',
                            unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div class="alert-warning"><i class="fas fa-info-circle icon"></i>Please fill in all fields.</div>',
                        unsafe_allow_html=True)