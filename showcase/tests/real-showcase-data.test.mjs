import test from "node:test";
import assert from "node:assert/strict";
import { getShowcaseData } from "../lib/real-showcase-data.js";
import { containsRestrictedSchoolName } from "../lib/sanitize.js";

test("real showcase data loads from processed artifacts", async () => {
  const data = await getShowcaseData();

  assert.equal(data.totalVideos, 55);
  assert.ok(data.videos.length >= 55);
  assert.ok(data.testers.length > 0);
  assert.ok(data.cohortOverview.stats.length > 0);
  assert.ok(data.videos[0].label.length > 0);
});

test("public showcase data stays free of restricted school names", async () => {
  const data = await getShowcaseData();
  assert.equal(containsRestrictedSchoolName(JSON.stringify(data)), false);
});
