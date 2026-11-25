/**
 * Test dive: open the site with `?test` (e.g. http://localhost:3000/?test) to play every prompt in the
 * McGill prompt bank against hardcoded answers, with no backend at all. Dev builds only, unless a deploy
 * opts in with NEXT_PUBLIC_TEST_DIVE=1, since the answer key gives the day's answers away.
 */
export const TEST_MODE =
  typeof window !== "undefined" &&
  (process.env.NODE_ENV === "development" || process.env.NEXT_PUBLIC_TEST_DIVE === "1") &&
  new URLSearchParams(window.location.search).has("test");
