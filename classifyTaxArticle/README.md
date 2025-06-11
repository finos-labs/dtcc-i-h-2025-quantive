# Article Classification Lambda Function

This AWS Lambda function processes text files uploaded to S3, summarizes the article content, analyzes its business impact, classifies it into a relevant category, and stores the result in DynamoDB. It uses the Claude Haiku model via Amazon Bedrock for summarization, impact assessment, and classification.

## Technologies Used

- Amazon S3: To receive article text uploads and retrieve configuration files.
- Amazon DynamoDB: To store the processed results.
- Amazon Bedrock: To access Claude Haiku for NLP processing.
- AWS Lambda: Serverless compute for processing uploaded articles.
- Python & Boto3: For implementation and AWS interactions.

## Environment Variables

- `CATEGORY_TABLE`: DynamoDB table name where classification data will be stored.
- `CATEGORY_BUCKET`: S3 bucket containing the classification categories file.
- `CLASSIFICATION_CATEGORIES_FILE`: Path to the classification categories file in the bucket&#x20;
- `HAIKU_MODEL_ID`: Model ID for Claude Haiku deployed in Amazon Bedrock.

## Function Workflow

1. **Trigger**: Invoked when a file is uploaded to S3.
2. **Skip Check**: If the uploaded file is from the `metadata/` folder, skip processing.
3. **Text Extraction**: Download and extract up to 4000 characters of the article text.
4. **Category Loading**: Load the list of valid classification categories from the provided S3 file.
5. **Summarization**: Generate a concise summary of the article using Claude Haiku.
6. **Impact Analysis**: Categorize the article's impact as Critical, High, Medium, or Low.
7. **Classification**: Assign the article to one category from the loaded list.
8. **Persistence**: Store the key, summary, impact, category, and source bucket in DynamoDB.

## IAM Permissions Required

- `s3:GetObject`
- `dynamodb:PutItem`
- `bedrock:InvokeModel`
