#!/usr/bin/env python3
"""Test the agents API."""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_agent_info():
    """Test getting agent information."""
    print_section("Getting Agent Information")

    response = requests.get(f"{BASE_URL}/agents/info")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_agent_planning():
    """Test agent planning."""
    print_section("Testing Agent Planning")

    goal = "Calculate the sum of squares from 1 to 10"

    response = requests.post(
        f"{BASE_URL}/agents/plan", json={"goal": goal, "verbose": True}
    )

    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"\nGoal: {result['goal']}")
    print(f"\nPlan:\n{result['plan']}")


def test_agent_execution_simple():
    """Test simple agent execution."""
    print_section("Testing Agent Execution - Simple Math")

    goal = "What is 2 to the power of 10?"

    response = requests.post(
        f"{BASE_URL}/agents/execute",
        json={"goal": goal, "max_iterations": 5, "verbose": True},
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\nSuccess: {result['success']}")

    if result['success']:
        print(f"\nFinal Answer: {result['final_answer']}\n")

        print("Execution Steps:")
        for step in result['steps']:
            print(f"\nStep {step['step_number']}:")
            print(f"  Thought: {step['thought']}")
            if step['action']:
                print(f"  Action: {step['action']}")
                print(f"  Input: {step['action_input']}")
            if step['observation']:
                print(f"  Observation: {step['observation']}")
    else:
        print(f"\nError: {result['error']}")


def test_agent_execution_complex():
    """Test complex agent execution with multiple tools."""
    print_section("Testing Agent Execution - Multi-Tool Task")

    goal = "First calculate the factorial of 5, then create a Python list with the first 5 prime numbers"

    response = requests.post(
        f"{BASE_URL}/agents/execute",
        json={"goal": goal, "max_iterations": 10, "verbose": True},
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\nSuccess: {result['success']}")

    if result['success']:
        print(f"\nFinal Answer: {result['final_answer']}\n")

        print("Execution Trace:")
        for step in result['steps']:
            print(f"\n--- Step {step['step_number']} ---")
            print(f"Thought: {step['thought'][:150]}...")
            if step['action']:
                print(f"Action: {step['action']}")
            if step['observation']:
                obs = step['observation'][:200]
                print(f"Observation: {obs}...")
    else:
        print(f"\nError: {result['error']}")

    print(f"\nTotal iterations: {result.get('metadata', {}).get('iterations', 'N/A')}")


def test_agent_execution_research():
    """Test agent execution with web search."""
    print_section("Testing Agent Execution - Research Task")

    goal = "Search for information about Python programming and tell me one key feature"

    response = requests.post(
        f"{BASE_URL}/agents/execute",
        json={"goal": goal, "max_iterations": 5, "verbose": True},
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\nSuccess: {result['success']}")

    if result['success']:
        print(f"\nFinal Answer: {result['final_answer']}\n")
    else:
        print(f"\nError: {result['error']}")


if __name__ == "__main__":
    print("\n🤖 Testing Cortex Agent System\n")

    try:
        # Test 1: Get agent info
        test_agent_info()

        time.sleep(1)

        # Test 2: Planning
        test_agent_planning()

        time.sleep(2)

        # Test 3: Simple execution
        test_agent_execution_simple()

        time.sleep(2)

        # Test 4: Complex execution
        # test_agent_execution_complex()

        # time.sleep(2)

        # Test 5: Research task
        # test_agent_execution_research()

        print("\n" + "=" * 70)
        print("✅ Agent tests completed!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
