#!/usr/bin/env python3
"""
COMPREHENSIVE QUALITY ASSESSMENT OF ENTIRE EVALUATION REPORT

Evaluates ALL sections against key quality parameters:
1. Motivation - Does it inspire and encourage?
2. Objectivity - Based on facts, not salesy?
3. Value - Provides actionable insights?
4. Personalization - Recalls user's specific quiz inputs?
5. Real-World Sense - Practical and realistic?
6. Tech-Focus - Only tech-relevant recommendations?
7. Conversational/Verbose - Detailed and friendly?
8. Value to End User - Overall usefulness?
9. Recall of User Options - Mentions their choices?
"""

import requests
import json
from typing import Dict, Any, List

API_URL = "http://localhost:8000/evaluate"


def evaluate_profile_notes(notes: str, quiz: Dict, score: int) -> Dict[str, Any]:
    """Evaluate profile strength notes"""

    checks = {
        "motivation": 0,  # 0-10
        "objectivity": 0,  # 0-10
        "personalization": 0,  # 0-10
        "conversational": 0,  # 0-10
        "recall": 0  # 0-10
    }

    # MOTIVATION: Check for encouraging language
    motivating_phrases = ["on the right track", "within reach", "ready", "solid foundation",
                         "strong", "excellent", "dedication", "progress", "achievable"]
    demotivating_phrases = ["not ready", "far from", "unrealistic", "won't work"]

    motivating_count = sum(1 for p in motivating_phrases if p in notes.lower())
    demotivating_count = sum(1 for p in demotivating_phrases if p in notes.lower())

    if score < 45:
        checks["motivation"] = 0  # Score below 45% is demotivating
    elif demotivating_count > 0:
        checks["motivation"] = 3
    elif motivating_count >= 3:
        checks["motivation"] = 9
    elif motivating_count >= 1:
        checks["motivation"] = 6
    else:
        checks["motivation"] = 4

    # OBJECTIVITY: Not too salesy
    salesy_phrases = ["expert guidance", "book a call", "sign up", "limited time",
                     "don't miss", "act now", "exclusive"]
    salesy_count = sum(1 for p in salesy_phrases if p in notes.lower())

    if salesy_count == 0:
        checks["objectivity"] = 10
    elif salesy_count == 1:
        checks["objectivity"] = 6
    else:
        checks["objectivity"] = 3

    # PERSONALIZATION: Recalls specific quiz values
    company = quiz.get("currentCompany", "")
    experience = quiz.get("experience", "")

    recall_count = 0
    if company and company.lower() in notes.lower():
        recall_count += 1
    if experience and experience in notes:
        recall_count += 1
    if any(num in notes for num in ["100+", "51-100", "11-50", "0-10", "5+", "1-5"]):
        recall_count += 1
    if any(term in notes.lower() for term in ["faang", "product", "backend", "frontend"]):
        recall_count += 1

    checks["personalization"] = min(10, recall_count * 3)

    # CONVERSATIONAL: Friendly, not robotic
    conversational_markers = ["you're", "you've", "your", "here's", "let's", "shows", "demonstrates"]
    conversational_count = sum(1 for m in conversational_markers if m in notes.lower())

    checks["conversational"] = min(10, conversational_count)

    # RECALL: Specific mention of user choices
    checks["recall"] = checks["personalization"]  # Same as personalization

    avg_score = sum(checks.values()) / len(checks)

    return {
        "scores": checks,
        "average": avg_score,
        "pass": avg_score >= 7.0,
        "notes_sample": notes[:300] + "..."
    }


