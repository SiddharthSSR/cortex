#!/usr/bin/env python3
"""Test agent workflow with code generation and execution."""

import requests
import json


BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_simple_generate_and_execute():
    """Test if agent can generate code and execute it."""
    print_section("Test 1: Generate and Execute Simple Code")

    response = requests.post(
        f"{BASE_URL}/agents/execute",
        json={
            "goal": "Use the code generator to create a simple Python function that adds two numbers, then use the Python REPL to test it with values 5 and 3",
            "max_iterations": 15,
            "verbose": True,
        },
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\nSuccess: {result['success']}")
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")

    print("\n--- Execution Trace ---")
    for step in result.get("steps", []):
        print(f"\nStep {step['step_number']}:")
        print(f"  Thought: {step['thought'][:200]}...")
        if step["action"]:
            print(f"  Action: {step['action']}")
        if step.get("observation"):
            print(f"  Observation: {step['observation'][:150]}...")

    return result["success"]


def test_fibonacci_workflow():
    """Test agent generating Fibonacci code and calculating value."""
    print_section("Test 2: Generate Fibonacci Function and Calculate 10th Number")

    response = requests.post(
        f"{BASE_URL}/agents/execute",
        json={
            "goal": "First, use the code_generator to create a Python function that calculates the nth Fibonacci number. Then, use python_repl to run that code and calculate the 10th Fibonacci number.",
            "max_iterations": 20,
            "verbose": True,
        },
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\nSuccess: {result['success']}")
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")

    if not result["success"]:
        print(f"Error: {result.get('error', 'Unknown error')}")

    print("\n--- Execution Trace (Last 5 steps) ---")
    steps = result.get("steps", [])
    for step in steps[-5:]:
        print(f"\nStep {step['step_number']}:")
        print(f"  Thought: {step['thought'][:200]}")
        if step["action"]:
            print(f"  Action: {step['action']}")
        if step.get("observation"):
            print(f"  Observation: {step['observation'][:200]}")

    return result["success"]


def test_direct_two_step():
    """Test simpler workflow - just calculate something with generated code."""
    print_section("Test 3: Simple Calculation with Code Generator")

    response = requests.post(
        f"{BASE_URL}/agents/execute",
        json={
            "goal": "Generate Python code to calculate the sum of squares from 1 to 5, then execute it",
            "max_iterations": 12,
            "verbose": True,
        },
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\nSuccess: {result['success']}")
    print(f"Final Answer: {result.get('final_answer', 'N/A')}")

    if not result["success"]:
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Iterations used: {result.get('metadata', {}).get('iterations', 'N/A')}")

    return result["success"]


if __name__ == "__main__":
    print("\n🔬 Testing Agent Code Generation + Execution Workflows\n")

    try:
        # Test 3: Simplest test first
        success3 = test_direct_two_step()

        import time
        time.sleep(2)

        # Test 1: Simple workflow
        success1 = test_simple_generate_and_execute()

        time.sleep(2)

        # Test 2: More complex workflow
        success2 = test_fibonacci_workflow()

        print("\n" + "=" * 70)
        print("RESULTS SUMMARY:")
        print(f"  Test 1 (Simple Add): {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"  Test 2 (Fibonacci):  {'✅ PASS' if success2 else '❌ FAIL'}")
        print(f"  Test 3 (Sum Squares): {'✅ PASS' if success3 else '❌ FAIL'}")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
