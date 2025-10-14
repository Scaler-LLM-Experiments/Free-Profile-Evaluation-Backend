import hashlib
import json
import logging
import os
import sys
from time import sleep
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI
from redis import Redis
from redis.exceptions import RedisError

from models import FullProfileEvaluationResponse, enrich_full_profile_evaluation
from models_raw import FullProfileEvaluationResponseRaw
from pydantic import ValidationError

load_dotenv()

logger = logging.getLogger(__name__)


DEFAULT_INPUT: Dict[str, Any] = {
    "background": "tech",
    "quizResponses": {
        "currentRole": "swe-product",
        "experience": "3-5",
        "targetRole": "faang-sde",
        "problemSolving": "51-100",
        "systemDesign": "once",
        "portfolio": "active-5+",
        "mockInterviews": "monthly",
        "currentCompany": "Google",
        "currentSkill": "51-100",
        "requirementType": "upskilling",
        "targetCompany": "faang",
    },
    "goals": {
        "requirementType": [],
        "targetCompany": "Google",
        "topicOfInterest": [],
    },
}

_redis_client: Optional[Redis] = None
_CACHE_DISABLED = False


def _normalise_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a JSON-normalised deep copy of the payload for caching."""

    return json.loads(json.dumps(payload, sort_keys=True))


def _get_cache_client() -> Optional[Redis]:
    """Return a singleton Redis client if available; otherwise disable caching."""

    global _redis_client, _CACHE_DISABLED

    if _CACHE_DISABLED:
        return None

    if _redis_client is not None:
        return _redis_client

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        client = Redis.from_url(redis_url, decode_responses=True)
        client.ping()
    except RedisError as exc:  # pragma: no cover - network dependent
        logger.warning("Redis cache disabled: %s", exc)
        _CACHE_DISABLED = True
        return None

    _redis_client = client
    return _redis_client


def _make_cache_key(payload: Dict[str, Any], model: str) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"full_profile:{model}:{payload_hash}"


def call_openai_structured(
    *,
    api_key: Optional[str],
    openai_model: str,
    input_payload: Dict[str, Any],
) -> FullProfileEvaluationResponse:
    client = OpenAI(api_key=api_key) if api_key else OpenAI()

    system_instruction = (
        "You are a career advisor. Given the candidate's background, quiz responses, and goals, "
        "produce a structured FullProfileEvaluationResponse focusing on prospects, role fit, gaps, and a roadmap.\n\n"
        "Field guide for the input JSON:\n"
        "- background: 'tech' means the user already works or studies in software; 'non-tech' means they are transitioning "
        "from another domain and several quiz answers were inferred for them.\n"
        "- quizResponses.currentRole: tech respondents choose from student, swe-product, swe-service, career-switcher; "
        "non-tech respondents are prefixed with 'non-tech-' plus non-tech, it-services, technical, or fresh-graduate.\n"
        "- quizResponses.experience: total years of professional experience expressed as '0', '0-2', '3-5', or '5+'.\n"
        "- quizResponses.targetRole: primary role ambition (faang-sde, backend, fullstack, data-ml, tech-lead, data-analyst, not-sure).\n"
        "- quizResponses.problemSolving: recency of coding practice measured by problems solved (0-10, 11-50, 51-100, 100+). "
        "For non-tech users we map code comfort to this scale.\n"
        "- quizResponses.systemDesign: exposure to designing systems (multiple, once, not-yet). Non-tech defaults to not-yet.\n"
        "- quizResponses.portfolio: GitHub health (active-5+, limited-1-5, inactive, none).\n"
        "- quizResponses.mockInterviews: cadence of mock interview practice (weekly+, monthly, rarely, never).\n"
        "- quizResponses.currentCompany: employer name if provided; otherwise 'Not provided' or 'Transitioning from non-tech background'.\n"
        "- quizResponses.currentSkill: mirrors the problemSolving scale and represents overall coding comfort.\n"
        "- quizResponses.requirementType: key motivation behind the change (upskilling, career-transition, learn-new-skill, peer-influence, interest, salary).\n"
        "- quizResponses.targetCompany: short-hand for the target company or domain focus the user named.\n"
        "- goals.targetCompany: for tech respondents this is the concrete company/tier they typed; non-tech flows may leave this blank.\n"
        "- goals.topicOfInterest: for non-tech respondents, the themes they want to explore (ai-ml, web-development, mobile-development, "
        "data-science, cybersecurity, cloud-computing, blockchain, game-development, iot, ar-vr, fintech, healthtech, edtech, ecommerce, automation).\n"
        "- goals.requirementType: currently unused and often empty; rely on quizResponses.requirementType instead.\n\n"
        "IMPORTANT GUIDELINES FOR recommended_roles_based_on_interests:\n"
        "- Recommend roles that MATCH the candidate's technical skills and experience level.\n"
        "- For tech professionals with systemDesign='multiple' or '5+' years of experience, suggest SENIOR-LEVEL or MID-SENIOR technical roles (Senior SDE, Staff Engineer, Tech Lead, Engineering Manager, Solutions Architect), NOT junior roles.\n"
        "- For tech professionals with strong coding skills (problemSolving='100+' or '51-100'), prioritize ENGINEERING roles (Backend Engineer, Full Stack Engineer, SDE), NOT product management roles unless they explicitly target PM.\n"
        "- Only recommend Product Manager roles if: (a) the user explicitly targets PM/product roles, OR (b) they have 3-5+ years experience AND explicitly show product interests.\n"
        "- For candidates with limited coding skills (problemSolving='0-10') but strong system design, suggest Technical Program Manager or Solutions Architect roles.\n"
        "- Match seniority level to experience: 0-2 years → Entry/Junior, 3-5 years → Mid-Senior, 5+ years → Senior/Staff/Lead.\n"
        "- Provide 3-5 diverse role recommendations that align with the candidate's actual strengths and target interests.\n\n"
        "In your advice, acknowledge when values show limited exposure (e.g., not-yet, none, never) and tailor guidance for the user's background pivot."
    )

    schema = FullProfileEvaluationResponseRaw.model_json_schema()

    def _apply_json_schema_normalizers(node: Any) -> None:
        if isinstance(node, dict):
            # Ensure $ref nodes have no sibling keywords; OpenAI rejects any extras.
            if "$ref" in node and len(node) > 1:
                ref_value = node["$ref"]
                node.clear()
                node["$ref"] = ref_value

            if node.get("type") == "object":
                props = node.setdefault("properties", {})
                if not isinstance(props, dict):
                    raise TypeError("Object schema 'properties' must be a mapping")

                node["additionalProperties"] = False
                node["required"] = list(props.keys())

                for child in props.values():
                    _apply_json_schema_normalizers(child)
            if "items" in node:
                _apply_json_schema_normalizers(node["items"])
            for key in ("oneOf", "anyOf", "allOf"):
                if key in node and isinstance(node[key], list):
                    for child in node[key]:
                        _apply_json_schema_normalizers(child)
            if "$defs" in node and isinstance(node["$defs"], dict):
                for child in node["$defs"].values():
                    _apply_json_schema_normalizers(child)
            if "definitions" in node and isinstance(node["definitions"], dict):
                for child in node["definitions"].values():
                    _apply_json_schema_normalizers(child)
        elif isinstance(node, list):
            for child in node:
                _apply_json_schema_normalizers(child)

    _apply_json_schema_normalizers(schema)

    base_messages = [
        {"role": "system", "content": system_instruction},
        {
            "role": "user",
            "content": (
                "Using this input JSON, return only a JSON object that matches FullProfileEvaluationResponse.\n\n"
                + json.dumps(input_payload)
            ),
        },
    ]

    messages = list(base_messages)

    for attempt in range(1, 4):
        completion = None
        try:
            completion = client.chat.completions.create(
                model=openai_model,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "FullProfileEvaluationResponse",
                        "schema": schema,
                        "strict": True,
                    },
                },
            )
        except Exception as exc:  # pragma: no cover - network/service errors
            if attempt == 3:
                raise
            sleep(1.5 * attempt)
            continue

        if completion is None:
            if attempt == 3:
                raise RuntimeError("OpenAI completion failed without raising an exception")
            sleep(1.5 * attempt)
            continue

        content = completion.choices[0].message.content or ""
        if not content:
            error_text = "Empty response from OpenAI chat.completions"
        else:
            try:
                raw_obj = json.loads(content)
            except json.JSONDecodeError as exc:
                error_text = (
                    "Model response is not valid JSON: "
                    f"{exc}\nResponse text: {content}"
                )
            else:
                try:
                    raw_instance = FullProfileEvaluationResponseRaw.model_validate(raw_obj)
                except ValidationError as exc:
                    error_text = (
                        "Model response failed validation against FullProfileEvaluationResponse: "
                        f"{exc}"
                    )
                else:
                    return enrich_full_profile_evaluation(raw_instance)

        if attempt == 3:
            raise RuntimeError(error_text)

        correction_prompt = (
            "The previous response did not satisfy the required schema. "
            f"Error details:\n{error_text}\n\n"
            "Please respond again with only a JSON object that strictly matches the schema."
        )
        messages = base_messages + [
            {"role": "assistant", "content": content or ""},
            {"role": "user", "content": correction_prompt},
        ]
        sleep(1.5 * attempt)

    raise RuntimeError("Exhausted attempts without valid response")
    # content = completion.choices[0].message.content
    # if not content:
    #     raise RuntimeError("Empty response from OpenAI chat.completions")

    # try:
    #     raw_obj = json.loads(content)
    # except json.JSONDecodeError as exc:
    #     raise RuntimeError(f"Model response is not valid JSON: {exc}\nResponse text: {content}")

    # # Validate to Pydantic instance
    # return FullProfileEvaluationResponse.model_validate(raw_obj)


def run_poc(
    *,
    input_payload: Optional[Dict[str, Any]] = None,
) -> FullProfileEvaluationResponse:
    """Execute the structured OpenAI call with the provided payload."""

    payload_input = input_payload if input_payload is not None else DEFAULT_INPUT
    payload = _normalise_payload(payload_input)

    model_name = "gpt-4o"
    cache_client = _get_cache_client()
    cache_key = None
    cached_json = None

    if cache_client is not None:
        cache_key = _make_cache_key(payload, model_name)
        try:
            cached_json = cache_client.get(cache_key)
        except RedisError as exc:  # pragma: no cover - network dependent
            logger.warning("Redis cache read failed: %s", exc)
            cached_json = None

    if cached_json:
        return FullProfileEvaluationResponse.model_validate_json(cached_json)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Provide it via the environment variable.")

    result = call_openai_structured(
        api_key=api_key,
        openai_model=model_name,
        input_payload=payload,
    )

    result_json = result.model_dump_json()
    if cache_client is not None and cache_key is not None:
        try:
            cache_client.set(cache_key, result_json)
        except RedisError as exc:  # pragma: no cover - network dependent
            logger.warning("Redis cache write failed: %s", exc)

    return FullProfileEvaluationResponse.model_validate_json(result_json)


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "Error: OPENAI_API_KEY is not set. Set it in your environment and re-run.",
            file=sys.stderr,
        )
        return 2

    input_path = os.environ.get("INPUT_PATH")
    if input_path and os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = DEFAULT_INPUT

    try:
        raw = run_poc(
            input_payload=payload,
        )
    except Exception as exc:
        print(f"OpenAI API call failed: {exc}", file=sys.stderr)
        return 3

    # raw is already a validated FullProfileEvaluationResponse
    instance = raw
    print(instance.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
