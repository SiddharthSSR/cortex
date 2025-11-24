"""ReAct (Reasoning + Acting) Agent implementation."""

import json
import re
from typing import Dict, Any, Optional, List
import logging

from app.agents.base_agent import BaseAgent, AgentResult, AgentStep, AgentStatus
from app.tools.registry import ToolRegistry
from app.core.llm_service import LLMModel
from app.schemas.chat import Message, MessageRole

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    """ReAct agent that uses reasoning and acting loop to solve problems."""

    def __init__(
        self,
        llm: LLMModel,
        tool_registry: ToolRegistry,
        name: str = "ReAct Agent",
        description: str = "Agent that reasons and acts using available tools",
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        """Initialize ReAct agent.

        Args:
            llm: Language model for reasoning
            tool_registry: Registry of available tools
            name: Agent name
            description: Agent description
            max_iterations: Maximum reasoning iterations
            verbose: Enable verbose logging
        """
        super().__init__(name, description, max_iterations, verbose)
        self.llm = llm
        self.tool_registry = tool_registry

    async def plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Plan how to achieve the goal.

        Args:
            goal: The goal to achieve
            context: Additional context

        Returns:
            Planning thoughts
        """
        tools_description = self._format_tools()

        planning_prompt = f"""You are a planning assistant. Given a goal and available tools, create a step-by-step plan.

Available Tools:
{tools_description}

Goal: {goal}

Create a brief plan (2-4 steps) on how to achieve this goal using the available tools."""

        messages = [Message(role=MessageRole.USER, content=planning_prompt)]

        try:
            response = await self.llm.generate(messages=messages, max_tokens=300)
            return response.content
        except Exception as e:
            return f"Planning failed: {str(e)}"

    async def execute(
        self, goal: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Execute the ReAct agent loop.

        Args:
            goal: The goal to achieve
            context: Additional context

        Returns:
            AgentResult with execution trace and final answer
        """
        self.reset()
        self._status = AgentStatus.THINKING

        try:
            for iteration in range(1, self.max_iterations + 1):
                self._current_step = iteration
                self._log(f"=== Iteration {iteration}/{self.max_iterations} ===")

                # Get next thought/action from LLM
                step_result = await self._reasoning_step(goal, iteration)

                if step_result is None:
                    # Error occurred
                    return AgentResult(
                        success=False,
                        error="Failed to generate reasoning step",
                        steps=self.memory.get_all_steps(),
                    )

                # Check if agent wants to finish
                if step_result.get("action") == "finish":
                    final_answer = step_result.get("action_input", {}).get(
                        "answer", step_result.get("thought", "")
                    )

                    self._log(f"Agent finished with answer: {final_answer}")
                    self._status = AgentStatus.COMPLETED

                    return AgentResult(
                        success=True,
                        final_answer=final_answer,
                        steps=self.memory.get_all_steps(),
                        metadata={
                            "iterations": iteration,
                            "goal": goal,
                        },
                    )

                # Execute action
                if step_result.get("action"):
                    observation = await self._execute_action(
                        step_result["action"], step_result.get("action_input", {})
                    )

                    # Update step with observation
                    current_step = self.memory.steps[-1]
                    current_step.observation = observation
                    current_step.status = AgentStatus.OBSERVING

                    self._log(f"Observation: {observation[:200]}...")

            # Max iterations reached
            self._status = AgentStatus.FAILED
            return AgentResult(
                success=False,
                error=f"Maximum iterations ({self.max_iterations}) reached without finding answer",
                steps=self.memory.get_all_steps(),
            )

        except Exception as e:
            self._status = AgentStatus.FAILED
            logger.error(f"Agent execution failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                steps=self.memory.get_all_steps(),
            )

    async def _reasoning_step(
        self, goal: str, step_number: int
    ) -> Optional[Dict[str, Any]]:
        """Perform one reasoning step.

        Args:
            goal: The goal to achieve
            step_number: Current step number

        Returns:
            Dictionary with thought, action, and action_input
        """
        try:
            # Build prompt with history
            prompt = self._build_react_prompt(goal)

            messages = [Message(role=MessageRole.USER, content=prompt)]

            # Get LLM response
            response = await self.llm.generate(messages=messages, max_tokens=500)

            # Parse response
            parsed = self._parse_llm_response(response.content)

            # Create step
            step = AgentStep(
                step_number=step_number,
                thought=parsed.get("thought", ""),
                action=parsed.get("action"),
                action_input=parsed.get("action_input"),
                status=AgentStatus.THINKING if parsed.get("action") else AgentStatus.IDLE,
            )

            self.memory.add_step(step)
            self._log(f"Thought: {step.thought}")
            if step.action:
                self._log(f"Action: {step.action}({step.action_input})")

            return parsed

        except Exception as e:
            logger.error(f"Reasoning step failed: {e}")
            return None

    async def _execute_action(
        self, action: str, action_input: Dict[str, Any]
    ) -> str:
        """Execute an action using a tool.

        Args:
            action: Tool name to execute
            action_input: Tool parameters

        Returns:
            Observation from tool execution
        """
        self._status = AgentStatus.ACTING

        try:
            result = await self.tool_registry.execute_tool(action, action_input)

            if result.success:
                return f"Success: {result.result}"
            else:
                return f"Error: {result.error}"

        except Exception as e:
            return f"Action execution failed: {str(e)}"

    def _build_react_prompt(self, goal: str) -> str:
        """Build ReAct-style prompt with explicit examples.

        Args:
            goal: The goal to achieve

        Returns:
            Formatted prompt string
        """
        tools_description = self._format_tools()
        history = self.memory.format_history()

        prompt = f"""You are a helpful AI assistant that uses tools to accomplish tasks step by step.

Available Tools:
{tools_description}

CRITICAL FORMAT REQUIREMENTS:
You MUST respond using this EXACT format with proper JSON for Action Input:

Thought: [your reasoning about what to do next]
Action: [exact tool name]
Action Input: {{"parameter_name": "parameter_value"}}

IMPORTANT:
- Action Input MUST be valid JSON with double quotes
- Use the exact parameter names shown for each tool
- Include ALL required parameters

TOOL USAGE EXAMPLES (FOLLOW THESE EXACTLY):

Example 1 - calculator tool requires "expression" parameter:
Thought: I need to calculate 2^10
Action: calculator
Action Input: {{"expression": "2**10"}}

Example 2 - python_repl tool requires "code" parameter (NOT "input"):
Thought: I need to execute Python code to create a list
Action: python_repl
Action Input: {{"code": "print([x**2 for x in range(5)])"}}

Example 3 - code_generator tool requires "request" and optional "language":
Thought: I need to generate a function to add two numbers
Action: code_generator
Action Input: {{"request": "Create a function to add two numbers", "language": "python"}}

Example 4 - web_search tool requires "query" and optional "num_results":
Thought: I need to search for information about Python
Action: web_search
Action Input: {{"query": "Python programming tutorial", "num_results": 3}}

Example 5 - finish action requires "answer" parameter:
Thought: I have the answer, which is 1024
Action: finish
Action Input: {{"answer": "1024"}}

COMMON MISTAKES TO AVOID:
- DO NOT use "input" as parameter name - use the exact names shown above
- DO NOT forget quotes around string values in JSON
- DO NOT use single quotes - always use double quotes in JSON

MULTI-STEP WORKFLOW EXAMPLES:

Workflow 1 - Generate and execute code:
Step 1:
  Thought: I need to generate a function to add two numbers
  Action: code_generator
  Action Input: {{"request": "Create a function called add_numbers that adds two numbers", "language": "python"}}
  Observation: Success: def add_numbers(a, b):\n    return a + b

Step 2:
  Thought: Now I have the function code. I need to execute it with values 5 and 3. I'll combine the function definition with a call to it in a single python_repl execution.
  Action: python_repl
  Action Input: {{"code": "def add_numbers(a, b):\\n    return a + b\\n\\nresult = add_numbers(5, 3)\\nprint(result)"}}
  Observation: Success: 8

Step 3:
  Thought: I got the result which is 8
  Action: finish
  Action Input: {{"answer": "8"}}

IMPORTANT: Each python_repl execution is independent! If you generate a function with code_generator, you must include both the function definition AND the function call in the same python_repl code parameter.

Goal: {goal}

{history}

Now, what is your next step? Follow the exact format shown above."""

        return prompt

    def _format_tools(self) -> str:
        """Format available tools for prompt with detailed parameter info.

        Returns:
            Formatted tools description with parameter details
        """
        tools = self.tool_registry.list_tools(enabled_only=True)

        if not tools:
            return "No tools available."

        tool_descriptions = []
        for tool in tools:
            # Build parameter details
            param_details = []
            for name, param in tool.parameters.items():
                required = "REQUIRED" if param.required else "optional"
                param_details.append(f'  - {name} ({param.type}, {required}): {param.description}')

            params_str = "\n".join(param_details) if param_details else "  No parameters"

            tool_descriptions.append(
                f"{tool.name}:\n  Description: {tool.description}\n  Parameters:\n{params_str}"
            )

        return "\n\n".join(tool_descriptions)

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into thought, action, and action_input.

        Args:
            response: Raw LLM response

        Returns:
            Dictionary with parsed components
        """
        result = {"thought": "", "action": None, "action_input": {}}

        # Extract Thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\n(?:Action:|$))", response, re.DOTALL)
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        # Extract Action
        action_match = re.search(r"Action:\s*(\w+)", response)
        if action_match:
            result["action"] = action_match.group(1).strip()

        # Extract Action Input
        action_input_match = re.search(
            r"Action Input:\s*(\{.+?\})", response, re.DOTALL
        )
        if action_input_match:
            try:
                result["action_input"] = json.loads(action_input_match.group(1))
            except json.JSONDecodeError:
                # Try to extract key-value pairs
                input_str = action_input_match.group(1)
                # Simple fallback: treat as single string parameter
                result["action_input"] = {"input": input_str.strip("{}")}

        return result

    def get_capabilities(self) -> List[str]:
        """Get agent capabilities.

        Returns:
            List of capabilities
        """
        return [
            "Multi-step reasoning",
            "Tool usage",
            "Self-correction",
            "Goal-oriented problem solving",
        ]
