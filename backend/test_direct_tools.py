"""Test direct tool calling without agent."""

import asyncio
import sys
sys.path.insert(0, '/Users/siddharthsingh/codingtensor/cortex/backend')

from app.core.llm_service import LLMModel
from app.tools import initialize_tools, get_tool_registry
from app.schemas.chat import Message, MessageRole


async def test_direct_tool_calling():
    """Test direct tool calling mode."""
    print("=" * 60)
    print("Testing Direct Tool Calling (No Agent)")
    print("=" * 60)

    # Initialize tools
    initialize_tools()
    tool_registry = get_tool_registry()

    # Load model
    print("\n1. Loading model...")
    model = LLMModel("mlx-community/Llama-3.2-3B-Instruct-4bit")
    await model.load()
    print("✓ Model loaded")

    # Get tool definitions
    tools = tool_registry.get_tool_definitions(enabled_only=True)
    print(f"\n2. Loaded {len(tools)} tools:")
    for tool in tools:
        tool_name = tool.get("function", {}).get("name", "")
        print(f"   - {tool_name}")

    # Test query
    test_query = "Search the web for Go programming tutorials"
    print(f"\n3. Test Query: {test_query}")

    messages = [Message(role=MessageRole.USER, content=test_query)]

    # Generate response with tools
    print("\n4. Generating response with tools...")
    response = await model.generate(
        messages=messages,
        tools=tools,
        temperature=0.7,
        max_tokens=500,
    )

    print(f"\n5. LLM Response:")
    print(f"   Content: {response.content}")
    print(f"   Tool Calls: {response.tool_calls}")

    if response.tool_calls:
        print(f"\n6. Executing tool calls...")
        for tool_call in response.tool_calls:
            function_name = tool_call.get("function", {}).get("name")
            print(f"\n   Tool: {function_name}")

            result = await tool_registry.execute_tool_call(tool_call)
            print(f"   Success: {result.success}")
            if result.success:
                print(f"   Result: {result.result[:200]}...")
            else:
                print(f"   Error: {result.error}")
    else:
        print("\n6. No tool calls detected in LLM response")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_direct_tool_calling())
