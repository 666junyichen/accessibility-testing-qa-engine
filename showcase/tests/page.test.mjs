import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const showcaseRoot = path.resolve(testDir, "..");

test("landing page includes hero and demo sections", () => {
  const page = readFileSync(path.join(showcaseRoot, "app/page.tsx"), "utf8");
  assert.match(page, /Single Video Review/);
  assert.match(page, /Tester Trajectory/);
  assert.match(page, /Cohort Overview/);
  assert.match(page, /What I Completed/);
});
