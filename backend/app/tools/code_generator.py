"""Code generation tool using LLM."""

import logging
from typing import Dict, Optional

from app.tools.base_tool import BaseTool, ToolParameter, ToolResult
from app.core.llm_service import LLMModel
from app.schemas.chat import Message, MessageRole

logger = logging.getLogger(__name__)


class CodeGeneratorTool(BaseTool):
    """Generate code based on natural language descriptions using LLM."""

    def __init__(self, llm: Optional[LLMModel] = None):
        """Initialize code generator.

        Args:
            llm: Language model for code generation (will be set later if None)
        """
        super().__init__()
        self._llm = llm

    def set_llm(self, llm: LLMModel):
        """Set the LLM for code generation.

        Args:
            llm: Language model instance
        """
        self._llm = llm

    @property
    def name(self) -> str:
        return "code_generator"

    @property
    def description(self) -> str:
        return "Generate code based on natural language descriptions. Supports Python, JavaScript, and other languages."

    @property
    def parameters(self) -> Dict[str, ToolParameter]:
        return {
            "request": ToolParameter(
                name="request",
                type="string",
                description="Description of what the code should do (e.g., 'create a function to calculate fibonacci numbers')",
                required=True,
            ),
            "language": ToolParameter(
                name="language",
                type="string",
                description="Programming language (e.g., 'python', 'javascript', 'go'). Defaults to 'python'.",
                required=False,
            ),
        }

    async def execute(
        self, request: str, language: str = "python"
    ) -> ToolResult:
        """Generate code based on a request.

        Args:
            request: Description of what the code should do
            language: Programming language to generate code in

        Returns:
            ToolResult with generated code
        """
        if not self._llm:
            return ToolResult(
                success=False,
                error="LLM not initialized. Code generator requires an LLM instance.",
            )

        if not request or not request.strip():
            return ToolResult(
                success=False, error="Request description cannot be empty"
            )

        try:
            # Create prompt for code generation
            prompt = self._create_code_generation_prompt(request, language)

            messages = [Message(role=MessageRole.USER, content=prompt)]

            # Generate code using LLM
            response = await self._llm.generate(
                messages=messages,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more deterministic code
            )

            generated_code = response.content.strip()

            # Extract code from markdown code blocks if present
            generated_code = self._extract_code_from_markdown(generated_code)

            if not generated_code:
                return ToolResult(
                    success=False, error="Failed to generate code from LLM response"
                )

            return ToolResult(success=True, result=generated_code)

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return ToolResult(success=False, error=f"Code generation failed: {str(e)}")

    def _create_code_generation_prompt(self, request: str, language: str) -> str:
        """Create a prompt for code generation.

        Args:
            request: User's code request
            language: Programming language

        Returns:
            Formatted prompt for the LLM
        """
        prompt = f"""You are an expert programmer. Generate {language} code based on the following request.

Request: {request}

Requirements:
- Write clean, efficient, well-commented code
- Include docstrings/comments explaining the code
- Follow {language} best practices and conventions
- Make the code production-ready
- Only return the code, no explanations outside of code comments

Generate the {language} code now:"""

        return prompt

    def _extract_code_from_markdown(self, text: str) -> str:
        """Extract code from markdown code blocks.

        Args:
            text: Text potentially containing markdown code blocks

        Returns:
            Extracted code or original text if no code blocks found
        """
        import re

        # Try to extract code from markdown code blocks (```language ... ```)
        code_block_pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)

        if matches:
            # Return the first code block found
            return matches[0].strip()

        # If no code blocks, return the original text
        return text.strip()

    def get_examples(self) -> list:
        """Get example uses of the code generator.

        Returns:
            List of example requests
        """
        return [
            {
                "request": "Create a function to calculate the factorial of a number",
                "language": "python",
            },
            {
                "request": "Write a binary search algorithm",
                "language": "python",
            },
            {
                "request": "Generate a function to validate email addresses using regex",
                "language": "javascript",
            },
            {
                "request": "Create a class for a basic linked list with insert and delete methods",
                "language": "python",
            },
        ]
