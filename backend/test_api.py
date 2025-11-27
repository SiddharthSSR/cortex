#!/usr/bin/env python3
"""Test the chat API."""

import requests
import json

url = "http://localhost:8000/api/chat/completions"

payload = {
    "messages": [
        {"role": "user", "content": "Say only: I am working correctly!"}
    ],
    "max_tokens": 30,
    "temperature": 0.7
}

print("Sending request to:", url)
print("Payload:", json.dumps(payload, indent=2))
print("\nWaiting for response...")

response = requests.post(url, json=payload)

print(f"\nStatus Code: {response.status_code}")
print("\nResponse:")
print(json.dumps(response.json(), indent=2))
