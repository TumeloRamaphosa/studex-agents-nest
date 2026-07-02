-- ============================================================
-- Tumelo Wellness OS — SQLite Database Schema
-- Studex Meat · Health & Performance Tracking
-- ============================================================
-- Run with: sqlite3 /var/data/studex-wellness.db < database-schema.sql
-- Or from Node: db.exec(schema) via better-sqlite3

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- ──────────────────────────────────────────────
-- 1. USERS — Tumelo's profile
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY CHECK (id = 1),  -- single-user app
    name            TEXT    NOT NULL DEFAULT 'Tumelo Ramaphosa',
    pin_hash        TEXT    NOT NULL,                    -- bcrypt hash of 4-digit PIN
    telegram_chat_id TEXT,                               -- for notifications
    elevenlabs_api_key TEXT,                            -- encrypted, stored server-side
    voice_robusca    TEXT,                               -- ElevenLabs voice ID
    voice_charlie    TEXT,
    voice_naledi     TEXT,
    voice_delivery   TEXT,
    voice_wellness   TEXT,
    protein_target_g INTEGER DEFAULT 180,
    carbs_target_g   INTEGER DEFAULT 120,
    water_target_ml  INTEGER DEFAULT 3000,
    calorie_target   INTEGER DEFAULT 2400,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 2. DAILY_LOGS — daily health snapshot
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL UNIQUE,              -- YYYY-MM-DD
    weight_kg       REAL,
    energy_level    INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    wellbeing_score INTEGER CHECK (wellbeing_score BETWEEN 1 AND 10),
    notes           TEXT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 3. MEALS — food log entries
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meals (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             TEXT    NOT NULL,                     -- YYYY-MM-DD
    meal_slot        TEXT    NOT NULL CHECK (meal_slot IN ('breakfast','lunch','supper','snack')),
    food_description TEXT    NOT NULL,                    -- raw or parsed text
    protein_g        REAL    NOT NULL DEFAULT 0,
    carbs_g          REAL    NOT NULL DEFAULT 0,
    calories_est     INTEGER,
    water_ml         INTEGER,
    photo_url        TEXT,                                -- local path: /uploads/YYYY-MM-DD/uuid.jpg
    parsed_json      TEXT,                                -- full AI parse result as JSON string
    logged_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 4. SUPPLEMENTS — supplement & medicine log
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS supplements (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    date              TEXT    NOT NULL,                   -- YYYY-MM-DD
    supplement_name   TEXT    NOT NULL,
    dosage            TEXT,                               -- e.g. "2 capsules", "1 scoop"
    taken_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    taken_on_schedule INTEGER NOT NULL DEFAULT 1,        -- 1 = yes, 0 = skipped
    scheduled_for     TEXT,                               -- e.g. "07:00", "19:00"
    category          TEXT    NOT NULL DEFAULT 'supplement'
                        CHECK (category IN ('supplement','medicine','kefi'),
                               supplement_name = 'KEFI' AND category = 'kefi' OR supplement_name != 'KEFI'),
    notes             TEXT
);

-- ──────────────────────────────────────────────
-- 5. SLEEP_LOGS — sleep & recovery
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sleep_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL UNIQUE,              -- YYYY-MM-DD (night ending date)
    bed_time        TEXT    NOT NULL,                     -- HH:MM
    wake_time       TEXT    NOT NULL,                     -- HH:MM
    duration_hours  REAL    NOT NULL,                     -- calculated: wake - bed (handles midnight crossing)
    quality_rating  INTEGER CHECK (quality_rating BETWEEN 1 AND 5),
    resting_hr      INTEGER,
    hrv_score       INTEGER,
    notes           TEXT,
    logged_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 6. FITNESS_LOGS — training & activity
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fitness_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL,                     -- YYYY-MM-DD
    type            TEXT    NOT NULL
                        CHECK (type IN ('run','walk','cycle','swim','gym','mobility','yoga','other')),
    duration_min    INTEGER NOT NULL,
    details         TEXT,                                -- JSON string: exercises, sets, reps, weights
    distance_km     REAL,
    avg_hr          INTEGER,
    calories_burned INTEGER,
    notes           TEXT,
    logged_at       TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Example `details` JSON:
-- {
--   "muscle_groups": ["chest", "triceps"],
--   "exercises": [
--     {"name": "Bench Press", "sets": 4, "reps": 5, "weight_kg": 80},
--     {"name": "Incline DB Press", "sets": 3, "reps": 10, "weight_kg": 30}
--   ]
-- }

-- ──────────────────────────────────────────────
-- 7. JOURNAL_ENTRIES — voice dumps & reflections
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS journal_entries (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    date          TEXT    NOT NULL,                       -- YYYY-MM-DD
    entry_type    TEXT    NOT NULL
                        CHECK (entry_type IN ('morning','evening','general')),
    content       TEXT    NOT NULL,                       -- transcribed + cleaned text
    emotion_tags  TEXT,                                   -- JSON array: ["energized","grateful"]
    action_items  TEXT,                                   -- JSON array of strings
    wellbeing_score INTEGER CHECK (wellbeing_score BETWEEN 1 AND 10),
    logged_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 8. WATER_LOGS — hydration tracking
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS water_logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    date      TEXT    NOT NULL,                           -- YYYY-MM-DD
    amount_ml INTEGER NOT NULL,                           -- e.g. 250, 500, 750
    logged_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 9. DAILY_GOALS — configurable targets per day
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_goals (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             TEXT    NOT NULL UNIQUE,             -- YYYY-MM-DD
    protein_target_g INTEGER,
    carbs_target_g   INTEGER,
    water_target_ml  INTEGER,
    calorie_target   INTEGER,
    notes            TEXT
);

-- ──────────────────────────────────────────────
-- 10. AGENT_REPORTS — board meeting minutes
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,                         -- YYYY-MM-DD
    agent_name  TEXT    NOT NULL,
    yesterday   TEXT,
    today       TEXT,
    blockers    TEXT,
    midnight_build TEXT,
    logged_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 11. MORNING_PLANS — daily plan ritual entries
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS morning_plans (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL UNIQUE,                  -- YYYY-MM-DD
    business_goals TEXT,
    agent_tasks TEXT,                                     -- JSON object: { "charlie": "...", "naledi": "..." }
    personal    TEXT,
    top_3       TEXT,                                     -- JSON array of 3 strings
    raw_text    TEXT,                                     -- original voice transcription
    synced_to_obsidian INTEGER NOT NULL DEFAULT 0,        -- 1 = synced
    logged_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- 12. WELLNESS_ADVISOR_LOG — AI advisor output history
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wellness_advisor_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    date      TEXT    NOT NULL UNIQUE,                    -- YYYY-MM-DD
    input_json TEXT,                                      -- what was fed to the advisor
    output_md  TEXT    NOT NULL,                          -- markdown briefing output
    model_used TEXT,
    logged_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ──────────────────────────────────────────────
-- INDEXES — for performance on date-range queries
-- ──────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_meals_date       ON meals(date);
CREATE INDEX IF NOT EXISTS idx_meals_slot        ON meals(date, meal_slot);
CREATE INDEX IF NOT EXISTS idx_supplements_date ON supplements(date);
CREATE INDEX IF NOT EXISTS idx_sleep_date        ON sleep_logs(date);
CREATE INDEX IF NOT EXISTS idx_fitness_date      ON fitness_logs(date);
CREATE INDEX IF NOT EXISTS idx_journal_date      ON journal_entries(date);
CREATE INDEX IF NOT EXISTS idx_water_date        ON water_logs(date);
CREATE INDEX IF NOT EXISTS idx_agent_reports_date ON agent_reports(date);

-- ──────────────────────────────────────────────
-- VIEWS — common aggregated queries
-- ──────────────────────────────────────────────

-- Today's nutrition totals
CREATE VIEW IF NOT EXISTS v_today_nutrition AS
SELECT
    date,
    SUM(protein_g)     AS total_protein_g,
    SUM(carbs_g)        AS total_carbs_g,
    SUM(calories_est)   AS total_calories,
    COUNT(*)            AS meal_count
FROM meals
WHERE date = date('now', 'localtime')
GROUP BY date;

-- Today's water total
CREATE VIEW IF NOT EXISTS v_today_water AS
SELECT
    date,
    SUM(amount_ml) AS total_ml
FROM water_logs
WHERE date = date('now', 'localtime')
GROUP BY date;

-- KEFI adherence (last 7 days)
CREATE VIEW IF NOT EXISTS v_kefi_adherence AS
SELECT
    COUNT(*) AS scheduled_count,
    SUM(taken_on_schedule) AS taken_count,
    ROUND(CAST(SUM(taken_on_schedule) AS REAL) / COUNT(*) * 100, 1) AS adherence_pct
FROM supplements
WHERE supplement_name = 'KEFI'
  AND date >= date('now', '-7 days', 'localtime');

-- Weekly sleep summary
CREATE VIEW IF NOT EXISTS v_weekly_sleep AS
SELECT
    date,
    duration_hours,
    quality_rating
FROM sleep_logs
WHERE date >= date('now', '-7 days', 'localtime')
ORDER BY date ASC;

-- Weekly training summary
CREATE VIEW IF NOT EXISTS v_weekly_fitness AS
SELECT
    date,
    type,
    duration_min,
    details
FROM fitness_logs
WHERE date >= date('now', '-7 days', 'localtime')
ORDER BY date ASC;

-- ──────────────────────────────────────────────
-- TRIGGERS — auto-update updated_at
-- ──────────────────────────────────────────────
CREATE TRIGGER IF NOT EXISTS tr_users_updated
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = datetime('now') WHERE id = OLD.id;
END;
