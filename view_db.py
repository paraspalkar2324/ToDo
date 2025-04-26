import sqlite3

conn = sqlite3.connect('planner.db')
c = conn.cursor()

# Show all tables
print("Tables:")
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    print(" -", row[0])

# Show users
print("\n Users:")
for row in c.execute("SELECT * FROM users;"):
    print(row)

# Show tasks
print("\n Tasks:")
for row in c.execute("SELECT * FROM tasks;"):
    status = "Done" if row[5] else "Not Done"
    print(row[:5], "-", status)

conn.close()

