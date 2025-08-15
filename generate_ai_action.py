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

def generate_daily_plan_for_date(date_str, type_counts):
    """
    Create a plan file with randomized human-like times and concise, natural copy.
    - date_str: 'YYYY-MM-DD'
    - type_counts: dict like {'create_comment': 1, 'send_dm': 1, 'like_post': 1, ...}
    """
    plan_path = get_plan_path(date_str)
    if os.path.exists(plan_path):
        print(f"✅ Plan for {date_str} already exists at {plan_path}.")
        return

    print(f"🔧 Generating plan for {date_str} with type counts: {type_counts}")

    actions = []
    base_date = datetime.strptime(date_str, "%Y-%m-%d")

    # Randomize between 8:00–20:59; sample without replacement, refill if needed
    candidate_times = [(h, m) for h in range(8, 21) for m in range(0, 60)]
    random.shuffle(candidate_times)

    def next_time():
        # cycle when we run out
        nonlocal candidate_times
        if not candidate_times:
            candidate_times = [(h, m) for h in range(8, 21) for m in range(0, 60)]
            random.shuffle(candidate_times)
        return candidate_times.pop()

    for a_type, count in (type_counts or {}).items():
        # Skip invalid or zero-count entries gracefully
        if not isinstance(count, int) or count <= 0:
            continue

        for _ in range(count):
            h, m = next_time()
            tstamp = base_date + timedelta(hours=h, minutes=m)

            account = generate_account_handle("nature, photography, or travel")

            action = {
                "time": tstamp.strftime("%Y-%m-%d %H:%M:%S"),
                "type": a_type,
                "account": account,
                "link": "https://instagram.com/example",
                "executed": False
            }

            # Content only if the action type needs text
            if a_type != "like_post":
                text = generate_text_for_type(a_type).strip()
                # Put a conservative length cap as a last defense against verbosity
                if len(text) > 220:
                    text = text[:217].rstrip() + "…"
                if text:
                    action["content"] = text

            actions.append(action)

    if not actions:
        print(f"⚠️ No actions were generated for {date_str}. Plan not saved.")
        return

    with open(plan_path, "w") as f:
        json.dump(actions, f, indent=2, ensure_ascii=False)
    print(f"✅ Plan for {date_str} saved to {plan_path} with {len(actions)} actions.")
