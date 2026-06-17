import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')
api_key = os.getenv('XAI_API_KEY')
res = requests.get('https://api.x.ai/v1/models', headers={'Authorization': f'Bearer {api_key}'})
print("AVAILABLE MODELS:")
for m in res.json().get('data', []):
    print("- " + m['id'])
