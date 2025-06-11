# sendEmailNotifications Lambda

This AWS Lambda function listens to new article classifications in a DynamoDB table and sends email notifications to users who have subscribed to relevant tax news categories.

---

## Configuration Notes

- DynamoDB Tables:
  - `ArticleClassifications`: Should have a stream enabled for INSERT events.
  - `UserTaxNewsSubscriptions`: Must contain `emailID` and `subscriptionCategories`.

- SES Configuration:
  - Update `Source` in `send_email()` with a verified SES email address.

- IAM Role Requirements:
  - `dynamodb:Scan` (for reading subscriptions)
  - `ses:SendEmail` (to dispatch notifications)

- Environment Setup:
  - Ensure the Lambda has permissions and proper environment variables if required.
  
---

## Technologies Used

- Amazon DynamoDB: Stores user subscriptions and newly classified articles.
- Amazon SES (Simple Email Service): Sends email alerts to subscribed users.
- AWS Lambda: Serverless compute to handle real-time notification logic.
- Python & Boto3: For implementation and AWS service interactions.

---

## Function Overview

### Trigger
- DynamoDB Stream: Invoked when a new item is inserted into the `ArticleClassifications` table.

### Input (event)
- event.Records: Contains new DynamoDB INSERT records.
  - Each record is expected to contain:
    - `Category` (string): Topic under which the article is classified.
    - `Summary` (string, optional): Brief description of the article.

### Output
- Sends emails to all users subscribed to the detected category.

---

## Key Logic Steps

1. Handle INSERT Events only:
   - Skips any non-INSERT DynamoDB stream events.

2. Extract Metadata from new classification:
   - Pulls `Category` and `Summary` fields.

3. Scan User Subscriptions:
   - Finds users whose `subscriptionCategories` list contains the new category.

4. Send Emails via SES:
   - Sends an alert email to each matched user.