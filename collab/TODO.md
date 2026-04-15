# Action Items

## This Week

### [Decision Needed] Expand Dev Samples from 6 to 8
**Status**: Waiting for Nix to approve

**Problem**: In the current 6 dev samples, `terryaflint17_suncorp` contributes 203 out of 211 Layer 1 flags (96%). The other 5 testers have very low silence ratios (<0.1) and high narration density (>0.93), making them near-uniform. If Layer 2 clustering and Layer 3 LLM classification run on these 6 samples, the results will be dominated by a single extreme case and lack generalisability.

**Proposal**: Add 1-2 "mid-sparse" testers to the dev sample set:
- `jenniferparry7_uq` — already included but relatively sparse (190 segments)
- `thanoptions` — 7 segments, very sparse (may be too extreme)
- Other candidates TBD from full dataset analysis

**Decision needed by Nix**:
- [ ] Approve expanding to 8 samples
- [ ] Confirm which testers to add
- [ ] Decide if this happens before or after Step 4 (clustering)

### [Done] CSV Artifact Verification Rule
- Added to `collab/README.md` — all preprocessing script changes now require CSV re-run + diff verification.

### [Note] Scope Creep Reporting
- R4 reminder: any deviation from task scope must be documented in commit message. See `collab/README.md` Section 1.
