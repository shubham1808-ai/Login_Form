import streamlit as st
from pymongo import MongoClient
import bcrypt

MONGO_URL="mongodb+srv://shubhamdalal612:aXJogK6ewAHMyvA0@cluster0.a8ldobb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)

db = client["Login_Form"]
user_collection=db["login"]

def check_user(username,password):
    user=user_collection.find_one({"username": username})
    if user:
        return user["password"]==password
    return False

def create_user(username,password):
    if user_collection.find_one({"username":username}):
        return False
    user_collection.insert_one({"username":username,"password":password})
    return True


st.set_page_config(page_title="Login App", layout="centered")
# st.sidebar.title("Options")

tab=st.sidebar.radio("Select an option", ("Login", "SignUp"))

st.title("Login & SignUp Form")

if tab=="Login":
    st.subheader("Login Here")
    username=st.text_input("Username",key="login_username")
    password=st.text_input("Password",key="login_password",type="password")

    if st.button("Login"):
        if check_user(username,password):
            st.success("Login Successful")
            st.write(f"Welcome {username}")
        else:
            st.error("Invalid Username or Password")

elif tab=="SignUp":
    st.subheader("Create Account")
    new_username=st.text_input("New Username",key="signup_username")
    new_password=st.text_input("New Password",key="signup_password",type="password")

    if st.button("SignUp"):
        if create_user(new_username,new_password):
            st.success("Signup Successful! You can login now.")
        else:
            st.error("Username already exists. Please try a different one.")

