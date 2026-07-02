# Tumelo Wellness OS — Backend API Specification

**Base URL:** `http://67.213.119.157:3000/api`
**Auth:** Bearer JWT token (issued on PIN login)
**Content-Type:** `application/json`
**Encoding:** UTF-8

---

## Authentication

### POST /api/auth/login
Log in with 4-digit PIN. Returns JWT + user profile.

**Request:**
```json
{ "pin": "1234" }
```

**Response `200`:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "name": "Tumelo Ramaphosa",
    "protein_target_g": 180,
    "carbs_target_g": 120,
    "water_target_ml": 3000,
    "calorie_target": 2400
  },
  "expiresIn": 86400
}
```

**Errors:**
- `401 { "error": "Invalid PIN" }`
- `429 { "error": "Too many attempts. Try again in 5 minutes." }` (rate limited)

---

## Meals

### POST /api/log/meal
Log a meal (with optional AI parsing).

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "meal_slot": "breakfast",
  "food_description": "3 eggs scrambled, 2 slices of toast with butter, 150ml orange juice",
  "protein_g": 27,
  "carbs_g": 35,
  "calories_est": 420,
  "photo_base64": "<optional base64 image>"
}
```

> If `protein_g` / `carbs_g` are omitted, backend runs AI parsing on `food_description`.

**Response `201`:**
```json
{
  "id": 42,
  "date": "2026-06-29",
  "meal_slot": "breakfast",
  "food_description": "3 eggs scrambled, 2 slices of toast with butter, 150ml orange juice",
  "protein_g": 27,
  "carbs_g": 35,
  "calories_est": 420,
  "photo_url": null,
  "logged_at": "2026-06-29T07:45:00"
}
```

### GET /api/meals
Get all meals for a date. Defaults to today.

**Query params:** `?date=2026-06-29`

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "meals": [
    {
      "id": 42,
      "meal_slot": "breakfast",
      "food_description": "3 eggs scrambled...",
      "protein_g": 27,
      "carbs_g": 35,
      "calories_est": 420,
      "logged_at": "2026-06-29T07:45:00"
    }
  ],
  "totals": {
    "protein_g": 142,
    "carbs_g": 89,
    "calories_est": 1840
  },
  "goals": {
    "protein_target_g": 180,
    "carbs_target_g": 120
  }
}
```

### DELETE /api/meals/:id
Delete a meal log entry.

**Response `204`:** No content.

---

## Supplements

### POST /api/log/supplement
Log a supplement or medicine taken.

**Request:**
```json
{
  "supplement_name": "KEFI",
  "dosage": "1 scoop",
  "scheduled_for": "07:00",
  "taken_on_schedule": true,
  "category": "kefi",
  "notes": ""
}
```

**Response `201`:**
```json
{
  "id": 18,
  "date": "2026-06-29",
  "supplement_name": "KEFI",
  "dosage": "1 scoop",
  "taken_at": "2026-06-29T07:05:00",
  "taken_on_schedule": 1,
  "scheduled_for": "07:00",
  "category": "kefi"
}
```

### GET /api/supplements
Get supplement log. Defaults to today.

**Query params:** `?date=2026-06-29`

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "supplements": [
    {
      "id": 18,
      "supplement_name": "KEFI",
      "dosage": "1 scoop",
      "taken_at": "2026-06-29T07:05:00",
      "taken_on_schedule": 1,
      "scheduled_for": "07:00",
      "category": "kefi"
    }
  ],
  "adherence": {
    "kefi": { "taken": 1, "scheduled": 2, "pct": 50 },
    "vitamin_d": { "taken": 1, "scheduled": 1, "pct": 100 }
  }
}
```

---

## Sleep

### POST /api/log/sleep
Log sleep data.

**Request (full):**
```json
{
  "bed_time": "23:00",
  "wake_time": "06:30",
  "duration_hours": 7.5,
  "quality_rating": 4,
  "resting_hr": 58,
  "notes": "Woke up once around 3am but fell back asleep quickly"
}
```

**Request (simple — from voice):**
```json
{
  "raw_text": "I slept 7 hours and it was really good actually",
  "duration_hours": 7,
  "quality_rating": 4
}
```