def evaluate_quick_wins(quick_wins: List[Dict], quiz: Dict) -> Dict[str, Any]:
    """Evaluate quick wins section"""

    if not quick_wins:
        return {"scores": {}, "average": 0, "pass": False, "reason": "No quick wins provided"}

    checks = {
        "motivation": 0,
        "value": 0,
        "specificity": 0,
        "tech_focus": 0,
        "actionable": 0
    }

    # Check each quick win
    specific_count = 0
    actionable_count = 0
    generic_count = 0
    tech_focused_count = 0

    for qw in quick_wins:
        desc = qw.get("description", "").lower()

        # Check for specificity (numbers, concrete actions)
        if any(indicator in desc for indicator in ["solve", "build", "create", "complete", "master",
                                                     "10", "20", "3-5", "2-3", "1-2", "daily", "weekly"]):
            specific_count += 1
            actionable_count += 1

        # Check for generic recommendations
        if any(generic in desc for generic in ["practice more", "learn more", "improve your", "study"]):
            generic_count += 1

        # Check for tech-relevant actions
        if any(tech in desc for tech in ["code", "project", "system design", "algorithm", "api",
                                          "github", "deploy", "architecture", "database"]):
            tech_focused_count += 1

    total = len(quick_wins)

    checks["specificity"] = int((specific_count / total) * 10)
    checks["actionable"] = int((actionable_count / total) * 10)
    checks["tech_focus"] = int((tech_focused_count / total) * 10)
    checks["value"] = int(((specific_count + tech_focused_count) / (total * 2)) * 10)
    checks["motivation"] = 8 if generic_count == 0 else 5  # Specific is more motivating

    avg_score = sum(checks.values()) / len(checks)

    return {
        "scores": checks,
        "average": avg_score,
        "pass": avg_score >= 7.0,
        "sample": [qw.get("description", "") for qw in quick_wins[:2]]
    }


def evaluate_tools(tools: List[Dict]) -> Dict[str, Any]:
    """Evaluate tools recommendations"""

    if not tools:
        return {"scores": {}, "average": 0, "pass": False, "reason": "No tools provided"}

    checks = {
        "tech_focus": 0,
        "professional": 0,
        "value": 0,
        "real_world": 0
    }

    # Banned tools (generic, not professional-grade)
    banned = ["leetcode", "hackerrank", "github", "vs code", "coursera", "udemy", "youtube"]

    # Professional tools
    professional_tools = ["terraform", "prometheus", "grafana", "k6", "locust", "datagrip",
                         "dbeaver", "excalidraw", "draw.io", "miro", "postman", "insomnia",
                         "docker", "kubernetes", "redis", "elasticsearch"]

    banned_count = sum(1 for t in tools if any(banned_tool in t.get("name", "").lower() for banned_tool in banned))
    professional_count = sum(1 for t in tools if any(prof in t.get("name", "").lower() for prof in professional_tools))

    checks["professional"] = 10 if banned_count == 0 else max(0, 10 - banned_count * 2)
    checks["tech_focus"] = 10 if banned_count == 0 else 5
    checks["value"] = int((professional_count / len(tools)) * 10)
    checks["real_world"] = checks["professional"]  # Same criterion

    avg_score = sum(checks.values()) / len(checks)

    return {
        "scores": checks,
        "average": avg_score,
        "pass": avg_score >= 8.0,
        "banned_detected": banned_count,
        "sample": [t.get("name", "") for t in tools[:3]]
    }


def evaluate_job_opportunities(jobs: List[Dict], quiz: Dict) -> Dict[str, Any]:
    """Evaluate job opportunities section"""

    if not jobs:
        return {"scores": {}, "average": 0, "pass": False, "reason": "No jobs provided"}

    checks = {
        "specificity": 0,
        "tech_focus": 0,
        "real_world": 0,
        "personalization": 0,
        "value": 0
    }

    # Check for generic phrases (bad)
    generic_phrases = ["aligns with your", "matches your", "based on your", "suitable for you"]

    # Check for specific requirements (good)
    specific_indicators = ["microservices", "scale", "architecture", "trade-off", "distributed",
                          "leadership", "cross-team", "10m+", "high-throughput"]

    generic_count = 0
    specific_count = 0

    for job in jobs:
        desc = job.get("description", "").lower()

        if any(generic in desc for generic in generic_phrases):
            generic_count += 1

        if any(indicator in desc for indicator in specific_indicators):
            specific_count += 1

    total = len(jobs)

    checks["specificity"] = int((specific_count / total) * 10)
    checks["tech_focus"] = 10 if all("engineer" in j.get("role", "").lower() or "developer" in j.get("role", "").lower() for j in jobs) else 6
    checks["real_world"] = int(((total - generic_count) / total) * 10)
    checks["personalization"] = 5  # Job recs are generally not highly personalized
    checks["value"] = int((specific_count / total) * 10)

    avg_score = sum(checks.values()) / len(checks)

    return {
        "scores": checks,
        "average": avg_score,
        "pass": avg_score >= 7.0,
        "generic_detected": generic_count,
        "sample": [j.get("role", "") for j in jobs[:2]]
    }


