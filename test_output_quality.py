#!/usr/bin/env python3
"""
QUALITY EVALUATION TEST

Core Objective: Motivate learners that achieving their dreams IS possible.
- Show where they stand today
- Show clear path to step up
- Drive them to request callback from career expert

Quality Metrics:
1. Motivational tone (not demotivating)
2. Personalization (recalls specific quiz inputs)
3. Actionable guidance (clear next steps)
4. Conversion potential (creates need for expert help)
"""

import requests
import json
import itertools
from typing import Dict, Any, List

API_URL = "http://localhost:8000/evaluate"


def create_test_profiles() -> List[Dict[str, Any]]:
    """Create diverse test profiles covering different scenarios"""

    profiles = []

    # SCENARIO 1: High Performer - Should feel validated and ready
    profiles.append({
        "name": "High Performer (Senior with strong SD)",
        "background": "tech",
        "quizResponses": {
            "experience": "5-8",
            "currentRole": "swe-product",
            "currentCompany": "Razorpay",
            "targetRole": "senior-faang",
            "problemSolving": "100+",
            "systemDesign": "multiple",
            "portfolio": "active-5+",
            "mockInterviews": "monthly",
            "currentSkill": "backend",
            "requirementType": "better-company",
            "targetCompany": "faang"
        },
        "goals": {
            "requirementType": ["better-company"],
            "targetCompany": "Google",
            "topicOfInterest": []
        },
        "expected_motivation": "HIGH",
        "expected_score_range": (85, 100),
        "expected_tone": "Validating - 'You're ready for FAANG'"
    })

    # SCENARIO 2: Mid-Level with Gaps - Should feel hopeful with clear path
    profiles.append({
        "name": "Mid-Level with Gaps (needs work but achievable)",
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
        },
        "expected_motivation": "MEDIUM-HIGH",
        "expected_score_range": (45, 65),
        "expected_tone": "Encouraging - 'You're on the right track, here's what to focus on'"
    })

    # SCENARIO 3: Junior Starting Out - Should feel motivated despite low score
    profiles.append({
        "name": "Junior Starting Out (early career)",
        "background": "tech",
        "quizResponses": {
            "experience": "0-2",
            "currentRole": "swe-service",
            "currentCompany": "Startup",
            "targetRole": "backend-sde",
            "problemSolving": "0-10",
            "systemDesign": "not-yet",
            "portfolio": "none",
            "mockInterviews": "never",
            "currentSkill": "backend",
            "requirementType": "better-company",
            "targetCompany": "product"
        },
        "goals": {
            "requirementType": ["better-company"],
            "targetCompany": "Better Company",
            "topicOfInterest": []
        },
        "expected_motivation": "MEDIUM",
        "expected_score_range": (45, 55),
        "expected_tone": "Encouraging - 'You're building your foundation, here's the roadmap'"
    })

    # SCENARIO 4: Career Switcher - Motivated (high commitment)
    profiles.append({
        "name": "Career Switcher - High Commitment",
        "background": "non-tech",
        "quizResponses": {
            "experience": "5+",
            "currentRole": "career-switcher",
            "targetRole": "backend-dev",
            "codeComfort": "learning",
            "stepsTaken": "completed-course",
            "timePerWeek": "10+"
        },
        "goals": {
            "requirementType": ["career-switch"],
            "targetCompany": "Tech Company",
            "topicOfInterest": ["web-development", "backend"]
        },
        "expected_motivation": "HIGH",
        "expected_score_range": (65, 95),
        "expected_tone": "Encouraging - 'Your commitment shows, you're on track for career switch'"
    })

    # SCENARIO 5: Career Switcher - Exploring (low commitment)
    profiles.append({
        "name": "Career Switcher - Just Exploring",
        "background": "non-tech",
        "quizResponses": {
            "experience": "0-2",
            "currentRole": "career-switcher",
            "targetRole": "exploring",
            "codeComfort": "complete-beginner",
            "stepsTaken": "just-exploring",
            "timePerWeek": "0-2"
        },
        "goals": {
            "requirementType": ["career-switch"],
            "targetCompany": "",
            "topicOfInterest": ["web-development"]
        },
        "expected_motivation": "MEDIUM",
        "expected_score_range": (45, 55),
        "expected_tone": "Encouraging but realistic - 'Set a deadline, here's your first steps'"
    })

    # SCENARIO 6: Contradictory Profile (claims SD expert but no coding)
    profiles.append({
        "name": "Contradictory Profile (claims expertise without practice)",
        "background": "tech",
        "quizResponses": {
            "experience": "3-5",
            "currentRole": "swe-service",
            "currentCompany": "Service Company",
            "targetRole": "senior-faang",
            "problemSolving": "0-10",
            "systemDesign": "multiple",  # Claims multiple but doesn't practice
            "portfolio": "none",
            "mockInterviews": "never",
            "currentSkill": "backend",
            "requirementType": "better-company",
            "targetCompany": "faang"
        },
        "goals": {
            "requirementType": ["better-company"],
            "targetCompany": "FAANG",
            "topicOfInterest": []
        },
        "expected_motivation": "MEDIUM",
        "expected_score_range": (45, 55),
        "expected_tone": "Reality check but motivating - 'Here's what you need to build first'"
    })

    return profiles


