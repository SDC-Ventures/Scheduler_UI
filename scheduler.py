import os
import json
import time
from datetime import datetime

PLAN_DIR = "plans"
EXECUTED_LOG = "executed_actions.json"

os.makedirs(PLAN_DIR, exist_ok=True)

def get_today_plan_path():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(PLAN_DIR, f"daily_plan_{today}.json")

def load_today_actions():
    path = get_today_plan_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f), path
    return [], path

def save_today_actions(actions, path):
    with open(path, "w") as f:
        json.dump(actions, f, indent=2)

def log_executed_action(action):
    log = []
    if os.path.exists(EXECUTED_LOG):
        with open(EXECUTED_LOG, "r") as f:
            log = json.load(f)
    log.append(action)
    with open(EXECUTED_LOG, "w") as f:
        json.dump(log, f, indent=2)

def should_execute(action_time):
    now = datetime.now()
    action_dt = datetime.strptime(action_time, "%Y-%m-%d %H:%M:%S")
    return now >= action_dt

def scheduler_loop():
    while True:
        actions, path = load_today_actions()
        updated = False
        for action in actions:
            if not action.get("executed", False) and should_execute(action["time"]):
                print(f"⚙ Executing: {action}")
                action["executed"] = True
                log_executed_action(action)
                updated = True
        if updated:
            save_today_actions(actions, path)
        time.sleep(60)  # Wait 1 minute between checks

if __name__ == "__main__":
    scheduler_loop()
