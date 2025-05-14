import streamlit as st
from pymongo import MongoClient
import os

MONGO_URL = "mongodb+srv://shubhamdalal612:aXJogK6ewAHMyvA0@cluster0.a8ldobb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)

db = client["Login_Form"]
user_collection = db["login"]

def check_user(username, password):
    user = user_collection.find_one({"username": username})
    if user:
        return user["password"] == password
    return False

def create_user(username, password):
    if user_collection.find_one({"username": username}):
        return False
    user_collection.insert_one({"username": username, "password": password})
    return True

st.set_page_config(page_title="Login App")

if "Logged_in" not in st.session_state:
    st.session_state.Logged_in = False

if st.session_state.Logged_in:
    st.title("Welcome to the Download Page")
    st.write(f"Welcome {st.session_state.username}")

    folder_path = "C:\\Users\\2328038\\Desktop\\Streamlit\\Login Form"
    files = [f for f in os.listdir(folder_path) if not f.startswith('.') and f.endswith(('.txt', '.csv', '.xlsx'))]
    selected_file = st.selectbox("Select a file to download", files)

    file_path = os.path.join(folder_path, selected_file)
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
        st.download_button(label="Download File", data=file_data, file_name=selected_file)
    except FileNotFoundError:
        st.error("File not found. Please make sure the file exists in the working directory.")

    if st.button("Back to Login"):
        st.session_state.Logged_in = False
        st.rerun()
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
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    elif tab == "SignUp":
        st.subheader("Create Account")
        new_username = st.text_input("New Username", key="signup_username")
        new_password = st.text_input("New Password", key="signup_password", type="password")

        if st.button("SignUp"):
            if create_user(new_username, new_password):
                st.success("Signup Successful! You can login now.")
            else:
                st.error("Username already exists. Please try a different one.")
