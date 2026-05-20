# R5 Review: 5.1-B Coaching Compatibility Assessment

## Overview

Review of `src/layer3/schemas_b.py` and `src/layer3/prompts_b.py` from **6.2 recommendation engine (coaching generation)** perspective.

Focus on whether the video-level output fields:

* `narration_quality`
* `recording_quality`
* `coaching_evidence`

are sufficient for downstream coaching generation, including:

* recommendation taxonomy
* template-based advice generation
* fine-grained, actionable coaching outputs

---

## Fields Analysis

### 1. narration_quality

* **Enum Values**: `none`, `sparse`, `adequate`, `rich`

* **Role in 6.2**:

  * Serves as a **primary coaching taxonomy axis**
  * Can directly map to narration-related coaching categories
  * Supports template-based recommendations:

    * `none/sparse` → encourage more verbalisation
    * `adequate` → minor optimisation
    * `rich` → narration not a primary issue

* **Limitations**:

  * Video-level only (1:1 per video)
  * No localisation (no segment/timestamp)
  * No explanation (why narration is sparse)

* **Assessment**:

  * ✔ Sufficient for **high-level categorisation**
  * ✖ Not sufficient for **fine-grained coaching generation**

---

### 2. recording_quality

* **Enum Values**: `poor`, `acceptable`, `good`

* **Role in 6.2**:

  * Directly supports recording-related coaching
  * Well-suited for **template-based advice generation**
  * Can be used as:

    * gating condition (e.g. skip deep analysis if `poor`)
    * modifier for recommendation confidence

* **Strengths**:

  * Clear semantic meaning
  * Stable and consistent
  * No ambiguity in interpretation

* **Limitations**:

  * No detailed breakdown (e.g. noise vs missing audio)
  * No localisation of issues

* **Assessment**:

  * ✔ Fully sufficient for **recording-related coaching**
  * ✖ Limited for granular diagnosis (but acceptable for 6.2 scope)

---

### 3. coaching_evidence

* **Enum Values**: `none`, `explicit`

* **Role in 6.2**:

  * Indicates whether moderator intervention exists
  * Used to trigger coaching-related recommendations

* **Limitations (Critical)**:

  * Binary scale is **too coarse**
  * No distinction between:

    * light prompting
    * repeated guidance
    * directive coaching
  * No supporting text or evidence span
  * No timestamp information

* **Impact on 6.2**:

  * Cannot generate detailed coaching such as:

    * where the intervention happened
    * how strong the intervention was
  * Limits recommendation quality to generic suggestions

* **Assessment**:

  * ✔ Usable for **basic detection**
  * ✖ Insufficient for **high-quality coaching generation**

* **Suggestion**:

  * Expand to 3-level scale:

    * `{none, minimal, directive}`
  * OR supplement with:

    * evidence span (timestamp)
    * evidence text

---

## Granularity Compatibility

* 5.1-B operates at **video/session-level (1:1 per video)**
* 6.2 requires **issue-level / segment-level granularity**

Mismatch:

| Requirement (6.2)   | Provided by 5.1-B |
| ------------------- | ----------------- |
| Issue-level detail  | ✖                 |
| Timestamp reference | ✖                 |
| Evidence text       | ✖                 |
| Severity signal     | ✖                 |

Conclusion:

> 5.1-B is **not designed for fine-grained analysis**, and cannot independently support detailed coaching generation.

---

## Coaching Generation Suitability

### What 5.1-B CAN support

* High-level coaching categories:

  * narration quality issues
  * recording quality issues
  * moderator coaching presence

* Template-based recommendations:

  * narration improvement
  * recording hygiene
  * moderation behaviour

---

### What 5.1-B CANNOT support (alone)

* Fine-grained recommendations with:

  * timestamp references
  * specific behavioural evidence
  * actionable step-by-step corrections

* Example of unsupported output:

> “At 1:23–1:40, the moderator explicitly guided the participant…”

This requires **finding-level evidence (5.1-A)**.

---

## Overall Assessment

### Sufficiency for 6.2

* ✔ **Sufficient as top-level coaching taxonomy input**
* ✔ Supports initial recommendation engine implementation (MVP)
* ✖ Not sufficient for production-quality, fine-grained coaching

---

### Design Intent Alignment

From prompt design:

* 5.1-B explicitly avoids:

  * issue listing
  * severity scoring
  * detailed reasoning

This confirms:

> 5.1-B is designed as a **lightweight session-level signal layer**, not a detailed coaching source.

---

## Recommendations

1. **Proceed with current schema for MVP**

   * Use 5.1-B as primary classification input for 6.2

2. **Combine with 5.1-A for fine-grained coaching**

   * Use finding-level outputs for:

     * timestamp references
     * evidence extraction
     * detailed recommendations

3. **Extend coaching_evidence (high priority)**

   * Upgrade to `{none, minimal, directive}`
   * OR add supporting evidence fields

4. **Define mapping logic in recommendation engine**

   * narration_quality → narration coaching templates
   * recording_quality → recording templates
   * coaching_evidence → moderation-related coaching

---

## Final Conclusion

> 5.1-B is sufficient as the **category anchor** for the recommendation engine (6.2), but not sufficient on its own for generating **fine-grained, actionable coaching suggestions**.
> The recommendation engine should consume 5.1-B for high-level classification, and rely on 5.1-A (or future schema extensions) for detailed evidence and localisation.

---

## Next Steps

* Finalise this review with team
* Confirm whether:

  * 5.1-A will be consumed by 6.2
  * `coaching_evidence` will be expanded
* Start implementing `src/coaching/recommendation_engine.py` with:

  * template-based logic (phase 1)
  * optional fine-grained extension (phase 2)
