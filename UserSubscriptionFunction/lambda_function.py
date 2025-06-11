import json
import boto3
import os

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
SUBSCRIPTION_TABLE = os.environ.get('SUBSCRIPTION_TABLE')


def lambda_handler(event, context):
    try:
        body = event if isinstance(event, dict) else json.loads(event['body'])

        emailID = body.get('emailID')
        userID = body.get('userID')
        subscriptionCategory = body.get('subscriptionCategory')
        subscriptionValue = body.get('subscriptionValue')

        if not all([emailID, userID, subscriptionCategory, subscriptionValue]):
            return {
                'statusCode': 400,
                'body': json.dumps("Missing required fields")
            }

        

        table = dynamodb.Table(SUBSCRIPTION_TABLE)
        table.put_item(Item={
            'userID': userID,
            'emailID': emailID,
            'subscriptionCategory': subscriptionCategory,
            'subscriptionValue': subscriptionValue
        })

        return {
            'statusCode': 200,
            'body': json.dumps(f'Subscription stored with value: {subscriptionValue}')
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps("Internal server error")
        }
