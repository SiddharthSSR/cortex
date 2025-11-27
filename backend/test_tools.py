#!/usr/bin/env python3
"""Test the tools API."""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_calculator():
    """Test the calculator tool."""
    print("=" * 60)
    print("Testing Calculator Tool")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/tools/execute",
        json={
            "tool_name": "calculator",
            "parameters": {"expression": "2 ** 8 + sqrt(16)"}
        }
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_python_repl():
    """Test the Python REPL tool."""
    print("=" * 60)
    print("Testing Python REPL Tool")
    print("=" * 60)

    code = """
import math
result = [x**2 for x in range(1, 6)]
print(f"Squares: {result}")
print(f"Sum: {sum(result)}")
print(f"Pi: {math.pi:.4f}")
"""

    response = requests.post(
        f"{BASE_URL}/tools/execute",
        json={
            "tool_name": "python_repl",
            "parameters": {"code": code}
        }
    )

    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_web_search():
    """Test the web search tool."""
    print("=" * 60)
    print("Testing Web Search Tool")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/tools/execute",
        json={
            "tool_name": "web_search",
            "parameters": {"query": "Python programming", "num_results": 3}
        }
    )

    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"\nSearch Results:\n{result['result'][:500]}...")  # First 500 chars
    else:
        print(f"Error: {result['error']}")
    print()

if __name__ == "__main__":
    print("\n🧪 Testing Cortex Tools System\n")

    try:
        test_calculator()
        test_python_repl()
        test_web_search()

        print("✅ All tool tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