def evaluate_personalization(profile_notes: str, quiz_responses: Dict) -> Dict[str, Any]:
    """Check if notes recall specific quiz inputs"""

    checks = {
        "recalls_company": False,
        "recalls_experience": False,
        "recalls_specific_numbers": False,
        "conversational_tone": False,
        "mentions_target": False
    }

    # Check company mention
    company = quiz_responses.get("currentCompany", "")
    if company and company.lower() in profile_notes.lower():
        checks["recalls_company"] = True

    # Check experience mention
    experience = quiz_responses.get("experience", "")
    if experience and experience in profile_notes:
        checks["recalls_experience"] = True

    # Check for specific numbers (problems solved, repos, etc.)
    if any(num in profile_notes for num in ["100+", "51-100", "11-50", "0-10", "5+", "1-5"]):
        checks["recalls_specific_numbers"] = True

    # Check conversational tone
    conversational_phrases = [
        "you're", "you've", "your", "here's", "let's", "being honest",
        "reality", "shows", "demonstrates", "focus on"
    ]
    if any(phrase in profile_notes.lower() for phrase in conversational_phrases):
        checks["conversational_tone"] = True

    # Check target mention (FAANG, product, etc.)
    target = quiz_responses.get("targetCompany", "") or quiz_responses.get("targetRole", "")
    if target and (target.lower() in profile_notes.lower() or "faang" in profile_notes.lower()):
        checks["mentions_target"] = True

    score = sum(checks.values()) / len(checks) * 100

    return {
        "score": score,
        "checks": checks,
        "is_personalized": score >= 60
    }


