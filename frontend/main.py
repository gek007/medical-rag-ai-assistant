import os
import time

import requests
import streamlit as st
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_URL = os.getenv("API_URL")
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))

st.set_page_config(
    page_title="Medical RAG AI Assistant",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not API_URL:
    st.error("API_URL is not configured. Please set the API_URL environment variable.")
    st.stop()

if "username" not in st.session_state:
    st.session_state["username"] = ""
    st.session_state["password"] = ""
    st.session_state["role"] = ""
    st.session_state["logged_in"] = False
    st.session_state["last_activity"] = time.time()


def get_auth():
    return HTTPBasicAuth(st.session_state["username"], st.session_state["password"])


def parse_error(res: requests.Response, fallback: str = "Unknown error") -> str:
    try:
        detail = res.json().get("detail", fallback)
        # FastAPI 422 validation errors return detail as a list of error dicts
        if isinstance(detail, list):
            return "; ".join(e.get("msg", str(e)) for e in detail)
        return detail
    except Exception:
        return fallback


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
                timeout=30,
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
                st.error(f"Login failed: {parse_error(res)}")

    with tab2:
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        new_role = st.selectbox("Role", ["doctor", "user"], key="signup_role")
        if st.button("Signup"):
            res = requests.post(
                f"{API_URL}/signup",
                json={"username": new_user, "password": new_pass, "role": new_role},
                timeout=30,
            )
            if res.status_code == 200:
                st.success(f"Account created for {new_user}. Please log in.")
            else:
                st.error(f"Signup failed: {parse_error(res)}")


def chat_ui():
    if time.time() - st.session_state.get("last_activity", 0) > SESSION_TIMEOUT:
        st.session_state.clear()
        st.warning("Your session has expired. Please log in again.")
        st.rerun()
    st.session_state["last_activity"] = time.time()

    st.title("Medical RAG AI Assistant")

    with st.sidebar:
        st.write(f"Logged in as **{st.session_state['username']}**")
        st.write(f"Role: `{st.session_state['role']}`")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

        if st.session_state.get("role") == "admin":
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
                    files={
                        "file": (uploaded_file.name, uploaded_file, "application/pdf")
                    },
                    data={"role": target_role},
                    timeout=120,
                )
                if res.status_code == 200:
                    st.success(f"Uploaded: {uploaded_file.name}")
                else:
                    st.error(f"Upload failed: {parse_error(res)}")

    with st.sidebar:
        st.divider()
        st.subheader("Available Documents")
        try:
            docs_res = requests.get(
                f"{API_URL}/documents",
                auth=get_auth(),
                timeout=15,
            )
            if docs_res.status_code == 200:
                docs = docs_res.json().get("documents", [])
                if docs:
                    for doc in docs:
                        label = doc.get("filename", "Unknown")
                        role_tag = doc.get("role", "")
                        uploaded_at = doc.get("uploaded_at", "")[:10]
                        caption = f"Role: `{role_tag}`"
                        if uploaded_at:
                            caption += f" | {uploaded_at}"
                        st.markdown(f"**{label}**")
                        st.caption(caption)
                else:
                    st.info("No documents uploaded yet.")
            else:
                st.warning("Could not load documents.")
        except Exception:
            st.warning("Could not reach server.")

    st.write("Ask a question based on documents available to your role.")
    question = st.text_input("Question")
    if st.button("Submit") and question:
        with st.spinner("Thinking..."):
            res = requests.post(
                f"{API_URL}/chat",
                auth=get_auth(),
                json={"question": question},
                timeout=60,
            )
        if res.status_code == 200:
            data = res.json()
            st.markdown(f"**Answer:** {data['answer']}")
            if data.get("sources"):
                st.markdown("**Sources:** " + ", ".join(data["sources"]))
        else:
            st.error(f"Error: {parse_error(res)}")


if st.session_state.get("logged_in"):
    chat_ui()
else:
    auth_ui()
