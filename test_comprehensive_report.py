"""
Comprehensive test script for all permutations and combinations of user profiles.
Generates detailed report showing AI responses for different scenarios.
"""

from typing import Dict, Any, List
import json
from quick_wins_logic import generate_quick_wins, _determine_user_level
from timeline_logic import calculate_timeline_to_role
from job_descriptions import _get_seniority_level, generate_job_opportunities
from scoring_logic import calculate_profile_strength

# Define all possible values for each quiz parameter
EXPERIENCE_LEVELS = ["0-2", "3-5", "5-8", "8+"]
CURRENT_ROLES = ["swe-product", "swe-service", "devops", "qa-support"]
PROBLEM_SOLVING_LEVELS = ["0-10", "11-50", "51-100", "100+"]
SYSTEM_DESIGN_LEVELS = ["not-yet", "once", "multiple"]
PORTFOLIO_LEVELS = ["none", "limited-1-5", "active-5+"]
TARGET_ROLES = ["backend-sde", "senior-backend", "tech-lead"]
TARGET_COMPANIES = ["faang", "unicorns", "product"]


def generate_test_profile(
    experience: str,
    current_role: str,
    problem_solving: str,
    system_design: str,
    portfolio: str,
    target_role: str,
    target_company: str
) -> Dict[str, Any]:
    """Generate a complete test profile."""
    return {
        "experience": experience,
        "currentRole": current_role,
        "currentCompany": "Test Company",
        "problemSolving": problem_solving,
        "systemDesign": system_design,
        "portfolio": portfolio,
        "targetRole": target_role,
        "targetCompany": target_company,
        "currentSkill": "backend",
        "requirementType": ["switch-company"],
        "mockInterviews": "0"
    }


