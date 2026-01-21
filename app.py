from flask import Flask, render_template, redirect, url_for, request
import json
from datetime import date, timedelta

app = Flask(__name__)

# -----------------------
# Load & save chores
# -----------------------
def load_chores():
    with open("chores.json", "r") as file:
        chores = json.load(file)

    for chore in chores.values():
        if chore["last_done"] is not None:
            chore["last_done"] = date.fromisoformat(chore["last_done"])

    return chores

def save_chores(chores):
    with open("chores.json", "w") as file:
        json.dump(chores, file, default=str, indent=2)

# -----------------------
# Load & save notes
# -----------------------
def load_notes():
    with open("notes.json", "r") as file:
        return json.load(file)

def save_notes(notes):
    with open("notes.json", "w") as file:
        json.dump(notes, file, indent=2)

# -----------------------
# Chore logic
# -----------------------
def chores_due_today(chores):
    today = date.today()
    due = []

    for name, info in chores.items():
        last_done = info["last_done"]
        freq = info["frequency"]

        if last_done is None or (today - last_done).days >= freq:
            due.append(name)

    return due

def weekly_overview(chores):
    today = date.today()
    end_of_week = today + timedelta(days=7)
    upcoming = []

    for name, info in chores.items():
        last_done = info["last_done"]
        freq = info["frequency"]

        if last_done is None:
            due_date = today
        else:
            due_date = last_done + timedelta(days=freq)

        if today <= due_date <= end_of_week:
            upcoming.append((name, due_date))

    upcoming.sort(key=lambda x: x[1])
    return upcoming

# -----------------------
# Routes
# -----------------------
@app.route("/", methods=["GET", "POST"])
def index():
    chores = load_chores()
    notes = load_notes()
    today_str = str(date.today())

    # Handle form submission
    if request.method == "POST":
        completed = request.form.getlist("chore")
        for chore in completed:
            chores[chore]["last_done"] = date.today()

        notes[today_str] = request.form.get("notes", "")
        save_chores(chores)
        save_notes(notes)

        return redirect(url_for("index"))

    due_today = chores_due_today(chores)
    weekly = weekly_overview(chores)
    today_notes = notes.get(today_str, "")

    return render_template(
        "index.html",
        chores=due_today,
        weekly=weekly,
        notes=today_notes
    )

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)

