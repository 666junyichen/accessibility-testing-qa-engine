import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const showcaseRoot = path.resolve(testDir, "..");

test("landing page includes hero and demo sections", () => {
  const page = readFileSync(path.join(showcaseRoot, "app/page.tsx"), "utf8");
  const clientPage = readFileSync(path.join(showcaseRoot, "app/showcase-page-client.tsx"), "utf8");
  assert.match(page, /ShowcasePageClient/);
  assert.match(clientPage, /Overview/);
  assert.match(clientPage, /Findings/);
  assert.match(clientPage, /Coaching/);
  assert.match(clientPage, /Layer detail/);
  assert.match(clientPage, /tester-trajectory/);
  assert.match(clientPage, /cohort-overview/);
  assert.match(clientPage, /showcase-language/);
  assert.match(clientPage, /中文/);
});
