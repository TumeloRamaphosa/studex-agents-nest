# Tumelo Wellness OS — Frontend Specification

**Framework:** React 18 + Vite + Tailwind CSS
**Hosting:** `http://67.213.119.157:3001`
**State:** Zustand (lightweight, minimal boilerplate)
**Routing:** React Router v6
**API Client:** Axios with interceptors for JWT auth
**Voice:** Web Speech API (SpeechRecognition)
**Camera:** `navigator.mediaDevices.getUserMedia`

---

## Design Tokens (Tailwind config)

```js
// tailwind.config.js — Kanan Band dark theme
colors: {
  void:    '#0a0505',
  surface: '#120808',
  raised:  '#1e0f0f',
  red:     '#8B1A1A',
  'red-glow': '#c0392b',
  gold:    '#d4a017',
  'gold-light': '#f0c040',
  cream:   '#f5f0e8',
  'cream-dim': '#b8a89a',
  border:  '#2a1515',
}
```

---

## App Shell

### Global Layout
```
<Header>          — Logo, date, streak badge, menu toggle
<main>            — Page content (scrollable)
<VoiceButton>     — Fixed FAB bottom-right
<CameraModal>     — Camera capture modal
<BottomNav>       — Mobile nav tabs (5 icons)
```

### Routes
| Path | Component | Description |
|------|-----------|-------------|
| `/` | `Dashboard` | Main overview |
| `/nutrition` | `NutritionPage` | Full meal history |
| `/sleep` | `SleepPage` | Sleep tracking + chart |
| `/supplements` | `SupplementsPage` | KEFI + medicine log |
| `/fitness` | `FitnessPage` | Workout history + logger |
| `/journal` | `JournalPage` | Voice dumps + history |
| `/plan` | `DailyPlanPage` | 9am ritual |
| `/board` | `BoardMeetingPage` | 10pm stand-up |
| `/advisor` | `AdvisorPage` | Full health advisor view |
| `/settings` | `SettingsPage` | PIN change, goals, profile |

---

## Components

