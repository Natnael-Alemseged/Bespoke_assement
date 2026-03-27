# Terminal Bench / Harbor Task Grading Rubric

Use this rubric to evaluate DevOps/Backend take-home tasks created for the Terminal Bench 2.0 workflow.

## How To Use This

1. Apply the **Must-Pass Gates** first (fail-fast checks).
2. If the submission passes gates, score each weighted category.
3. Apply penalties.
4. Record final score and recommendation.

---

## A) Must-Pass Gates (Fail-Fast)

If any gate fails, stop scoring and mark as **Reject** unless there is clear evidence the issue is a trivial packaging mistake.

- **Gate A1 - Required structure exists**  
  Must include: `task.toml`, `instruction.md`, `environment/`, `solution/`, `tests/`.
- **Gate A2 - Oracle passes**  
  `harbor run -p "<task_path>" -a oracle` passes reliably.
- **Gate A3 - No leakage / no cheating path**  
  Agent cannot solve by simply reading a prewritten answer in `environment/`.
- **Gate A4 - Test isolation enforced**  
  `tests/` logic is not available to the agent inside runtime image.
- **Gate A5 - Confidentiality and originality**  
  No obvious plagiarism / policy breach.

**Gate Outcome Template**

- A1: Pass/Fail
- A2: Pass/Fail
- A3: Pass/Fail
- A4: Pass/Fail
- A5: Pass/Fail
- Result: Continue Scoring / Reject

---

## B) Weighted Scoring Rubric (100 points)

### 1) Task Design Quality (20 pts)

- **Problem clarity (5 pts)**
  - 5: Goal and constraints are explicit; expected end-state is unambiguous.
  - 3: Mostly clear with minor ambiguity.
  - 1: Vague or underspecified.
- **Real-world relevance (5 pts)**
  - 5: Strongly resembles practical DevOps/SWE debugging or build-fix workflows.
  - 3: Some relevance but partly contrived.
  - 1: Mostly toy scenario.
- **Difficulty fit (10 pts)**
  - 10: Hard but solvable; requires genuine reasoning.
  - 6: Moderate difficulty.
  - 2: Too easy, too random, or brute-forceable.

### 2) Instruction Quality (`instruction.md`) (15 pts)

- **Outcome-focused phrasing (5 pts)**
  - 5: States what to achieve, not solution steps.
  - 3: Slight hint leakage.
  - 1: Gives away key solution path.
- **Requirement completeness (5 pts)**
  - 5: All expected outputs/conditions are covered.
  - 3: Minor missing requirement.
  - 1: Multiple missing requirements.
- **Path/model correctness (5 pts)**
  - 5: Correct `/app/...` references and consistent environment assumptions.
  - 3: Minor inconsistency.
  - 1: Incorrect path model or contradictory instructions.

### 3) Environment Engineering (`environment/`, Dockerfile) (20 pts)

- **Build reliability (6 pts)**
  - 6: Build and run are stable from clean setup.
  - 3: Intermittent failures or manual steps needed.
  - 0: Frequently broken.
- **Reproducibility and pinning (5 pts)**
  - 5: Dependencies pinned and deterministic.
  - 3: Partial pinning.
  - 1: Mostly floating/latest versions.
- **Failure-mode realism (5 pts)**
  - 5: Errors and conditions are authentically reproduced.
  - 3: Partly realistic.
  - 1: Artificial or simulated poorly.
- **No environment leakage (4 pts)**
  - 4: No answer artifacts or accidental hints.
  - 2: Mild leakage risk.
  - 0: Major leakage.

### 4) Test Suite Strength (`tests/`) (25 pts)

- **Coverage of instruction requirements (8 pts)**
  - 8: Every requirement in `instruction.md` is validated.
  - 5: Most requirements validated.
  - 2: Significant gaps.
- **Functional depth (7 pts)**
  - 7: End-to-end behavioral checks dominate.
  - 4: Mix of functional and shallow checks.
  - 1: Mostly superficial assertions.
- **Multiple meaningful scenarios (4 pts)**
  - 4: Includes normal + edge/failure paths.
  - 2: Limited case variety.
  - 0: Single narrow path.
- **Isolation and policy adherence (3 pts)**
  - 3: `tests/` hidden from runtime image; `test.sh` untouched.
  - 1: Minor process issue.
  - 0: Major violation.
