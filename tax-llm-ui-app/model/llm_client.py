import boto3
import json
import re
import requests

def remove_pii(query: str) -> str:
    try:
        response = requests.post("http://localhost:5000/redact", json={"text": query})
        response.raise_for_status()

        print(response.json())

        return response.json().get("redacted_text", query)
    except Exception as e:
        print(f"PII remover failed: {e}")
        return query


def query_llm(history_text, user_query):

    #cleaned_user_query = remove_pii(user_query)

    client = boto3.client("lambda", region_name="us-west-2")
    payload = {
        "chat_history": history_text,
        "query": user_query
    }

    response = client.invoke(
        FunctionName="arn:aws:lambda:us-west-2:730356633374:function:taxLLMRAGFunction",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )

    response_payload = json.loads(response["Payload"].read().decode())

    if response_payload.get("statusCode") == 200:
        body_str = response_payload["body"]
        
        body = json.loads(body_str)
        
        answer = body.get("answer", "").replace("\\n", "\n")
        used_docs = body.get("used_documents", [])
        updated_history = body.get("chat_history", [])

        answer = re.sub(r'\n\s*\n+', '\n', answer.strip())

        #output = answer + "\n\n\nSource(s):\n" + "\n".join(used_docs)
        return answer, body.get("source_links", [])

    return "No response from model.", []
