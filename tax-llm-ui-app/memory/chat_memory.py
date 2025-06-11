from datetime import datetime
from utils.aws_session import get_boto3_resource

MAX_MESSAGE_LENGTH = 4000
MAX_CHAT_MESSAGES = 40

def truncate_message(message):
    if len(message["content"]) > MAX_MESSAGE_LENGTH:
        message["content"] = message["content"][:MAX_MESSAGE_LENGTH]
    return message

def save_chat_history(user_id, chat):
    try:
        trimmed_chat = chat[-MAX_CHAT_MESSAGES:]

        truncated_chat = [truncate_message(msg) for msg in trimmed_chat]

        table = get_chat_table()
        
        table.put_item(Item={
            "userID": user_id,
            "chat_history": trimmed_chat,
            "last_updated": datetime.utcnow().isoformat()
        })

    except Exception as e:
        print(f"[save_chat_history] Error: {e}")
        
def get_chat_table():
    dynamodb = get_boto3_resource("dynamodb")
    return dynamodb.Table("TaxLLMChatHistory")

def load_chat_history(user_id: str) -> list:
    try:
        table = get_chat_table()
        response = table.get_item(Key={"userID": user_id})
        return response.get("Item", {}).get("chat_history", [])

    except Exception as e:
        print(f"[load_chat_history] Error: {e}")
        return []