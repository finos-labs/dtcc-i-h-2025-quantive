# User Subscription Lambda Function

This AWS Lambda function handles the storage of user subscription preferences in **Amazon DynamoDB**. It validates the user input and writes a new item to the designated subscription table.

---

## Technologies Used

- **Amazon DynamoDB**: To store user subscription records.
- **AWS Lambda**: To process and handle requests serverlessly.
- **Python & Boto3**: For implementation and service communication.

---

## Function Overview

### Input (`event`)
The function expects a JSON input with the following fields:
- `emailID` *(string)*
- `userID` *(string)*
- `subscriptionCategory` *(string)*
- `subscriptionValue` *(string)*

### Output
- `200 OK`: On successful storage.
- `400 Bad Request`: If required fields are missing.
- `500 Internal Server Error`: On unexpected failures.

---

## Key Logic Steps

1. Parse the event body (if not already a dictionary).
2. Validate all required fields are present.
3. Write the subscription record to the DynamoDB table specified by the `SUBSCRIPTION_TABLE` environment variable.
4. Return appropriate response status.

---

## Configuration Notes

- Set the environment variable `SUBSCRIPTION_TABLE` to your DynamoDB table name.
- Ensure the Lambda has IAM permissions for:
  - `dynamodb:PutItem`

---