> If `raw_text` is sent without explicit values, backend parses with AI.

**Response `201`:**
```json
{
  "id": 11,
  "date": "2026-06-29",
  "bed_time": "23:00",
  "wake_time": "06:30",
  "duration_hours": 7.5,
  "quality_rating": 4,
  "resting_hr": 58,
  "logged_at": "2026-06-29T06:35:00"
}
```

### GET /api/sleep
Get sleep log. Defaults to today.

**Query params:** `?date=2026-06-29`

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "sleep": {
    "id": 11,
    "bed_time": "23:00",
    "wake_time": "06:30",
    "duration_hours": 7.5,
    "quality_rating": 4,
    "resting_hr": 58,
    "notes": "Woke up once..."
  },
  "weekly": [
    { "date": "2026-06-23", "duration_hours": 7.0, "quality_rating": 3 },
    { "date": "2026-06-24", "duration_hours": 6.5, "quality_rating": 2 },
    ...
  ]
}
```

---

## Fitness

### POST /api/log/fitness
Log a workout.

**Request (cardio):**
```json
{
  "type": "run",
  "duration_min": 45,
  "distance_km": 5.2,
  "avg_hr": 142,
  "details": { "notes": "Easy pace, felt strong" }
}
```

**Request (strength):**
```json
{
  "type": "gym",
  "duration_min": 60,
  "details": {
    "muscle_groups": ["chest", "triceps"],
    "exercises": [
      { "name": "Bench Press", "sets": 4, "reps": 5, "weight_kg": 80 },
      { "name": "Incline DB Press", "sets": 3, "reps": 10, "weight_kg": 30 },
      { "name": "Tricep Pushdown", "sets": 3, "reps": 12, "weight_kg": 25 }
    ]
  }
}
```

**Request (from voice):**
```json
{
  "raw_text": "Did a 45 minute run this morning, felt pretty good",
  "type": "run"
}
```

**Response `201`:**
```json
{
  "id": 7,
  "date": "2026-06-29",
  "type": "run",
  "duration_min": 45,
  "distance_km": 5.2,
  "avg_hr": 142,
  "calories_burned": 420,
  "details": "{...}",
  "logged_at": "2026-06-29T07:30:00"
}
```

### GET /api/fitness
Get fitness logs. Defaults to today.

**Query params:** `?date=2026-06-29&week=true`

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "logs": [...],
  "weekly_summary": {
    "total_days": 4,
    "total_minutes": 210,
    "total_volume_kg": 12800,
    "types": { "gym": 2, "run": 2 }
  }
}
```

---

## Journal

### POST /api/log/journal
Save a voice dump or reflection.

**Request:**
```json
{
  "entry_type": "morning",
  "content": "Feeling really energized this morning. Grateful for the good sleep. Main concern is the supplier meeting at 2pm...",
  "emotion_tags": ["energized", "grateful", "stressed"],
  "wellbeing_score": 7,
  "action_items": [
    "Follow up with supplier before 2pm",
    "Check in with Charlie on delivery route",
    "20 min stretching after gym"
  ]
}
```

**Response `201`:**
```json
{
  "id": 23,
  "date": "2026-06-29",
  "entry_type": "morning",
  "content": "Feeling really energized...",
  "emotion_tags": ["energized","grateful","stressed"],
  "action_items": ["Follow up with supplier...", "..."],
  "wellbeing_score": 7,
  "logged_at": "2026-06-29T06:45:00"
}
```

### GET /api/journal
Get journal entries. Defaults to today.

**Query params:** `?date=2026-06-29&type=morning`

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "entries": [
    {
      "id": 23,
      "entry_type": "morning",
      "content": "Feeling really energized...",
      "emotion_tags": ["energized","grateful"],
      "wellbeing_score": 7,
      "logged_at": "2026-06-29T06:45:00"
    }
  ]
}
```

---

## Water

### POST /api/log/water
Log a water intake.

**Request:**
```json
{ "amount_ml": 500 }
```

**Response `201`:**
```json
{ "id": 55, "date": "2026-06-29", "amount_ml": 500, "logged_at": "2026-06-29T10:00:00" }
```

### GET /api/water
Get water logs for date. Defaults to today.

**Query params:** `?date=2026-06-29`

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "logs": [
    { "id": 55, "amount_ml": 500, "logged_at": "2026-06-29T10:00:00" },
    { "id": 54, "amount_ml": 250, "logged_at": "2026-06-29T08:00:00" }
  ],
  "total_ml": 1750,
  "target_ml": 3000,
  "pct": 58
}
```

