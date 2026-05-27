import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const showcaseRoot = path.resolve(testDir, "..");
const repoRoot = path.resolve(showcaseRoot, "..");

test("README does not mention restricted school names", () => {
  const readme = readFileSync(path.join(repoRoot, "README.md"), "utf8");
  assert.equal(/The University of Queensland|\bUQ\b/.test(readme), false);
});

test("Streamlit label map no longer exposes school short names", () => {
  const styles = readFileSync(path.join(repoRoot, "app/styles.py"), "utf8");
  assert.equal(styles.includes('"the-university-of-queensland": "UQ"'), false);
  assert.equal(styles.includes('"uq": "UQ"'), false);
});
