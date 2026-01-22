from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

CHORE_FILE = "chores.json"
NOTES_FILE = "notes.json"

# -------------------------
# Utility functions
# -------------------------

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default


def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def get_week_start(date_obj):
    return date_obj - timedelta(days=date_obj.weekday())


# -------------------------
# Load data
# -------------------------

def load_chores():
    return load_json(CHORE_FILE, {
        "Vacuum": {"frequency": 7, "last_done": None},
        "Bathrooms": {"frequency": 7, "last_done": None},
        "Laundry": {"frequency": 3, "last_done": None}
    })


def load_notes():
    return load_json(NOTES_FILE, {})


# -------------------------
# Routes
# -------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    chores = load_chores()
    notes = load_notes()
    today = datetime.today().strftime("%Y-%m-%d")

    # Handle form submission
    if request.method == "POST":
        completed = request.form.getlist("completed")
        note = request.form.get("note", "").strip()

        for chore in completed:
            if chore in chores:
                chores[chore]["last_done"] = today

        if note:
            notes[today] = note

        save_json(CHORE_FILE, chores)
        save_json(NOTES_FILE, notes)

        return redirect("/")

    # -------------------------
    # Weekly overview (upcoming)
    # -------------------------

    weekly_overview = []
    today_date = datetime.strptime(today, "%Y-%m-%d")

    for chore, data in chores.items():
        last_done = data["last_done"]
        frequency = data["frequency"]

        if last_done:
            last_date = datetime.strptime(last_done, "%Y-%m-%d")
            due_date = last_date + timedelta(days=frequency)
        else:
            due_date = today_date

        if due_date <= today_date + timedelta(days=7):
            weekly_overview.append({
                "chore": chore,
                "due": due_date.strftime("%Y-%m-%d")
            })

    # -------------------------
    # Weekly history (PAST)
    # -------------------------

    weekly_history = {}

    for chore, data in chores.items():
        if data["last_done"]:
            date_obj = datetime.strptime(data["last_done"], "%Y-%m-%d")
            week_start = get_week_start(date_obj).strftime("%Y-%m-%d")

            weekly_history.setdefault(week_start, {"chores": [], "notes": []})
            weekly_history[week_start]["chores"].append(chore)

    for date_str, note in notes.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        week_start = get_week_start(date_obj).strftime("%Y-%m-%d")

        weekly_history.setdefault(week_start, {"chores": [], "notes": []})
        weekly_history[week_start]["notes"].append(note)

    return render_template(
    "index.html",
    chores=chores,
    today=today,
    weekly=weekly_overview,  
    weekly_history=weekly_history,
    notes=notes
)


# -------------------------
# Run app
# -------------------------

if __name__ == "__main__":
    app.run()