def analyze_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Run all analysis functions on a profile and return results."""

    # Calculate seniority
    seniority = _get_seniority_level(profile)
    user_level = _determine_user_level(profile)

    # Generate quick wins
    quick_wins = generate_quick_wins("tech", profile)

    # Calculate timeline
    timeline = calculate_timeline_to_role(profile["targetRole"], profile)

    # Generate job opportunities
    jobs = generate_job_opportunities("tech", profile)

    # Calculate profile strength
    scoring_result = calculate_profile_strength("tech", profile)

    return {
        "seniority": seniority,
        "user_level": user_level,
        "profile_score": scoring_result["score"],
        "quick_wins": quick_wins,
        "timeline": timeline,
        "jobs": jobs[:3],  # First 3 jobs
        "contradictions": scoring_result.get("contradictions", [])
    }


def check_for_issues(profile: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
    """Check for potential issues in the analysis."""
    issues = []

    experience = profile["experience"]
    problem_solving = profile["problemSolving"]
    system_design = profile["systemDesign"]
    portfolio = profile["portfolio"]
    seniority = analysis["seniority"]
    quick_wins = analysis["quick_wins"]
    timeline = analysis["timeline"]

    # Issue 1: Senior engineers getting junior recommendations
    if experience in ["5-8", "8+"]:
        for qw in quick_wins:
            title_lower = qw["title"].lower()
            desc_lower = qw["description"].lower()

            # "Build GitHub" is a problem if they already have a portfolio
            if "build github" in title_lower and portfolio in ["limited-1-5", "active-5+"]:
                issues.append(f"❌ ISSUE: Experienced engineer ({experience} years) with portfolio getting: '{qw['title']}'")

            # "Start System Design" is ONLY a problem if they already know system design
            if "start system design" in title_lower and system_design in ["once", "multiple"]:
                issues.append(f"❌ ISSUE: Experienced engineer ({experience} years) who knows system design getting: '{qw['title']}'")

            # "Build Coding Foundation" is ALWAYS wrong for experienced engineers
            if "build coding foundation" in title_lower:
                issues.append(f"❌ ISSUE: Experienced engineer ({experience} years) getting junior recommendation: '{qw['title']}'")

            if "build foundation" in desc_lower and experience in ["8+"]:
                issues.append(f"❌ ISSUE: 8+ year engineer told to 'build foundation'")

    # Issue 2: System design masters getting basic recommendations
    if system_design == "multiple":
        for qw in quick_wins:
            if "system design" in qw["title"].lower() or "start system design" in qw["description"].lower():
                issues.append(f"❌ ISSUE: System design master getting basic recommendation: '{qw['title']}'")

    # Issue 3: Active portfolio users getting build portfolio recommendations
    if portfolio == "active-5+":
        for qw in quick_wins:
            if "github presence" in qw["title"].lower() or "build" in qw["title"].lower() and "portfolio" in qw["description"].lower():
                issues.append(f"❌ ISSUE: User with active-5+ portfolio getting build portfolio recommendation: '{qw['title']}'")

    # Issue 4: Interview-ready seniors getting unrealistic timelines
    if (experience in ["5-8", "8+"] and
        problem_solving in ["51-100", "100+"] and
        system_design in ["once", "multiple"] and
        portfolio in ["limited-1-5", "active-5+"]):

        if timeline["min_months"] > 4:
            issues.append(f"❌ ISSUE: Interview-ready senior getting {timeline['timeline_text']} timeline (should be 2-4 months)")

    # Issue 5: 3-5 years marked as junior
    if experience == "3-5" and seniority == "junior":
        # Only acceptable if ALL signals are weak
        if not (problem_solving == "0-10" and portfolio == "none" and profile["currentRole"] == "swe-service"):
            issues.append(f"❌ ISSUE: 3-5 year engineer marked as junior (problem_solving: {problem_solving}, portfolio: {portfolio})")

    # Issue 6: 5-8+ years not marked as senior
    if experience in ["5-8", "8+"] and seniority not in ["senior", "staff"]:
        issues.append(f"❌ ISSUE: {experience} year engineer not marked as senior/staff (got: {seniority})")

    return issues


def generate_summary_report(all_results: List[Dict[str, Any]]) -> str:
    """Generate comprehensive summary report."""

    total_profiles = len(all_results)
    profiles_with_issues = sum(1 for r in all_results if r["issues"])
    total_issues = sum(len(r["issues"]) for r in all_results)

    # Count issues by type
    issue_types = {
        "Junior recommendations for seniors": 0,
        "Basic system design for masters": 0,
        "Build portfolio for active users": 0,
        "Unrealistic timelines": 0,
        "Incorrect seniority determination": 0
    }

    for result in all_results:
        for issue in result["issues"]:
            if "junior recommendation" in issue or "build foundation" in issue:
                issue_types["Junior recommendations for seniors"] += 1
            elif "System design master" in issue:
                issue_types["Basic system design for masters"] += 1
            elif "active-5+ portfolio" in issue:
                issue_types["Build portfolio for active users"] += 1
            elif "timeline" in issue:
                issue_types["Unrealistic timelines"] += 1
            elif "marked as junior" in issue or "not marked as senior" in issue:
                issue_types["Incorrect seniority determination"] += 1

    # Generate report
    report = []
    report.append("\n" + "=" * 100)
    report.append("COMPREHENSIVE TEST REPORT - ALL PERMUTATIONS")
    report.append("=" * 100)

    report.append(f"\n📊 **TEST SUMMARY:**")
    report.append(f"   - Total Profiles Tested: {total_profiles}")
    report.append(f"   - Profiles with Issues: {profiles_with_issues}")
    report.append(f"   - Total Issues Found: {total_issues}")
    report.append(f"   - Success Rate: {((total_profiles - profiles_with_issues) / total_profiles * 100):.1f}%")

    report.append(f"\n🔍 **ISSUES BY TYPE:**")
    for issue_type, count in issue_types.items():
        if count > 0:
            report.append(f"   - {issue_type}: {count}")

    report.append(f"\n✅ **PROFILES WITHOUT ISSUES:** {total_profiles - profiles_with_issues}/{total_profiles}")

    if profiles_with_issues > 0:
        report.append(f"\n❌ **PROFILES WITH ISSUES:** {profiles_with_issues}/{total_profiles}")

    return "\n".join(report)


def generate_detailed_report(results: List[Dict[str, Any]], output_file: str = "test_report_detailed.txt"):
    """Generate detailed report with all profiles and their analysis."""

    with open(output_file, "w") as f:
        f.write("=" * 100 + "\n")
        f.write("DETAILED PROFILE ANALYSIS REPORT\n")
        f.write("=" * 100 + "\n\n")

        for i, result in enumerate(results, 1):
            profile = result["profile"]
            analysis = result["analysis"]
            issues = result["issues"]

            f.write(f"\n{'='*100}\n")
            f.write(f"PROFILE #{i}: {profile['experience']} years, {profile['currentRole']}, targeting {profile['targetRole']}\n")
            f.write(f"{'='*100}\n\n")

            # Profile details
            f.write(f"📋 **PROFILE DETAILS:**\n")
            f.write(f"   Experience: {profile['experience']}\n")
            f.write(f"   Current Role: {profile['currentRole']}\n")
            f.write(f"   Problem Solving: {profile['problemSolving']}\n")
            f.write(f"   System Design: {profile['systemDesign']}\n")
            f.write(f"   Portfolio: {profile['portfolio']}\n")
            f.write(f"   Target Role: {profile['targetRole']}\n")
            f.write(f"   Target Company: {profile['targetCompany']}\n\n")

            # Analysis results
            f.write(f"🎯 **ANALYSIS RESULTS:**\n")
            f.write(f"   Seniority: {analysis['seniority']}\n")
            f.write(f"   User Level: {analysis['user_level']}\n")
            f.write(f"   Profile Score: {analysis['profile_score']}/100\n")
            f.write(f"   Timeline: {analysis['timeline']['timeline_text']}\n")
            f.write(f"   Key Gap: {analysis['timeline']['key_gap']}\n\n")

            # Quick wins
            f.write(f"⚡ **QUICK WINS:**\n")
            for j, qw in enumerate(analysis['quick_wins'], 1):
                f.write(f"   {j}. {qw['title']}\n")
                f.write(f"      {qw['description']}\n")

            # Timeline milestones
            f.write(f"\n📅 **TIMELINE MILESTONES:**\n")
            for j, milestone in enumerate(analysis['timeline']['milestones'], 1):
                f.write(f"   {j}. {milestone}\n")

            # Job opportunities
            f.write(f"\n💼 **JOB OPPORTUNITIES (Top 3):**\n")
            for j, job in enumerate(analysis['jobs'], 1):
                f.write(f"   {j}. {job}\n")

            # Issues
            if issues:
                f.write(f"\n❌ **ISSUES FOUND:**\n")
                for issue in issues:
                    f.write(f"   {issue}\n")
            else:
                f.write(f"\n✅ **NO ISSUES - Profile handled correctly!**\n")

            # Contradictions
            if analysis.get('contradictions'):
                f.write(f"\n⚠️  **CONTRADICTIONS DETECTED:**\n")
                for contradiction in analysis['contradictions']:
                    f.write(f"   - {contradiction}\n")

            f.write("\n" + "-"*100 + "\n")


def main():
    """Run comprehensive tests on strategic profile combinations."""

    print("\n" + "#" * 100)
    print("# COMPREHENSIVE BACKEND LOGIC TEST - ALL PERMUTATIONS")
    print("#" * 100 + "\n")

    print("🔄 Testing strategic combinations of profiles...")
    print("   This will test key scenarios that represent real user profiles.\n")

    # Define strategic test cases (not all permutations - that would be 4*4*4*3*3*3*3 = 6,048 combinations!)
    # Instead, test representative scenarios covering all edge cases

    test_scenarios = [
        # === SENIOR ENGINEERS (8+ years) ===
        ("Senior - Interview Ready", "8+", "swe-product", "100+", "multiple", "active-5+", "senior-backend", "faang"),
        ("Senior - Rusty on Everything", "8+", "swe-product", "0-10", "once", "inactive", "senior-backend", "faang"),
        ("Senior - Rusty on Coding", "8+", "swe-product", "0-10", "multiple", "active-5+", "senior-backend", "faang"),
        ("Senior - Service Company", "8+", "swe-service", "51-100", "once", "limited-1-5", "senior-backend", "product"),
        ("Senior - DevOps Background", "8+", "devops", "11-50", "not-yet", "limited-1-5", "tech-lead", "unicorns"),

        # === EXPERIENCED (5-8 years) ===
        ("5-8 Years - Strong Profile", "5-8", "swe-product", "100+", "multiple", "active-5+", "senior-backend", "faang"),
        ("5-8 Years - No Portfolio", "5-8", "swe-product", "51-100", "once", "none", "senior-backend", "unicorns"),
        ("5-8 Years - Service Company", "5-8", "swe-service", "11-50", "not-yet", "limited-1-5", "backend-sde", "product"),
        ("5-8 Years - System Design Gap", "5-8", "swe-product", "100+", "not-yet", "active-5+", "senior-backend", "faang"),

        # === MID-LEVEL (3-5 years) ===
        ("3-5 Years - Product Company Strong", "3-5", "swe-product", "100+", "once", "active-5+", "senior-backend", "faang"),
        ("3-5 Years - Product Company Moderate", "3-5", "swe-product", "51-100", "not-yet", "limited-1-5", "backend-sde", "unicorns"),
        ("3-5 Years - Service Company Good Prep", "3-5", "swe-service", "51-100", "once", "limited-1-5", "backend-sde", "product"),
        ("3-5 Years - Service Company Weak", "3-5", "swe-service", "0-10", "not-yet", "none", "backend-sde", "product"),
        ("3-5 Years - Service Company Some Prep", "3-5", "swe-service", "11-50", "not-yet", "none", "backend-sde", "product"),

        # === JUNIOR (0-2 years) ===
        ("Junior - Strong Prep", "0-2", "swe-service", "100+", "not-yet", "limited-1-5", "backend-sde", "product"),
        ("Junior - Moderate Prep", "0-2", "swe-service", "51-100", "not-yet", "none", "backend-sde", "unicorns"),
        ("Junior - Weak Prep", "0-2", "swe-service", "0-10", "not-yet", "none", "backend-sde", "product"),
        ("Junior - Fresh Grad LeetCode Grinder", "0-2", "swe-service", "100+", "not-yet", "none", "backend-sde", "faang"),

        # === EDGE CASES ===
        ("QA → SDE Transition", "3-5", "qa-support", "51-100", "not-yet", "limited-1-5", "backend-sde", "product"),
        ("DevOps → Backend Transition", "5-8", "devops", "11-50", "once", "active-5+", "backend-sde", "unicorns"),
        ("Service → FAANG Ambition", "3-5", "swe-service", "100+", "multiple", "active-5+", "tech-lead", "faang"),
        ("Product Company - No Interview Prep", "5-8", "swe-product", "0-10", "not-yet", "limited-1-5", "senior-backend", "faang"),
    ]

    all_results = []

    for i, scenario in enumerate(test_scenarios, 1):
        name, exp, role, ps, sd, port, target_role, target_company = scenario

        print(f"Testing {i}/{len(test_scenarios)}: {name}...", end=" ")

        profile = generate_test_profile(exp, role, ps, sd, port, target_role, target_company)
        analysis = analyze_profile(profile)
        issues = check_for_issues(profile, analysis)

        all_results.append({
            "name": name,
            "profile": profile,
            "analysis": analysis,
            "issues": issues
        })

        if issues:
            print(f"❌ {len(issues)} issues found")
        else:
            print("✅ Passed")

    # Generate summary report
    summary = generate_summary_report(all_results)
    print(summary)

    # Generate detailed report
    print(f"\n📄 Generating detailed report...")
    generate_detailed_report(all_results, "test_report_comprehensive.txt")
    print(f"✅ Detailed report saved to: test_report_comprehensive.txt")

    # Show sample profiles
    print(f"\n" + "=" * 100)
    print("SAMPLE PROFILE ANALYSIS (First 3 profiles)")
    print("=" * 100)

    for i in range(min(3, len(all_results))):
        result = all_results[i]
        profile = result["profile"]
        analysis = result["analysis"]

        print(f"\n{'─'*100}")
        print(f"PROFILE: {result['name']}")
        print(f"{'─'*100}")
        print(f"Experience: {profile['experience']} | Role: {profile['currentRole']} | Target: {profile['targetRole']}")
        print(f"Problem Solving: {profile['problemSolving']} | System Design: {profile['systemDesign']} | Portfolio: {profile['portfolio']}")
        print(f"\n✨ Seniority: {analysis['seniority']} | Score: {analysis['profile_score']}/100 | Timeline: {analysis['timeline']['timeline_text']}")
        print(f"\n⚡ Quick Wins:")
        for j, qw in enumerate(analysis['quick_wins'][:3], 1):
            print(f"   {j}. {qw['title']}")

        if result['issues']:
            print(f"\n❌ Issues ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"   {issue}")
        else:
            print(f"\n✅ No issues found!")

    print(f"\n{'='*100}\n")

    # Final verdict
    total_issues = sum(len(r["issues"]) for r in all_results)
    if total_issues == 0:
        print("🎉 **ALL TESTS PASSED!** Backend logic is working correctly for all scenarios.")
    else:
        print(f"⚠️  **FOUND {total_issues} ISSUES** across {len(test_scenarios)} scenarios.")
        print("   Review the detailed report for specific problems.")

    print(f"\n{'#'*100}\n")


if __name__ == "__main__":
    main()
