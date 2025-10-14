import logging
import os
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

from models import FullProfileEvaluationResponse
from run_poc import run_poc


logger = logging.getLogger(__name__)


class QuizResponses(BaseModel):
    currentRole: str
    experience: str
    targetRole: str
    problemSolving: str
    systemDesign: str
    portfolio: str
    mockInterviews: str
    currentCompany: str
    currentSkill: str
    requirementType: str
    targetCompany: str

    model_config = ConfigDict(extra="forbid")


class Goals(BaseModel):
    requirementType: list[str]
    targetCompany: str
    topicOfInterest: list[str]

    model_config = ConfigDict(extra="forbid")


class EvaluationRequest(BaseModel):
    background: str
    quizResponses: QuizResponses
    goals: Goals

    model_config = ConfigDict(extra="forbid")


app = FastAPI(title="Full Profile Evaluation API")


def _determine_allowed_origins() -> list[str]:
    """Return the list of origins permitted to call the API."""

    env_value = os.environ.get("ALLOWED_ORIGINS", "")
    if env_value:
        origins = [origin.strip() for origin in env_value.split(",") if origin.strip()]
        if origins:
            return origins

    return [
        "https://frontend-production-d53f.up.railway.app",
        "http://127.0.0.1:3000",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_determine_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/evaluate", response_model=FullProfileEvaluationResponse)
async def evaluate_profile(request: EvaluationRequest) -> FullProfileEvaluationResponse:
    """Generate a full profile evaluation for the provided payload."""

    try:
        return run_poc(
            input_payload=request.model_dump(),
        )
    except RuntimeError as exc:
        logger.exception("Evaluation failed due to configuration error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - unexpected path
        logger.exception("Unexpected error while generating evaluation")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate evaluation. Check server logs for details.",
        ) from exc


@app.get("/health")
async def healthcheck() -> Dict[str, str]:
    """Lightweight health endpoint for readiness probes."""

    return {"status": "ok"}


def create_app() -> FastAPI:
    """Provide an app factory for tooling (e.g., uvicorn workers)."""

    return app
