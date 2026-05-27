import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const showcaseRoot = path.resolve(testDir, "..");

test("showcase workspace files exist", () => {
  for (const rel of [
    "package.json",
    "tsconfig.json",
    "next.config.ts",
    "next-env.d.ts",
  ]) {
    assert.equal(fs.existsSync(path.join(showcaseRoot, rel)), true, `${rel} missing`);
  }
});
