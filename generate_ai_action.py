import os
import json
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PLANS_DIR = "plans"
os.makedirs(PLANS_DIR, exist_ok=True)

def get_plan_path(date_str):
    return os.path.join(PLANS_DIR, f"daily_plan_{date_str}.json")

def generate_action_text(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        if not content:
            raise ValueError("Empty GPT response.")
        return content
    except Exception as e:
        print(f"⚠️ GPT error for prompt '{prompt}': {e}")
        return "Fallback content due to error"

def generate_daily_plan_for_date(date_str, type_counts):
    plan_path = get_plan_path(date_str)

    if os.path.exists(plan_path):
        print(f"✅ Plan for {date_str} already exists at {plan_path}.")
        return

    print(f"🔧 Generating plan for {date_str} with type counts: {type_counts}")

    actions = []
    time_index = 0

    for action_type, count in type_counts.items():
        for i in range(count):
            hour = 9 + (time_index * 3) % 12  # Spread in 3-hour increments
            time_str = f"{hour:02}:00:00"
            full_time = f"{date_str} {time_str}"
            time_index += 1

            prompt = f"Generate a creative Instagram {action_type.replace('_', ' ')} message."
            content = generate_action_text(prompt)

            account_prompt = "Suggest a relevant Instagram account handle related to nature."
            account = generate_action_text(account_prompt)

            if not content or not account:
                print(f"⚠️ Skipping action due to missing content/account")
                continue

            action = {
                "time": full_time,
                "type": action_type,
                "account": account,
                "link": "https://instagram.com/example",
                "content": content,
                "executed": False
            }
            actions.append(action)

    if not actions:
        print(f"⚠️ No actions were generated for {date_str}. Plan not saved.")
        return

    with open(plan_path, "w") as f:
        json.dump(actions, f, indent=2)
    print(f"✅ Plan for {date_str} saved to {plan_path} with {len(actions)} actions.")
