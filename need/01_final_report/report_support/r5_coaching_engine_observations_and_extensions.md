# R5 Coaching Engine – Observation & Extension Notes (Observations and extensions based on 57 generated Quality Reports)

## 1. Overview

This document presents observations based on 57 generated Quality Reports generated from the Step 6.1 fusion pipeline.

The analysis focuses on:
- distribution of coaching recommendations
- overall quality tier (fusion output)
- limitations of the current rule-based approach
- potential directions for extension

---

## 2. Recommendation Distribution

### 2.1 Recommendation Density

- Average recommendations per report: ~0.89  
- Minimum: 0  
- Maximum: 2  

**Observation:**
A significant number of reports contain no recommendations, indicating limited trigger coverage and conservative rule conditions.

---

### 2.2 Category Distribution

- Recording: dominant (majority of recommendations)
- Narration: very limited
- Moderation: not observed

**Observation:**
The coaching engine is heavily biased towards recording-related recommendations, while narration is underrepresented and moderation is not triggered at all.

This suggests:
- narration triggers are too strict or rarely activated  
- coaching_evidence rarely appears in the dataset or is not effectively mapped  

---

### 2.3 Priority Distribution

- Majority of recommendations fall under priority = 2  
- Very few high-priority or low-priority cases  

**Observation:**
Priority lacks differentiation and does not effectively reflect varying severity or importance.

---

## 3. Tier Distribution (Step 6.1 Fusion Output)

The overall quality tier shows:

- Predominantly "poor" and "acceptable"
- No "good" cases observed

---

### 3.1 Interpretation

This does **not necessarily imply that all videos are of poor quality**.

Instead, the distribution is influenced by:

1. **Conservative fusion logic**
   - Any detected issue (e.g., S1/S2 severity or recording defects) leads to downgrade
   - Limited conditions to qualify as "good"

2. **Problem-focused dataset**
   - Data is derived from annotated findings and violation-oriented samples
   - Bias towards detecting issues rather than balanced sessions

3. **Dominance of recording quality**
   - Recording quality frequently marked as "acceptable"
   - Combined with findings, leads to systematic downgrading

---

### 3.2 Key Insight

> The absence of "good" tier reflects **evaluation bias and rule design**, rather than actual dataset quality.

---

## 4. Key Limitations of Current MVP

### 4.1 Imbalanced Recommendation Coverage

- Over-reliance on recording quality
- Under-utilisation of narration signals
- No moderation recommendations triggered

---

### 4.2 Low Recommendation Coverage

- Many reports contain zero recommendations
- Indicates overly strict triggering conditions

---

### 4.3 Lack of Priority Sensitivity

- Priority values are mostly static
- No integration with severity or frequency signals

---

### 4.4 Template-Based Behaviour

- Recommendations are deterministic
- No variation or contextualisation
- No use of L3 (5.1-A) findings

---

### 4.5 No Temporal Grounding

- Recommendations are session-level only
- No reference to timestamps or specific events

---

## 5. Suggested Extension Directions

### 5.1 Integrate 5.1-A Findings (High Priority)

- Use:
  - `friction_type`
  - `severity_s`
  - `rationale`

- Inject into:
  - recommendation summary
  - evidence_note
  - advice generation

---

### 5.2 Improve Moderation Detection

- Revisit mapping from `coaching_evidence`
- Ensure explicit moderator behaviour triggers recommendations

---

### 5.3 Adjust Trigger Sensitivity

- Relax strict thresholds
- Increase coverage for narration-related issues
- Avoid zero-recommendation reports

---

### 5.4 Severity-Aware Priority

- Dynamically assign priority using:
  - severity distribution
  - number of findings

---

### 5.5 Improve Tier Calibration

- Redefine conditions for "good"
- Reduce over-sensitivity to minor issues
- Introduce scoring-based fusion instead of strict rule-based downgrade

---

### 5.6 Add Temporal Grounding

- Link recommendations to:
  - window_id
  - timestamps

Example:
> "At 01:23–02:10, narration is sparse..."

---

### 5.7 Introduce LLM-Based Generation (Optional)

- For complex issues:
  - sentiment mismatch
  - multi-factor usability problems

Use LLM to:
- generate contextualised coaching advice
- synthesise multiple findings

---

## 6. Conclusion

The current Step 6.2 coaching engine successfully delivers a stable MVP with:

- consistent output structure  
- integration with fusion pipeline  
- full test coverage  

However, it remains a high-level, template-driven system with:

- imbalanced recommendation distribution  
- limited coverage  
- conservative quality tier assignment  

Future work should focus on:

- integrating L3 evidence  
- improving recommendation diversity  
- enhancing tier calibration  
- enabling more context-aware coaching outputs  