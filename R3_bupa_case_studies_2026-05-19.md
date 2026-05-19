# R3 Bupa Held-out Case Study Notes

Date: 2026-05-19

These notes are for held-out evidence review only. They are not Final Report
prose and they do not change prompts, taxonomy, scoring, or report logic.

Common held-out caveat across all cases:

- The corrected Bupa run produced valid Layer 3 findings and reports, but it did
  not regenerate Layer 1 flags or Layer 2 cluster assignments.
- As a result, Bupa reports show `l1_total=0` and `l2_coverage=0.0` for all
  videos. This should be treated as an evaluation limitation, not as evidence
  that no Layer 1 or Layer 2 issues existed.

## 1. olekwane__web-health-information-bupa

- Video ID: `olekwane__web-health-information-bupa`
- Report tier and reason: `poor` - task-blocking friction: `S1/S2 present`
- Windows / L3 findings: `97` windows, `82` findings
- Top severity: `S1`
- Dominant friction types: `F1=24`, `F3=17`, `F2=13`, `F5=11`

### Evidence

- `olekwane__web-health-information-bupa_w077` - `F3`, `S1`: participant said
  the site was effectively unusable because inconsistent text and image sizing
  created major readability and contrast problems for visual access.
- `olekwane__web-health-information-bupa_w002` - `F1`, `S1`: pricing and value
  presentation created enough dissatisfaction that the participant said they
  would switch to a competitor instead.
- `olekwane__web-health-information-bupa_w057` - `F3`, `S3`: participant
  identified missing semantic markup and focus-trap behaviour, indicating that
  screen-reader and keyboard access would break down in interactive areas.

### Interpretation

This is a strong product-risk case because the friction is not only aesthetic
or preference-based. The participant reports concrete accessibility breakdowns,
especially readability, semantics, and focus management, while also expressing
loss of trust in the product offer itself. The case shows how accessibility and
comprehension failures can combine into both exclusion risk and commercial risk.

### Caveat

The evidence is still useful because narration is rich and recording quality is
good, but the case should still be framed as Layer 3 evidence from a held-out
run with `l2_coverage=0.0`.

## 2. iakhtar1__web-health-information-bupa

- Video ID: `iakhtar1__web-health-information-bupa`
- Report tier and reason: `poor` - task-blocking friction: `S1/S2 present`
- Windows / L3 findings: `76` windows, `78` findings
- Top severity: `S2`
- Dominant friction types: `F1=25`, `F2=17`, `F3=16`, `F5=9`

### Evidence

- `iakhtar1__web-health-information-bupa_w050` - `F3`, `S2`: a plan-comparison
  table could not be accessed through the screen reader because ticks, crosses,
  and yes/no coverage indicators were not exposed properly.
- `iakhtar1__web-health-information-bupa_w007` - `F3`, `S4`: participant could
  not find any editable search field through screen-reader navigation, despite
  repeated attempts and use of keyboard shortcuts.
- `iakhtar1__web-health-information-bupa_w008` - `F4`, `S4`: participant
  activated search-related controls but received no clear feedback or useful
  result, creating uncertainty about whether the interface had responded.

### Interpretation

This is the clearest accessibility case in the Bupa held-out set. The product
does not merely slow the participant down; it prevents a screen-reader user
from accessing comparison and search functions needed for decision-making. The
case is especially useful because it connects markup and interaction failures
directly to loss of functional access.

### Caveat

The session is still reportable because narration is rich and recording is
acceptable, but the recording quality is not marked good. Fine-grained claims
about every failed interaction should therefore stay close to the reported
finding text.

## 3. sharelinsonny__web-health-information-bupa

- Video ID: `sharelinsonny__web-health-information-bupa`
- Report tier and reason: `poor` - task-blocking friction: `S1/S2 present`
- Windows / L3 findings: `82` windows, `46` findings
- Top severity: `S1`
- Dominant friction types: `F1=13`, `F2=12`, `F6=10`, `F3=5`

### Evidence

- `sharelinsonny__web-health-information-bupa_w074` - `F6`, `S1`: participant
  could not find relevant service information for their location and ended up
  abandoning the task because the pathway did not match their geography.
- `sharelinsonny__web-health-information-bupa_w074` - `F2`, `S2`: participant
  was unsure whether a quote was required before making a booking and stopped
  before completing the intended journey.
- `sharelinsonny__web-health-information-bupa_w042` - `F6`, `S3`: participant
  said accessibility features were not visible or discoverable enough for older
  or less confident users.

