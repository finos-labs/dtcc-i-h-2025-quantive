import streamlit as st
from utils.aws_session import get_boto3_resource
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamodb = get_boto3_resource("dynamodb")
alerts_table = dynamodb.Table('ArticleClassifications')

def fetch_alerts_for_user(subscribed_categories):
    try:
        if not subscribed_categories:
            return []

        filter_expression = Attr('Category').is_in(subscribed_categories)
        response = alerts_table.scan(FilterExpression=filter_expression)
        items = response.get('Items', [])

        return items

    except ClientError as e:
        st.error(f"Error fetching alerts: {e}")
        return []

def alerts_ui(user_id, user_subscriptions):
    if not user_subscriptions:
        st.info("You're not subscribed to any categories. Subscribe on the right to start receiving alerts.")
        return

    alerts = fetch_alerts_for_user(user_subscriptions)

    if not alerts:
        st.write("No alerts to show yet.")
        return

    

    impact_colors = {
        'Critical': 'rgba(255, 99, 132, 0.18)',
        'High': 'rgba(220, 53, 69, 0.14)',
        'Medium': 'rgba(255, 193, 7, 0.14)',
        'Low': 'rgba(23, 162, 184, 0.14)'
    }

    impact_priority = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}

    alerts.sort(
        key=lambda x: (
            impact_priority.get(x.get('Impact', 'Low'), 3),
            x.get('timestamp', '')
        ),
        reverse=False
    )
    
    alerts = alerts[:75]

    if not alerts:
        st.info("No alerts match your selected filters.")
        return

    with st.container(height=600):
        impact_filter = st.selectbox("Filter by impact:", options=["All", "Critical", "High", "Medium", "Low"], key="impact_filter")
        if impact_filter != "All":
            alerts = [a for a in alerts if a.get('Impact', 'Low') == impact_filter]
            
        for alert in alerts:
            impact = alert.get('Impact', 'Low')
            bg_color = impact_colors.get(impact, '#f0f0f0')

            st.markdown(
                f"""
                <div style="background-color: {bg_color}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <strong>Category:</strong> {alert['Category']}<br>
                    <strong>Impact:</strong> {impact}<br>
                    <strong>Summary:</strong> {alert['Summary']}<br>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("---")
