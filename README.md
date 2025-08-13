# 📋 Instagram Action Planner (Manual Execution)

## 1. Overview

This tool helps plan, organize, and track Instagram engagement activities — such as commenting, liking, following, and sending direct messages — according to a daily schedule.

It is designed for the marketing team to **plan in advance** and manage these actions **manually** through a simple dashboard.

---

## 2. What It Can Do

* **Daily Action Plans**

  * Generate an AI-suggested daily plan for Instagram interactions.
  * Customize the number of each action type (e.g., 3 comments, 2 DMs, etc.).
  * Manually create or edit any action.

* **Execution Tracking**

  * Each action shows its status: ⏳ *Pending* or ✔ *Executed*.
  * You can mark an action as executed **only by clicking the button** in the dashboard.

* **Organized History**

  * Easily browse previous days’ plans.
  * Edit or delete actions from any day.

---

## 3. How It Works

1. **Planning**

   * Pick a date and set how many of each action type you want.
   * The AI will fill in account names, links, and suggested content.
   * You can also add actions manually.

2. **Execution**

   * You perform the planned actions yourself.
   * When you finish an action, click **Mark as Executed** in the dashboard.

3. **Storage**

   * Every day’s plan is saved in a JSON file inside the `plans/` folder.
   * This keeps a permanent history of what was planned and executed.

---

## 4. Files & Roles

| File                    | Purpose                                                                                             |
| ----------------------- | --------------------------------------------------------------------------------------------------- |
| `app.py`                | Main Flask web app – handles routes, plan generation, manual action management, and status updates. |
| `generate_ai_action.py` | AI logic for creating the daily plan based on your input.                                           |
| `scheduler.py`          | Reserved for future scheduling features (currently unused for execution).                           |
| `templates/index.html`  | Main dashboard to view, edit, delete, and mark actions as executed.                                 |
| `templates/create.html` | Form to manually create a new action.                                                               |

---

## 5. How to Use

1. **Open the Dashboard**

   * Visit `http://127.0.0.1:5000` in your browser (after starting the app).

2. **Generate a Plan**

   * Pick a date.
   * Set the number of each action type.
   * Click **🧠 Generate Plan**.

3. **Review & Edit**

   * Use **Edit** to change details.
   * Use **Delete** to remove an action.

4. **Mark Actions as Done**

   * When you finish an action, click **Mark as Executed**.
   * There is no automatic execution — you are always in control.

---

## 6. Deployment

For setup on a fresh computer or cloud environment:

1. **Get the Code**

   * Clone the repository:

     ```bash
     git clone <repo-url>
     cd <repo-folder>
     ```
2. **Install Requirements**

   * ```bash
     pip install -r requirements.txt
     ```
3. **Run the App**

   * ```bash
     python app.py
     ```
4. **Open in Browser**

   * Go to `http://127.0.0.1:5000`.
