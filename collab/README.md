# Collaboration Guidelines

## Commit Rules

### 1. Scope Discipline
- Each commit must only modify the files specified in the task description.
- If you need to touch files outside the task scope, you **must** document the deviation in the commit message with a clear reason (e.g., "Deviation: also updated X because Y").

### 2. CSV Artifact Verification (Mandatory)
Whenever you modify any script under `src/preprocessing/` or any other script that produces CSV output:

1. **Re-run the script** to regenerate the affected CSV(s).
2. **Verify the output** by running `git diff` on the CSV file and checking:
   - Row count changes
   - Column changes
   - Distribution shifts in key fields (e.g., flag counts, feature means)
3. **Include the verification summary** in your commit message or PR description. Example:
   ```
   Re-ran audio_features.py:
   - audio_features.csv: 871 rows (unchanged)
   - silence_ratio mean: 0.12 → 0.11
   ```

**Why**: Commit `4f91242` changed `find_video_path` and `SILENCE_ENERGY_THRESHOLD` but the CSV was not regenerated, causing downstream analysis to use stale data. Flag distribution shifted from 333 to 211 when finally re-run.

### 3. Review Checklist
Before marking any preprocessing-related PR as "ready for review":

- [ ] All affected scripts re-run successfully
- [ ] CSV outputs regenerated and committed
- [ ] `git diff` on CSV files reviewed for unexpected changes
- [ ] Row counts and key distributions noted in PR description