def evaluate_motivation(profile_notes: str, score: int) -> Dict[str, Any]:
    """Evaluate if the tone is motivating"""

    # Demotivating phrases
    demotivating = [
        "not ready", "far from", "unrealistic", "impossible", "won't work",
        "too difficult", "you can't", "no chance", "forget about"
    ]

    # Motivating phrases
    motivating = [
        "on the right track", "within reach", "you're ready", "you've built",
        "shows commitment", "demonstrates", "you can", "focus on", "next step",
        "achievable", "doable", "on track", "solid foundation", "you're building",
        "keep going", "momentum", "dedication", "paying off"
    ]

    # Reality check phrases (balanced, not demotivating)
    reality_check = [
        "here's the reality", "being honest", "focus area", "gap to fill",
        "needs work", "should be your priority", "next major focus"
    ]

    demotivating_count = sum(1 for phrase in demotivating if phrase in profile_notes.lower())
    motivating_count = sum(1 for phrase in motivating if phrase in profile_notes.lower())
    reality_count = sum(1 for phrase in reality_check if phrase in profile_notes.lower())

    # Score is below 45% - automatically demotivating (shouldn't happen!)
    if score < 45:
        return {
            "motivation_level": "DEMOTIVATING",
            "reason": f"Score {score}% is below 45% minimum",
            "demotivating_phrases": demotivating_count,
            "motivating_phrases": motivating_count,
            "is_motivating": False
        }

    # Check for demotivating language
    if demotivating_count > 0:
        return {
            "motivation_level": "DEMOTIVATING",
            "reason": f"Contains {demotivating_count} demotivating phrases",
            "demotivating_phrases": demotivating_count,
            "motivating_phrases": motivating_count,
            "is_motivating": False
        }

    # Check for balance
    if motivating_count >= 2 and reality_count <= 2:
        return {
            "motivation_level": "MOTIVATING",
            "reason": f"Good balance: {motivating_count} motivating phrases, {reality_count} reality checks",
            "demotivating_phrases": demotivating_count,
            "motivating_phrases": motivating_count,
            "is_motivating": True
        }

    if reality_count > motivating_count:
        return {
            "motivation_level": "NEUTRAL",
            "reason": f"More reality checks ({reality_count}) than motivation ({motivating_count})",
            "demotivating_phrases": demotivating_count,
            "motivating_phrases": motivating_count,
            "is_motivating": False
        }

    return {
        "motivation_level": "NEUTRAL",
        "reason": "Lacks motivating language",
        "demotivating_phrases": demotivating_count,
        "motivating_phrases": motivating_count,
        "is_motivating": False
    }


def evaluate_actionability(quick_wins: List[Dict]) -> Dict[str, Any]:
    """Check if quick wins are specific and actionable"""

    if not quick_wins:
        return {
            "is_actionable": False,
            "reason": "No quick wins provided",
            "specific_count": 0
        }

    specific_count = 0
    for qw in quick_wins:
        description = qw.get("description", "")

        # Check for specific numbers, tools, or actions
        if any(indicator in description.lower() for indicator in [
            "solve", "build", "create", "write", "practice", "complete",
            "add", "polish", "deploy", "master", "learn",
            "10", "20", "3-5", "2-3", "1-2"
        ]):
            specific_count += 1

    actionability_score = specific_count / len(quick_wins) * 100

    return {
        "is_actionable": actionability_score >= 60,
        "actionability_score": actionability_score,
        "specific_count": specific_count,
        "total_count": len(quick_wins),
        "reason": f"{specific_count}/{len(quick_wins)} quick wins are specific and actionable"
    }


