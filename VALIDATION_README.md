# AI Response Validation System

This directory contains tools to validate AI-generated profile evaluation responses for logical consistency and identify prompt improvement opportunities.

## Problem Statement

The AI may sometimes generate recommendations that don't align with user inputs. Common issues include:

1. **Seniority Mismatch**: Recommending junior roles for experienced professionals
2. **Skills Mismatch**: Suggesting PM roles for strong coders targeting engineering
3. **Target Misalignment**: Ignoring user's explicit career goals (targetRole)
4. **System Design Blind Spot**: Not acknowledging strong system design experience

## Files

- **`validate_response.py`**: Main validation script that checks responses for logical issues
- **`improved_prompt.txt`**: Enhanced system prompt with stricter rules and examples
- **`VALIDATION_README.md`**: This file

## Usage

### 1. Basic Validation

```bash
# Validate a response against an input
python3 validate_response.py sample_input.json output.json
```

### 2. Generate and Validate

```bash
# Generate a response and save it
INPUT_PATH=sample_input.json python3 run_poc.py > output.json

# Validate the response
python3 validate_response.py sample_input.json output.json
```

### 3. Test with Your Own Input

Create your own test input JSON:

```json
{
  "background": "tech",
  "quizResponses": {
    "currentRole": "swe-product",
    "experience": "5+",
    "targetRole": "faang-sde",
    "problemSolving": "100+",
    "systemDesign": "multiple",
    "portfolio": "active-5+",
    "mockInterviews": "monthly",
    "currentCompany": "Startup",
    "currentSkill": "100+",
    "requirementType": "upskilling",
    "targetCompany": "faang"
  },
  "goals": {
    "requirementType": [],
    "targetCompany": "Google",
    "topicOfInterest": []
  }
}
```

Then run:
```bash
INPUT_PATH=my_test.json python3 run_poc.py > my_output.json
python3 validate_response.py my_test.json my_output.json
```

## Validation Checks

The script performs these validations:

### 1. **Role Seniority Match**
- Checks if recommended roles match experience level
- **Example Issue**: 5+ years experience → Junior PM recommended
- **Expected**: Senior/Staff/Lead roles

### 2. **Technical Role Alignment**
- Verifies technical skills match technical roles
- **Example Issue**: problemSolving=100+, systemDesign=multiple → PM recommended
- **Expected**: Senior SDE, Staff Engineer, Tech Lead

### 3. **PM Role Appropriateness**
- Ensures PM roles are only suggested when appropriate
- **Criteria**: User targets PM OR has 3-5+ years with weak coding
- **Example Issue**: Strong coder targeting SDE → PM recommended

### 4. **Skill vs Opportunities**
- Checks if opportunities match skill level
- **Example Issue**: Strong skills → Junior opportunities suggested

### 5. **System Design Acknowledgment**
- Verifies system design experience is highlighted
- **Example Issue**: systemDesign='multiple' → Not in strengths

### 6. **Experience vs Readiness**
- Validates interview readiness matches experience
- **Example Issue**: 5+ years + regular mocks → Low technical readiness

### 7. **Score Consistency**
- Checks profile score vs success likelihood alignment
- **Example Issue**: 80% profile strength, 40% success likelihood

### 8. **Portfolio vs Roles**
- Ensures GitHub activity boosts engineering roles
- **Example Issue**: Active portfolio → No engineering roles

## Output Format

The validation script produces a detailed report:

