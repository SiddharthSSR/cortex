"""Agent execution endpoints."""

import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.agents import ReActAgent, AgentResult, AgentStep
from app.tools import get_tool_registry
from app.core.llm_service import LLMModel
from app.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


class AgentExecutionRequest(BaseModel):
    """Agent execution request."""

    goal: str
    model: Optional[str] = None
    max_iterations: Optional[int] = 10
    verbose: Optional[bool] = True
    context: Optional[Dict[str, Any]] = None


class AgentPlanRequest(BaseModel):
    """Agent planning request."""

    goal: str
    model: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentStepResponse(BaseModel):
    """Agent step response."""

    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    status: str


class AgentExecutionResponse(BaseModel):
    """Agent execution response."""

    success: bool
    final_answer: Optional[str] = None
    steps: List[AgentStepResponse]
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class AgentPlanResponse(BaseModel):
    """Agent planning response."""

    plan: str
    goal: str


@router.post("/agents/plan", response_model=AgentPlanResponse)
async def create_plan(request: AgentPlanRequest, http_request: Request):
    """Create a plan for achieving a goal.

    Args:
        request: Planning request with goal
        http_request: FastAPI request object

    Returns:
        Planning response with step-by-step plan
    """
    settings = get_settings()
    model_registry = http_request.app.state.model_registry
    tool_registry = get_tool_registry()

    # Get model
    model_id = request.model or settings.default_model

    try:
        # Get or load model
        if model_id not in model_registry:
            logger.info(f"Loading model for agent: {model_id}")
            model = LLMModel(model_id)
            await model.load()
            model_registry[model_id] = model
        else:
            model = model_registry[model_id]

        # Create agent
        agent = ReActAgent(
            llm=model,
            tool_registry=tool_registry,
            verbose=True,
        )

        # Generate plan
        plan = await agent.plan(request.goal, request.context)

        return AgentPlanResponse(plan=plan, goal=request.goal)

    except Exception as e:
        logger.error(f"Planning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@router.post("/agents/execute", response_model=AgentExecutionResponse)
async def execute_agent(request: AgentExecutionRequest, http_request: Request):
    """Execute an agent to achieve a goal.

    Args:
        request: Execution request with goal and parameters
        http_request: FastAPI request object

    Returns:
        Execution response with steps and final answer
    """
    settings = get_settings()
    model_registry = http_request.app.state.model_registry
    tool_registry = get_tool_registry()

    # Get model
    model_id = request.model or settings.default_model

    try:
        # Get or load model
        if model_id not in model_registry:
            logger.info(f"Loading model for agent: {model_id}")
            model = LLMModel(model_id)
            await model.load()
            model_registry[model_id] = model
        else:
            model = model_registry[model_id]

        # Create agent
        agent = ReActAgent(
            llm=model,
            tool_registry=tool_registry,
            max_iterations=request.max_iterations or 10,
            verbose=request.verbose if request.verbose is not None else True,
        )

        logger.info(f"Executing agent for goal: {request.goal}")

        # Execute agent
        result = await agent.execute(request.goal, request.context)

        # Convert steps to response format
        step_responses = []
        for step in result.steps:
            step_responses.append(
                AgentStepResponse(
                    step_number=step.step_number,
                    thought=step.thought,
                    action=step.action,
                    action_input=step.action_input,
                    observation=step.observation,
                    status=step.status.value,
                )
            )

        return AgentExecutionResponse(
            success=result.success,
            final_answer=result.final_answer,
            steps=step_responses,
            error=result.error,
            metadata=result.metadata,
        )

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Agent execution failed: {str(e)}"
        )


@router.get("/agents/info")
async def get_agent_info():
    """Get information about available agents.

    Returns:
        Information about available agent types
    """
    return {
        "agents": [
            {
                "type": "react",
                "name": "ReAct Agent",
                "description": "Agent that uses reasoning and acting to solve problems with tools",
                "capabilities": [
                    "Multi-step reasoning",
                    "Tool usage",
                    "Self-correction",
                    "Goal-oriented problem solving",
                ],
            }
        ]
    }