def evaluate_skill_analysis(skills: Dict) -> Dict[str, Any]:
    """Evaluate skill analysis section"""

    if not skills:
        return {"scores": {}, "average": 0, "pass": False, "reason": "No skill analysis provided"}

    checks = {
        "specificity": 0,
        "value": 0,
        "actionable": 0
    }

    strengths = skills.get("strengths", [])
    areas_to_develop = skills.get("areas_to_develop", [])

    total_items = len(strengths) + len(areas_to_develop)

    if total_items == 0:
        return {"scores": checks, "average": 0, "pass": False}

    # Check for specific vs generic
    specific_terms = ["system design", "algorithm", "data structure", "api", "database",
                     "architecture", "distributed", "microservices", "testing"]

    specific_count = sum(1 for s in strengths + areas_to_develop
                        if any(term in s.lower() for term in specific_terms))

    checks["specificity"] = int((specific_count / total_items) * 10)
    checks["value"] = 8 if len(areas_to_develop) >= 2 else 5  # Identifying gaps is valuable
    checks["actionable"] = 7 if len(areas_to_develop) > 0 else 4

    avg_score = sum(checks.values()) / len(checks)

    return {
        "scores": checks,
        "average": avg_score,
        "pass": avg_score >= 6.0,
        "sample": {
            "strengths": strengths[:2],
            "areas_to_develop": areas_to_develop[:2]
        }
    }


