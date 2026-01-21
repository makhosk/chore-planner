import json
from datetime import date, timedelta

# -----------------------
# Load chores from file
# -----------------------
with open("chores.json", "r") as file:
    chores = json.load(file)

# Convert saved date strings back to date objects
for chore in chores.values():
    if chore["last_done"] is not None:
        chore["last_done"] = date.fromisoformat(chore["last_done"])

today = date.today()

# -----------------------
# Determine chores due today
# -----------------------
available_chores = []

for chore, info in chores.items():
    last_done = info["last_done"]
    frequency = info["frequency"]

    if last_done is None:
        available_chores.append(chore)
    else:
        days_since = (today - last_done).days
        if days_since >= frequency:
            available_chores.append(chore)

# -----------------------
# Ask what was done today
# -----------------------
print("What chores are due today?\n")

if not available_chores:
    print("🎉 All chores are done for today!")
else:
    for index, chore in enumerate(available_chores, start=1):
        print(f"{index}. {chore}")

    choice = input("\nEnter the number of the chore you completed (or press Enter to skip): ")

    if choice:
        choice = int(choice)
        chore_name = available_chores[choice - 1]
        chores[chore_name]["last_done"] = today
        print(f"\n{chore_name} marked as done today!")

# -----------------------
# Show chores due today (summary)
# -----------------------
print("\nChores due today:")

any_due = False

for chore, info in chores.items():
    last_done = info["last_done"]
    frequency = info["frequency"]

    if last_done is None:
        print(f"- {chore}")
        any_due = True
    else:
        days_since = (today - last_done).days
        if days_since >= frequency:
            print(f"- {chore}")
            any_due = True

if not any_due:
    print("None 🎉")

# -----------------------
# Weekly overview
# -----------------------
print("\nWeekly overview (next 7 days):")

end_of_week = today + timedelta(days=7)
weekly_items = []

for chore, info in chores.items():
    last_done = info["last_done"]
    frequency = info["frequency"]

    if last_done is None:
        due_date = today
    else:
        due_date = last_done + timedelta(days=frequency)

    if today <= due_date <= end_of_week:
        weekly_items.append((chore, due_date))

if not weekly_items:
    print("🎉 No chores coming up this week!")
else:
    weekly_items.sort(key=lambda x: x[1])

    for chore, due_date in weekly_items:
        day_name = due_date.strftime("%A")
        print(f"{day_name}: {chore}")

# -----------------------
# Save chores back to file
# -----------------------
with open("chores.json", "w") as file:
    json.dump(chores, file, default=str, indent=2)
