from flask import Flask, render_template, request, redirect
from datetime import date, datetime, timedelta
import json
import os

app = Flask(__name__)

CHORES_FILE = "chores.json"
NOTES_FILE = "notes.json"


def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default


def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    today = date.today()
    today_str = today.isoformat()
    start_of_week = today - timedelta(days=today.weekday())

    chores_data = load_json(CHORES_FILE, {})
    notes_data = load_json(NOTES_FILE, {})

    # ---------------- SAVE TODAY ----------------
    if request.method == "POST":
        completed = request.form.getlist("chore")
        notes = request.form.get("notes", "")

        for chore in completed:
            if chore in chores_data:
                chores_data[chore]["last_done"] = today_str

        if notes.strip():
            notes_data[today_str] = notes

        save_json(CHORES_FILE, chores_data)
        save_json(NOTES_FILE, notes_data)

        return redirect("/")

    # ---------------- CHORES DUE TODAY ----------------
    chores = []
    weekly_overview = []

    for chore, data in chores_data.items():
        freq = data.get("frequency", 7)
        last_done = data.get("last_done")

        if last_done:
            last_date = datetime.strptime(last_done, "%Y-%m-%d").date()
        else:
            last_date = None

        due_date = last_date + timedelta(days=freq) if last_date else today

        if due_date <= today:
            chores.append(chore)
        elif due_date <= start_of_week + timedelta(days=6):
            weekly_overview.append((chore, due_date))

    weekly_overview.sort(key=lambda x: x[1])

    # ---------------- WEEKLY HISTORY ----------------
    weekly_history = {}

    # Chore history
    for chore, data in chores_data.items():
        last_done = data.get("last_done")
        if not last_done:
            continue

        done_date = datetime.strptime(last_done, "%Y-%m-%d").date()
        week_start = done_date - timedelta(days=done_date.weekday())

        if week_start >= start_of_week:
            continue

        key = week_start.isoformat()
        weekly_history.setdefault(key, {"chores": [], "notes": []})
        weekly_history[key]["chores"].append(chore)

    # Notes history
    for note_date, note_text in notes_data.items():
        note_day = datetime.strptime(note_date, "%Y-%m-%d").date()
        week_start = note_day - timedelta(days=note_day.weekday())

        if week_start >= start_of_week:
            continue

        key = week_start.isoformat()
        weekly_history.setdefault(key, {"chores": [], "notes": []})
        weekly_history[key]["notes"].append(note_text)

    notes = notes_data.get(today_str, "")

    return render_template(
        "index.html",
        chores=chores,
        today=today,
        weekly=weekly_overview,
        weekly_history=weekly_history,
        notes=notes
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
