import os
import json
import random
from datetime import datetime, timedelta
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PLANS_DIR = "plans"
os.makedirs(PLANS_DIR, exist_ok=True)

def get_plan_path(date_str):
    return os.path.join(PLANS_DIR, f"daily_plan_{date_str}.json")

# ---------- Small, reusable style “voice” ----------
STYLE_SYSTEM = (
    "You write brief, human-sounding Instagram text. "
    "Keep it natural, friendly, specific, and conversational. "
    "Avoid clichés, generic praise, and corporate tone. "
    "Prefer 1–2 sentences. Use at most one emoji, only if helpful. "
    "Do not use hashtags unless explicitly asked."
)

# A couple of tiny few-shot examples to reduce “AI-ish” feel
FEW_SHOT = [
    # Comment
    ("user", "Write a short, natural Instagram comment about a calm forest photo."),
    ("assistant", "That light through the trees is unreal—feels like the air is standing still."),
    # DM
    ("user", "Write a brief, friendly DM asking to connect about travel photography."),
    ("assistant", "Hey! I love your travel shots—mind if we swap a few tips about locations and lenses sometime?"),
]

# Per-type prompt templates (concise + grounded)
PROMPTS = {
    "create_comment": (
        "Write a short, natural Instagram comment about their latest post. "
        "Be specific (1 detail you might notice). Friendly, 1 sentence. "
        "At most one emoji."
    ),
    "reply_comment": (
        "Write a brief, warm reply to someone's comment. "
        "Acknowledge what they said and add one small thought. "
        "Keep it to 1 sentence, casual tone."
    ),
    "send_dm": (
        "Write a short, friendly Instagram DM to start a conversation. "
        "State why you're reaching out in one sentence (specific, not generic). "
        "Then ask one simple question. Max 2 sentences, no hashtags, at most one emoji."
    ),
    "reply_dm": (
        "Write a brief DM reply. Thank them in a natural way and answer in one sentence. "
        "If helpful, ask one small follow-up. Max 2 sentences."
    ),
    "view_story": (
        "Write a very short reaction line you might note after viewing their story. "
        "1 sentence, specific and human, no hashtags."
    ),
    # like_post has no content (we'll skip below)
}

def generate_chat(messages, temperature=0.7):
    # Compose with a system style + tiny few-shot for more human outputs
    chat_messages = [{"role": "system", "content": STYLE_SYSTEM}]
    for role, content in FEW_SHOT:
        chat_messages.append({"role": role, "content": content})
    chat_messages.extend(messages)

    resp = client.chat.completions.create(
        model="gpt-4",
        temperature=temperature,
        messages=chat_messages,
    )
    content = resp.choices[0].message.content.strip()
    if not content:
        raise ValueError("Empty model response")
    return content

def generate_account_handle(topic_hint="nature or travel"):
    try:
        return generate_chat(
            [{"role": "user",
              "content": (
                  f"Suggest a plausible Instagram handle related to {topic_hint}. "
                  "Return only the handle starting with @, no extra text."
              )}],
            temperature=0.6
        )
    except Exception as e:
        print(f"⚠️ Account handle generation failed: {e}")
        return "@example_account"

def generate_text_for_type(action_type: str) -> str:
    """Build a concise, natural text for supported action types."""
    if action_type not in PROMPTS:
        # default guard for any new action type
        base = "Write a short, natural line for this Instagram interaction. Keep it human and specific."
        prompt = base
    else:
        prompt = PROMPTS[action_type]

    try:
        return generate_chat([{"role": "user", "content": prompt}], temperature=0.7)
    except Exception as e:
        print(f"⚠️ Text generation error for {action_type}: {e}")
        return ""

def randomized_times(count, start_hour=9, end_hour=21, min_gap_min=20, max_gap_min=180):
    """
    Return a list of (hour, minute) tuples spread somewhat human-like within the window.
    """
    slots = []
    current_minutes = start_hour * 60 + random.randint(0, 30)
    end_minutes = end_hour * 60

    for _ in range(count):
        # record the current slot
        h, m = divmod(current_minutes, 60)
        slots.append((h, m))

        # advance by a random gap
        current_minutes += random.randint(min_gap_min, max_gap_min)
        if current_minutes > end_minutes:
            break

    # If we produced fewer than requested, jitter forward a bit until we reach count
    while len(slots) < count and slots:
        h, m = slots[-1]
        m += random.randint(7, 20)
        if m >= 60:
            h += 1
            m -= 60
        # clamp to end of window if we overflow
        if h * 60 + m > end_minutes:
            h, m = divmod(end_minutes, 60)
        slots.append((h, m))

    return slots[:count]

def generate_daily_plan_for_date(date_str, type_counts):
    """
    Create a plan file with randomized human-like times and concise, natural copy.
    - date_str: 'YYYY-MM-DD'
    - type_counts: dict like {'create_comment': 1, 'reply_comment': 1, 'like_post': 1,
                              'post_post': 1, 'post_story': 1, 'like_comment': 1}
    """
    plan_path = get_plan_path(date_str)
    if os.path.exists(plan_path):
        print(f"✅ Plan for {date_str} already exists at {plan_path}.")
        return

    print(f"🔧 Generating plan for {date_str} with type counts: {type_counts}")

    actions = []
    base_date = datetime.strptime(date_str, "%Y-%m-%d")

    def times_for_type(a_type, count):
        if not isinstance(count, int) or count <= 0:
            return []
        # Constrain post_post to 6–9 PM
        if a_type == "post_post":
            return randomized_times(count, start_hour=18, end_hour=21, min_gap_min=15, max_gap_min=90)
        # Others use the default window (e.g., 09:00–21:00 inside randomized_times)
        return randomized_times(count)

    for a_type, count in (type_counts or {}).items():
        if not isinstance(count, int) or count <= 0:
            continue

        for h, m in times_for_type(a_type, count):
            # Randomize seconds so we don't get :00 every time
            sec = random.randint(5, 55)
            tstamp = base_date + timedelta(hours=h, minutes=m, seconds=sec)

            account = generate_account_handle("nature, photography, or travel")
            action = {
                "time": tstamp.strftime("%Y-%m-%d %H:%M:%S"),
                "type": a_type,
                "account": account,
                "link": "https://instagram.com/example",
                "executed": False
            }

            # Only generate text for types that need it
            if a_type not in {"like_post", "like_comment"}:
                text = generate_text_for_type(a_type).strip()
                if len(text) > 220:
                    text = text[:217].rstrip() + "…"
                if text:
                    action["content"] = text

            actions.append(action)

    # Keep the list chronological
    actions.sort(key=lambda a: a["time"])

    if not actions:
        print(f"⚠️ No actions were generated for {date_str}. Plan not saved.")
        return

    # Atomic write to avoid JSON corruption
    tmp_path = plan_path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(actions, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, plan_path)
    print(f"✅ Plan for {date_str} saved to {plan_path} with {len(actions)} actions.")
