import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional

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
    # Optional label fields for display (sent from frontend)
    currentRoleLabel: Optional[str] = None
    targetRoleLabel: Optional[str] = None
    targetCompanyLabel: Optional[str] = None
    primaryGoal: Optional[str] = None  # Add primaryGoal field

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
        "https://free-profile-evaluation.onrender.com",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
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

    # DEBUG: Log request to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_dir = os.path.join(os.path.dirname(__file__), "debug_logs")
    os.makedirs(debug_dir, exist_ok=True)

    request_file = os.path.join(debug_dir, f"request_{timestamp}.json")
    with open(request_file, 'w') as f:
        json.dump(request.model_dump(), f, indent=2)
    print(f"\n{'='*80}\nDEBUG: Request logged to {request_file}\n{'='*80}\n")

    try:
        result = run_poc(
            input_payload=request.model_dump(),
        )

        # DEBUG: Log response to file (use mode='json' to serialize Enums properly)
        response_file = os.path.join(debug_dir, f"response_{timestamp}.json")
        with open(response_file, 'w') as f:
            f.write(result.model_dump_json(indent=2))
        print(f"\n{'='*80}\nDEBUG: Response logged to {response_file}\n{'='*80}\n")

        return result
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
@app.head("/health")
async def healthcheck() -> Dict[str, str]:
    """Lightweight health endpoint for readiness probes."""

    return {"status": "ok"}


def create_app() -> FastAPI:
    """Provide an app factory for tooling (e.g., uvicorn workers)."""

    return app
