import streamlit as st
import boto3
from botocore.exceptions import ClientError
from utils.aws_session import get_boto3_resource, get_boto3_client

ALL_CATEGORIES = [
    'Policy Updates',
    'Deadline Changes',
    'Global Tax Updates',
    'Litigations and Rulings',
    'Technology and Compliance Innovations',
    'Funding & Mergers and Acquisitions',
    'Security and Fraud Alerts',
    'Emerging Tech Trends'
]

def fetch_categories():
    if "categories" in st.session_state:
        return st.session_state["categories"]

    s3 = get_boto3_client("s3")
    bucket = "quantive-tax-llm-scraper-code-bucket"
    key = "categories.txt"

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        categories = [line.strip() for line in content.splitlines() if line.strip()]
        st.session_state["categories"] = categories
        return categories
    except Exception as e:
        print(f"Failed to fetch categories: {e}")
        return ALL_CATEGORIES

dynamodb = get_boto3_resource("dynamodb")
subscription_table = dynamodb.Table('UserTaxNewsSubscriptions')

def get_user_subscriptions(user_id):
    try:
        response = subscription_table.get_item(Key={'userID': user_id})
        item = response.get('Item', {})
        return item.get('subscriptionCategories', [])
    except ClientError as e:
        st.error(f"Error fetching subscriptions: {e}")
        return []

def update_user_subscriptions(user_id, email, categories):
    try:
        subscription_table.put_item(
            Item={
                'userID': user_id,
                'emailID': email,
                'subscriptionCategories': categories
            }
        )
        return True
    except ClientError as e:
        st.error(f"Error updating subscriptions: {e}")
        return False

def subscription_ui(user_id, user_email):
    current_subs = get_user_subscriptions(user_id)
    cats = fetch_categories()

    with st.container(height=600):
        selected_categories = st.multiselect(
            "Select categories you want to subscribe to:",
            options=cats,
            default=current_subs,
            key="category_selector"
        )

        if st.button("Update Subscriptions"):
            success = update_user_subscriptions(user_id, user_email, selected_categories)
            if success:
                st.success("Subscriptions updated!")
                st.rerun()  # 🔁 this triggers the alert column to refresh
            else:
                st.error("Failed to update subscriptions.")


                
