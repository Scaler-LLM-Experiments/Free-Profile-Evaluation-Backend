# PRODUCT AUDIT: Profile Evaluation System
## Comprehensive Analysis of Data Collection, Weighting, and Output Quality

**Date**: October 15, 2025
**Scope**: End-to-end evaluation flow from quiz → backend → results

---

## 🚨 CRITICAL ISSUES FOUND

### 1. **MISSING DATA COLLECTION - Portfolio Question**

**Problem**: Backend expects `portfolio` field but **quiz doesn't ask about it!**

```python
# backend/run_poc.py line 112
"- quizResponses.portfolio: active-5+, limited-1-5, inactive, none (DEPRECATED: not collected in new flow)"
```

```python
# backend/quick_wins_logic.py lines 124, 199-219
if portfolio in ["none", "no-portfolio"]:
    quick_wins.append(_create_quick_win(
        "Set Up GitHub Profile",
        ...
    ))
```

**Impact**:
- Quick wins about portfolio creation are shown to EVERYONE (even those with active GitHub)
- Cannot assess project quality or GitHub activity
- Missing signal for hiring readiness

**Frontend Quiz Questions (Tech Path)**:
1. currentRole
2. experience
3. currentSkill
4. primaryGoal
5. targetRole
6. targetCompany
7. problemSolving
8. systemDesign ← Only shows if problemSolving != '0-10'

**MISSING**: portfolio, mockInterviews

**Recommendation**: Add portfolio question to quiz OR remove all portfolio logic from backend

---

### 2. **WEIGHTING SYSTEM IS BACKWARDS**

**Problem**: System design expertise should indicate SENIOR LEVEL but problem-solving count is weighted equally or higher.

**Current Reality**:
```
User A: systemDesign='multiple' (led design discussions) + problemSolving='11-50'
User B: systemDesign='not-yet' + problemSolving='100+'

Current System treats User B as MORE ready for senior roles!
```

**Why This Is Wrong**:
- **Leading design discussions** requires 5+ years of production experience
- **You cannot lead architecture** without having built complex systems
- LeetCode grinding ≠ system design expertise
- System design is MUCH harder to fake than problem solving

**Correct Weighting** (from industry reality):
```
Senior/Staff Engineer Requirements:
1. System Design Experience (60% weight) ← CRITICAL for 5+ year roles
2. Production Experience (30% weight)
3. Problem Solving (10% weight) ← Nice to have, but not sufficient

Entry/Mid Engineer Requirements:
1. Problem Solving (60% weight) ← CRITICAL for 0-3 year roles
2. Portfolio Projects (30% weight)
3. System Design (10% weight) ← Bonus, not required
```

**Backend Prompt Already Knows This** (run_poc.py lines 118-133):
```
"🚨 IMPOSSIBLE COMBINATION: systemDesign='multiple' + problemSolving < '51-100'
Reality: You CANNOT have deep system design expertise without extensive coding practice."
```

**But this override logic is passive!** It only warns, doesn't fix scoring.

**Recommendation**:
- System design `multiple` → auto-bump profile strength by +20 points
- System design `multiple` + experience >= 5 → force "Senior/Staff" role recommendations
- Problem solving should be capped at +15 point contribution max

---

### 3. **CONTRADICTORY SKILL ASSESSMENTS**

**Problem**: User with "Full-stack development knowledge" (`currentSkill='fullstack'`) but `problemSolving='0-10'` is contradictory.

**Why This Happens**:
- We ask "What are you investing learning time in?" (currentSkill)
- We ask "How much problem solving practice?" (problemSolving)
- These can be COMPLETELY independent (watching tutorials vs actually coding)

**Example Contradiction**:
```
currentSkill: 'system-design' (System design & architecture)
problemSolving: '0-10' (Not Active)
experience: '3-5'

This person CLAIMS to focus on system design but doesn't code?
```

**Backend Has Contradiction Detection** (run_poc.py lines 116-143) but it only applies to RAW GPT response, not to quiz validation.

**Recommendation**:
1. **Frontend Validation**: Show warning if contradiction detected
   - "You selected 'System Design' as focus area but haven't solved many problems. System design requires strong coding foundations. Are you sure?"

2. **Backend Auto-Correction**: Apply contradiction overrides to quiz responses BEFORE sending to GPT
   - If `currentSkill='system-design'` + `problemSolving='0-10'` → override to `problemSolving='11-50'` OR downgrade `currentSkill`

3. **Add Verification Question**: "Have you designed production systems in your current role?" (yes/no)
   - If yes + systemDesign='multiple' → verified senior
   - If no + systemDesign='multiple' → aspirational, downgrade to 'once'

---

### 4. **GENERIC JOB OPPORTUNITY DESCRIPTIONS**

**Problem**: Job descriptions are vague and useless.

**Current Output** (from user complaint):
```
"Senior Backend Engineer at Razorpay - Aligns with your current experience and target role interests."
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      Generic fluff, no actionable info
```

**Backend Prompt Says** (run_poc.py line 254):
```
"- KEEP DESCRIPTIONS CRISP: Maximum 8-10 words per opportunity"
```