def evaluate_conversion_potential(result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate if the report creates need for expert guidance"""

    profile_eval = result.get("profile_evaluation", {})
    notes = profile_eval.get("profile_strength_notes", "")
    score = profile_eval.get("profile_strength_score", 0)
    quick_wins = profile_eval.get("quick_wins", [])

    # Factors that drive conversion:
    conversion_factors = {
        "shows_gap": False,  # Identifies areas to improve
        "shows_path": False,  # Shows what's possible
        "creates_urgency": False,  # Makes them want help NOW
        "overwhelming_info": False,  # Too much to do alone = need expert
    }

    # Check for gap identification
    gap_phrases = ["gap", "needs work", "should focus on", "priority", "next major focus", "develop"]
    if any(phrase in notes.lower() for phrase in gap_phrases):
        conversion_factors["shows_gap"] = True

    # Check for path/possibility
    path_phrases = ["within reach", "achievable", "on track", "ready", "can", "focus on", "next step"]
    if any(phrase in notes.lower() for phrase in path_phrases):
        conversion_factors["shows_path"] = True

    # Check for urgency
    urgency_phrases = ["3-6 months", "1-2 years", "now", "immediate", "priority", "should be"]
    if any(phrase in notes.lower() for phrase in urgency_phrases):
        conversion_factors["creates_urgency"] = True

    # Check if there's enough to do that they'd want expert help
    if len(quick_wins) >= 3:
        conversion_factors["overwhelming_info"] = True

    conversion_score = sum(conversion_factors.values()) / len(conversion_factors) * 100

    return {
        "conversion_potential": "HIGH" if conversion_score >= 75 else "MEDIUM" if conversion_score >= 50 else "LOW",
        "conversion_score": conversion_score,
        "factors": conversion_factors,
        "drives_callback": conversion_score >= 50
    }


def run_quality_test():
    """Run comprehensive quality evaluation"""

    profiles = create_test_profiles()

    print("=" * 120)
    print("PROFILE EVALUATION QUALITY TEST")
    print("=" * 120)
    print("\nCore Objective: Motivate learners that achieving their dreams IS possible")
    print("Goal: Drive callback requests to career experts")
    print("\n" + "=" * 120)

    results = []

    for idx, profile in enumerate(profiles, 1):
        print(f"\n\n{'='*120}")
        print(f"TEST {idx}/{len(profiles)}: {profile['name']}")
        print(f"{'='*120}")

        # Call API
        payload = {
            "background": profile["background"],
            "quizResponses": profile["quizResponses"],
            "goals": profile["goals"]
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()

            profile_eval = result.get("profile_evaluation", {})
            score = profile_eval.get("profile_strength_score", 0)
            notes = profile_eval.get("profile_strength_notes", "")
            quick_wins = profile_eval.get("quick_wins", [])

            # EVALUATION 1: Score Requirements
            print(f"\n📊 SCORE EVALUATION")
            print(f"   Score: {score}/100")
            print(f"   Expected Range: {profile['expected_score_range'][0]}-{profile['expected_score_range'][1]}")

            score_ok = profile['expected_score_range'][0] <= score <= profile['expected_score_range'][1]
            no_multiple_5 = score % 5 != 0
            above_45 = score >= 45

            print(f"   ✓ In expected range: {score_ok}")
            print(f"   ✓ Not multiple of 5: {no_multiple_5} (score: {score})")
            print(f"   ✓ Above 45% minimum: {above_45}")

            # EVALUATION 2: Personalization
            print(f"\n🎯 PERSONALIZATION EVALUATION")
            personalization = evaluate_personalization(notes, profile["quizResponses"])
            print(f"   Personalization Score: {personalization['score']:.1f}%")
            print(f"   ✓ Recalls company: {personalization['checks']['recalls_company']}")
            print(f"   ✓ Recalls experience: {personalization['checks']['recalls_experience']}")
            print(f"   ✓ Recalls specific numbers: {personalization['checks']['recalls_specific_numbers']}")
            print(f"   ✓ Conversational tone: {personalization['checks']['conversational_tone']}")
            print(f"   ✓ Mentions target: {personalization['checks']['mentions_target']}")
            print(f"   Result: {'PERSONALIZED ✓' if personalization['is_personalized'] else 'GENERIC ✗'}")

            # EVALUATION 3: Motivation
            print(f"\n💪 MOTIVATION EVALUATION")
            motivation = evaluate_motivation(notes, score)
            print(f"   Motivation Level: {motivation['motivation_level']}")
            print(f"   Motivating phrases: {motivation['motivating_phrases']}")
            print(f"   Demotivating phrases: {motivation['demotivating_phrases']}")
            print(f"   Reason: {motivation['reason']}")
            print(f"   Result: {'MOTIVATING ✓' if motivation['is_motivating'] else 'NEEDS IMPROVEMENT ✗'}")

            # EVALUATION 4: Actionability
            print(f"\n🎬 ACTIONABILITY EVALUATION")
            actionability = evaluate_actionability(quick_wins)
            print(f"   Actionability Score: {actionability['actionability_score']:.1f}%")
            print(f"   Specific quick wins: {actionability['specific_count']}/{actionability['total_count']}")
            print(f"   Result: {'ACTIONABLE ✓' if actionability['is_actionable'] else 'VAGUE ✗'}")

            # EVALUATION 5: Conversion Potential
            print(f"\n📞 CONVERSION POTENTIAL")
            conversion = evaluate_conversion_potential(result)
            print(f"   Conversion Potential: {conversion['conversion_potential']}")
            print(f"   Conversion Score: {conversion['conversion_score']:.1f}%")
            print(f"   ✓ Shows gap: {conversion['factors']['shows_gap']}")
            print(f"   ✓ Shows path: {conversion['factors']['shows_path']}")
            print(f"   ✓ Creates urgency: {conversion['factors']['creates_urgency']}")
            print(f"   ✓ Enough info to need expert: {conversion['factors']['overwhelming_info']}")
            print(f"   Result: {'DRIVES CALLBACK ✓' if conversion['drives_callback'] else 'WEAK CONVERSION ✗'}")

            # OVERALL QUALITY
            print(f"\n🏆 OVERALL QUALITY")
            overall_pass = (
                above_45 and no_multiple_5 and
                personalization['is_personalized'] and
                motivation['is_motivating'] and
                actionability['is_actionable'] and
                conversion['drives_callback']
            )
            print(f"   Overall: {'EXCELLENT ✓✓✓' if overall_pass else 'NEEDS IMPROVEMENT'}")

            # Sample output
            print(f"\n📝 SAMPLE PROFILE NOTES (first 500 chars):")
            print(f"   {notes[:500]}...")

            results.append({
                "name": profile["name"],
                "score": score,
                "score_ok": score_ok and above_45 and no_multiple_5,
                "personalized": personalization['is_personalized'],
                "motivating": motivation['is_motivating'],
                "actionable": actionability['is_actionable'],
                "drives_callback": conversion['drives_callback'],
                "overall_pass": overall_pass
            })

        except Exception as e:
            print(f"   ✗ ERROR: {str(e)}")
            results.append({
                "name": profile["name"],
                "score": 0,
                "score_ok": False,
                "personalized": False,
                "motivating": False,
                "actionable": False,
                "drives_callback": False,
                "overall_pass": False
            })

    # SUMMARY
    print(f"\n\n{'='*120}")
    print("FINAL SUMMARY")
    print(f"{'='*120}\n")

    total = len(results)
    passed = sum(1 for r in results if r["overall_pass"])

    print(f"Total Profiles Tested: {total}")
    print(f"Overall Pass: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"\nBreakdown:")
    print(f"  Score Requirements (≥45%, not multiple of 5): {sum(1 for r in results if r['score_ok'])}/{total}")
    print(f"  Personalized: {sum(1 for r in results if r['personalized'])}/{total}")
    print(f"  Motivating: {sum(1 for r in results if r['motivating'])}/{total}")
    print(f"  Actionable: {sum(1 for r in results if r['actionable'])}/{total}")
    print(f"  Drives Callback: {sum(1 for r in results if r['drives_callback'])}/{total}")

    print(f"\n{'='*120}")
    if passed == total:
        print("✓✓✓ ALL QUALITY CHECKS PASSED ✓✓✓")
        print("\nThe evaluation system successfully:")
        print("  • Motivates learners that their dreams are achievable")
        print("  • Shows where they stand today (with personalized insights)")
        print("  • Provides clear path to step up (actionable quick wins)")
        print("  • Drives callback requests (creates need for expert guidance)")
    else:
        print(f"⚠ {total - passed} profiles need improvement")
        print("\nFailing profiles:")
        for r in results:
            if not r["overall_pass"]:
                print(f"  - {r['name']}")
    print(f"{'='*120}\n")

    return passed == total


if __name__ == "__main__":
    success = run_quality_test()
    exit(0 if success else 1)
