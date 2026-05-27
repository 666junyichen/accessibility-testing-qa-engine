import test from "node:test";
import assert from "node:assert/strict";
import { containsRestrictedSchoolName, sanitizePublicLabel } from "../lib/sanitize.js";

test("sanitizePublicLabel removes school references", () => {
  assert.equal(
    sanitizePublicLabel("The University of Queensland Accessibility Review"),
    "Junyi Chen Accessibility Review",
  );
});

test("containsRestrictedSchoolName detects university references", () => {
  assert.equal(containsRestrictedSchoolName("Sample from UQ cohort"), true);
  assert.equal(containsRestrictedSchoolName("General accessibility workflow"), false);
});
