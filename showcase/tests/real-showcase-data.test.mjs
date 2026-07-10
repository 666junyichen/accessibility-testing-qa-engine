import test from "node:test";
import assert from "node:assert/strict";
import { getShowcaseData } from "../lib/real-showcase-data.js";
import { containsRestrictedSchoolName } from "../lib/sanitize.js";

test("real showcase data loads from processed artifacts", async () => {
  const data = await getShowcaseData();

  assert.equal(data.activeCase.label, "Sharelinsonny_wa");
  assert.equal(data.activeCase.findingsCount, 40);
  assert.equal(data.activeCase.windowCount, 105);
  assert.ok(data.trajectoryData.summary.length > 0);
  assert.ok(data.cohortOverview.stats.length > 0);
});

test("public showcase data stays free of restricted school names", async () => {
  const data = await getShowcaseData();
  assert.equal(containsRestrictedSchoolName(JSON.stringify(data)), false);
});