---

## Dashboard

### GET /api/dashboard/today
Full daily snapshot — all data for today.

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "day_streak": 14,
  "meals": { "meals": [...], "totals": {...}, "goals": {...} },
  "sleep": null,
  "supplements": { "supplements": [...], "adherence": {...} },
  "fitness": { "logs": [], "weekly_summary": {...} },
  "journal": { "morning": null, "evening": null },
  "water": { "total_ml": 1750, "target_ml": 3000, "pct": 58 },
  "wellness_advisor": {
    "yesterday_score": 8.2,
    "protein_yesterday": 142,
    "kefi_yesterday": true
  }
}
```

---

## Vision (Food Photo Analysis)

### POST /api/vision/analyze
Upload a food photo → AI returns structured nutrition data.

**Request:** `multipart/form-data`
- `photo`: image file (JPEG/PNG, max 5MB)
- `meal_slot`: string (breakfast/lunch/supper/snack)
- `date`: string (YYYY-MM-DD, defaults to today)

**Response `200`:**
```json
{
  "items": [
    { "description": "scrambled eggs (3 large)", "protein_g": 18, "carbs_g": 2, "calories_est": 210 },
    { "description": "whole wheat toast (2 slices)", "protein_g": 7, "carbs_g": 24, "calories_est": 160 },
    { "description": "butter (1 tbsp)", "protein_g": 0, "carbs_g": 0, "calories_est": 100 }
  ],
  "total_protein_g": 25,
  "total_carbs_g": 26,
  "total_calories_est": 470,
  "raw_description": "3 scrambled eggs, 2 slices whole wheat toast with butter",
  "confidence": 0.92
}
```

---

## Health Advisor

### GET /api/health/advisor
Get today's AI wellness morning briefing (generated fresh or cached from 6am run).

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "generated_at": "2026-06-29T06:00:00",
  "yesterday": {
    "sleep_hours": 7.5,
    "sleep_quality": 4,
    "protein_g": 142,
    "carbs_g": 89,
    "water_ml": 1750,
    "kefi_taken": true,
    "training_type": "run",
    "training_duration_min": 45,
    "wellbeing_score": 8
  },
  "briefing": {
    "recovery_status": "You're recovered. Energy score high. No red flags.",
    "protein_recommendation": "You hit 142g yesterday — solid. Today's target: 180g. Front-load at breakfast (30g+).",
    "supplement_timing": "KEFI AM: Take WITH breakfast (not empty stomach). Magnesium: Evening only.",
    "training_recommendation": "Yesterday: Run (cardio). Today: Strength — legs + shoulders. Pre-workout: 30g protein + carbs 90min before gym.",
    "priority_actions": [
      "Take KEFI with breakfast (not before)",
      "Eat 30g+ protein at breakfast within 1hr of waking",
      "Evening mobility: 15 min hip + spine stretch"
    ],
    "warnings": "Cortisol slightly elevated (journal noted stress). Add 10 min box breathing before bed."
  },
  "score": 8.2,
  "score_breakdown": {
    "sleep": 3.5,
    "nutrition": 2.5,
    "supplements": 1.0,
    "training": 0.7,
    "wellbeing": 0.5
  }
}
```

---

## Weekly Report

### GET /api/weekly-report
Full 7-day summary.

**Query params:** `?week=2026-W27` (defaults to current ISO week)

