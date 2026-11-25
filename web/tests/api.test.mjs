import assert from "node:assert/strict";
import { test } from "node:test";
import { loadTs } from "./helpers/load-ts.mjs";

// No window under Node, so this is always the server API, never the ?test dive.
const { api } = loadTs(new URL("../app/lib/api.ts", import.meta.url));

test("a correct Dive uses one request to check and score", async (t) => {
  const calls = [];
  const result = { accepted: true, result: { valid: true, points: 30 } };
  t.mock.method(globalThis, "fetch", async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body) });
    return Response.json(result);
  });
  assert.deepEqual(await api.attempt("player-aaaa", "residences", "RVC"), result);
  assert.deepEqual(calls, [{
    url: "/api/attempt",
    body: { player_id: "player-aaaa", prompt_id: "residences", answer: "RVC" },
  }]);
});

test("a rejected Dive does not send a guess that spends the prompt", async (t) => {
  const calls = [];
  const result = { accepted: false, check: { recognized: false, correct: false, suggestion: "Royal Victoria College" } };
  t.mock.method(globalThis, "fetch", async (url) => {
    calls.push(url);
    return Response.json(result);
  });
  assert.deepEqual(await api.attempt("player-aaaa", "residences", "Vctoria"), result);
  assert.deepEqual(calls, ["/api/attempt"]);
});

test("an older backend remains playable while deployments roll out", async (t) => {
  const calls = [];
  t.mock.method(globalThis, "fetch", async (url) => {
    calls.push(url);
    if (url === "/api/attempt") return new Response(null, { status: 404 });
    if (url === "/api/check") return Response.json({ recognized: true, correct: true, suggestion: null });
    return Response.json({ valid: true, points: 10 });
  });
  assert.deepEqual(await api.attempt("player-aaaa", "residences", "RVC"), {
    accepted: true, result: { valid: true, points: 10 },
  });
  assert.deepEqual(calls, ["/api/attempt", "/api/check", "/api/guess"]);
});

test("server errors do not trigger a second submission", async (t) => {
  const calls = [];
  t.mock.method(globalThis, "fetch", async (url) => {
    calls.push(url);
    return new Response(null, { status: 500 });
  });
  await assert.rejects(api.attempt("player-aaaa", "residences", "RVC"), /attempt failed \(500\)/);
  assert.deepEqual(calls, ["/api/attempt"]);
});