### `<Header />`
- Left: 🦁 Tumelo Wellness OS (gold text, Cormorant Garamond)
- Center: Mon 29 June 2026 · Day Streak 14 🔥
- Right: hamburger menu icon
- Background: `surface` (#120808)
- Sticky top, z-50

### `<VoiceButton />`
- Fixed bottom-right: `bottom-24 right-6`
- Size: 56px circle
- Default: gold border, void fill, mic icon
- Listening: pulsing red-glow ring animation, red fill
- States: idle → listening → processing → result
- On click: starts SpeechRecognition, streams interim results to UI
- Routes transcription to correct handler based on keywords:
  - "sleep" → SleepTracker
  - "kefi" / "took" / "supplement" → SupplementLogger
  - "gym" / "run" / "workout" / "training" → FitnessLogger
  - "ate" / "breakfast" / "lunch" / "dinner" / "supper" → MealLogger
  - "grateful" / "feeling" / "journal" → JournalVoiceDump
  - "plan" / "today i will" → DailyPlan
  - default → MealLogger

### `<BottomNav />`
- Mobile only (hidden on desktop via `md:hidden`)
- 5 tabs: Home | Nutrition | Sleep | Journal | More
- Active tab: gold icon + label
- Inactive: cream-dim

### `<SectionCard />`
- Background: `raised` (#1e0f0f)
- Border: 1px `border` (#2a1515)
- Border-radius: 12px
- Padding: 16px
- Collapsible: chevron on right header
- On expand: smooth height transition (200ms)

### `<ProgressBar />`
- Props: `value`, `max`, `label`, `unit`
- Track: `border` (#2a1515)
- Fill: gradient `red` → `gold` (dynamic by %)
- 0-50%: red fill
- 50-80%: gold fill
- 80-100%: gold-light fill with glow

---

## Pages

### `<Dashboard />`

The main landing page. Sections in a responsive grid.

**Desktop (md+):** 2-column card grid
**Mobile:** Single column, stacked cards

```
┌─────────────────────────────────────────┐
│  [Health Advisor Briefing Card — hero]  │
├───────────────────┬─────────────────────┤
│  Nutrition Mini   │  Sleep Mini         │
├───────────────────┼─────────────────────┤
│  Supplements Mini │  Fitness Mini       │
├───────────────────┴─────────────────────┤
│  [Today's Plan — if set]                │
├─────────────────────────────────────────┤
│  Today's Numbers (protein/carbs/water)  │
└─────────────────────────────────────────┘
```

#### HealthAdvisorCard (hero)
- Full-width card at top
- Background: gradient `void` → `raised`
- Left: Score badge (8.2, large gold number)
- Right: 5-point briefing text (scrollable on mobile)
- Background pattern: subtle diagonal lines (CSS)
- Voice button: "🔊 Read aloud" — triggers ElevenLabs TTS

#### NutritionMini
- Today's meals: icon + time + food summary
- Protein bar + Carbs bar (compact)
- "Log Meal" button → opens MealLogger

#### SleepMini
- Last night's sleep: hours + quality stars
- Weekly sparkline (7 days, inline)
- "Log Sleep" button → opens SleepTracker

#### SupplementsMini
- KEFI grid: today ✓✗ (AM/PM)
- Other supplements list (top 3)
- "Take KEFI" one-tap button

#### FitnessMini
- Today's workout type + duration
- Weekly training icons (Mon-Sun)
- "Log Workout" button

---

### `<NutritionPage />`

**Sections:**
1. Camera/Photo input bar
2. Voice input bar ("What did you eat?")
3. Today's meals list (by slot)
4. Daily totals card
5. Weekly bar chart (protein per day)

**`<MealLogger />` component (used here + as modal):**
- Photo capture button → CameraModal
- Voice input: large text area, listen button
- After transcription: editable parsed result shown
- Meal slot selector: Breakfast | Lunch | Supper | Snack
- Manual edit fields: protein (g), carbs (g), calories
- Save button → POST /api/log/meal

**`<CameraModal />`:**
- Full-screen modal
- Live camera preview (video element)
- Capture button (large circle)
- After capture: preview + "Analyze" button
- Loading state: spinner + "Analyzing..."
- Result: parsed nutrition card → user confirms/edits → saves

**Nutrition Chart (weekly):**
- Bar chart: 7 days
- Protein bars (gold), Carbs bars (cream-dim)
- Dashed goal lines
- Built with Chart.js or Recharts

---

### `<SleepPage />`

**Sections:**
1. Voice input ("I slept 7 hours")
2. Last night card: bed time, wake time, hours, quality
3. Quality selector: 1-5 star interactive
4. Manual time pickers
5. Weekly sleep chart (bar + quality dots)
6. Resting HR input (optional)

**`<SleepTracker />` component:**
- Bed time: time wheel picker (scrollable hour/min)
- Wake time: time wheel picker
- Duration: auto-calculated (shown between)
- Quality: tap-to-select stars (1-5)
- Voice button: "I slept X hours"
- Save → POST /api/log/sleep

**Weekly Sleep Chart:**
- X-axis: Mon–Sun
- Y-axis left: hours (0-10)
- Bar: duration
- Dot overlay: quality (1-5, scaled)
- Color coding: red <6h, gold 6-8h, green 8+h

---

### `<SupplementsPage />`

**Sections:**
1. KEFI Tracker hero (big AM/PM buttons)
2. Today's supplement timeline
3. Adherence stats (weekly %)
4. Add supplement form
5. Schedule management

**`<KEFIReminderCard />`:**
- Large: "TAKE KEFI" button (red, gold border)
- AM slot (07:00) + PM slot (19:00)
- Visual: checkmark grid, streak counter
- On tap: POST /api/log/supplement with `{ supplement_name: "KEFI" }`
- Success: confetti animation (CSS), button turns gold ✓

**`<SupplementLogger />`:**
- Name: autocomplete from known supplements
- Dosage: text field
- Time: time picker (defaults to now)
- Scheduled: toggle (for reminder system)
- Category: supplement | medicine | kefi

**Adherence View:**
- Per-supplement cards with weekly progress bars
- % taken, missed doses listed
- Color: green 80%+, gold 60-80%, red <60%

---

### `<FitnessPage />`

**Sections:**
1. Voice input ("Did a 45 minute run")
2. Today's workout card
3. Quick-log buttons: Run | Gym | Walk | Mobility
4. Exercise history (last 7 days)
5. Weekly training calendar

**`<FitnessLogger />` component:**

For **cardio** (run/walk/cycle):
- Type selector
- Duration: number input (minutes)
- Distance: number input (km, optional)
- Avg HR: number input (optional)
- Notes: textarea

For **strength** (gym):
- Muscle group: multi-select (chest, back, legs, shoulders, arms, core)
- Exercises list (add/remove):
  - Exercise name
  - Sets × Reps
  - Weight (kg)
  - [+] Add exercise button
- Total volume auto-calculated

**Training Calendar (weekly):**
- 7-day grid
- Day cell: activity icon + duration
- Rest day: dimmed
- Click: opens that day's full log

---

### `<JournalPage />`

**Sections:**
1. Morning Voice Dump button
2. Evening Reflection button
3. Today's entries
4. Wellbeing score trend (7-day line chart)
5. Emotion tags cloud
6. Full journal history

**`<JournalVoiceDump />` component:**
- Large microphone button → opens voice recorder modal
- Recording: red pulsing ring, waveform visualization (Canvas API)
- Duration: 30s minimum, 3 min max
- After recording: transcription preview
- Emotion tags: auto-detected chips (editable)
- Wellbeing slider: 1-10
- Action items: text area (one per line → parsed to array)
- Save → POST /api/log/journal

**Wellbeing Chart:**
- Line chart: 7-day trend
- Score on Y-axis (1-10)
- Dot per day, colored by score
- Goal line at 7 (dashed gold)

---

### `<DailyPlanPage />`

**9am Ritual Interface:**

```
## TODAY'S PLAN — Mon 29 June 2026

🏢 Business Goals
[textarea — voice enabled]

🤖 Agent Tasks
  Charlie:       [textarea]
  Naledi:        [textarea]
  Delivery:      [textarea]
  Robusca (You): [textarea]

💪 Personal
[textarea]

🎯 Top 3 Priorities
1. [textarea]
2. [textarea]
3. [textarea]

[Save & Sync to Obsidian]  ← Primary button
```

- Voice input per field (tap mic icon next to each)
- Save: POST /api/plans/morning
- Synced indicator: ✓ Obsidian (green check)
- "Read aloud" button: uses Robusca ElevenLabs voice

---

### `<BoardMeetingPage />`

**10pm Stand-up Interface:**

```
## Agent Board Meeting — Mon 29 June 2026
Chair: 🦁 Tumelo | ⏱ 22:00 SAST

[Start Meeting]  ← Triggers agent voice intros via ElevenLabs
```

**Agent Report Cards** (one per agent):
- Agent name + role
- Section: Yesterday (textarea)
- Section: Today (textarea)
- Section: Blockers (textarea)
- Section: Midnight Build (textarea)
- [Mark Complete] checkbox

**Timeline view:**
- Chronological: Robusca → Charlie → Naledi → Delivery → Tumelo Notes
- Each agent's card collapsible
- Completed: gold border, checkmark

**Chair Notes:**
- Textarea at bottom for Tumelo's notes during meeting
- "End Meeting" button → saves all + logs to Obsidian

---

### `<AdvisorPage />`

Full-screen health advisor view.

- Today's briefing (5 sections)
- Yesterday's data summary
- Score breakdown (donut chart)
- Supplement timing calendar
- Training recommendation
- Warnings/alerts section
- "Read aloud" (ElevenLabs voice)
- "Send to Telegram" button

---

### `<SettingsPage />`

- Change PIN (current PIN + new PIN + confirm)
- Nutrition goals: protein/carbs/water/calorie targets
- Supplement schedule manager
- Agent voice configuration
- Telegram chat ID field
- Obsidian vault path
- Export data (JSON download)
- Theme: Kanan Band (locked) — badge "Active"

---

## Shared UI Components

### `<VoiceInput />`
- Props: `onResult(text)`, `placeholder`, `alwaysOpen`
- States: idle (gold mic), listening (red pulse), processing (spinner)
- Text area below showing interim → final transcription
- Cancel button while listening

### `<TimePicker />`
- Custom scrollable wheel (mobile-first)
- Hour + minute columns
- AM/PM toggle (optional)
- 5-minute snap

### `<StarRating />`
- Props: `value`, `onChange`, `max=5`
- Gold stars (filled = selected, dim = unselected)
- Tap or drag to change

### `<ProgressRing />`
- SVG circle progress
- Used for: daily score, protein %, KEFI adherence
- Center: value + unit
- Stroke: gold gradient

### `<Toast />`
- Bottom notification: success (gold), error (red), info (cream-dim)
- Auto-dismiss: 3 seconds
- Slide up animation

---

## API Integration

### Axios Instance
```js
// src/lib/api.js
const api = axios.create({ baseURL: 'http://67.213.119.157:3000/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('studex_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.error(err => {
  if (err.response?.status === 401) {
    localStorage.removeItem('studex_token')
    window.location.href = '/login'
  }
  return Promise.reject(err)
})
```

### Zustand Store
```js
// src/stores/wellness.js
const useWellnessStore = create((set, get) => ({
  today: null,
  weeklyReport: null,
  
  fetchToday: async () => {
    const { data } = await api.get('/dashboard/today')
    set({ today: data })
  },
  
  logMeal: async (meal) => {
    const { data } = await api.post('/log/meal', meal)
    get().fetchToday()
    return data
  },
  
  logSupplement: async (supp) => {
    const { data } = await api.post('/log/supplement', supp)
    get().fetchToday()
    return data
  },
  // ...
}))
```

### Voice Integration
```js
// src/hooks/useVoice.js
export function useVoice(onResult) {
  const [listening, setListening] = useState(false)
  const recognition = useRef(null)

  const start = () => {
    const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)()
    r.continuous = false
    r.interimResults = true
    r.lang = 'en-ZA' // South African English for better local recognition
    
    r.onresult = (e) => {
      const text = Array.from(e.results)
        .map(r => r[0].transcript)
        .join('')
      onResult(text)
    }
    
    r.onend = () => setListening(false)
    r.start()
    setListening(true)
    recognition.current = r
  }

  const stop = () => {
    recognition.current?.stop()
    setListening(false)
  }

  return { start, stop, listening }
}
```

### Auth Flow
1. App loads → checks localStorage for token
2. No token → redirect to `/login`
3. Login page: 4-digit PIN pad (large buttons, mobile-first)
4. On success → store token, redirect to `/`
5. Token in Authorization header on every API call

---

## Responsive Breakpoints

| Breakpoint | Layout |
|------------|--------|
| < 640px (sm) | Single column, bottom nav, compact cards |
| 640–1024px (md) | 2-col grid, full nav |
| > 1024px (lg) | 3-col dashboard grid, sidebar nav |

---

## Performance

- Lazy load pages with `React.lazy` + `Suspense`
- Dashboard data fetched once on mount, cached in Zustand
- Optimistic UI updates for logging actions
- Image compression before upload (canvas resize to max 800px)
- Chart.js for data visualizations (tree-shakeable imports)
