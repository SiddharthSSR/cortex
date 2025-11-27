#!/usr/bin/env python3
"""Quick test for improved ReAct prompt."""

import requests

BASE_URL = "http://localhost:8000/api"

# Simple test: Generate and execute code
response = requests.post(
    f"{BASE_URL}/agents/execute",
    json={
        "goal": "Use code_generator to create a Python function that adds 5 and 3, then use python_repl to execute it and get the result",
        "max_iterations": 8,
        "verbose": True,
    },
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Answer: {result.get('final_answer', 'N/A')}")

if result["success"]:
    print("\n✅ TEST PASSED!")
else:
    print(f"\n❌ TEST FAILED: {result.get('error', 'Unknown')}")

# Show last few steps
print("\nLast 3 steps:")
for step in result.get("steps", [])[-3:]:
    print(f"\nStep {step['step_number']}:")
    print(f"  Action: {step['action']}")
    if step.get('action_input'):
        print(f"  Input: {step['action_input']}")
    if step.get('observation'):
        print(f"  Observation: {step['observation'][:100]}...")
