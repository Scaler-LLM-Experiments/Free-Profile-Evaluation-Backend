"""
Hardcoded tool recommendations - NO GENERIC TOOLS!

🚨 ABSOLUTE BAN LIST:
- LeetCode, HackerRank, CodeChef
- GitHub, GitLab, Bitbucket
- VS Code, IntelliJ IDEA
- Coursera, Udemy, GeeksForGeeks

✅ ONLY PROFESSIONAL, SPECIFIC TOOLS
"""

from typing import Any, Dict, List


def generate_tool_recommendations(background: str, quiz_responses: Dict[str, Any]) -> List[str]:
    """
    Generate 5-8 specific, professional tool recommendations.

    NO generic IDEs, NO basic platforms everyone knows.
    """
    tools = []

    current_role = quiz_responses.get("currentRole", "")
    target_role = quiz_responses.get("targetRole", "")
    current_skill = quiz_responses.get("currentSkill", "")
    experience = quiz_responses.get("experience", "0-2")
    system_design = quiz_responses.get("systemDesign", "not-yet")

    if background == "non-tech":
        # NON-TECH BACKGROUND - Beginner-friendly tools
        target_role = quiz_responses.get("targetRole", "")

        if target_role in ["backend", "backend-dev"]:
            tools = [
                "Postman - API testing and debugging",
                "DBeaver - Database client for SQL learning",
                "Flask or Django - Python web frameworks",
                "Replit - Online coding environment (no setup needed)",
                "TablePlus - Visual database management"
            ]
        elif target_role in ["fullstack", "fullstack-dev"]:
            tools = [
                "CodeSandbox - Online React playground",
                "Postman - API testing and integration",
                "MongoDB Compass - Visual database tool",
                "React DevTools - Browser extension for debugging",
                "Netlify or Vercel - One-click deployment platforms"
            ]
        elif target_role == "data-ml":
            tools = [
                "Jupyter Notebook - Interactive Python environment",
                "Pandas & NumPy - Data manipulation libraries",
                "Kaggle - Dataset repository and competitions",
                "Google Colab - Free cloud Jupyter environment",
                "Matplotlib & Seaborn - Data visualization libraries"
            ]
        elif target_role == "data-analyst":
            tools = [
                "Power BI or Tableau - Dashboard creation tools",
                "DBeaver - SQL query and database management",
                "Excel Power Query - Advanced data transformation",
                "Kaggle Datasets - Practice with real-world data",
                "Google Data Studio - Free dashboard tool"
            ]
        else:
            # Generic non-tech starting
            tools = [
                "Replit - Online coding (no local setup)",
                "Postman - API testing basics",
                "CodeSandbox - Frontend practice",
                "DBeaver - SQL learning and practice",
                "Scaler Topics Playground - Interactive tutorials"
            ]

    else:
        # TECH BACKGROUND - Professional tools

        # Add system design tools for experienced engineers
        if experience in ["3-5", "5-8", "8+"] or system_design in ["once", "multiple"]:
            tools.append("Excalidraw or Draw.io - System architecture diagrams")
            tools.append("Miro - Collaborative design whiteboarding")

        # Role-specific tools
        if current_skill in ["backend", "database"] or target_role in ["backend-sde", "backend"]:
            tools.extend([
                "Postman or Insomnia - API development and testing",
                "DataGrip or DBeaver - Advanced database management",
                "Docker - Containerization for local development",
                "k6 or Locust - Load testing and performance"
            ])

            if experience in ["3-5", "5-8", "8+"] or system_design != "not-yet":
                tools.append("Terraform - Infrastructure as Code")
                tools.append("Prometheus + Grafana - Monitoring and metrics")

        elif current_skill in ["frontend", "web"] or target_role == "frontend-sde":
            tools.extend([
                "React DevTools - Browser debugging extension",
                "Lighthouse - Performance and accessibility audits",
                "Storybook - Component documentation and testing",
                "Webpack Bundle Analyzer - Bundle size optimization"
            ])

            if experience in ["3-5", "5-8", "8+"]:
                tools.append("Chromatic - Visual regression testing")
                tools.append("Sentry - Error tracking and monitoring")

        elif current_skill == "fullstack" or target_role in ["fullstack-sde", "fullstack"]:
            tools.extend([
                "Postman - API development and testing",
                "Docker - Full-stack containerization",
                "React DevTools - Frontend debugging",
                "GitHub Actions or Jenkins - CI/CD pipelines"
            ])

            if experience in ["3-5", "5-8", "8+"]:
                tools.append("Datadog or New Relic - Application monitoring")
                tools.append("Sentry - Error tracking across stack")

        elif current_skill in ["cloud", "containers", "cicd", "iac"] or current_role == "devops":
            tools.extend([
                "Terraform or Pulumi - Infrastructure as Code",
                "Kubernetes Dashboard - K8s cluster management",
                "Prometheus + Grafana - Metrics and alerting",
                "ArgoCD - GitOps continuous delivery"
            ])

            if experience in ["3-5", "5-8", "8+"]:
                tools.append("Datadog - Cloud infrastructure monitoring")
                tools.append("Vault - Secrets management")

        elif target_role in ["data-ml", "data-engineer", "ml-engineer"]:
            tools.extend([
                "MLflow - ML experiment tracking",
                "Weights & Biases - Model training visualization",
                "Airflow or Prefect - Data pipeline orchestration",
                "Great Expectations - Data quality testing"
            ])

            if experience in ["3-5", "5-8", "8+"]:
                tools.append("Databricks - Big data and ML platform")
                tools.append("Kubeflow - ML operations on Kubernetes")

        elif target_role == "tech-lead" or system_design == "multiple":
            tools.extend([
                "Excalidraw - System architecture diagrams",
                "Miro - Team collaboration and whiteboarding",
                "Terraform - Infrastructure design and management",
                "Datadog or New Relic - Production system monitoring"
            ])

            tools.append("Sentry or Rollbar - Error tracking and alerting")
            tools.append("PagerDuty - Incident management")

        # Add general professional tools for all tech roles
        if len(tools) < 5:
            tools.extend([
                "Postman - API development and testing",
                "Docker - Containerization basics",
                "Sentry - Error tracking and monitoring"
            ])

    # Remove duplicates while preserving order
    seen = set()
    unique_tools = []
    for tool in tools:
        if tool not in seen:
            seen.add(tool)
            unique_tools.append(tool)

    # Return 5-8 tools max
    return unique_tools[:8]


