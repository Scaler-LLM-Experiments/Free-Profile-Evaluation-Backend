"""
Job opportunity descriptions - uses frontend labels (no actual company names).

Generates specific, crisp job descriptions based on user profile.
Uses human-readable labels from frontend quiz questions.
"""

from typing import Any, Dict, List
import hashlib
from label_mappings import format_job_title, get_role_label, get_company_label


def _get_seniority_level(quiz_responses: Dict[str, Any]) -> str:
    """
    Determine seniority level from experience and skills.

    CRITICAL: Consider multiple signals - not just interview prep metrics.
    A 3-5 year product engineer with strong portfolio deserves senior roles.
    """
    experience = quiz_responses.get("experience", "0-2")
    problem_solving = quiz_responses.get("problemSolving", "0-10")
    system_design = quiz_responses.get("systemDesign", "not-yet")
    portfolio = quiz_responses.get("portfolio", "none")
    current_role = quiz_responses.get("currentRole", "")

    # Advanced: 5+ years + strong system design
    if experience in ["5-8", "8+"] and system_design == "multiple":
        return "staff"  # Staff/Principal Engineer

    # Senior: 5+ years (always senior regardless of prep)
    if experience in ["5-8", "8+"]:
        return "senior"

    # Senior: 3-5 years with strong experience signals (not just interview prep)
    if experience == "3-5":
        experience_signals = 0

        # Interview readiness signals
        if problem_solving in ["51-100", "100+"]: experience_signals += 2
        if system_design in ["once", "multiple"]: experience_signals += 2

        # Real-world experience signals (equally important!)
        if portfolio in ["active-5+", "limited-1-5"]: experience_signals += 1
        if current_role in ["swe-product", "devops"]: experience_signals += 1

        # 3+ signals = senior level (can be mix of interview prep + experience)
        if experience_signals >= 3:
            return "senior"

    # Mid: 3-5 years DEFAULT to mid-level (respect real-world experience)
    if experience == "3-5":
        # Only mark as junior if VERY weak signals (service company + no prep + no portfolio)
        if (problem_solving == "0-10" and
            portfolio == "none" and
            current_role == "swe-service"):
            return "junior"

        # Otherwise, 3-5 years of experience = mid-level
        return "mid"

    # Junior: 0-2 years get junior roles
    # Even with 100+ LeetCode problems, fresh grads lack production experience
    # Companies want 2-4 years for SDE-2/mid-level roles
    return "junior"


# Generic job description templates (no company names, just skill requirements)
JOB_TEMPLATES = {
    # === BACKEND ROLES ===
    "backend_junior": [
        "Java/Python, REST APIs, SQL, strong DSA fundamentals",
        "Go/Python, microservices basics, distributed systems interest",
        "Node.js or Java, API design, testing, debugging skills",
    ],
    "backend_mid": [
        "Microservices, Kafka, Redis, 3+ years production experience",
        "System design knowledge, database optimization, API scaling",
        "Distributed systems, event-driven architecture, mentoring juniors",
    ],
    "backend_senior": [
        "Microservices at scale, trade-off analysis, architecture decisions",
        "High-throughput systems, cross-team collaboration, technical leadership",
        "System architecture, 10M+ scale, strategic technical direction",
    ],

    # === FULLSTACK ROLES ===
    "fullstack_junior": [
        "React + Node.js, REST APIs, SQL, strong fundamentals",
        "JavaScript/TypeScript, frontend + backend, testing, cloud basics",
        "MERN or Django + React, API design, deployment",
    ],
    "fullstack_mid": [
        "React + Node.js, system design, 3+ years production",
        "End-to-end ownership, microservices, database optimization",
        "Architecture decisions, scalability, mentor juniors, cloud platforms",
    ],
    "fullstack_senior": [
        "Technical leadership, architecture, cross-team projects, 5+ years",
        "Frontend + backend at scale, strategic decisions, org impact",
        "Full-stack architecture, mentoring, performance optimization expertise",
    ],

    # === FRONTEND ROLES ===
    "frontend_junior": [
        "React, JavaScript, CSS, API integration, testing",
        "React/Vue, responsive design, REST APIs, version control",
        "HTML/CSS/JavaScript, React basics, mobile-first design",
    ],
    "frontend_mid": [
        "React + TypeScript, state management, performance optimization",
        "Component architecture, testing, accessibility, 3+ years",
        "React, Next.js, GraphQL, cross-browser compatibility",
    ],
    "frontend_senior": [
        "Frontend architecture, design systems, technical leadership",
        "React ecosystem, performance, mentor engineers, strategic decisions",
        "UI architecture, scalability, cross-team impact, 5+ years",
    ],

    # === DATA/ML ROLES ===
    "data_junior": [
        "Python, SQL, Airflow, data pipelines, ETL basics",
        "Python, Pandas, scikit-learn, model deployment basics",
        "SQL, Python, data visualization, business insights",
    ],
    "data_mid": [
        "Spark, Airflow, data lakes, 3+ years experience",
        "PyTorch/TensorFlow, MLOps, model deployment, scaling",
        "Python, ML models, A/B testing, production deployments",
    ],
    "data_senior": [
        "Data architecture, large-scale pipelines, technical leadership",
        "ML systems, model optimization, cross-functional leadership",
        "Data strategy, ML infrastructure, org-wide impact",
    ],

    # === DEVOPS/SRE ROLES ===
    "devops_junior": [
        "AWS/GCP, Docker, CI/CD, Linux, scripting",
        "Kubernetes, monitoring, incident response, automation",
        "AWS services, infrastructure as code, basic networking",
    ],
    "devops_mid": [
        "Kubernetes, Terraform, monitoring, 3+ years production",
        "Site reliability, incident management, automation, on-call",
        "AWS/GCP/Azure, infrastructure design, cost optimization",
    ],
    "devops_senior": [
        "Platform engineering, reliability, technical leadership, 5+ years",
        "Cloud infrastructure, team mentoring, strategic planning",
        "Infrastructure architecture, cross-team impact, org strategy",
    ],

    # === LEADERSHIP ROLES ===
    "tech_lead": [
        "Technical direction, architecture, team mentoring, delivery",
        "Team leadership, project planning, technical decisions, hiring",
        "Technical strategy, cross-team collaboration, architecture",
    ],

    "architect": [
        "System design, scalability, cloud architecture, technical consulting",
        "Enterprise architecture, strategic planning, org-wide impact",
        "Distributed systems, technical roadmaps, architecture reviews",
    ],
}


