import boto3
from botocore.exceptions import ClientError
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YuliaUserTokens')

# VERY TEMPORARY STORAGE
tokens = {}

def save_user_token(user_id, provider, token_data):
    try: 
        token_data["last_updated"] = datetime.utcnow().isoformat()
        response = table.get_item(Key={"user_id": user_id })
        existing_data = response.get('Item', {})

        existing_data[provider] = token_data
        existing_data['user_id'] = user_id
        table.put_item(Item=existing_data)

    except ClientError as e:
        print(f"[DynamoDB] Error saving token for {user_id}: {e}")

def get_user_token(user_id, provider):
    try:
        response = table.get_item(Key={'user_id': user_id})
        item = response.get('Item')
        if item:
            return item.get(provider)
        return None
    except ClientError as e:
        print(f"[DynamoDB] Error getting token for {user_id}: {e}")
        return None

def get_all_users():
    try:
        response = table.scan()
        users = response.get('Items', [])
        return {u['user_id']: u for u in users}
    except ClientError as e:
        print(f"[DynamoDB] Error scanning table: {e}")
        return {}