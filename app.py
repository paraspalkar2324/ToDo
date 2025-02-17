import time
from pywebio import start_server
from pywebio.input import input, select
from pywebio.output import put_text, put_buttons, put_table, put_markdown, put_success, put_warning, put_error, put_processbar, set_processbar, clear

import sqlite3

# Database Setup
conn = sqlite3.connect("planner.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    time TEXT,
    note TEXT,
    done INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
conn.commit()

current_user = None  # Store logged-in user ID


def sign_up():
    global current_user
    username = input("Enter a new username:")
    password = input("Enter a new password:", type="password")
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        put_success("Account created successfully! Please log in.")
    except sqlite3.IntegrityError:
        put_error("Username already exists. Try again.")
        return sign_up()

    log_in()


def log_in():
    global current_user
    username = input("Enter your username:")
    password = input("Enter your password:", type="password")

    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        current_user = user[0]
        put_success(f"Welcome, {username}! 🎉")
        task_menu()
    else:
        put_error("Invalid credentials. Try again.")
        log_in()


def add_task():
    task = input("Enter task:")
    time = input("Enter time:")
    note = input("Enter note (optional):")

    cursor.execute("INSERT INTO tasks (user_id, task, time, note) VALUES (?, ?, ?, ?)", (current_user, task, time, note))
    conn.commit()
    put_success("Task added successfully! ✅")


def view_tasks():
    cursor.execute("SELECT id, task, time, note, done FROM tasks WHERE user_id = ?", (current_user,))
    tasks = cursor.fetchall()

    if not tasks:
        put_warning("No tasks found!")
        return

    table_data = [["ID", "Task", "Time", "Note", "Status"]]
    completed_tasks = sum(1 for t in tasks if t[4] == 1)
    total_tasks = len(tasks)
    progress = (completed_tasks / total_tasks) if total_tasks > 0 else 0  # Value between 0 and 1

    for t in tasks:
        status = "✔ Done" if t[4] else "❌ Pending"
        table_data.append([t[0], t[1], t[2], t[3], status])

    put_table(table_data)

    # Display Progress Bar
    put_text(f"Task Completion Progress: {int(progress * 100)}%")
    put_processbar("progress_bar")
    set_processbar("progress_bar", progress)  # Set progress dynamically


def mark_done():
    view_tasks()
    task_id = input("Enter Task ID to mark as done:")
    
    cursor.execute("UPDATE tasks SET done = 1 WHERE id = ? AND user_id = ?", (task_id, current_user))
    conn.commit()
    put_success("Task marked as done! ✅")


def delete_task():
    view_tasks()
    task_id = input("Enter Task ID to delete:")

    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user))
    conn.commit()
    put_success("Task deleted successfully! 🗑️")


def focus_timer():
    cursor.execute("SELECT id, task FROM tasks WHERE user_id = ? AND done = 0", (current_user,))
    tasks = cursor.fetchall()

    if not tasks:
        put_warning("No pending tasks found! Add a task first.")
        return

    task_options = {str(t[0]): t[1] for t in tasks}
    task_id = select("Select a task to focus on:", list(task_options.keys()))
    selected_task = task_options[task_id]

    duration = select("Select focus time (seconds):", [30, 60, 120, 300])

    put_markdown(f"## 🧘‍♂️ Focusing on: **{selected_task}** for {duration} seconds!")
    put_processbar("focus_progress")

    for i in range(duration):
        set_processbar("focus_progress", (i + 1) / duration)
        time.sleep(1)  # Simulating the timer countdown

    put_success(f"Great job! You focused on **{selected_task}** for {duration} seconds. 🎉")


def task_menu():
    while True:
        choice = select("Choose an action:", ["Add Task", "View Tasks", "Mark Task Done", "Delete Task", "Focus Timer", "Logout"])
        if choice == "Add Task":
            add_task()
        elif choice == "View Tasks":
            view_tasks()
        elif choice == "Mark Task Done":
            mark_done()
        elif choice == "Delete Task":
            delete_task()
        elif choice == "Focus Timer":
            focus_timer()
        elif choice == "Logout":
            put_warning("Logged out successfully!")
            break


def main():
    put_markdown("# 📝 Welcome to the Planner App!")
    choice = select("What would you like to do?", ["Sign Up", "Log In", "Exit"])

    if choice == "Sign Up":
        sign_up()
    elif choice == "Log In":
        log_in()
    else:
        put_text("Goodbye! 👋")


if __name__ == "__main__":
    start_server(main, port=8080, debug=True)

