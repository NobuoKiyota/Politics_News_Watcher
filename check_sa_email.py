import json

try:
    with open('service_account.json', 'r') as f:
        data = json.load(f)
        print(f"Service Account Email: {data.get('client_email')}")
        print(f"Project ID: {data.get('project_id')}")
except Exception as e:
    print(f"Error reading service account: {e}")
