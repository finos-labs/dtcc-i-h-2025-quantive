import streamlit as st
import bcrypt
from boto3.dynamodb.conditions import Key
from utils.aws_session import get_boto3_resource

dynamodb = get_boto3_resource("dynamodb")
users_table = dynamodb.Table("TaxLLMUsers")

def get_user_email(user_id):
    try:
        response = users_table.get_item(Key={'userID': user_id})
        item = response.get('Item', {})
        return item.get('email', "")
    except ClientError as e:
        print(f"Error fetching email for user {user_id}: {e}")
        return ""

def verify_user(user_id, password):
    response = users_table.get_item(Key={"userID": user_id})
    user = response.get("Item")

    if not user:
        return False, "User not found."

    hashed_pw = user["hashed_password"].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), hashed_pw):
        return True, "Login successful."
    else:
        return False, "Incorrect password."


def create_user(user_id, email, password):
    response = users_table.get_item(Key={"userID": user_id})
    if "Item" in response:
        return False, "User already exists."

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users_table.put_item(Item={
        "userID": user_id,
        "email": email,
        "hashed_password": hashed_pw.decode("utf-8")
    })
    return True, "Signup successful."


def login_or_signup_form():
    st.markdown("## Tax Insights LLM")

    tabs = st.tabs(["Login", "Sign Up"])

    with tabs[0]:
        st.subheader("Login")
        with st.form("login_form"):
            user_id = st.text_input("User ID", placeholder="Enter your user ID")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if not user_id or not password:
                    st.warning("Please enter both User ID and Password.")
                else:
                    success, msg = verify_user(user_id, password)
                    if success:
                        st.success(msg)
                        return user_id
                    else:
                        st.error(msg)

    with tabs[1]:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            new_user_id = st.text_input("User ID", placeholder="Choose a user ID")
            email = st.text_input("Email", placeholder="Enter your email address")
            new_password = st.text_input("Password", type="password", placeholder="Create a password")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                if not new_user_id or not new_password or not email:
                    st.warning("Please fill in all fields.")
                else:
                    success, msg = create_user(new_user_id, email, new_password)
                    if success:
                        st.success(msg)
                        return new_user_id
                    else:
                        st.error(msg)

    return None