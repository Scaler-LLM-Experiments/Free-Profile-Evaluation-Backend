"""
AI Response Validation Script

This script validates the AI-generated profile evaluation responses for logical consistency
and provides suggestions for prompt improvements.
"""

import json
import sys
from typing import Dict, List, Any, Tuple


class ResponseValidator:
    def __init__(self, input_payload: Dict[str, Any], response: Dict[str, Any]):
        self.input = input_payload
        self.response = response
        self.issues = []
        self.warnings = []
        self.suggestions = []

    def validate_all(self) -> Tuple[List[str], List[str], List[str]]:
        """Run all validation checks"""
        self.validate_role_seniority_match()
        self.validate_technical_role_alignment()
        self.validate_no_non_technical_roles()
        self.validate_skill_vs_opportunities()
        self.validate_system_design_acknowledgment()
        self.validate_experience_vs_readiness()
        self.validate_score_consistency()
        self.validate_portfolio_vs_roles()
        self.validate_no_basic_tools()

        return self.issues, self.warnings, self.suggestions

    def validate_role_seniority_match(self):
        """Check if recommended roles match experience level"""
        quiz = self.input.get("quizResponses", {})
        experience = quiz.get("experience", "")
        recommended_roles = self.response.get("profile_evaluation", {}).get(
            "recommended_roles_based_on_interests", []
        )

        # Define seniority levels
        junior_keywords = ["junior", "entry", "associate", "trainee"]
        mid_keywords = ["mid", "engineer", "developer", "sde", "analyst"]
        senior_keywords = ["senior", "staff", "lead", "principal", "architect", "manager"]

        experience_level = None
        if experience in ["0", "0-2"]:
            experience_level = "junior"
        elif experience == "3-5":
            experience_level = "mid-senior"
        elif experience == "5+":
            experience_level = "senior"

        if not experience_level:
            return

        for role_obj in recommended_roles:
            role_title = role_obj.get("title", "").lower()

            # Check for mismatches
            if experience_level == "senior" and any(kw in role_title for kw in junior_keywords):
                self.issues.append(
                    f"CRITICAL: User has {experience} years experience but recommended '{role_obj.get('title')}' "
                    f"which is a junior role. Should recommend Senior/Staff/Lead roles instead."
                )
                self.suggestions.append(
                    "Improve prompt: Add stronger constraint that maps experience directly to seniority: "
                    "0-2 years → Entry/Junior, 3-5 years → Mid/Senior, 5+ years → Senior/Staff/Lead/Principal"
                )

            if experience_level == "mid-senior" and any(kw in role_title for kw in junior_keywords):
                self.warnings.append(
                    f"User has {experience} years experience but recommended '{role_obj.get('title')}' "
                    f"which seems junior. Consider mid-level roles."
                )

    def validate_technical_role_alignment(self):
        """Check if technical skills match technical roles"""
        quiz = self.input.get("quizResponses", {})
        problem_solving = quiz.get("problemSolving", "")
        system_design = quiz.get("systemDesign", "")
        target_role = quiz.get("targetRole", "")
        recommended_roles = self.response.get("profile_evaluation", {}).get(
            "recommended_roles_based_on_interests", []
        )

        # Strong coding indicators
        strong_coding = problem_solving in ["51-100", "100+"]
        has_system_design = system_design in ["once", "multiple"]
        targets_engineering = target_role in ["faang-sde", "backend", "fullstack", "tech-lead"]

        # Check if user has strong technical skills
        if strong_coding or has_system_design:
            non_technical_roles = []
            for role_obj in recommended_roles:
                role_title = role_obj.get("title", "").lower()
                # Check for non-technical roles
                if any(keyword in role_title for keyword in [
                    "product manager", "pm ", "program manager", "business analyst",
                    "product owner", "scrum master"
                ]):
                    non_technical_roles.append(role_obj.get("title"))

            if non_technical_roles and targets_engineering:
                self.issues.append(
                    f"CRITICAL: User has strong technical skills (problemSolving={problem_solving}, "
                    f"systemDesign={system_design}) and targets {target_role}, but AI recommended "
                    f"non-technical roles: {', '.join(non_technical_roles)}"
                )
                self.suggestions.append(
                    "Improve prompt: Add explicit rule - 'If problemSolving >= 51-100 AND targetRole contains "
                    "'sde'/'backend'/'fullstack', ONLY recommend engineering roles (SDE, Backend Engineer, "
                    "Full Stack Engineer, etc.), NOT Product Manager or Business Analyst roles.'"
                )

    def validate_pm_role_appropriateness(self):
        """Check if PM roles are only suggested when appropriate"""
        quiz = self.input.get("quizResponses", {})
        target_role = quiz.get("targetRole", "")
        experience = quiz.get("experience", "")
        problem_solving = quiz.get("problemSolving", "")
        recommended_roles = self.response.get("profile_evaluation", {}).get(
            "recommended_roles_based_on_interests", []
        )

        pm_roles = [
            role for role in recommended_roles
            if "product manager" in role.get("title", "").lower() or "pm" in role.get("title", "").lower()
        ]

        if pm_roles:
            # PM should only be recommended if:
            # 1. User explicitly targets PM roles, OR
            # 2. User has 3-5+ years AND weak coding skills
            targets_pm = "product" in target_role.lower() or "pm" in target_role.lower()
            has_experience_for_pm = experience in ["3-5", "5+"]
            weak_coding = problem_solving in ["0-10", "11-50"]

            if not targets_pm and not (has_experience_for_pm and weak_coding):
                self.issues.append(
                    f"INAPPROPRIATE: AI recommended Product Manager role but user targets '{target_role}' "
                    f"with {experience} experience and {problem_solving} problem-solving score. "
                    f"PM should only be suggested if user explicitly wants PM or has 3-5+ years with limited coding."
                )
                self.suggestions.append(
                    "Improve prompt: Add stricter PM recommendation rule - 'ONLY recommend Product Manager if: "
                    "(a) targetRole explicitly contains 'product' or 'pm', OR "
                    "(b) experience >= 3-5 years AND problemSolving <= 11-50 AND user shows product interest.'"
                )

    def validate_skill_vs_opportunities(self):
        """Check if opportunities match skill level"""
        quiz = self.input.get("quizResponses", {})
        problem_solving = quiz.get("problemSolving", "")
        system_design = quiz.get("systemDesign", "")
        opportunities = self.response.get("profile_evaluation", {}).get(
            "opportunities_you_qualify_for", []
        )

        has_strong_skills = (
            problem_solving in ["51-100", "100+"] and
            system_design in ["once", "multiple"]
        )

        if has_strong_skills:
            junior_opportunities = [
                opp for opp in opportunities
                if any(kw in opp.lower() for kw in ["junior", "entry", "intern", "trainee"])
            ]

            if junior_opportunities:
                self.warnings.append(
                    f"User has strong skills (problemSolving={problem_solving}, systemDesign={system_design}) "
                    f"but AI suggested junior opportunities: {', '.join(junior_opportunities)}"
                )

    def validate_system_design_acknowledgment(self):
        """Check if system design skills are acknowledged in recommendations"""
        quiz = self.input.get("quizResponses", {})
        system_design = quiz.get("systemDesign", "")
        skill_analysis = self.response.get("profile_evaluation", {}).get("skill_analysis", {})
        strengths = skill_analysis.get("strengths", [])

        if system_design == "multiple":
            # Check if system design is mentioned in strengths
            system_design_mentioned = any(
                "system design" in strength.lower() or "architecture" in strength.lower()
                for strength in strengths
            )

            if not system_design_mentioned:
                self.warnings.append(
                    "User has 'multiple' system design experience but it's not mentioned in strengths. "
                    "This is a valuable skill that should be highlighted."
                )
                self.suggestions.append(
                    "Improve prompt: Add rule - 'If systemDesign = multiple, MUST include system design "
                    "or architecture as a key strength in skill_analysis.strengths'"
                )

    def validate_experience_vs_readiness(self):
        """Check if interview readiness matches experience"""
        quiz = self.input.get("quizResponses", {})
        experience = quiz.get("experience", "")
        mock_interviews = quiz.get("mockInterviews", "")
        interview_readiness = self.response.get("profile_evaluation", {}).get(
            "interview_readiness", {}
        )
        technical_percent = interview_readiness.get("technical_interview_percent", 0)

        # If user has 5+ years and does mock interviews, technical readiness should be high
        if experience == "5+" and mock_interviews in ["weekly+", "monthly"]:
            if technical_percent < 60:
                self.warnings.append(
                    f"User has {experience} years experience and practices mocks {mock_interviews}, "
                    f"but technical readiness is only {technical_percent}%. This seems low."
                )

    def validate_score_consistency(self):
        """Check if profile strength score matches other indicators"""
        profile_eval = self.response.get("profile_evaluation", {})
        score = profile_eval.get("profile_strength_score", 0)
        success_likelihood = profile_eval.get("success_likelihood", {})
        success_score = success_likelihood.get("score_percent", 0)

        # Scores should be somewhat correlated
        if abs(score - success_score) > 30:
            self.warnings.append(
                f"Profile strength score ({score}%) and success likelihood ({success_score}%) "
                f"differ by more than 30 points. Scores should be more consistent."
            )

    def validate_portfolio_vs_roles(self):
        """Check if GitHub portfolio activity matches recommended roles"""
        quiz = self.input.get("quizResponses", {})
        portfolio = quiz.get("portfolio", "")
        recommended_roles = self.response.get("profile_evaluation", {}).get(
            "recommended_roles_based_on_interests", []
        )

        # Active GitHub should boost engineering roles
        active_portfolio = portfolio in ["active-5+", "limited-1-5"]
        engineering_roles = [
            role for role in recommended_roles
            if any(kw in role.get("title", "").lower() for kw in [
                "engineer", "developer", "sde", "sre", "devops"
            ])
        ]

        if active_portfolio and len(engineering_roles) == 0:
            self.warnings.append(
                f"User has active GitHub portfolio ({portfolio}) but no engineering roles recommended. "
                f"Active portfolio is a strong signal for engineering roles."
            )

    def validate_no_non_technical_roles(self):
        """Check that NO non-technical roles are recommended"""
        recommended_roles = self.response.get("profile_evaluation", {}).get(
            "recommended_roles_based_on_interests", []
        )

        # List of forbidden non-technical roles
        non_technical_keywords = [
            "product manager", "product owner", "pm ",
            "ux designer", "ui designer", "product designer", "design",
            "business analyst", "project manager", "scrum master",
            "technical writer", "documentation specialist",
            "qa manual", "manual tester", "test analyst"
        ]

        non_technical_roles_found = []
        for role_obj in recommended_roles:
            role_title = role_obj.get("title", "").lower()
            for keyword in non_technical_keywords:
                if keyword in role_title:
                    non_technical_roles_found.append(role_obj.get("title"))
                    break

        if non_technical_roles_found:
            self.issues.append(
                f"CRITICAL: Non-technical roles found in recommendations: {', '.join(non_technical_roles_found)}. "
                f"We are a technical education platform - ONLY recommend hands-on engineering roles "
                f"(SDE, Backend/Frontend Engineer, DevOps, ML Engineer, Data Engineer, Mobile Engineer, etc.)"
            )
            self.suggestions.append(
                "Update prompt: Add explicit restriction - 'NEVER recommend Product Manager, UX Designer, "
                "Business Analyst, Project Manager, or any non-coding roles. We teach technical skills, "
                "so ONLY recommend software engineering and hands-on technical positions.'"
            )

    def validate_no_basic_tools(self):
        """Check that recommended tools are not basic/generic platforms"""
        tools = self.response.get("profile_evaluation", {}).get("recommended_tools", [])

        # Basic/generic tools to avoid
        basic_tools = [
            "github", "gitlab", "bitbucket",
            "leetcode", "hackerrank", "coursera", "udemy", "geeksforgeeks", "codechef",
            "turbo c", "dev c++", "code::blocks",
            "notepad++", "sublime text", "atom",
            "visual studio code", "vscode", "intellij idea", "intellij"
        ]

        basic_tools_found = []
        for tool in tools:
            tool_lower = tool.lower()
            for basic in basic_tools:
                if basic in tool_lower:
                    basic_tools_found.append(tool)
                    break

        if basic_tools_found:
            self.issues.append(
                f"CRITICAL: Basic/generic tools recommended: {', '.join(basic_tools_found)}. "
                f"These are too common/basic. Recommend specific, valuable tools instead "
                f"(e.g., Postman, DataGrip, Prometheus, Grafana, JMeter, Terraform, Sentry, etc.)"
            )
            self.suggestions.append(
                "Update prompt: Strengthen tool recommendation rules - "
                "'NEVER recommend GitHub/GitLab/LeetCode/HackerRank/Coursera/IDEs. Recommend specific advanced tools based on role: "
                "For Backend → Postman, DataGrip, Redis Commander, Prometheus, k6. "
                "For Full Stack → Storybook, React DevTools, Lighthouse, Sentry. "
                "For DevOps → ArgoCD, Helm, Terraform, Datadog, PagerDuty.'"
            )


