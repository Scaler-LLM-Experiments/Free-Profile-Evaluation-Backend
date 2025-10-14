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
        "You are a career advisor specializing in the Indian tech market. Given the candidate's background, quiz responses, and goals, "
        "produce a structured FullProfileEvaluationResponse focusing on prospects, role fit, gaps, and a roadmap.\n\n"
        "CONTEXT: The user is based in India and looking for opportunities in the Indian tech ecosystem (Bangalore, Hyderabad, Pune, NCR) "
        "or remote roles with Indian/global companies. Tailor all recommendations to be realistic and relevant for the Indian market.\n\n"
        "Field guide for the input JSON:\n"
        "- background: 'tech' = already works/studies in software; 'non-tech' = transitioning from another domain\n"
        "- quizResponses.currentRole: tech (student, swe-product, swe-service, career-switcher); non-tech (prefixed with 'non-tech-')\n"
        "- quizResponses.experience: '0', '0-2', '3-5', or '5+' years\n"
        "- quizResponses.targetRole: faang-sde, backend, fullstack, data-ml, tech-lead, data-analyst, not-sure\n"
        "- quizResponses.problemSolving: 0-10, 11-50, 51-100, 100+ (coding practice intensity)\n"
        "- quizResponses.systemDesign: multiple, once, not-yet (CRITICAL: 'multiple' indicates senior-level expertise)\n"
        "- quizResponses.portfolio: active-5+, limited-1-5, inactive, none\n"
        "- quizResponses.mockInterviews: weekly+, monthly, rarely, never\n"
        "- goals.topicOfInterest: ai-ml, web-development, mobile-development, data-science, cybersecurity, cloud-computing, blockchain, etc.\n\n"
        "CRITICAL GUIDELINES FOR recommended_roles_based_on_interests:\n"
        "1. SENIORITY MATCHING (HIGHEST PRIORITY):\n"
        "   - 0-2 years → Entry/Junior/SDE-1 roles ONLY\n"
        "   - 3-5 years → Mid-Level/SDE-2/Senior (lower-bound) roles\n"
        "   - 5+ years → Senior/SDE-3/Staff/Lead/Principal roles\n"
        "   - systemDesign='multiple' + 5+ years → MUST include Staff/Principal/Architect roles\n\n"
        "2. TECHNICAL SKILLS ALIGNMENT:\n"
        "   - problemSolving >= 51-100 + systemDesign != 'not-yet' → PRIORITIZE Engineering roles (Backend/Full Stack/SDE)\n"
        "   - systemDesign='multiple' is a CRITICAL signal for senior technical roles\n"
        "   - portfolio='active-5+' → Strong indicator for IC engineering roles\n\n"
        "3. RESPECT TARGET ROLE:\n"
        "   - If targetRole='faang-sde'/'backend'/'fullstack' → Top 3 recommendations MUST be engineering roles\n"
        "   - If targetRole='tech-lead' → Include Lead/Architect roles\n\n"
        "4. TECHNICAL ROLES ONLY - CRITICAL RESTRICTION:\n"
        "   ❌ NEVER RECOMMEND NON-TECHNICAL ROLES:\n"
        "   - Product Manager / Product Owner\n"
        "   - UX Designer / UI Designer / Product Designer\n"
        "   - Business Analyst / Data Analyst (non-coding)\n"
        "   - Project Manager / Scrum Master\n"
        "   - Technical Writer / Documentation Specialist\n"
        "   - QA Manual Tester (non-automation)\n\n"
        "   ✅ ONLY RECOMMEND HANDS-ON TECHNICAL/ENGINEERING ROLES:\n"
        "   - Software Development Engineer (SDE-1/2/3)\n"
        "   - Backend Engineer / Frontend Engineer / Full Stack Engineer\n"
        "   - DevOps Engineer / Site Reliability Engineer (SRE)\n"
        "   - Data Engineer / ML Engineer / AI Engineer\n"
        "   - Mobile Engineer (iOS/Android)\n"
        "   - Platform Engineer / Infrastructure Engineer\n"
        "   - Security Engineer / Cloud Engineer\n"
        "   - Tech Lead / Staff Engineer / Principal Engineer (for 5+ years)\n"
        "   - Solutions Architect / System Architect (for systemDesign='multiple')\n\n"
        "   RATIONALE: We are a technical education platform teaching coding, system design, and engineering skills.\n"
        "   All recommendations must align with technical/hands-on engineering career paths.\n\n"
        "5. INDIA MARKET CONTEXT:\n"
        "   - Include Indian unicorns/startups: Flipkart, Swiggy, Zomato, CRED, PhonePe, Razorpay, Ola, Byju's, Freshworks, Zoho\n"
        "   - Include product companies: Microsoft India, Google India, Amazon India, Adobe India, Oracle, SAP Labs\n"
        "   - For topicOfInterest='fintech' → Mention Paytm, PhonePe, Razorpay, CRED\n"
        "   - For topicOfInterest='ecommerce' → Mention Flipkart, Meesho, Myntra\n"
        "   - For topicOfInterest='edtech' → Mention BYJU'S, Unacademy, Vedantu, upGrad\n"
        "   - For topicOfInterest='healthtech' → Mention PharmEasy, Practo, 1mg\n\n"
        "CRITICAL RULES FOR recommended_tools:\n"
        "❌ NEVER recommend basic/generic platforms:\n"
        "   - GitHub, GitLab, Bitbucket (everyone already uses these)\n"
        "   - LeetCode, HackerRank, Coursera, Udemy, GeeksForGeeks, CodeChef (generic learning platforms)\n"
        "   - Turbo C, Dev C++, Code::Blocks, VS Code, IntelliJ IDEA (basic IDEs everyone uses)\n"
        "   - Generic platforms without specific professional value\n\n"
        "✅ ALWAYS recommend SPECIFIC, VALUABLE tools based on targetRole:\n"
        "   For Backend Engineers:\n"
        "   - Postman/Insomnia (API testing)\n"
        "   - DataGrip/DBeaver (database management)\n"
        "   - Redis Commander (cache visualization)\n"
        "   - Prometheus + Grafana (monitoring)\n"
        "   - k6/Locust (load testing)\n"
        "   - Temporal/Airflow (workflow orchestration)\n\n"
        "   For Full Stack Engineers:\n"
        "   - Storybook (component development)\n"
        "   - React Developer Tools / Vue Devtools\n"
        "   - Webpack Bundle Analyzer\n"
        "   - Lighthouse CI (performance monitoring)\n"
        "   - Sentry (error tracking)\n\n"
        "   For System Design & Architecture:\n"
        "   - Excalidraw/Miro (architecture diagrams)\n"
        "   - Apache JMeter (performance testing)\n"
        "   - New Relic/Datadog (APM tools)\n"
        "   - Terraform/Pulumi (infrastructure as code)\n"
        "   - Consul/Vault (service mesh & secrets)\n\n"
        "   For Data/ML Engineers:\n"
        "   - Weights & Biases (ML experiment tracking)\n"
        "   - MLflow (ML lifecycle management)\n"
        "   - Great Expectations (data validation)\n"
        "   - Apache Superset (data visualization)\n"
        "   - Feast (feature store)\n\n"
        "   For DevOps/SRE:\n"
        "   - Kubernetes Dashboard\n"
        "   - ArgoCD (GitOps)\n"
        "   - Helm (package management)\n"
        "   - Falco (runtime security)\n"
        "   - PagerDuty/Opsgenie (incident management)\n\n"
        "CRITICAL RULES FOR quick_wins:\n"
        "❌ AVOID vague, generic suggestions like:\n"
        "   - 'Improve coding skills'\n"
        "   - 'Practice more problems'\n"
        "   - 'Learn system design'\n\n"
        "✅ PROVIDE SPECIFIC, ACTIONABLE quick wins (3-5 items) with clear steps:\n"
        "   Format: '[ACTION] → [SPECIFIC OUTCOME] → [TIME ESTIMATE]'\n\n"
        "   EXCELLENT Examples:\n"
        "   - 'Solve 20 medium-difficulty problems on LeetCode focusing on Trees and Graphs → Build pattern recognition → 2-3 weeks'\n"
        "   - 'Design a URL shortener system on paper with complete architecture (DB schema, caching strategy, scaling approach) → Prepare for L4/L5 system design rounds → 1 week'\n"
        "   - 'Build a production-ready REST API with authentication, rate limiting, and monitoring using FastAPI + Redis + Prometheus → Showcase in interviews → 2 weeks'\n"
        "   - 'Contribute 3 meaningful PRs to open-source projects in your target tech stack (Node.js/Python/Java) → Demonstrate collaboration skills → 3-4 weeks'\n"
        "   - 'Complete 5 mock interviews on Pramp/Interviewing.io focusing on behavioral + technical rounds → Build confidence and get feedback → 2 weeks'\n"
        "   - 'Write 2-3 technical blog posts about complex problems you solved (e.g., optimizing database queries, implementing caching) → Build personal brand → 2-3 weeks'\n"
        "   - 'Refactor your GitHub projects to include: comprehensive README, CI/CD pipeline, unit tests (>80% coverage), Docker setup → Make projects interview-ready → 1-2 weeks'\n\n"
        "CRITICAL RULES FOR opportunities_you_qualify_for:\n"
        "- List 5-7 realistic job opportunities with SPECIFIC company names from Indian market\n"
        "- Match experience level: Junior roles for 0-2 years, Mid/Senior for 3-5, Senior/Staff for 5+\n"
        "- Include mix of: Product companies, Unicorns, Well-funded startups, Service-based (if experience < 2 years)\n"
        "- Format: '[ROLE] at [SPECIFIC COMPANY] - [KEY REQUIREMENT]'\n"
        "  Examples:\n"
        "  - 'Senior Backend Engineer at Razorpay - Strong in distributed systems and payment processing'\n"
        "  - 'Staff Engineer at CRED - 5+ years with microservices architecture experience'\n"
        "  - 'SDE-2 at Flipkart - 3-5 years with e-commerce domain knowledge'\n"
        "  - 'Tech Lead at PhonePe - Proven track record in scaling fintech applications'\n\n"
        "VALIDATION CHECKLIST (Internal - Review Before Finalizing):\n"
        "☑ Does EVERY recommended role match experience level?\n"
        "☑ Does systemDesign='multiple' lead to senior/staff roles?\n"
        "☑ Are ALL roles HANDS-ON TECHNICAL/ENGINEERING roles (no PM/UX/BA/QA Manual)?\n"
        "☑ Are recommended_tools SPECIFIC and NOT basic platforms (no GitHub/GitLab/Turbo C)?\n"
        "☑ Are quick_wins DETAILED with action → outcome → timeline?\n"
        "☑ Are opportunities REALISTIC with REAL Indian company names?\n"
        "☑ Does targetRole align with top 3 recommendations?\n"
        "☑ Zero non-technical roles in the entire response?\n\n"
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
