# Instagram Action Scheduler (Local UI)

A tiny Flask app that generates a daily plan of Instagram actions (comments, likes, posts, stories, etc.) with AI-written copy where needed. It stores one plan per day as JSON and includes a simple “scheduler” loop that marks items executed when their time passes.

> **Local tool** for planning only — there is no real Instagram automation in this repo yet.

---

## Features

- **Daily plan generator** (per date) that:
  - Produces randomized, human-like times
  - Adds random **seconds** (no more `:00`)
  - Schedules **`post_post`** actions specifically between **18:00–21:00**; other types spread across the day
  - Generates concise copy via OpenAI for actions that require text
  - Saves atomically to prevent JSON corruption
- **Web UI** to:
  - Pick a date and generate a plan
  - Manually create / edit / delete actions
  - Toggle actions executed/pending
  - Browse existing dates
- **Lightweight scheduler** that marks actions as executed once their time passes (no network calls).

---

## Project Layout

```
.
├─ app.py                     # Flask app (routes, HTML views)
├─ generate_ai_action.py      # Daily plan generation + OpenAI prompts
├─ scheduler.py               # Simple loop that marks actions executed
├─ templates/
│  ├─ index.html              # Dashboard (generate, list, toggle, etc.)
│  ├─ create.html             # Create a single action
│  └─ edit.html               # Edit an action
├─ plans/
│  └─ daily_plan_YYYY-MM-DD.json   # One plan per date (created at runtime)
├─ executed_actions.json      # Log of executed actions (created at runtime)
└─ requirements.txt
```

---

## Requirements

- Python **3.9+**
- An OpenAI API key (for AI-generated copy)

Install deps:

```bash
pip install -r requirements.txt
```

Set your API key (example for macOS/Linux):

```bash
export OPENAI_API_KEY="sk-xxxx"
```

Windows (PowerShell):

```powershell
$env:OPENAI_API_KEY="sk-xxxx"
```

---

## Run

Start the web app:

```bash
python app.py
```

(Visit http://127.0.0.1:5000/)

> The app writes plan files into `./plans/` as `daily_plan_YYYY-MM-DD.json`.  
> If a plan file for that date **already exists**, generation is **skipped** (by design).

Optional: start the scheduler in another terminal:

```bash
python scheduler.py
```

The scheduler reads today’s plan every minute; when an item’s time has passed, it sets `executed: true` and appends the action to `executed_actions.json`.  
**Note:** Scheduler does not perform real Instagram actions — it only marks/logs.

---

## Action Types

**Backend keys** (what the code expects):

- `create_comment`  → shown in UI as **comment_post**
- `reply_comment`
- `like_post`       *(no AI copy)*
- `post_post`
- `post_story`
- `like_comment`    *(no AI copy)*

**UI labels/order** are handled in the templates.  
If you only rename in the UI, keep the backend keys the same (as above).

---

## Generation Rules

Implemented in `generate_ai_action.py`:

- **Time windows**
  - `post_post`: scheduled between **18:00–21:00**
  - All other types: randomized within the default window (09:00–21:00)
- **Seconds jitter**: each timestamp gets a random `:SS` between 05–55
- **Copy generation** (OpenAI) for types other than `like_post` and `like_comment`
- **Atomic save** using `os.replace` to avoid half-written JSON files
- **Chronological sorting** before writing the plan

---

## Using the UI

1. **Pick a date** and set counts per action type.
2. Click **🧠 Generate Plan**.
   - If a plan exists, the generator won’t overwrite it.
3. **Create New Action** lets you add a single item by hand.
4. In the table:
   - Click **Mark Executed** to toggle status.
   - Edit or Delete an action with the links on the right.
   - Type column uses a display map (e.g., `create_comment` → `comment_post`).

---

## File Paths

- Plans: `plans/daily_plan_YYYY-MM-DD.json`
- Executed log: `executed_actions.json`

> If you change a plan **after** running the scheduler, remember it will keep marking based on current times.

---

## Customization

- **Change time windows**  
  In `generate_ai_action.py` → `generate_daily_plan_for_date(...)`, adjust:

  ```python
  def times_for_type(a_type, count):
      if a_type == "post_post":
          return randomized_times(count, start_hour=18, end_hour=21, min_gap_min=15, max_gap_min=90)
      return randomized_times(count)  # default window
  ```

- **Tweak seconds jitter**  
  Change `sec = random.randint(5, 55)` to your preferred range.

- **UI labels/order**  
  See `templates/index.html` (display map + ordering for inputs and table).

- **Overwriting an existing plan**  
  Current behavior is “do not overwrite.” To regenerate for the same date:
  - Delete `plans/daily_plan_YYYY-MM-DD.json` and click **Generate** again, or
  - Add a `force` flag to the form and update generation code to honor it.

---

## Troubleshooting

- **Only a few items generated (e.g., 3 instead of 6):**  
  Ensure `ACTION_TYPES` in `app.py` matches the fields you use in the template. The generator only reads counts for keys in that list:
  ```python
  ACTION_TYPES = ["create_comment", "reply_comment", "like_post",
                  "post_post", "post_story", "like_comment"]
  ```
  Also generate for a **new date** or delete the existing plan file.

- **`JSONDecodeError: Extra data` while viewing a plan:**  
  A plan file was partially written (e.g., simultaneous write). We already switched to atomic saves, but if you hit this:
  1) Stop the scheduler while generating.  
  2) Delete the corrupted `plans/daily_plan_YYYY-MM-DD.json`.  
  3) Generate again.

- **`UndefinedError: 'datetime' is undefined` in a template:**  
  Jinja can’t access Python names unless passed in. Use a simple link like  
  `{{ url_for('index') }}` or pass `current_date` from the view.

- **`NameError: randomized_times is not defined`:**  
  Make sure `randomized_times(...)` exists **above** `generate_daily_plan_for_date(...)` in `generate_ai_action.py`:

  ```python
  def randomized_times(count, start_hour=9, end_hour=21, min_gap_min=20, max_gap_min=180):
      # returns a list of (hour, minute) tuples
      ...
  ```

---

## Next Steps (nice-to-have)

- Real execution: integrate `instagrapi` / Selenium to actually perform actions
- “Force regenerate” checkbox on the UI
- Export plan to CSV/Google Sheets
- Authentication for the web UI

---

## Notes

- Don’t commit your `OPENAI_API_KEY`.
- Plans and logs are local files; back them up if needed.
- This is a local utility for planning and copy-drafting — always review copy before posting.
