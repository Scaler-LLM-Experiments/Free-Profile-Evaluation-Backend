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
        "- quizResponses.currentRole:\n"
        "  * Tech roles: swe-product (Product Company SDE), swe-service (Service Company SDE), devops (DevOps/Cloud/Infra), qa-support (QA/Support/Other Technical)\n"
        "  * Non-tech roles: non-tech-role, support-qa, other-engineering, student (Non-CS background)\n"
        "  * Legacy: career-switcher (treat as non-tech)\n"
        "- quizResponses.experience: '0-2', '3-5', '5-8', or '8+' years (NEW: 4 tiers instead of 3)\n"
        "- quizResponses.targetRole:\n"
        "  * Tech: backend-sde, fullstack-sde, frontend-sde, data-ml, devops-sre, mobile-dev, tech-lead\n"
        "  * Non-tech: backend-dev, fullstack-dev, data-analyst, automation-qa, exploring\n"
        "  * Legacy: faang-sde, backend, fullstack (still valid)\n"
        "- quizResponses.problemSolving: 0-10, 11-50, 51-100, 100+ (coding practice intensity - DERIVED from codingActivity/learningActivity)\n"
        "- quizResponses.systemDesign: multiple, once, not-yet (CRITICAL: 'multiple' indicates senior-level expertise - DERIVED from systemDesign comfort)\n"
        "- quizResponses.portfolio: active-5+, limited-1-5, inactive, none (DEPRECATED: not collected in new flow)\n"
        "- quizResponses.mockInterviews: weekly+, monthly, rarely, never (DEPRECATED: not collected in new flow)\n"
        "- quizResponses.requirementType: Maps to primaryGoal (better-company, level-up, higher-comp, switch-domain, upskilling, career-switch, job-security, personal-interest)\n"
        "- goals.topicOfInterest: ai-ml, web-development, mobile-development, data-science, cybersecurity, cloud-computing, blockchain, etc.\n\n"
        "⚠️ CRITICAL: LOGICAL CONSISTENCY CHECK (Evaluate FIRST before making recommendations):\n"
        "INPUT CONTRADICTIONS - Real-world skill progression rules:\n\n"
        "1. SYSTEM DESIGN vs CODING CONTRADICTION:\n"
        "   🚨 IMPOSSIBLE COMBINATION: systemDesign='multiple' + problemSolving < '51-100'\n"
        "   Reality: You CANNOT have deep system design expertise without extensive coding practice.\n"
        "   System design requires years of building production systems, which means 100s of problems solved.\n\n"
        "   Resolution Rules:\n"
        "   - If systemDesign='multiple' + problemSolving='0-10' or '11-50' + experience <= '3-5':\n"
        "     → User likely misunderstood questions or is being aspirational\n"
        "     → OVERRIDE: Treat as systemDesign='once' or 'not-yet'\n"
        "     → Recommend Junior/Mid roles (NOT senior)\n"
        "     → In profile_strength_notes: 'Strong interest in system design, but limited coding practice. Focus on solving 100+ problems first.'\n\n"
        "   - If systemDesign='multiple' + problemSolving < '51-100' + experience in ['5-8', '8+'] + currentRole contains 'manager'/'architect':\n"
        "     → Rare case: Transitioned to management/architecture, coding skills atrophied\n"
        "     → Can recommend Architect/Lead roles BUT:\n"
        "     → MUST flag in areas_to_develop: 'Hands-on coding skills - rusty from lack of practice'\n"
        "     → In profile_strength_notes: 'Architecture experience is valuable, but hands-on coding needs refresh for IC roles.'\n\n"
        "   - General rule: NEVER recommend Staff/Principal/Senior SDE if problemSolving < '51-100'\n"
        "     → These roles require deep coding expertise, no exceptions\n\n"
        "2. EXPERIENCE vs SKILLS CONTRADICTION:\n"
        "   - If experience in ['5-8', '8+'] + problemSolving='0-10':\n"
        "     → Likely stuck in maintenance roles or exaggerating experience\n"
        "     → Recommend mid-level roles, NOT senior\n"
        "     → Flag in notes: 'Experience level doesn't match interview preparation. Results may not reflect actual capability.'\n\n"
        "3. PORTFOLIO vs CODING CONTRADICTION:\n"
        "   - If portfolio='active-5+' + problemSolving='0-10':\n"
        "     → Projects likely tutorials/clones, not production-grade\n"
        "     → Good signal for potential, but not for senior roles\n\n"
        "CRITICAL GUIDELINES FOR recommended_roles_based_on_interests:\n"
        "1. SENIORITY MATCHING (HIGHEST PRIORITY - NEW 4-TIER SYSTEM):\n"
        "   - 0-2 years → Entry/Junior/SDE-1 roles ONLY\n"
        "   - 3-5 years → Mid-Level/SDE-2/Senior (lower-bound) roles\n"
        "   - 5-8 years → Senior/SDE-3/Staff roles (IF coding skills match - see consistency check)\n"
        "   - 8+ years → Staff/Principal/Lead/Architect roles (IF coding skills match - see consistency check)\n"
        "   - systemDesign='multiple' + problemSolving >= '51-100' + experience in ['5-8', '8+'] → MUST include Staff/Principal/Architect roles\n"
        "   - experience='8+' + strong skills → Prioritize Principal/Architect/Engineering Manager roles\n\n"
        "2. TECHNICAL SKILLS ALIGNMENT:\n"
        "   - problemSolving >= 51-100 + systemDesign != 'not-yet' → PRIORITIZE Engineering roles (Backend/Full Stack/SDE)\n"
        "   - systemDesign='multiple' + problemSolving >= '51-100' → CRITICAL signal for senior technical roles (Staff/Principal)\n"
        "   - systemDesign='multiple' WITHOUT strong coding (< 51-100) → See LOGICAL CONSISTENCY CHECK above - override system design claim\n"
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
        "✅ ALWAYS recommend SPECIFIC, VALUABLE tools from these curated lists:\n\n"
        "   NON-TECH BACKGROUND TOOL RECOMMENDATIONS:\n"
        "   → Non-Tech → Backend Engineer:\n"
        "      Core: Python, Flask, SQL, Git, Postman\n"
        "      Guidance: Start with automating small tasks, practice REST API testing with Postman\n\n"
        "   → Non-Tech → Full-Stack Engineer:\n"
        "      Core: HTML, CSS, JavaScript (basics) → React + Node.js\n"
        "      Sandboxes: Replit, CodeSandbox (for practice without local setup)\n"
        "      Guidance: Start with frontend basics, then add backend gradually\n\n"
        "   → Non-Tech → Data/ML Engineer:\n"
        "      Core: Python, Pandas, NumPy, scikit-learn, Jupyter\n"
        "      Guidance: Start with EDA on public datasets (Kaggle), focus on data cleaning\n\n"
        "   → Non-Tech → Data Analyst:\n"
        "      Core: Excel (advanced formulas), SQL, PowerBI/Tableau\n"
        "      Guidance: Practice with Kaggle datasets, build dashboards\n\n"
        "   TECH BACKGROUND TOOL RECOMMENDATIONS:\n"
        "   → Tech → FAANG/Product SDE:\n"
        "      Interview Prep: System Design Primer (GitHub), LLD/HLD prep materials\n"
        "      Project Tools: Postman (API testing), Docker (containerization), GitHub Actions (CI/CD)\n"
        "      Do NOT recommend LeetCode/HackerRank - assume they already know these\n\n"
        "   → Tech → Full-stack / Startup Engineer:\n"
        "      Stack: MERN stack tools (React DevTools, MongoDB Compass, Postman)\n"
        "      DevOps: Docker basics, GitHub Actions, Vercel/Netlify deployment\n"
        "      Guidance: Focus on rapid prototyping and deployment tools\n\n"
        "   → Tech → Data/ML Engineer:\n"
        "      ML Tools: PyTorch/TensorFlow, MLflow, Weights & Biases\n"
        "      Data Pipeline: Airflow, Databricks basics, Great Expectations\n"
        "      Guidance: Focus on productionizing models and data pipelines\n\n"
        "   → Tech → Tech Lead/Architect:\n"
        "      Design: Draw.io, Excalidraw, Miro (architecture diagrams)\n"
        "      Cloud Infra: AWS/GCP tools (CloudFormation, Terraform)\n"
        "      Monitoring: Datadog, New Relic, Prometheus + Grafana\n"
        "      Guidance: Focus on system architecture, scaling, and team collaboration\n\n"
        "   ADDITIONAL PROFESSIONAL TOOLS (pick 3-5 based on role):\n"
        "   - API Testing: Postman, Insomnia, Thunder Client\n"
        "   - Database Management: DataGrip, DBeaver, TablePlus\n"
        "   - Monitoring: Prometheus + Grafana, Datadog, New Relic\n"
        "   - Load Testing: k6, Locust, Apache JMeter\n"
        "   - Error Tracking: Sentry, Rollbar, Bugsnag\n"
        "   - Infrastructure: Terraform, Pulumi, Ansible\n"
        "   - Containerization: Docker, Kubernetes Dashboard\n"
        "   - CI/CD: GitHub Actions, Jenkins, ArgoCD\n"
        "   - ML/Data: MLflow, Weights & Biases, Great Expectations\n\n"
        "CRITICAL RULES FOR quick_wins:\n"
        "❌ AVOID vague, generic suggestions like:\n"
        "   - 'Improve coding skills'\n"
        "   - 'Practice more problems'\n"
        "   - 'Learn system design'\n\n"
        "✅ PROVIDE SPECIFIC, ACTIONABLE quick wins (3-5 items) with clear steps:\n"
        "   Format: '[ACTION] → [SPECIFIC OUTCOME] → [TIME ESTIMATE]'\n\n"
        "   Use the following decision tree based on user's quiz responses:\n\n"
        "   NON-TECH BACKGROUND QUICK WINS:\n"
        "   → Current Role = 'non-tech' (sales, ops, design, etc.):\n"
        "      'Start with basic programming: try \"Intro to Python\" (Scaler Topics / W3Schools). Build a small automation like Excel-to-CSV script.'\n\n"
        "   → Current Role = 'it-services' (IT services / testing / support):\n"
        "      'Brush up on coding fundamentals — loops, conditions. Try solving 5 problems on HackerRank.'\n\n"
        "   → Current Role = 'technical' (Other technical but not software dev):\n"
        "      'Revisit core CS concepts. Build a basic CRUD app using Python or Node.js.'\n\n"
        "   → Current Role = 'fresh-graduate' (non-CS branch):\n"
        "      'Learn DSA basics and attempt 10 beginner-level problems this week.'\n\n"
        "   → Experience = '0' years:\n"
        "      'Set up GitHub, complete 1 online course on programming basics.'\n\n"
        "   → Experience = '0-2' years:\n"
        "      'Create a mini-project — e.g., to-do app or data dashboard.'\n\n"
        "   → Experience = '3-5' years:\n"
        "      'Add measurable projects to your portfolio showing transition intent.'\n\n"
        "   → Experience = '5+' years:\n"
        "      'Update your resume headline to reflect transition goals (e.g., \"Operations Manager → Aspiring Backend Engineer\").'\n\n"
        "   → Target Role = 'backend':\n"
        "      'Build a small REST API using Flask/Django. Learn SQL basics.'\n\n"
        "   → Target Role = 'fullstack':\n"
        "      'Build a simple web app with HTML, CSS, JS. Host it on GitHub Pages.'\n\n"
        "   → Target Role = 'data-ml':\n"
        "      'Do 1 mini project using Pandas & scikit-learn (e.g., movie recommender).'\n\n"
        "   → Target Role = 'data-analyst':\n"
        "      'Explore Excel → SQL → Power BI sequence. Analyze a public dataset.'\n\n"
        "   → Code Comfort = 'havent-tried' (Haven't tried yet):\n"
        "      'Write your first \"Hello World\" program today — use Scaler Topics Playground.'\n\n"
        "   → Code Comfort = 'follow-tutorials' (Can follow tutorials but struggle independently):\n"
        "      'Practice 5 easy-level problems.'\n\n"
        "   → Code Comfort = 'solve-problems' (Can solve simple problems):\n"
        "      'Attempt 1 beginner DSA contest or solve 10 new problems in a week.'\n\n"
        "   → Motivation = 'interest' (Interest in technology):\n"
        "      'Explore open-source projects — try contributing small edits.'\n\n"
        "   → Motivation = 'job-stability' (Job stability / future-proofing):\n"
        "      'Learn a growing tech like Python or Cloud Fundamentals.'\n\n"
        "   TECH BACKGROUND QUICK WINS:\n"
        "   → Current Role = 'student-freshgrad' (Student / Fresh Grad):\n"
        "      'Complete 10 DSA problems this week. Attend 1 coding contest.'\n\n"
        "   → Current Role = 'swe-product' (Working SWE - Product):\n"
        "      'Revise 1 core concept daily (System Design / DSA).'\n\n"
        "   → Current Role = 'swe-service' (Working SWE - Service):\n"
        "      'Try building a side project or switch tech stack exposure (MERN, backend).'\n\n"
        "   → Current Role = 'career-switcher' (Career Switcher):\n"
        "      'Start documenting learnings on GitHub and LinkedIn.'\n\n"
        "   → Experience = '0' years:\n"
        "      'Focus on fundamentals — arrays, loops, functions.'\n\n"
        "   → Experience = '0-2' years:\n"
        "      'Create a resume-ready project showing practical application.'\n\n"
        "   → Experience = '3-5' years:\n"
        "      'Mentor juniors or write blogs on tech concepts.'\n\n"
        "   → Experience = '5+' years:\n"
        "      'Prepare for leadership — learn system design + mentoring skills.'\n\n"
        "   → Target Role = 'faang-sde' (FAANG / Product SDE):\n"
        "      'Start a 90-day Code streak. Revise system design weekly.'\n\n"
        "   → Target Role = 'backend' (Backend Engineer):\n"
        "      'Build an API with Node/Express or Django.'\n\n"
        "   → Target Role = 'data-ml' (Data/ML Engineer):\n"
        "      'Try Kaggle competitions or build 1 model with scikit-learn.'\n\n"
        "   → Target Role = 'fullstack' (Full-stack / Startup Engineer):\n"
        "      'Create a complete CRUD app using MERN or Django + React.'\n\n"
        "   → Target Role = 'tech-lead' (Tech Lead):\n"
        "      'Write design docs for a personal project. Focus on scalability concepts.'\n\n"
        "   → System Design = 'multiple' (Yes, multiple times):\n"
        "      'Try low-level design problems (class diagrams, APIs).'\n\n"
        "   → System Design = 'once' (Yes, once):\n"
        "      'Read 2 new design case studies (TinyURL, Instagram).'\n\n"
        "   → System Design = 'not-yet' (Not yet):\n"
        "      'Watch 1 short \"System Design for Beginners\" video today.'\n\n"
        "   → Portfolio = 'active-5+' (GitHub active - 5+ repos):\n"
        "      'Add README, host one project live.'\n\n"
        "   → Portfolio = 'limited-1-5' (GitHub limited - 1-5 repos):\n"
        "      'Commit 1 new project this week.'\n\n"
        "   → Portfolio = 'inactive' (GitHub inactive):\n"
        "      'Upload your practice code or course projects.'\n\n"
        "   → Portfolio = 'none' (No GitHub):\n"
        "      'Create a GitHub account and push first project today.'\n\n"
        "   IMPLEMENTATION GUIDELINES:\n"
        "   - Select 3-5 most relevant quick wins based on the user's specific profile\n"
        "   - Prioritize based on: current role → experience → target role → skills\n"
        "   - Combine related suggestions when appropriate\n"
        "   - Ensure actionable items that can be completed in 1-4 weeks\n"
        "   - Use the exact wording provided above, but adapt if multiple conditions apply\n\n"
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