# Example usage for testing
if __name__ == "__main__":
    print("=" * 80)
    print("TOOL RECOMMENDATIONS TEST CASES")
    print("=" * 80)

    # Test 1: Senior Backend Engineer
    test_1 = {
        "currentRole": "swe-product",
        "experience": "5-8",
        "targetRole": "backend-sde",
        "currentSkill": "backend",
        "systemDesign": "multiple"
    }
    tools_1 = generate_tool_recommendations("tech", test_1)
    print(f"\nTest 1: Senior Backend Engineer")
    for i, tool in enumerate(tools_1, 1):
        print(f"  {i}. {tool}")

    # Test 2: Junior Fullstack
    test_2 = {
        "currentRole": "swe-service",
        "experience": "0-2",
        "targetRole": "fullstack-sde",
        "currentSkill": "fullstack",
        "systemDesign": "not-yet"
    }
    tools_2 = generate_tool_recommendations("tech", test_2)
    print(f"\nTest 2: Junior Fullstack Engineer")
    for i, tool in enumerate(tools_2, 1):
        print(f"  {i}. {tool}")

    # Test 3: Non-Tech → Backend
    test_3 = {
        "targetRole": "backend",
        "experience": "0",
        "codeComfort": "learning"
    }
    tools_3 = generate_tool_recommendations("non-tech", test_3)
    print(f"\nTest 3: Non-Tech Career Switcher (Backend)")
    for i, tool in enumerate(tools_3, 1):
        print(f"  {i}. {tool}")

    # Test 4: DevOps Engineer
    test_4 = {
        "currentRole": "devops",
        "experience": "3-5",
        "targetRole": "devops-sre",
        "currentSkill": "cloud",
        "systemDesign": "once"
    }
    tools_4 = generate_tool_recommendations("tech", test_4)
    print(f"\nTest 4: DevOps Engineer")
    for i, tool in enumerate(tools_4, 1):
        print(f"  {i}. {tool}")

    # Test 5: ML Engineer
    test_5 = {
        "currentRole": "swe-product",
        "experience": "3-5",
        "targetRole": "data-ml",
        "currentSkill": "backend",
        "systemDesign": "once"
    }
    tools_5 = generate_tool_recommendations("tech", test_5)
    print(f"\nTest 5: ML Engineer")
    for i, tool in enumerate(tools_5, 1):
        print(f"  {i}. {tool}")

    print("\n" + "=" * 80)
    print("KEY PRINCIPLES:")
    print("=" * 80)
    print("❌ NEVER: LeetCode, HackerRank, GitHub, VS Code, Coursera")
    print("✅ ALWAYS: Postman, Docker, Terraform, Datadog, Sentry, MLflow")
    print("✅ SPECIFIC to role: Backend → k6/Locust, Frontend → Lighthouse/Storybook")
    print("✅ SENIORITY-AWARE: Junior → basics, Senior → monitoring/infrastructure")