def validate_response_file(input_path: str, response_path: str):
    """Validate a response from file paths"""
    with open(input_path, 'r') as f:
        input_payload = json.load(f)

    with open(response_path, 'r') as f:
        response = json.load(f)

    validator = ResponseValidator(input_payload, response)
    issues, warnings, suggestions = validator.validate_all()

    print("=" * 80)
    print("AI RESPONSE VALIDATION REPORT")
    print("=" * 80)

    if not issues and not warnings:
        print("\n✅ No issues found! The response appears logically consistent.")

    if issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND: {len(issues)}")
        print("-" * 80)
        for i, issue in enumerate(issues, 1):
            print(f"\n{i}. {issue}")

    if warnings:
        print(f"\n⚠️  WARNINGS: {len(warnings)}")
        print("-" * 80)
        for i, warning in enumerate(warnings, 1):
            print(f"\n{i}. {warning}")

    if suggestions:
        print(f"\n💡 PROMPT IMPROVEMENT SUGGESTIONS: {len(suggestions)}")
        print("-" * 80)
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion}")

    print("\n" + "=" * 80)

    # Return exit code based on severity
    if issues:
        return 1
    elif warnings:
        return 0
    else:
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate_response.py <input.json> <response.json>")
        sys.exit(2)

    input_file = sys.argv[1]
    response_file = sys.argv[2]

    exit_code = validate_response_file(input_file, response_file)
    sys.exit(exit_code)
