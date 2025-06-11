# taxLLMRAGFunction Lambda Function (Kendra + Bedrock Claude)

This AWS Lambda function provides answers to user questions by retrieving relevant documents from **Amazon Kendra** and generating responses using **Claude 3.5 Sonnet** via **Amazon Bedrock**.

---

##  Technologies Used

- **Amazon Kendra**: To retrieve relevant documents based on the user's query.
- **Amazon Bedrock**: To invoke Claude 3.5 Sonnet for generating answers.
- **AWS Lambda**: To host and run the function serverlessly.
- **Python & Boto3**: For implementation and AWS service interactions.

---

##  Function Overview

### Input (`event`)
- `query` *(string)*: The user's current question. *(default: "Explain capital gains tax")*

### Output
- `answer` *(string)*: Claude's response based on Kendra documents.
- `source_links` *(list)*: URLs of the source documents used.

---

##  Key Logic Steps

1. **Query Kendra** using the provided user query.
2. **Extract Top 3 Passages** from Kendra search results.
3. **Construct Prompt** including:
   - User's last 3 turns from chat history.
   - Extracted document context.
   - Safety instructions (redaction, no speculation, time-awareness).
4. **Invoke Claude 3.5 Sonnet** via Amazon Bedrock with the constructed prompt.
5. **Parse and Return Response** along with sources and updated chat history.

---

##  Configuration Notes

- `kendra_index_id` must match your deployed Kendra index.
- `model_ref` should align with the Claude model ID in Bedrock (`anthropic.claude-3-5-sonnet-20240620-v1:0`).
- Ensure the Lambda has necessary IAM permissions:
  - `kendra:Query`
  - `bedrock:InvokeModel`