**But GPT Ignores This!**

**Examples of GOOD vs BAD descriptions**:

❌ **BAD** (current):
- "Aligns with your current experience and target role interests"
- "Matches your skills and career goals"
- "Good fit for your background"

✅ **GOOD** (specific, crisp):
- "Payment systems expertise required"
- "5+ years microservices experience"
- "Scala/Kafka stack knowledge needed"
- "Led 3+ design reviews minimum"
- "Experience scaling to 10M+ users"

**Recommendation**:
1. **Hardcode job descriptions** in backend based on role patterns
2. Create job description templates:
```python
JOB_DESC_TEMPLATES = {
    'backend-senior-fintech': "Payment systems, high-volume transactions",
    'backend-senior-ecommerce': "Order processing, inventory systems",
    'fullstack-mid-startup': "React + Node.js, fast-paced growth",
    'staff-engineer-product': "Architecture decisions, mentoring engineers"
}
```

3. **Match based on user profile**:
   - experience + targetRole + currentSkill → template key
   - Return 5-7 opportunities with REAL requirements from templates

4. **OR use GPT with strict format**:
   ```
   Format: [ROLE] at [COMPANY] - [SPECIFIC TECH/REQUIREMENT]
   Max 8 words after hyphen. NO generic statements.

   Examples:
   - "Staff SDE at CRED - Kafka, Redis, 10M+ scale"
   - "Senior Backend at Razorpay - Payment gateway integration"
   ```

---

### 5. **MISSING CONTEXTUAL WEIGHTING**

**Problem**: All signals are treated independently when they should compound or contradict.

**Example Signal Combinations**:

**Scenario A: Strong Senior Engineer**
```
experience: '5-8'
problemSolving: '51-100'
systemDesign: 'multiple' (led discussions)
currentRole: 'swe-product'

Expected: Top 10% profile, Staff/Senior roles
Actual: ???
```

**Scenario B: Aspiring Junior (contradictory)**
```
experience: '0-2'
problemSolving: '0-10'
systemDesign: 'multiple' (CLAIMS to have led discussions)
currentRole: 'qa-support'

Expected: Flag contradiction, downgrade systemDesign claim
Actual: Takes it at face value
```

**Scenario C: Career Switcher (realistic)**
```
background: 'non-tech'
codeComfort: 'learning'
timePerWeek: '10+'
experience: '5+'

Expected: 12-18 months to job-ready, leverage domain expertise
Actual: ???
```

**Recommendation**:
Create scoring matrix that considers signal combinations:

```python
def calculate_profile_strength(quiz_responses):
    base_score = 0

    # Experience contributes differently based on role
    if current_role == 'swe-product':
        base_score += experience_years * 8  # 8 points per year
    elif current_role == 'qa-support':
        base_score += experience_years * 4  # 4 points per year (less relevant)

    # System design is HUGE multiplier for senior
    if system_design == 'multiple' and experience >= 5:
        base_score += 30  # MASSIVE boost
    elif system_design == 'multiple' and experience < 5:
        base_score += 5   # Suspicious, small boost only

    # Problem solving capped contribution
    problem_solving_points = min(15, problem_count_to_points(problemSolving))
    base_score += problem_solving_points

    # Contradiction penalty
    if has_contradictions(quiz_responses):
        base_score -= 10

    return min(100, max(0, base_score))
```

---

## 📊 RECOMMENDED FIXES (Priority Order)

### P0 - CRITICAL (Do Now)

1. ✅ **Already Fixed**: Quick Wins Logic - Hardcoded decision tree with priority
   - Status: Completed ✓

2. **Add Portfolio Question** to quiz OR remove all portfolio logic
   - Options:
     - "How active is your GitHub?" (active-5+ / limited-1-5 / inactive / none)
     - OR remove lines 124-130, 199-219 from `quick_wins_logic.py`

3. **Fix System Design Weighting**
   - Create `scoring_logic.py` with proper weighting
   - systemDesign='multiple' + experience >= 5 → force profile_strength >= 75
   - Override GPT's profile_strength_score if it violates rules

4. **Hardcode Job Descriptions**
   - Create `job_descriptions.py` with templates
   - Match based on (experience, targetRole, currentSkill) combination
   - Bypass GPT for `opportunities_you_qualify_for`

### P1 - HIGH (Do This Week)

5. **Add Contradiction Detection to Frontend**
   - Show warnings when user selects contradictory combinations
   - Example: systemDesign='multiple' + problemSolving='0-10' + experience='0-2'

6. **Create Comprehensive Scoring System**
   - File: `backend/scoring_logic.py`
   - Calculates profile_strength_score deterministically
   - Considers signal combinations and contradictions
   - GPT can override with explanation, but default is calculation

7. **Add Mock Interview Question** (if we care about this signal)
   - "How often do you practice mock interviews?"
   - Options: weekly+ / monthly / rarely / never
   - OR deprecate completely from backend prompt

### P2 - MEDIUM (Do Next Sprint)