def run_comprehensive_quality_test():
    """Run comprehensive quality evaluation on entire report"""

    # Test profile: Mid-level engineer with some gaps
    test_profile = {
        "background": "tech",
        "quizResponses": {
            "experience": "3-5",
            "currentRole": "swe-service",
            "currentCompany": "TCS",
            "targetRole": "backend-sde",
            "problemSolving": "11-50",
            "systemDesign": "not-yet",
            "portfolio": "limited-1-5",
            "mockInterviews": "never",
            "currentSkill": "backend",
            "requirementType": "better-company",
            "targetCompany": "product"
        },
        "goals": {
            "requirementType": ["better-company"],
            "targetCompany": "Product Company",
            "topicOfInterest": []
        }
    }

    print("=" * 120)
    print("COMPREHENSIVE QUALITY ASSESSMENT - FULL EVALUATION REPORT")
    print("=" * 120)
    print("\nQuality Parameters:")
    print("  1. Motivation - Inspires and encourages")
    print("  2. Objectivity - Factual, not salesy")
    print("  3. Value - Actionable insights")
    print("  4. Personalization - Recalls quiz inputs")
    print("  5. Real-World Sense - Practical and realistic")
    print("  6. Tech-Focus - Tech-relevant only")
    print("  7. Conversational/Verbose - Detailed and friendly")
    print("  8. Value to End User - Overall usefulness")
    print("  9. Recall of User Options - Mentions choices")
    print("\n" + "=" * 120)

    try:
        print("\n🔄 Calling API...")
        response = requests.post(API_URL, json=test_profile, timeout=120)
        response.raise_for_status()
        result = response.json()

        profile_eval = result.get("profile_evaluation", {})

        print("✓ API call successful\n")

        all_scores = {}

        # 1. PROFILE STRENGTH NOTES
        print(f"\n{'='*120}")
        print("1. PROFILE STRENGTH NOTES")
        print(f"{'='*120}")

        notes = profile_eval.get("profile_strength_notes", "")
        score = profile_eval.get("profile_strength_score", 0)
        notes_eval = evaluate_profile_notes(notes, test_profile["quizResponses"], score)

        print(f"\n  Motivation Score:      {notes_eval['scores']['motivation']}/10 {'✓' if notes_eval['scores']['motivation'] >= 7 else '✗'}")
        print(f"  Objectivity Score:     {notes_eval['scores']['objectivity']}/10 {'✓' if notes_eval['scores']['objectivity'] >= 7 else '✗'}")
        print(f"  Personalization Score: {notes_eval['scores']['personalization']}/10 {'✓' if notes_eval['scores']['personalization'] >= 7 else '✗'}")
        print(f"  Conversational Score:  {notes_eval['scores']['conversational']}/10 {'✓' if notes_eval['scores']['conversational'] >= 7 else '✗'}")
        print(f"  Recall Score:          {notes_eval['scores']['recall']}/10 {'✓' if notes_eval['scores']['recall'] >= 7 else '✗'}")
        print(f"\n  OVERALL: {notes_eval['average']:.1f}/10 {'✓✓✓ EXCELLENT' if notes_eval['pass'] else '⚠ NEEDS IMPROVEMENT'}")
        print(f"\n  Sample: {notes_eval['notes_sample']}")

        all_scores["profile_notes"] = notes_eval

        # 2. QUICK WINS
        print(f"\n{'='*120}")
        print("2. QUICK WINS")
        print(f"{'='*120}")

        quick_wins = profile_eval.get("quick_wins", [])
        qw_eval = evaluate_quick_wins(quick_wins, test_profile["quizResponses"])

        print(f"\n  Motivation Score:   {qw_eval['scores'].get('motivation', 0)}/10 {'✓' if qw_eval['scores'].get('motivation', 0) >= 7 else '✗'}")
        print(f"  Value Score:        {qw_eval['scores'].get('value', 0)}/10 {'✓' if qw_eval['scores'].get('value', 0) >= 7 else '✗'}")
        print(f"  Specificity Score:  {qw_eval['scores'].get('specificity', 0)}/10 {'✓' if qw_eval['scores'].get('specificity', 0) >= 7 else '✗'}")
        print(f"  Tech-Focus Score:   {qw_eval['scores'].get('tech_focus', 0)}/10 {'✓' if qw_eval['scores'].get('tech_focus', 0) >= 7 else '✗'}")
        print(f"  Actionable Score:   {qw_eval['scores'].get('actionable', 0)}/10 {'✓' if qw_eval['scores'].get('actionable', 0) >= 7 else '✗'}")
        print(f"\n  OVERALL: {qw_eval['average']:.1f}/10 {'✓✓✓ EXCELLENT' if qw_eval['pass'] else '⚠ NEEDS IMPROVEMENT'}")
        print(f"\n  Samples:")
        for i, sample in enumerate(qw_eval.get('sample', []), 1):
            print(f"    {i}. {sample}")

        all_scores["quick_wins"] = qw_eval

        # 3. TOOLS RECOMMENDATIONS
        print(f"\n{'='*120}")
        print("3. TOOLS RECOMMENDATIONS")
        print(f"{'='*120}")

        tools = profile_eval.get("recommended_tools", [])
        tools_eval = evaluate_tools(tools)

        print(f"\n  Tech-Focus Score:    {tools_eval['scores'].get('tech_focus', 0)}/10 {'✓' if tools_eval['scores'].get('tech_focus', 0) >= 7 else '✗'}")
        print(f"  Professional Score:  {tools_eval['scores'].get('professional', 0)}/10 {'✓' if tools_eval['scores'].get('professional', 0) >= 7 else '✗'}")
        print(f"  Value Score:         {tools_eval['scores'].get('value', 0)}/10 {'✓' if tools_eval['scores'].get('value', 0) >= 7 else '✗'}")
        print(f"  Real-World Score:    {tools_eval['scores'].get('real_world', 0)}/10 {'✓' if tools_eval['scores'].get('real_world', 0) >= 7 else '✗'}")
        print(f"\n  Banned Tools Detected: {tools_eval.get('banned_detected', 0)} {'✗' if tools_eval.get('banned_detected', 0) > 0 else '✓'}")
        print(f"\n  OVERALL: {tools_eval['average']:.1f}/10 {'✓✓✓ EXCELLENT' if tools_eval['pass'] else '⚠ NEEDS IMPROVEMENT'}")
        print(f"\n  Samples:")
        for i, sample in enumerate(tools_eval.get('sample', []), 1):
            print(f"    {i}. {sample}")

        all_scores["tools"] = tools_eval

        # 4. JOB OPPORTUNITIES
        print(f"\n{'='*120}")
        print("4. JOB OPPORTUNITIES")
        print(f"{'='*120}")

        jobs = profile_eval.get("opportunities_you_qualify_for", [])
        jobs_eval = evaluate_job_opportunities(jobs, test_profile["quizResponses"])

        print(f"\n  Specificity Score:      {jobs_eval['scores'].get('specificity', 0)}/10 {'✓' if jobs_eval['scores'].get('specificity', 0) >= 7 else '✗'}")
        print(f"  Tech-Focus Score:       {jobs_eval['scores'].get('tech_focus', 0)}/10 {'✓' if jobs_eval['scores'].get('tech_focus', 0) >= 7 else '✗'}")
        print(f"  Real-World Score:       {jobs_eval['scores'].get('real_world', 0)}/10 {'✓' if jobs_eval['scores'].get('real_world', 0) >= 7 else '✗'}")
        print(f"  Personalization Score:  {jobs_eval['scores'].get('personalization', 0)}/10 {'✓' if jobs_eval['scores'].get('personalization', 0) >= 7 else '✗'}")
        print(f"  Value Score:            {jobs_eval['scores'].get('value', 0)}/10 {'✓' if jobs_eval['scores'].get('value', 0) >= 7 else '✗'}")
        print(f"\n  Generic Phrases Detected: {jobs_eval.get('generic_detected', 0)} {'✗' if jobs_eval.get('generic_detected', 0) > 0 else '✓'}")
        print(f"\n  OVERALL: {jobs_eval['average']:.1f}/10 {'✓✓✓ EXCELLENT' if jobs_eval['pass'] else '⚠ NEEDS IMPROVEMENT'}")
        print(f"\n  Samples:")
        for i, sample in enumerate(jobs_eval.get('sample', []), 1):
            print(f"    {i}. {sample}")

        all_scores["jobs"] = jobs_eval

        # 5. SKILL ANALYSIS
        print(f"\n{'='*120}")
        print("5. SKILL ANALYSIS")
        print(f"{'='*120}")

        skills = profile_eval.get("skill_analysis", {})
        skills_eval = evaluate_skill_analysis(skills)

        print(f"\n  Specificity Score:  {skills_eval['scores'].get('specificity', 0)}/10 {'✓' if skills_eval['scores'].get('specificity', 0) >= 7 else '✗'}")
        print(f"  Value Score:        {skills_eval['scores'].get('value', 0)}/10 {'✓' if skills_eval['scores'].get('value', 0) >= 7 else '✗'}")
        print(f"  Actionable Score:   {skills_eval['scores'].get('actionable', 0)}/10 {'✓' if skills_eval['scores'].get('actionable', 0) >= 7 else '✗'}")
        print(f"\n  OVERALL: {skills_eval['average']:.1f}/10 {'✓✓✓ EXCELLENT' if skills_eval['pass'] else '⚠ NEEDS IMPROVEMENT'}")
        print(f"\n  Sample:")
        print(f"    Strengths: {skills_eval.get('sample', {}).get('strengths', [])}")
        print(f"    Areas to Develop: {skills_eval.get('sample', {}).get('areas_to_develop', [])}")

        all_scores["skills"] = skills_eval

        # FINAL SUMMARY
        print(f"\n\n{'='*120}")
        print("FINAL SUMMARY - OVERALL QUALITY ASSESSMENT")
        print(f"{'='*120}\n")

        overall_avg = sum(eval_result['average'] for eval_result in all_scores.values()) / len(all_scores)

        print(f"  Profile Notes:       {all_scores['profile_notes']['average']:.1f}/10 {'✓' if all_scores['profile_notes']['pass'] else '✗'}")
        print(f"  Quick Wins:          {all_scores['quick_wins']['average']:.1f}/10 {'✓' if all_scores['quick_wins']['pass'] else '✗'}")
        print(f"  Tools:               {all_scores['tools']['average']:.1f}/10 {'✓' if all_scores['tools']['pass'] else '✗'}")
        print(f"  Job Opportunities:   {all_scores['jobs']['average']:.1f}/10 {'✓' if all_scores['jobs']['pass'] else '✗'}")
        print(f"  Skill Analysis:      {all_scores['skills']['average']:.1f}/10 {'✓' if all_scores['skills']['pass'] else '✗'}")

        print(f"\n  {'='*120}")
        print(f"  OVERALL QUALITY SCORE: {overall_avg:.1f}/10")
        print(f"  {'='*120}")

        if overall_avg >= 8.0:
            print("\n  ✓✓✓ EXCELLENT - Report meets all quality standards")
        elif overall_avg >= 7.0:
            print("\n  ✓✓ GOOD - Report meets most quality standards with minor improvements needed")
        elif overall_avg >= 6.0:
            print("\n  ⚠ FAIR - Report needs improvement in several areas")
        else:
            print("\n  ✗ POOR - Report requires significant improvements")

        print(f"\n  {'='*120}\n")

        return overall_avg >= 7.0

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_comprehensive_quality_test()
    exit(0 if success else 1)
