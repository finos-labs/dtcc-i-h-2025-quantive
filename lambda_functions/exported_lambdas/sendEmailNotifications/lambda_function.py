import boto3
from boto3.dynamodb.conditions import Attr
import os

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
user_table = dynamodb.Table('UserTaxNewsSubscriptions')

def lambda_handler(event, context):

    for record in event['Records']:
        
        if record['eventName'] != 'INSERT':
            continue
        
        new_item = record['dynamodb']['NewImage']
        category = new_item.get('Category', {}).get('S')
        summary = new_item.get('Summary', {}).get('S', 'No summary provided')

        if not category:
            print("Missing 'Category' in new item.")
            continue

        # Scan for users subscribed to this category
        response = user_table.scan(
            FilterExpression=Attr('subscriptionCategories').contains(category)
            )

        print("Scan response items:", response.get('Items'))
        emails = [item['emailID'] for item in response.get('Items', [])]

        print("Emails to send to:", emails)
        for email in emails:
            print("Sending email to:", email)
            response=send_email(email, category, summary)
            print("SES response:", response)

    return {'statusCode': 200, 'body': 'Notifications sent'}

def send_email(recipient, category, summary):
    ses.send_email(
        Source='quantive8@gmail.com',  # Replace with verified SES sender
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': f'New Update: {category}'},
            'Body': {
                'Text': {
                    'Data': f'A new article has been classified under "{category}".\n\nSummary:\n{summary}'
                }
            }
        }
    )
