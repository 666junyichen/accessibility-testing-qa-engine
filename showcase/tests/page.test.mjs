import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const showcaseRoot = path.resolve(testDir, "..");

test("landing page includes hero and demo sections", () => {
  const page = readFileSync(path.join(showcaseRoot, "app/page.tsx"), "utf8");
  assert.match(page, /SMP Demo/);
  assert.match(page, /Intelligent Tester Quality Assessment/);
  assert.match(page, /Overview/);
  assert.match(page, /Findings/);
  assert.match(page, /Coaching/);
  assert.match(page, /Layer detail/);
  assert.match(page, /tester-trajectory/);
  assert.match(page, /cohort-overview/);
});
