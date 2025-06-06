import streamlit as st
from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB Connection
MONGO_URL = "mongodb+srv://shubhamdalal612:aXJogK6ewAHMyvA0@cluster0.a8ldobb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)

db = client["Login_Form"]
user_collection = db["login"]
file_collection = db["files"]
activity_collection = db["actions"]  # New collection for activity logs

# Functions
def check_user(username, password):
    user = user_collection.find_one({"username": username})
    if user:
        return user["password"] == password
    return False

def create_user(name, username, email, password):
    if user_collection.find_one({"username": username}):
        return False
    user_collection.insert_one({"name": name, "username": username, "email": email, "password": password})
    return True

def upload_file(file_name, file_data):
    file_content = file_data.decode("utf-8")
    file_collection.insert_one({"filename": file_name, "data": file_content})

def log_activity(username, action, filename=None):
    activity_collection.insert_one({
        "username": username,
        "action": action,
        "filename": filename,
        "timestamp": datetime.now()
    })

# Streamlit UI
st.set_page_config(page_title="Login App")

if "Logged_in" not in st.session_state:
    st.session_state.Logged_in = False

if st.session_state.Logged_in:
    if st.button("Back to Login"):
        st.session_state.Logged_in = False
        st.rerun()

    st.title("Welcome to the Download Page")
    st.write(f"Welcome {st.session_state.username}")

    # Sidebar Activity Log
    st.sidebar.title("Activity Log")
    logs = activity_collection.find({"username": st.session_state.username}).sort("timestamp", -1)
    for log in logs:
        action_time = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        if log["action"] == "login":
            st.sidebar.write(f"Logged in at {action_time}")
        elif log["action"] == "download":
            st.sidebar.write(f"Downloaded **{log['filename']}** at {action_time}")
        elif log["action"] == "upload":
            st.sidebar.write(f"Uploaded **{log['filename']}** at {action_time}")

    # File list
    folder_path = os.getcwd()
    files = [f for f in os.listdir(folder_path) if not f.startswith('.') and f.endswith(('.txt', '.csv', '.xlsx'))]
    selected_file = st.selectbox("Select a file", files)
    file_path = os.path.join(folder_path, selected_file)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Download File")
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
            if st.download_button(label="Download File", data=file_data, file_name=selected_file):
                log_activity(st.session_state.username, "download", selected_file)
        except FileNotFoundError:
            st.error("File not found. Please make sure the file exists in the working directory.")

    with col2:
        st.subheader("Upload File to MongoDB")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            if st.button("Upload to MongoDB"):
                file_data = uploaded_file.read()
                upload_file(uploaded_file.name, file_data)
                log_activity(st.session_state.username, "upload", uploaded_file.name)
                st.success("File uploaded to MongoDB successfully!")

else:
    tab = st.sidebar.radio("Select an option", ("Login", "SignUp"))
    st.title("Login & SignUp Form")

    if tab == "Login":
        st.write("### Enter the credentials to login:")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", key="login_password", type="password")

        if st.button("Login"):
            if check_user(username, password):
                st.session_state.Logged_in = True
                st.session_state.username = username
                log_activity(username, "login")
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    elif tab == "SignUp":
        st.subheader("Create Account")
        name = st.text_input("Name", key="signup_name")
        new_username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email ID", key="signup_email")
        new_password = st.text_input("Password", key="signup_password", type="password")
        confirm_password = st.text_input("Confirm Password", key="signup_confirm_password", type="password")

        if st.button("SignUp"):
            if new_password == confirm_password:
                if create_user(name, new_username, email, new_password):
                    st.success("Signup Successful! You can login now.")
                else:
                    st.error("Username already exists. Please try a different one.")
            else:
                st.error("Passwords do not match. Please try again.")