- **Determinism and stability (3 pts)**
  - 3: Repeatable outcomes with low flake risk.
  - 1: Occasional nondeterminism.
  - 0: Flaky.

### 5) Golden Solution Quality (`solution/`, `solve.sh`) (10 pts)

- **Oracle correctness (5 pts)**
  - 5: Oracle pass is consistent.
  - 3: Passes but brittle.
  - 0: Fails.
- **Implementation quality (3 pts)**
  - 3: Clean, minimal, maintainable scripts.
  - 2: Works but rough.
  - 0: Fragile or poor quality.
- **Legitimacy of approach (2 pts)**
  - 2: No hardcoded shortcuts or unfair bypasses.
  - 1: Borderline shortcuts.
  - 0: Invalid/hacked approach.

### 6) Difficulty Validation Evidence (10 pts)

- **Run evidence quality (4 pts)**
  - 4: Clear evidence from `k=10` runs including model/config.
  - 2: Partial evidence.
  - 0: No evidence.
- **Target success rate compliance (4 pts)**
  - 4: Average success is `> 0.0` and `< 0.7`.
  - 2: Near-boundary or weak evidence.
  - 0: Outside target.
- **Reasoning requirement met (2 pts)**
  - 2: Agent must reason through logs/dependencies/system state.
  - 1: Light reasoning only.
  - 0: Mostly simple file edits.

---

## C) Penalties (Apply After Base Score)

- Missing required structure: `-20`
- Tests leaked into runtime image: `-15`
- `test.sh` modified against instructions: `-10`
- No practical version pinning: `-5`
- Trivial answer leakage in environment: `-20`
- Plagiarism / confidentiality breach: **Auto-fail**

---

## D) Grade Bands

- **90-100**: Strong Hire / Fast-track
- **80-89**: Hire
- **70-79**: Borderline
- **60-69**: Weak
- **<60**: Reject

---

## E) 15-Minute Rapid Review Checklist

Use this when screening many submissions quickly.

### Minute 0-3: Packaging and gates

- Confirm required files/folders exist.
- Scan for obvious leakage (solution artifacts in `environment/`).
- Check if tests appear isolated by design.

### Minute 3-6: Instruction and task design

- Read `instruction.md`: is it outcome-focused and clear?
- Check complexity: does it look reasoning-heavy vs simple edit?
- Confirm `/app/...` references are coherent.

### Minute 6-10: Tests and oracle validity

- Review `tests/test_outputs.py`: does it verify all required behaviors?
- Confirm tests are functional, not purely superficial.
- Validate `solve.sh` and expected oracle behavior quickly.

### Minute 10-13: Difficulty evidence

- Look for `k=10` run evidence and aggregate success-rate report.
- Verify success rate sits in target band (`>0.0` and `<0.7`).

### Minute 13-15: Final decision

- Fill weighted score + penalties.
- Write 3 strengths and 3 risks.
- Assign grade band + recommendation.

---

## F) Reusable Evaluation Form (Copy/Paste)

```md
# Submission Evaluation

## Must-Pass Gates
- A1 Required structure: Pass/Fail
- A2 Oracle passes: Pass/Fail
- A3 No leakage/cheating path: Pass/Fail
- A4 Test isolation: Pass/Fail
- A5 Originality/confidentiality: Pass/Fail
- Gate result: Continue / Reject

## Weighted Scores
- 1) Task Design Quality (20): __/20
- 2) Instruction Quality (15): __/15
- 3) Environment Engineering (20): __/20
- 4) Test Suite Strength (25): __/25
- 5) Golden Solution Quality (10): __/10
- 6) Difficulty Validation Evidence (10): __/10

Base Score: __/100
Penalties: __
Final Score: __/100

## Decision
- Grade Band: Strong Hire / Hire / Borderline / Weak / Reject
- Recommendation: __

## Top Strengths
1) __
2) __
3) __

## Top Risks
1) __
2) __
3) __
```

---

## G) Evidence You Should Collect Before Grading

When you ask for a grade, provide:

- Zipped submission contents or extracted folder.
- Oracle run output.
- Agent run output (`k=10`) with model/config.
- Any notes on known limitations.

This enables consistent and defensible scoring.
