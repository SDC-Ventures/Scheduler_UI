import os
import json
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from generate_ai_action import generate_daily_plan_for_date

app = Flask(__name__)
PLANS_DIR = "plans"
os.makedirs(PLANS_DIR, exist_ok=True)

ACTION_TYPES = ["create_comment", "reply_comment", "like_post",
                "post_post", "post_story", "like_comment"]

def get_plan_path(date_str):
    return os.path.join(PLANS_DIR, f"daily_plan_{date_str}.json")

def load_plan_for_date(date_str):
    """Load actions for a given date without changing their executed status."""
    path = get_plan_path(date_str)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

def save_plan_for_date(date_str, actions):
    with open(get_plan_path(date_str), "w") as f:
        json.dump(actions, f, indent=2)

def get_existing_dates():
    return sorted(
        [f[11:-5] for f in os.listdir(PLANS_DIR) if f.startswith("daily_plan_") and f.endswith(".json")]
    )

@app.route("/")
def index():
    today_str = datetime.now().strftime("%Y-%m-%d")
    return redirect(url_for("view_plan_for_date", date=today_str))

@app.route("/plan/<date>")
def view_plan_for_date(date):
    actions = load_plan_for_date(date)
    existing_dates = get_existing_dates()
    return render_template(
        "index.html",
        actions=actions,
        current_date=date,
        existing_dates=existing_dates
    )

@app.route("/generate", methods=["POST"])
def generate():
    date_str = request.form.get("selected_date")
    type_counts = {}
    for action_type in ACTION_TYPES:
        count = request.form.get(action_type, "0")
        try:
            type_counts[action_type] = int(count)
        except ValueError:
            type_counts[action_type] = 0

    generate_daily_plan_for_date(date_str, type_counts)
    return redirect(url_for("view_plan_for_date", date=date_str))

@app.route("/create")
def create():
    return render_template("create.html")

@app.route("/create", methods=["POST"])
def create_post():
    date_str = request.form["time"].split("T")[0]
    action = {
        "time": request.form["time"].replace("T", " "),
        "type": request.form["type"],
        "account": request.form["account"],
        "link": request.form["link"],
        "content": request.form["content"],
        "executed": False
    }
    actions = load_plan_for_date(date_str)
    actions.append(action)
    save_plan_for_date(date_str, actions)
    return redirect(url_for("view_plan_for_date", date=date_str))

@app.route("/edit/<date>/<int:index>")
def edit(date, index):
    actions = load_plan_for_date(date)
    action = actions[index]
    return render_template("edit.html", action=action, date=date, index=index)

@app.route("/edit/<date>/<int:index>", methods=["POST"])
def edit_post(date, index):
    actions = load_plan_for_date(date)
    actions[index] = {
        "time": request.form["time"].replace("T", " "),
        "type": request.form["type"],
        "account": request.form["account"],
        "link": request.form["link"],
        "content": request.form["content"],
        "executed": actions[index].get("executed", False)
    }
    save_plan_for_date(date, actions)
    return redirect(url_for("view_plan_for_date", date=date))

@app.route("/delete/<date>/<int:index>")
def delete(date, index):
    actions = load_plan_for_date(date)
    if 0 <= index < len(actions):
        actions.pop(index)
        save_plan_for_date(date, actions)
    return redirect(url_for("view_plan_for_date", date=date))

@app.route("/toggle/<date>/<int:index>", methods=["POST"])
def toggle_executed(date, index):
    actions = load_plan_for_date(date)
    if 0 <= index < len(actions):
        actions[index]["executed"] = not bool(actions[index].get("executed", False))
        save_plan_for_date(date, actions)
    return redirect(url_for("view_plan_for_date", date=date))

if __name__ == "__main__":
    app.run(debug=True)
