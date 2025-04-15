import sys
import subprocess
import importlib.util
import platform

def install_and_import(package, import_name=None, pip_name=None):
    """
    Prüft, ob ein Paket installiert ist, und installiert es ggf. per pip.
    - package: Name für importlib/util (z.B. 'stringcolor')
    - import_name: Name für import (z.B. 'stringcolor')
    - pip_name: Name für pip (z.B. 'windows-curses')
    """
    if import_name is None:
        import_name = package
    if pip_name is None:
        pip_name = package
    if importlib.util.find_spec(import_name) is None:
        print(f"Installing missing package: {pip_name} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
    else:
        print(f"Package '{pip_name}' already installed.")

# --- Dependencies prüfen und ggf. installieren ---
install_and_import("stringcolor")
if platform.system() == "Windows":
    install_and_import("curses", import_name="curses", pip_name="windows-curses")

# --- Jetzt die Imports ---
import os
import datetime
import json
import random
import stringcolor
import curses

# =========================
# Hilfsfunktionen
# =========================

def read_users(file_path):
    with open(file_path, 'r') as file:
        users = json.load(file)
    return users

def write_users(file_path, users):
    with open(file_path, 'w') as file:
        json.dump(users, file, indent=4)

def create_user_json(user_id):
    data = {
        "user_id": user_id,
        "notes": {}
    }
    os.makedirs("./JSON", exist_ok=True)
    with open(f"./JSON/{user_id}.json", "w") as file:
        json.dump(data, file, indent=4)

def delete_user_json(user_id):
    try:
        os.remove(f"./JSON/{user_id}.json")
        print(f"User {user_id}.json file deleted successfully.")
    except FileNotFoundError:
        print(f"User {user_id}.json file not found.")

def create_note_json(user_id, note_id, note_content, note_private):
    note_data = {
        "note_content": note_content,
        "note_private": note_private
    }
    with open(f"./JSON/{user_id}.json", "r") as file:
        data = json.load(file)
    data["notes"][note_id] = note_data
    with open(f"./JSON/{user_id}.json", "w") as file:
        json.dump(data, file, indent=4)

def print_user_notes(user_id):
    with open(f"./JSON/{user_id}.json", "r") as file:
        data = json.load(file)
        notes = data["notes"]
    print(f"{user_id} has notes:")
    for note_id, note_data in notes.items():
        print(f"Note ID: {note_id} Content: {note_data['note_content']}")

# =========================
# Cursor-Menü Funktion
# =========================

def cursor_menu(options, title="--- Menu ---"):
    def inner(stdscr):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        current_row = 0
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, title)
            for idx, row in enumerate(options):
                x = 2
                y = idx + 2
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, row)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x, row)
            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options) - 1:
                current_row += 1
            elif key in [curses.KEY_ENTER, ord('\n')]:
                return current_row
    return curses.wrapper(inner)

# =========================
# Hauptprogramm
# =========================

menu_options = [
    "Add/Edit User",
    "Delete User",
    "Create Note",
    "Edit User Notes",
    "Exit"
]

# Sicherstellen, dass die User-Datenbank existiert
os.makedirs("./JSON", exist_ok=True)
if not os.path.exists('./JSON/stinky.json'):
    with open('./JSON/stinky.json', 'w') as f:
        json.dump({}, f)

users = read_users('./JSON/stinky.json') # main dictionary with all users

while True:
    choice_idx = cursor_menu(menu_options)
    choice = str(choice_idx + 1) if choice_idx < 4 else "0"

    if choice == "1":
        print("You selected: Add/Edit User")
        user_id = input("Add user ID: ")
        if user_id in users:
            print(f"User {user_id} already exists. You can change Full+name and Password.")
            fullname = input("Change Full Name: ")
            password = input("Change Password: ")
        else:          
            fullname = input("Add Full Name: ")
            password = input("Add Password: ")
        users[user_id] = {
            "fullname": fullname,
            "password": password
        }
        write_users('./JSON/stinky.json', users)
        create_user_json(user_id)
        print(f"User {user_id} added successfully.")
    elif choice == "2":
        print("You selected: Delete User")
        user_id = input("Enter user ID to delete: ")
        if user_id in users:
            delete_user_json(user_id)
            users.pop(user_id)
            write_users('./JSON/stinky.json', users)
            print(f"User {user_id} deleted successfully.")
        else:
            print(f"User {user_id} not found.")
    elif choice == "3":
        print("You selected: Create Note")
        user_id = input("Log in to create a note for: ")
        password = input("Enter password: ")
        if user_id in users and password == users[user_id]["password"]:
            print("Logged in successfully.")
            note_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            note_content = input("Enter note content: ")
            note_private = input("Is this note private? (yes/no): ").lower()
            if note_private in ("yes", "y"):
                note_private = True
            elif note_private in ("no", "n"):
                note_private = False
            else:
                print("Invalid input. Defaulting to public.")
                note_private = True
            create_note_json(user_id, note_id, note_content, note_private)
        else:
            print("Incorrect user or password.")
            continue
    elif choice == "4":
        print("You selected: Edit Notes")
        user_id = input("Log in to edit notes for: ")
        password = input("Enter password: ")
        if user_id in users and password == users[user_id]["password"]:
            print("Logged in successfully.")
            print_user_notes(user_id)
            # Hier kannst du weitere Editierfunktionen einbauen
        else:
            print("Incorrect user or password.")
            continue
    elif choice == "0":
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid option. Please try again.")

print(users)