**Response `200`:**
```json
{
  "week": "2026-W27",
  "start_date": "2026-06-23",
  "end_date": "2026-06-29",
  "sleep": {
    "avg_hours": 7.1,
    "avg_quality": 3.4,
    "nights_below_6h": 1,
    "best_night": "2026-06-28"
  },
  "nutrition": {
    "avg_daily_protein_g": 158,
    "avg_daily_carbs_g": 95,
    "days_met_protein_target": 5,
    "total_meals": 21
  },
  "supplements": {
    "kefi_adherence_pct": 86,
    "missed_doses": ["2026-06-24 AM", "2026-06-27 PM"]
  },
  "fitness": {
    "training_days": 4,
    "total_minutes": 210,
    "types": { "gym": 2, "run": 1, "mobility": 1 }
  },
  "wellbeing": {
    "avg_score": 7.4,
    "trend": "stable"
  },
  "water": {
    "avg_daily_ml": 2200,
    "days_met_target": 3
  }
}
```

---

## Morning Plans

### POST /api/plans/morning
Save the 9am daily planning ritual.

**Request:**
```json
{
  "business_goals": "Finalize Q3 pricing. Review delivery route with Charlie.",
  "agent_tasks": {
    "charlie": "Optimize Tuesday delivery route. Check vehicle maintenance.",
    "naledi": "Draft next week's social media calendar. Post Instagram reel.",
    "delivery_agent": "Confirm Tuesday order slots. Update ETA estimates.",
    "robusca": "Review this week's revenue. Prepare board meeting notes."
  },
  "personal": "Gym at 6pm. 20 min stretching after.",
  "top_3": [
    "Close the supplier negotiation",
    "Send agent weekly brief",
    "Film the new product demo reel"
  ],
  "raw_text": "My plan for today is..."
}
```

**Response `201`:**
```json
{
  "id": 9,
  "date": "2026-06-29",
  "synced_to_obsidian": 1,
  "obsidian_path": "/workspace/studex-obsidian-vault/2026-06-29.md",
  "logged_at": "2026-06-29T09:05:00"
}
```

### GET /api/plans/morning
Get today's morning plan.

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "business_goals": "...",
  "agent_tasks": {...},
  "personal": "...",
  "top_3": ["...", "...", "..."],
  "synced_to_obsidian": 1
}
```

---

## Agent Board Meeting

### POST /api/agents/report
Log an agent's stand-up report.

**Request:**
```json
{
  "agent_name": "Charlie",
  "yesterday": "Optimized the Tuesday route, reduced drive time by 12%. Confirmed 3 new customer addresses.",
  "today": "Monitor Tuesday deliveries in real-time. Follow up on late customer.",
  "blockers": "Customer address on Oak Street still unresolved.",
  "midnight_build": "Added geocoding for new addresses. Pushed to production at 23:47."
}
```

**Response `201`:**
```json
{ "id": 31, "agent_name": "Charlie", "date": "2026-06-29", "logged_at": "2026-06-29T22:05:00" }
```

### GET /api/agents/board-meeting
Get all agent reports for today's board meeting.

**Response `200`:**
```json
{
  "date": "2026-06-29",
  "reports": [
    {
      "agent_name": "Robusca",
      "yesterday": "...",
      "today": "...",
      "blockers": "...",
      "midnight_build": "..."
    },
    {
      "agent_name": "Charlie",
      "yesterday": "...",
      "today": "...",
      "blockers": "...",
      "midnight_build": "..."
    }
  ]
}
```

---

## Text-to-Speech

### POST /api/tts/speak
Generate ElevenLabs audio for an agent voice.

**Request:**
```json
{
  "text": "Good morning Tumelo. Your health advisor briefing is ready. Yesterday you slept 7.5 hours, your energy is high, and today's protein target is 180 grams. Take KEFI with breakfast. Let's crush today.",
  "voice": "robusca"
}
```

**Response `200`:**
```json
{
  "audio_url": "/audio/briefing-2026-06-29.mp3",
  "duration_seconds": 12.4
}
```

---

## Error Format

All errors follow this structure:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {}  // optional extra info
}
```

| HTTP Status | Code | Meaning |
|-------------|------|---------|
| 400 | `VALIDATION_ERROR` | Missing or invalid fields |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Valid token but wrong scope |
| 404 | `NOT_FOUND` | Resource doesn't exist |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