### Interpretation

This case shows a pathway-level failure rather than a single broken page. The
participant can see pieces of relevant information, but the journey still fails
because location fit, booking prerequisites, and accessibility support are not
clear enough to sustain task completion. It is useful evidence for product risk
around service discoverability and decision confidence.

### Caveat

Recording quality is only acceptable, not good, so the strongest claims should
stay tied to the clearest task-abandonment evidence. As with all Bupa cases,
`l1_total=0` and `l2_coverage=0.0` limit cross-layer interpretation.

## 4. margieflint__web-health-information-bupa

- Video ID: `margieflint__web-health-information-bupa`
- Report tier and reason: `acceptable` - multiple medium-severity findings
- Windows / L3 findings: `72` windows, `67` findings
- Top severity: `S3`
- Dominant friction types: `F1=30`, `F2=13`, `F6=13`

### Evidence

- `margieflint__web-health-information-bupa_w007` - `F6`, `S3`: participant
  could not find the needed health information through A-Z browsing, then used
  search as a fallback, but search also failed to surface the answer.
- `margieflint__web-health-information-bupa_w009` - `F6`, `S4`: repeated
  searching still led through unrelated results, and the participant expressed
  dissatisfaction at not locating the specific condition information needed.
- `margieflint__web-health-information-bupa_w041` - `F6`, `S4`: participant
  encountered accessibility issues with interactive elements and still could
  not locate a suitable support pathway for accessibility help.

### Interpretation

This is a good contrast case because the report tier is acceptable, yet the
session still contains a large volume of recoverable comprehension and content
discovery friction. The product risk here is less about a single hard blocker
and more about cumulative failure to deliver the right information route,
especially when the participant's need is specific or accessibility-related.

### Caveat

This case should not be overstated as catastrophic failure. It is more useful
as evidence that acceptable-tier sessions can still contain dense, repeated
content-not-found and comprehension costs.

## 5. daniellepaigejones07__web-health-information-bupa

- Video ID: `daniellepaigejones07__web-health-information-bupa`
- Report tier and reason: `acceptable` - multiple medium-severity findings
- Windows / L3 findings: `78` windows, `59` findings
- Top severity: `S3`
- Dominant friction types: `F3=14`, `F1=14`, `F2=11`, `F7=11`

### Evidence

- `daniellepaigejones07__web-health-information-bupa_w008` - `F3`, `S3`:
  participant described the bright white and green colour scheme as painful to
  look at and strongly visually uncomfortable.
- `daniellepaigejones07__web-health-information-bupa_w007` - `F3`, `S3`:
  participant said the brightness made them reluctant to read further and that
  they would be more likely to close the page than continue.
- `daniellepaigejones07__web-health-information-bupa_w026` - `F3`, `S3`:
  participant reported difficulty adjusting to white text on dark blue and said
  she would probably avoid using that section because of visual strain.

### Interpretation

This case is useful because it shows accessibility discomfort that is not a
formal task blocker but still meaningfully reduces engagement. The participant
can continue, yet visual contrast and brightness create enough strain that the
interface becomes self-limiting. It supports a claim about sustained visual
access cost rather than a one-off annoyance.

### Caveat

Because the report tier is acceptable, this case should be framed as medium
severity accessibility friction, not as complete breakdown. It is strongest
when used to show repeated visual discomfort patterns across several windows.

## 6. manyi_tan__web-health-information-bupa

- Video ID: `manyi_tan__web-health-information-bupa`
- Report tier and reason: `acceptable` - acceptable recording with some
  findings
- Windows / L3 findings: `6` windows, `2` findings
- Top severity: `S5`
- Dominant friction types: `F6=2`

### Evidence

- `manyi_tan__web-health-information-bupa_w002` - `F6`, `S5`: participant had
  to move through two pages before locating the relevant Bupa recommendation,
  indicating basic findability friction.
- `manyi_tan__web-health-information-bupa_w003` - `F6`, `S5`: participant
  rejected the first search result path for tooth-health information and had to
  reformulate the query around `orthodontics`.

### Interpretation

This is not a major product-conclusion case. Its value is as an evidence-limit
example showing how a short session can still surface mild findability issues
without supporting broader claims about the overall product experience.

### Caveat

This case has the clearest sample-size limitation in the selected set: only `6`
windows and `2` findings, with narration marked `adequate` and recording only
`acceptable`. It should be used only as a low-confidence caveat case.
