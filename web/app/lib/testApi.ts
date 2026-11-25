import type { AnswerRow, CheckResult, Daily, FinishResult, GuessResult, Leaderboard, LocalPlay } from "./api";
import { localAttempt } from "./localPlay";
import { TEST_DAILY } from "./testDive";

/**
 * Stands in for the server in test mode (see testMode.ts). Answers are scored from the hardcoded
 * test dive with the same local matcher real games use; nothing is sent anywhere.
 */
const played = new Map<string, GuessResult>();

function playOf(promptId: string): LocalPlay {
  const play = TEST_DAILY.prompts.find((p) => p.id === promptId)?.play;
  if (!play) throw new Error(`test dive has no prompt ${promptId}`);
  return play;
}

function scored(promptId: string, answer: string): GuessResult {
  const out = localAttempt(playOf(promptId), answer, true);
  if (!out.accepted) throw new Error("a forced attempt is always scored");
  return out.result;
}

const score = () => [...played.values()].reduce((sum, r) => sum + r.points, 0);

export const testApi = {
  /** Every load is a fresh run: refresh the page to start the test dive over. */
  daily: async (): Promise<Daily> => {
    localStorage.removeItem(`rb:dive:${TEST_DAILY.day}`);
    played.clear();
    return structuredClone(TEST_DAILY);
  },
  check: async (promptId: string, answer: string): Promise<CheckResult> => {
    const out = localAttempt(playOf(promptId), answer);
    return out.accepted ? { recognized: true, correct: true, suggestion: null } : out.check;
  },
  guess: async (_player: string, promptId: string, answer: string): Promise<GuessResult> => {
    const result = scored(promptId, answer);
    played.set(promptId, result);
    return result;
  },
  attempt: async (_player: string, promptId: string, answer: string) => localAttempt(playOf(promptId), answer),
  answers: async (_player: string, promptId: string): Promise<AnswerRow[]> => {
    const yours = played.get(promptId)?.answer;
    return playOf(promptId)
      .answers.map((a) => ({
        answer: a.names[0], pct: a.share_pct, points: a.points, rarity: a.rarity, golden: a.golden, yours: a.names[0] === yours,
      }))
      .sort((a, b) => b.pct - a.pct);
  },
  finish: async (): Promise<FinishResult> => ({ score: score(), percentile: 100, players: 1 }),
  leaderboard: async (): Promise<Leaderboard> => ({ players: [{ nickname: "Test Diver", score: score() }] }),
  devReset: async () => ({ ok: true }),
};