8. **Improve Recommended Tools Logic**
   - Similar to Quick Wins: hardcode decision tree
   - Tools should match (background, targetRole, experience)
   - Example: Non-tech + backend → Python, Flask, SQL, Postman
   - Bypass GPT's unreliable tool recommendations

9. **Add Verification Questions for Senior Claims**
   - "Have you designed production systems?" (if systemDesign='multiple')
   - "What's the largest system you've scaled?" (if experience >= 5)
   - Use answers to validate or downgrade claims

10. **Create Testing Suite**
    - File: `backend/test_evaluation_scenarios.py`
    - Test 20+ realistic user profiles
    - Verify scoring, role recommendations, quick wins are appropriate
    - Catch contradictions and edge cases

---

## 🎯 DATA COLLECTION AUDIT

### Currently Collected (Tech Quiz)
1. ✅ currentRole - Good signal
2. ✅ experience - Good signal
3. ✅ currentSkill - Good signal (learning focus)
4. ✅ primaryGoal - Good signal (motivation)
5. ✅ targetRole - Good signal (aspiration)
6. ✅ targetCompany - Good signal (company tier)
7. ✅ problemSolving - Good signal (interview prep)
8. ⚠️ systemDesign - Good signal BUT conditional (only if problemSolving != '0-10')

### Currently Collected (Non-Tech Quiz)
1. ✅ currentBackground - Good signal
2. ✅ experience - Good signal
3. ✅ stepsTaken - Good signal
4. ✅ targetRole - Good signal
5. ✅ motivation - Good signal
6. ✅ targetCompany - Good signal
7. ✅ codeComfort - Good signal (mapped to problemSolving)
8. ✅ timePerWeek - Good signal (timeline)

### Missing (Expected by Backend)
1. ❌ portfolio - Mentioned in prompt, not collected
2. ❌ mockInterviews - Mentioned in prompt, not collected

### Potential Additions
1. **Current Company** - For benchmarking current vs target
2. **Reason for Switch** - Better understand motivation (Tech users)
3. **Educational Background** - CS degree vs non-CS (affects timeline)
4. **Production System Scale** - Verification for senior claims
5. **Team Size** - Lead experience verification

---

## 🧪 TEST SCENARIOS TO VALIDATE FIXES

### Scenario 1: Senior Engineer with Strong System Design
```
Input:
  experience: '5-8'
  currentRole: 'swe-product'
  systemDesign: 'multiple'
  problemSolving: '51-100'
  targetRole: 'tech-lead'

Expected Output:
  profile_strength_score: >= 80
  recommended_roles: Staff Engineer, Tech Lead, Principal (NOT junior roles)
  quick_wins: Leadership prep, system design deep-dive (NOT "solve 100 problems")
  opportunities: Staff SDE at CRED, Principal at Razorpay (NOT SDE-1 roles)
```

### Scenario 2: Contradictory Beginner Claims
```
Input:
  experience: '0-2'
  currentRole: 'student-freshgrad'
  systemDesign: 'multiple' ← Contradiction!
  problemSolving: '0-10'
  targetRole: 'senior-faang'

Expected Output:
  profile_strength_score: <= 40
  systemDesign: Downgraded to 'learning' (with note about contradiction)
  recommended_roles: Junior Engineer, SDE-1 (NOT senior)
  quick_wins: Build coding foundation, not system design
  profile_strength_notes: "Claims of system design don't match experience. Focus on fundamentals first."
```

### Scenario 3: Career Switcher with Realistic Timeline
```
Input:
  background: 'non-tech'
  currentBackground: 'operations'
  codeComfort: 'learning'
  timePerWeek: '10+'
  targetRole: 'backend'

Expected Output:
  profile_strength_score: 50-60
  success_likelihood: 12-18 months timeline
  quick_wins: Build REST API, learn Python basics (NOT "prepare for FAANG")
  recommended_roles: Junior Backend Engineer (NOT senior roles)
  opportunities: Service companies, not FAANG
```

### Scenario 4: Grinding LeetCode Without Real Experience
```
Input:
  experience: '0-2'
  currentRole: 'swe-service'
  systemDesign: 'not-yet'
  problemSolving: '100+' ← High grind
  portfolio: 'none' (if we add this question)

Expected Output:
  profile_strength_score: 55-65
  recommended_roles: SDE-2 at service companies (NOT Staff Engineer)
  quick_wins: Build portfolio projects, learn system design
  areas_to_develop: Production experience, real-world projects
  opportunities: Mid-level roles, not senior
```

---

## 📝 SUMMARY

**The Core Problem**: We're collecting signals but not intelligently weighting them or detecting contradictions.

**Key Insight**: System design experience is GOLD for senior roles but we treat it like any other checkbox.

**Immediate Actions**:
1. Add portfolio question OR remove portfolio logic ← 5 min fix
2. Create `scoring_logic.py` with proper weighting ← 2 hours
3. Hardcode job descriptions with templates ← 1 hour
4. Add contradiction detection to frontend ← 1 hour

**Long-term Vision**:
- Deterministic scoring system (not GPT-based)
- Smart contradiction detection
- Role recommendations based on signal patterns
- Realistic timelines and expectations
- Test coverage for 20+ user profiles