def _get_tech_stack_from_profile(quiz_responses: Dict[str, Any]) -> str:
    """Infer primary tech stack from user's current skill and target role."""
    current_skill = quiz_responses.get("currentSkill", "")
    target_role = quiz_responses.get("targetRole", "")

    # Mapping of skills/roles to tech stacks
    if current_skill in ["backend", "database"]:
        return "backend"
    elif current_skill in ["frontend", "web"]:
        return "frontend"
    elif current_skill == "fullstack":
        return "fullstack"
    elif current_skill in ["system-design"]:
        return "architecture"
    elif current_skill in ["cloud", "containers", "cicd", "iac"]:
        return "devops"
    elif target_role in ["data-ml", "data-engineer"]:
        return "data"

    # Default based on target role
    if target_role in ["backend-sde", "backend", "backend-dev", "backend-fullstack", "senior-backend"]:
        return "backend"
    elif target_role in ["fullstack-sde", "fullstack", "fullstack-dev", "senior-fullstack"]:
        return "fullstack"
    elif target_role in ["data-ml", "data-engineer"]:
        return "data"
    elif target_role in ["tech-lead"]:
        return "architecture"

    return "fullstack"  # Default


def _get_template_key(tech_stack: str, seniority: str) -> str:
    """Generate template key from tech_stack and seniority."""
    # Map staff → senior for template lookup (we use senior templates for staff)
    template_seniority = "senior" if seniority == "staff" else seniority

    # Special cases for leadership roles
    if seniority == "staff" and tech_stack == "architecture":
        return "architect"
    if seniority in ["senior", "staff"] and tech_stack == "architecture":
        return "tech_lead"

    # Tech stack + seniority
    if tech_stack == "devops":
        return f"devops_{template_seniority}"
    elif tech_stack == "data":
        return f"data_{template_seniority}"
    elif tech_stack == "frontend":
        return f"frontend_{template_seniority}"
    elif tech_stack in ["backend", "fullstack", "architecture"]:
        return f"{tech_stack}_{template_seniority}"

    # Fallback to fullstack
    return f"fullstack_{template_seniority}"


def generate_job_opportunities(background: str, quiz_responses: Dict[str, Any]) -> List[str]:
    """
    Generate 5-7 specific job opportunities using frontend labels.

    Format: "{Role Label} - {Company Label} - {Requirements}"
    Example: "Senior Backend Engineer - FAANG / Big Tech - Microservices at scale, trade-off analysis..."

    NO ACTUAL COMPANY NAMES - uses generic company type labels from frontend.
    """
    seniority = _get_seniority_level(quiz_responses)
    tech_stack = _get_tech_stack_from_profile(quiz_responses)

    target_role = quiz_responses.get("targetRole", "")
    target_company = quiz_responses.get("targetCompany", "")

    # Format job title using frontend labels (e.g., "Senior Backend Engineer - FAANG / Big Tech")
    job_title_prefix = format_job_title(target_role, target_company)

    # Get template key
    template_key = _get_template_key(tech_stack, seniority)

    # Get job templates (requirements only, no company names)
    templates = JOB_TEMPLATES.get(template_key, JOB_TEMPLATES.get("fullstack_mid", []))

    # Generate opportunities (5-7 jobs with same title but different requirements)
    opportunities = []
    for requirement in templates[:7]:  # Max 7 variations
        opportunity = f"{job_title_prefix} - {requirement}"
        opportunities.append(opportunity)

    # If we have fewer than 5, return what we have (no duplication)
    # Better to have 3-4 unique opportunities than duplicate ones
    return opportunities


# Example usage for testing
if __name__ == "__main__":
    # Test case 1: Senior backend engineer targeting FAANG
    test_profile_1 = {
        "experience": "5-8",
        "currentRole": "swe-product",
        "targetRole": "senior-backend",
        "targetCompany": "faang",
        "currentSkill": "backend",
        "problemSolving": "100+",
        "systemDesign": "multiple"
    }

    print("Test Case 1: Senior Backend Engineer targeting FAANG")
    print("=" * 80)
    opportunities = generate_job_opportunities("tech", test_profile_1)
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp}")

    print("\n\nTest Case 2: Junior Fullstack targeting startups")
    print("=" * 80)
    test_profile_2 = {
        "experience": "0-2",
        "currentRole": "swe-service",
        "targetRole": "fullstack-sde",
        "targetCompany": "startups",
        "currentSkill": "fullstack",
        "problemSolving": "11-50",
        "systemDesign": "not-yet"
    }
    opportunities = generate_job_opportunities("tech", test_profile_2)
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. {opp}")
