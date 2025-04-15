import sys
import subprocess
import importlib.util
import platform

def install_and_import(package, import_name=None, pip_name=None):
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
import stringcolor
import curses

# =========================
# Hilfsfunktionen
# =========================

def colored_input(prompt, color="orange"):
    return input(stringcolor.cs(prompt, color))

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
    user_file = f"./JSON/{user_id}.json"
    if not os.path.exists(user_file):
        with open(user_file, "w") as file:
            json.dump(data, file, indent=4)

def delete_user_json(user_id):
    user_file = f"./JSON/{user_id}.json"
    try:
        os.remove(user_file)
        print(stringcolor.cs(f"User {user_id}.json file deleted successfully.", "yellow"))
    except FileNotFoundError:
        print(stringcolor.cs(f"User {user_id}.json file not found.", "red"))

def create_note_json(user_id, note_id, note_content, note_private):
    user_file = f"./JSON/{user_id}.json"
    if not os.path.exists(user_file):
        print(stringcolor.cs(f"User file {user_file} does not exist!", "red"))
        return
    note_data = {
        "note_content": note_content,
        "note_private": note_private
    }
    with open(user_file, "r") as file:
        data = json.load(file)
    data["notes"][note_id] = note_data
    with open(user_file, "w") as file:
        json.dump(data, file, indent=4)

def get_user_notes(user_id):
    user_file = f"./JSON/{user_id}.json"
    if not os.path.exists(user_file):
        return {}
    with open(user_file, "r") as file:
        data = json.load(file)
        return data["notes"]

def print_user_notes(user_id):
    notes = get_user_notes(user_id)
    if not notes:
        print(stringcolor.cs(f"{user_id} has no notes.", "yellow"))
        return
    print(stringcolor.cs(f"{user_id} has notes:", "yellow"))
    for note_id, note_data in notes.items():
        print(stringcolor.cs(f"Note ID: {note_id} Content: {note_data['note_content']}", "cyan"))

def edit_note_menu(user_id):
    while True:
        notes = get_user_notes(user_id)
        if not notes:
            print(stringcolor.cs("No notes to edit.", "yellow"))
            return
        note_ids = list(notes.keys())
        options = [f"{note_id}: {notes[note_id]['note_content']}" for note_id in note_ids]
        options.append("Back")
        idx = cursor_menu(options, title=stringcolor.cs("--- Select Note to Edit ---", "yellow").bold())
        if idx == len(options) - 1:
            # "Back" gewählt
            break
        note_id = note_ids[idx]
        print(stringcolor.cs(f"Editing Note: {note_id}", "yellow"))
        new_content = colored_input("Enter new note content: ")
        # Änderung speichern
        user_file = f"./JSON/{user_id}.json"
        with open(user_file, "r") as file:
            data = json.load(file)
        data["notes"][note_id]['note_content'] = new_content
        with open(user_file, "w") as file:
            json.dump(data, file, indent=4)
        print(stringcolor.cs("Note updated successfully.", "green"))

# =========================
# Cursor-Menü Funktion
# =========================

def cursor_menu(options, title="--- Menu ---"):
    def inner(stdscr):
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # yellow highlight
        current_row = 0
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, str(title))
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
    choice_idx = cursor_menu(menu_options, title=stringcolor.cs("--- StinkyNotes Menu ---", "yellow").bold())
    choice = str(choice_idx + 1) if choice_idx < 4 else "0"

    if choice == "1":
        print(stringcolor.cs("You selected: Add/Edit User", "yellow"))
        user_id = colored_input("Add user ID: ")
        if user_id in users:
            print(stringcolor.cs(f"User {user_id} already exists. You can change Fullname and Password.", "cyan"))
            fullname = colored_input("Change Full Name: ")
            password = colored_input("Change Password: ")
        else:          
            fullname = colored_input("Add Full Name: ")
            password = colored_input("Add Password: ")
        users[user_id] = {
            "fullname": fullname,
            "password": password
        }
        write_users('./JSON/stinky.json', users)
        create_user_json(user_id)
        print(stringcolor.cs(f"User {user_id} added successfully.", "green"))
    elif choice == "2":
        print(stringcolor.cs("You selected: Delete User", "yellow"))
        user_id = colored_input("Enter user ID to delete: ")
        if user_id in users:
            delete_user_json(user_id)
            users.pop(user_id)
            write_users('./JSON/stinky.json', users)
            print(stringcolor.cs(f"User {user_id} deleted successfully.", "green"))
        else:
            print(stringcolor.cs(f"User {user_id} not found.", "red"))
    elif choice == "3":
        print(stringcolor.cs("You selected: Create Note", "yellow"))
        user_id = colored_input("Log in to create a note for: ")
        password = colored_input("Enter password: ")
        if user_id in users and password == users[user_id]["password"]:
            print(stringcolor.cs("Logged in successfully.", "green"))
            note_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            note_content = colored_input("Enter note content: ")
            # Eingabe-Schleife für private/public
            while True:
                note_private_input = colored_input("Is this note private? (yes/no): ").strip().lower()
                if note_private_input in ("yes", "y"):
                    note_private = True
                    break
                elif note_private_input in ("no", "n"):
                    note_private = False
                    break
                elif note_private_input == "":
                    note_private = False
                    print(stringcolor.cs("No input. Defaulting to public note.", "yellow"))
                    break
                else:
                    print(stringcolor.cs("Please enter 'yes' or 'no'.", "red"))
            create_note_json(user_id, note_id, note_content, note_private)
            print(stringcolor.cs("Note created successfully.", "green"))
        else:
            print(stringcolor.cs("Incorrect user or password.", "red"))
            continue
    elif choice == "4":
        print(stringcolor.cs("You selected: Edit Notes", "yellow"))
        user_id = colored_input("Log in to edit notes for: ")
        password = colored_input("Enter password: ")
        if user_id in users and password == users[user_id]["password"]:
            print(stringcolor.cs("Logged in successfully.", "green"))
            edit_note_menu(user_id)
        else:
            print(stringcolor.cs("Incorrect user or password.", "red"))
            continue
    elif choice == "0":
        print(stringcolor.cs("Exiting the program. Goodbye!", "yellow"))
        break
    else:
        print(stringcolor.cs("Invalid option. Please try again.", "red"))

print(stringcolor.cs(str(users), "cyan"))
