import json
import boto3
import os

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')

DDB_TABLE = os.environ.get('CATEGORY_TABLE')
HAIKU_MODEL_ID = os.environ.get('HAIKU_MODEL_ID')
CLASSIFICATION_CATEGORIES_FILE = os.environ.get('CLASSIFICATION_CATEGORIES_FILE')  # e.g. "config/classification_categories.txt"
CATEGORY_BUCKET = os.environ.get('CATEGORY_BUCKET')  # bucket where the above file is stored

MAX_INPUT_CHARS = 4000  # Approx. 1000 tokens, safe limit

def get_categories_from_s3(key):
    try:
        obj = s3_client.get_object(Bucket=CATEGORY_BUCKET, Key=key)
        content = obj['Body'].read().decode('utf-8')
        categories = [line.strip() for line in content.splitlines() if line.strip()]
        return categories
    except Exception as e:
        print(f"Error reading categories from {key}:", str(e))
        return []

def summarize_article(text):
    try:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{
                "role": "user",
                "content": f"Please summarize the following article in 3-5 concise sentences:\n\n{text}"
            }],
            "max_tokens": 500,
            "temperature": 0.5,
            "top_p": 0.9
        }

        response = bedrock.invoke_model(
            modelId=HAIKU_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body).encode("utf-8")
        )
        result = json.loads(response["body"].read().decode("utf-8"))
        return result["content"][0]["text"].strip()

    except Exception as e:
        print("Error summarizing article:", str(e))
        return "Summary unavailable"

def analyze_impact(summary):
    try:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{
                "role": "user",
                "content": (
                    "Based on the following summary, classify the impact of the article into one of these categories only: "
                    "Critical, High, Medium, Low\n\nReturn only the category:\n\n" + summary
                )
            }],
            "max_tokens": 200,
            "temperature": 0.5,
            "top_p": 0.9
        }

        response = bedrock.invoke_model(
            modelId=HAIKU_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body).encode("utf-8")
        )
        result = json.loads(response["body"].read().decode("utf-8"))
        return result["content"][0]["text"].strip()

    except Exception as e:
        print("Error analyzing impact:", str(e))
        return "Impact unavailable"

def classify_article(summary, categories):
    try:
        category_string = ", ".join(categories)
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{
                "role": "user",
                "content": (
                    f"Classify the following summarized article into one of these categories: {category_string}.\n\n"
                    f"Return only the category.\n\n{summary}"
                )
            }],
            "max_tokens": 50,
            "temperature": 0.5,
            "top_p": 0.9
        }

        response = bedrock.invoke_model(
            modelId=HAIKU_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body).encode("utf-8")
        )
        result = json.loads(response["body"].read().decode("utf-8"))
        return result["content"][0]["text"].strip().split("\n")[0].strip()

    except Exception as e:
        print("Error classifying summary:", str(e))
        return "Unknown"

def lambda_handler(event, context):
    table = dynamodb.Table(DDB_TABLE)

    # Load classification categories from S3
    classification_categories = get_categories_from_s3(CLASSIFICATION_CATEGORIES_FILE)

    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        if key.startswith('metadata/'):
            print(f"Skipping metadata file: {key}")
            continue  # Skip processing
            
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        article_text = obj['Body'].read().decode('utf-8')[:MAX_INPUT_CHARS]

        summary = summarize_article(article_text)
        impact = analyze_impact(summary)
        category = classify_article(summary, classification_categories)

        table.put_item(Item={
            'ArticleKey': key,
            'Category': category,
            'Summary': summary,
            'Impact': impact,
            'Bucket': bucket
        })

    return {
        'statusCode': 200,
        'body': json.dumps('Summary, impact, and classification saved to DynamoDB')
    }
