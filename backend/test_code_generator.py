#!/usr/bin/env python3
"""Test the code generator tool."""

import requests
import json


BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_code_generator():
    """Test code generation."""
    print_section("Testing Code Generator Tool")

    # Test 1: Generate a simple function
    print("\n--- Test 1: Generate Factorial Function ---")
    response = requests.post(
        f"{BASE_URL}/tools/execute",
        json={
            "tool_name": "code_generator",
            "parameters": {
                "request": "Create a function to calculate the factorial of a number",
                "language": "python",
            },
        },
    )

    print(f"Status: {response.status_code}")
    result = response.json()
    if result["success"]:
        print(f"\nGenerated Code:\n{result['result']}")
    else:
        print(f"Error: {result['error']}")

    # Test 2: Generate a more complex function
    print("\n--- Test 2: Generate Binary Search ---")
    response = requests.post(
        f"{BASE_URL}/tools/execute",
        json={
            "tool_name": "code_generator",
            "parameters": {
                "request": "Write a binary search algorithm that returns the index of a target value in a sorted array",
                "language": "python",
            },
        },
    )

    print(f"Status: {response.status_code}")
    result = response.json()
    if result["success"]:
        print(f"\nGenerated Code:\n{result['result']}")
    else:
        print(f"Error: {result['error']}")


def test_agent_with_code_generation():
    """Test agent using code generation tool."""
    print_section("Testing Agent with Code Generation")

    # Agent should generate code and potentially execute it
    response = requests.post(
        f"{BASE_URL}/agents/execute",
        json={
            "goal": "Generate a Python function to calculate the first n Fibonacci numbers and return it as a list",
            "max_iterations": 10,
            "verbose": True,
        },
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\nSuccess: {result['success']}")

    if result["success"]:
        print(f"\nFinal Answer:\n{result['final_answer']}\n")

        print("Execution Steps:")
        for step in result["steps"]:
            print(f"\nStep {step['step_number']}:")
            print(f"  Thought: {step['thought'][:150]}...")
            if step["action"]:
                print(f"  Action: {step['action']}")
            if step["observation"]:
                obs = step["observation"][:300]
                print(f"  Observation: {obs}...")
    else:
        print(f"\nError: {result['error']}")


def test_list_tools():
    """Test that code_generator appears in tools list."""
    print_section("Verifying Code Generator in Tools List")

    response = requests.get(f"{BASE_URL}/tools")
    print(f"Status: {response.status_code}")

    result = response.json()
    print(f"\nTotal tools: {result['total_count']}")
    print(f"Enabled tools: {result['enabled_count']}")

    print("\nAvailable tools:")
    for tool in result["tools"]:
        print(f"  - {tool['name']}: {tool['description']}")

    # Check if code_generator is in the list
    tool_names = [tool["name"] for tool in result["tools"]]
    if "code_generator" in tool_names:
        print("\n✅ Code generator tool is registered!")
    else:
        print("\n❌ Code generator tool NOT found in registry")


if __name__ == "__main__":
    print("\n🔧 Testing Code Generator Tool\n")

    try:
        # Test 1: Verify tool is registered
        test_list_tools()

        import time

        time.sleep(1)

        # Test 2: Direct code generation
        test_code_generator()

        time.sleep(2)

        # Test 3: Agent using code generation
        test_agent_with_code_generation()

        print("\n" + "=" * 70)
        print("✅ Code generator tests completed!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
