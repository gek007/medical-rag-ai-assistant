import os

import requests
import streamlit as st
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(
    page_title="Medical RAG AI Assistant",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "username" not in st.session_state:
    st.session_state["username"] = ""
    st.session_state["password"] = ""
    st.session_state["role"] = ""
    st.session_state["logged_in"] = False


def get_auth():
    return HTTPBasicAuth(st.session_state["username"], st.session_state["password"])


def auth_ui():
    st.title("Medical RAG AI Assistant")
    st.subheader("Login or Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.get(
                f"{API_URL}/login",
                auth=HTTPBasicAuth(username, password),
            )
            if res.status_code == 200:
                user_data = res.json()
                st.session_state["username"] = username
                st.session_state["password"] = password
                st.session_state["role"] = user_data["role"]
                st.session_state["logged_in"] = True
                st.success(f"Logged in as {username} ({user_data['role']})")
                st.rerun()
            else:
                st.error(f"Login failed: {res.json().get('detail', 'Unknown error')}")

    with tab2:
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        new_role = st.selectbox("Role", ["doctor", "admin", "user"], key="signup_role")
        if st.button("Signup"):
            res = requests.post(
                f"{API_URL}/signup",
                json={"username": new_user, "password": new_pass, "role": new_role},
            )
            if res.status_code == 200:
                st.success(f"Account created for {new_user}. Please log in.")
            else:
                st.error(f"Signup failed: {res.json().get('detail', 'Unknown error')}")


def chat_ui():
    st.title("Medical RAG AI Assistant")

    with st.sidebar:
        st.write(f"Logged in as **{st.session_state['username']}**")
        st.write(f"Role: `{st.session_state['role']}`")
        if st.button("Logout"):
            for key in ["username", "password", "role", "logged_in"]:
                st.session_state[key] = "" if key != "logged_in" else False
            st.rerun()

        if st.session_state["role"] == "admin":
            st.divider()
            st.subheader("Upload Document")
            uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
            target_role = st.selectbox(
                "Assign to role", ["doctor", "admin", "user"], key="upload_role"
            )
            if st.button("Upload") and uploaded_file:
                res = requests.post(
                    f"{API_URL}/upload",
                    auth=get_auth(),
                    files={"file": (uploaded_file.name, uploaded_file, "application/pdf")},
                    data={"role": target_role},
                )
                if res.status_code == 200:
                    st.success(f"Uploaded: {uploaded_file.name}")
                else:
                    st.error(f"Upload failed: {res.json().get('detail', 'Unknown error')}")

    st.write("Ask a question based on documents available to your role.")
    question = st.text_input("Question")
    if st.button("Submit") and question:
        with st.spinner("Thinking..."):
            res = requests.post(
                f"{API_URL}/chat",
                auth=get_auth(),
                json={"question": question},
            )
        if res.status_code == 200:
            data = res.json()
            st.markdown(f"**Answer:** {data['answer']}")
            if data.get("sources"):
                st.markdown("**Sources:** " + ", ".join(data["sources"]))
        else:
            st.error(f"Error: {res.json().get('detail', 'Unknown error')}")


if st.session_state["logged_in"]:
    chat_ui()
else:
    auth_ui()