```
================================================================================
AI RESPONSE VALIDATION REPORT
================================================================================

🚨 CRITICAL ISSUES FOUND: 2
--------------------------------------------------------------------------------

1. CRITICAL: User has 5+ years experience but recommended 'Junior Product Manager'
   which is a junior role. Should recommend Senior/Staff/Lead roles instead.

2. CRITICAL: User has strong technical skills (problemSolving=100+,
   systemDesign=multiple) and targets faang-sde, but AI recommended
   non-technical roles: Junior Product Manager

⚠️  WARNINGS: 1
--------------------------------------------------------------------------------

1. User has 'multiple' system design experience but it's not mentioned in strengths.
   This is a valuable skill that should be highlighted.

💡 PROMPT IMPROVEMENT SUGGESTIONS: 2
--------------------------------------------------------------------------------

1. Improve prompt: Add stronger constraint that maps experience directly to seniority:
   0-2 years → Entry/Junior, 3-5 years → Mid/Senior, 5+ years → Senior/Staff/Lead/Principal

2. Improve prompt: Add explicit rule - 'If problemSolving >= 51-100 AND targetRole
   contains 'sde'/'backend'/'fullstack', ONLY recommend engineering roles (SDE,
   Backend Engineer, Full Stack Engineer, etc.), NOT Product Manager or Business
   Analyst roles.'

================================================================================
```

## Improving the Prompt

Based on validation findings, consider implementing the improved prompt from `improved_prompt.txt`. Key improvements:

### 1. **Hierarchical Rule Priority**
```
1. Seniority Matching (Highest Priority)
2. Technical Skills Matching
3. Respect Target Role
4. PM Roles - Strict Criteria
5. Diversify But Stay Relevant
```

### 2. **Stricter PM Recommendation Rules**
```
✅ ONLY recommend PM if:
   a) targetRole explicitly contains 'product' or 'pm', OR
   b) experience >= 3-5 years AND problemSolving <= 11-50 AND product interest, OR
   c) currentRole indicates PM experience

❌ NEVER recommend PM for:
   - Users targeting engineering roles
   - Users with strong coding (problemSolving >= 51-100)
   - Users with active GitHub targeting technical roles
```

### 3. **System Design Emphasis**
```
- systemDesign = 'multiple' → MUST include in recommendations:
  * Senior SDE
  * Staff Engineer
  * Solutions Architect
  * Tech Lead
```

### 4. **Validation Checklist in Prompt**
The AI should self-validate before returning:
- ☑ Seniority match?
- ☑ Leverages strongest skills?
- ☑ Aligns with targetRole?
- ☑ Logical next step?
- ☑ PM criteria met (if PM role)?

## Applying the Improved Prompt

To use the improved prompt, update `run_poc.py` lines 93-124:

```python
system_instruction = """
[Copy content from improved_prompt.txt]
"""
```

## Testing Strategy

### Test Cases to Validate

1. **Senior Engineer with System Design**
   - Input: experience='5+', systemDesign='multiple', targetRole='faang-sde'
   - Expected: Senior/Staff roles only

2. **Mid-Level Backend Engineer**
   - Input: experience='3-5', problemSolving='51-100', targetRole='backend'
   - Expected: Mid/Senior backend roles

3. **Career Switcher to PM**
   - Input: experience='3-5', problemSolving='11-50', targetRole='product'
   - Expected: PM roles acceptable

4. **Strong Coder Targeting Tech Lead**
   - Input: experience='5+', problemSolving='100+', systemDesign='multiple', targetRole='tech-lead'
   - Expected: Lead/Staff/Principal engineering roles

## Exit Codes

- **0**: No critical issues (warnings acceptable)
- **1**: Critical issues found
- **2**: Usage error

## Integration with CI/CD

You can integrate this into your testing pipeline:

```bash
#!/bin/bash
# test_ai_responses.sh

for test_file in tests/*.json; do
    echo "Testing $test_file..."
    INPUT_PATH=$test_file python3 run_poc.py > output_temp.json

    if python3 validate_response.py $test_file output_temp.json; then
        echo "✅ PASSED"
    else
        echo "❌ FAILED"
        exit 1
    fi
done
```

## Future Enhancements

1. Add validation for badge recommendations
2. Check quick wins relevance
3. Validate recommended tools match user's tech stack
4. Check peer comparison percentile realism
5. Validate salary expectations against market data

## Contributing

If you find new validation patterns or issues, add them to `validate_response.py`:

```python
def validate_new_pattern(self):
    """Check for new pattern"""
    # Your validation logic
    if condition:
        self.issues.append("Issue description")
        self.suggestions.append("Prompt improvement")
```

## Questions?

For issues or improvements, contact the AI/ML team or create an issue in the repository.
