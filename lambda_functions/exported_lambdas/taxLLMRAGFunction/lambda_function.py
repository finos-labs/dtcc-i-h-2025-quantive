import json
import boto3

kendra_index_id = "f1d2e48a-3598-4be9-b830-ed715a49e06b"
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
kendra = boto3.client("kendra", region_name="us-west-2")

model_ref = "anthropic.claude-3-5-sonnet-20240620-v1:0"

def lambda_handler(event, context):
    try:
        user_question = event.get("query", "Explain capital gains tax")
        chat_history = event.get("chat_history", [])  # List of {"user": "...", "ai": "..."} dicts

        # Step 1: Query Kendra
        kendra_response = kendra.query(
            IndexId=kendra_index_id,
            QueryText=user_question,
            PageNumber=1
        )

        # Step 2: Extract top passages
        top_chunks = []
        sources_links = []
        for result in kendra_response.get("ResultItems", [])[:3]:
            print(result)
            if "DocumentExcerpt" in result and result["DocumentExcerpt"]["Text"]:
                top_chunks.append(result["DocumentExcerpt"]["Text"].strip())

                try:
                    for attrib in result["DocumentAttributes"]:
                        if attrib["Key"] == "_source_uri" and attrib["Value"]["StringValue"].startswith("https") and not attrib["Value"]["StringValue"].startswith("https://quantive-tax-llm-bucket"):
                            sources_links.append(attrib["Value"]["StringValue"])
                except Exception as e:
                    print(f"Error extracting source link: {e}")
                    

        context_text = "\n\n".join(top_chunks) or "No Kendra context available."

        # Step 3: Build chat context string
        history_text = ""
        for turn in chat_history[-3:]:  # Only keep last 3 turns for brevity
            history_text += f"User: {turn['user']}\nAI: {turn['ai']}\n"

        # Step 4: Construct prompt
        claude_prompt = f"""
Use the following information from internal documents to answer the user's question. If unsure, say "I don't know".
If any personal identifiers (PAN, Aadhaar, account numbers) are present, redact them as [REDACTED].
Do not generate speculative advice. Stick to document facts.
If the user asks for the latest or recent data, prioritize the most recent information available.
If the information is outdated or historical, clearly mention that it is from the past and specify the relevant date or time period if available.

Chat History:
{history_text}

Context:
{context_text}

Current User Question: {user_question}

"""

        payload = {
            "messages": [
                {"role": "user", "content": claude_prompt}
            ],
            "max_tokens": 600,
            "temperature": 0.5,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        }

        # Step 5: Call Claude
        response = bedrock.invoke_model(
            modelId=model_ref,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )

        model_output = json.loads(response["body"].read().decode())
        answer = model_output["content"][0]["text"]

        # Step 6: Append to chat history (to be returned to UI for future reuse)
        chat_history.append({
            "user": user_question,
            "ai": answer
        })

        return {
            "statusCode": 200,
            "body": json.dumps({
                "answer": answer,
                "source_links": sources_links,
                "used_documents": top_chunks,
                "chat_history": chat_history  # Return updated history to client
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
