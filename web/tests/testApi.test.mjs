import assert from "node:assert/strict";
import { test } from "node:test";
import { loadTs } from "./helpers/load-ts.mjs";

const { testApi } = loadTs(new URL("../app/lib/testApi.ts", import.meta.url));
globalThis.localStorage ??= { removeItem() {} };

test("the test dive serves every McGill prompt with McGill zones", async () => {
  const daily = await testApi.daily();
  assert.equal(daily.zones[0].name, "Lower Field Shallows");
  assert.ok(daily.prompts.length >= 7);
  assert.ok(daily.prompts.every((p) => p.play && p.play.answers.some((a) => a.golden)));
});

test("golden answers score 100, decoys are rejected, and the reveal marks your pick", async () => {
  const daily = await testApi.daily();
  for (const p of daily.prompts) {
    const result = await testApi.guess("p", p.id, p.play.golden_answer);
    assert.equal(result.points, 100, p.id);
    assert.equal(result.golden, true, p.id);
    const decoy = await testApi.attempt("p", p.id, p.play.decoys[0]);
    assert.deepEqual(decoy, { accepted: false, check: { recognized: true, correct: false, suggestion: null } }, p.id);
    const rows = await testApi.answers("p", p.id);
    assert.deepEqual(rows.filter((r) => r.yours).map((r) => r.answer), [p.play.golden_answer], p.id);
  }
  assert.equal((await testApi.finish()).score, 100 * daily.prompts.length);
});
