-- Players' answers (the `guesses` table) are kept for their day only. Right after midnight Montreal time a pg_cron
-- job deletes every guess from an earlier day. The API only ever scores and tallies today's guesses (days.today()),
-- so nothing reads them once the day is over.
--
-- Not deleted: `daily_prompts` (the nightly generator reads recent sets to avoid repeats, and it stores sets two
-- days ahead) and `finishes` (the daily leaderboard).
--
-- pg_cron runs on UTC. Midnight Montreal is 05:00 UTC in winter (EST) and 04:00 UTC in summer (EDT), so the job
-- fires at 04:05 and 05:05 UTC. One of the two is 00:05 Montreal whatever the season. The other is 23:05 the night
-- before, and it's harmless: the cutoff is "today in Montreal", so it never touches the live day.
--
-- Plain Postgres (local docker, CI) has no pg_cron, so there it only prints a notice. Idempotent: cron.schedule
-- with an existing job name updates that job.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'pg_cron') THEN
        RAISE NOTICE 'pg_cron is not available here; skipping the nightly guess cleanup job';
        RETURN;
    END IF;

    CREATE EXTENSION IF NOT EXISTS pg_cron WITH SCHEMA pg_catalog;

    PERFORM cron.schedule(
        'mcgill-krillion-clear-old-guesses',
        '5 4,5 * * *',
        $job$DELETE FROM public.guesses WHERE day < to_char(now() AT TIME ZONE 'America/Toronto', 'YYYY-MM-DD')$job$
    );
END
$$;
