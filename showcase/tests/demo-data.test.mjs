import test from "node:test";
import assert from "node:assert/strict";
import { demoCases } from "../lib/demo-data.js";
import { containsRestrictedSchoolName } from "../lib/sanitize.js";

test("all demo cases are free of restricted school names", () => {
  for (const demoCase of demoCases) {
    assert.equal(containsRestrictedSchoolName(JSON.stringify(demoCase)), false);
  }
});

test("demo cases expose summary, findings, and recommendations", () => {
  for (const demoCase of demoCases) {
    assert.ok(demoCase.summary.title.length > 0);
    assert.ok(demoCase.findings.length > 0);
    assert.ok(demoCase.recommendations.length > 0);
  }
});
