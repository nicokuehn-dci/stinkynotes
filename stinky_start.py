import sys
import subprocess
import importlib.util
import platform
import uuid
import os
import datetime
import json
import stringcolor
import curses # Keep this import even if windows-curses might be used

# Create a requirements.txt file with the necessary dependencies
REQUIREMENTS = """stringcolor"""

# --- Environment Setup (Optional at Runtime) ---
def check_and_install_dependencies():
    """Checks for installed dependencies and installs missing ones."""
    print("Checking dependencies from requirements.txt...")
    try:
        with open("requirements.txt", "r") as req_file:
            dependencies = req_file.readlines()

        installed_changes = False
        for dependency in dependencies:
            dependency = dependency.strip()
            if not dependency or dependency.startswith('#'):
                continue

            # Handle conditional dependencies (like ; platform_system == 'Windows')
            parts = dependency.split(";")
            
            package_spec = parts[0].strip()
            condition = parts[1].strip() if len(parts) > 1 else None

            should_install = True
            if condition:
                try:
                    # Very basic evaluation for platform_system
                    if 'platform_system' in condition:
                         target_system = condition.split('==')[1].strip().replace("'", "").replace('"', '')
                         if platform.system().lower() != target_system.lower():
                             should_install = False
                             print(f"Skipping '{package_spec}' due to platform condition: {condition}")
                    # Add more condition evaluations here if needed
                except Exception as e:
                    print(f"Warning: Could not evaluate condition '{condition}' for {package_spec}: {e}")
                    # Decide if you want to attempt installation anyway or skip
                    # should_install = False # Or keep True and attempt install

            if should_install:
                # Extract package name for import check (handle ==, >=, etc.)
                package_name = package_spec.split("==")[0].split(">=")[0].split("<=")[0].split("!=")[0].split("~=")[0]
                # Special case for windows-curses -> import name is curses
                import_name = "curses" if package_name == "windows-curses" else package_name
                try:
                    importlib.import_module(import_name)
                    print(f"Dependency '{package_name}' already satisfied.")
                except ImportError:
                    print(f"Installing missing dependency: {package_spec}")
                    try:
                        # Use the full spec (e.g., package==1.0) for installation
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
                        installed_changes = True
                    except subprocess.CalledProcessError as e:
                        print(f"Error installing {package_spec}: {e}")
                        print("Please try installing it manually.")
                        sys.exit(1) # Exit if critical dependency fails
                    except Exception as e:
                         print(f"An unexpected error occurred during installation: {e}")
                         sys.exit(1)

        if installed_changes:
            print("\nDependencies installed. You might need to restart the script.")
            # Optional: Exit here if a restart is strongly recommended
            # sys.exit(0)

    except FileNotFoundError:
        print("requirements.txt not found. Creating one.")
        with open("requirements.txt", "w") as req_file:
            req_file.write(REQUIREMENTS)
        print("Created requirements.txt. Please run the script again to install dependencies.")
        sys.exit(0) # Exit so user can rerun
    except Exception as e:
        print(f"An error occurred during dependency check: {e}")
        sys.exit(1)

# --- Initial Setup Prompt ---
if __name__ == "__main__":
    # Create requirements.txt if it doesn't exist
    if not os.path.exists("requirements.txt"):
         with open("requirements.txt", "w") as req_file:
             req_file.write(REQUIREMENTS)
         print("Created requirements.txt.")

    run_env_setup = input("Do you want to check/install dependencies now? (yes/no): ").strip().lower()
    if run_env_setup in ("yes", "y"):
        print("Setting up the environment...")
        check_and_install_dependencies()
        print("Dependency check complete.")
    else:
        print("Skipping dependency check. The script might fail if dependencies are missing.")

# --- Dynamic Import Function (Less verbose alternative for simple cases) ---
# Keep this if you prefer it, but the check_and_install_dependencies is more robust for requirements.txt
def install_and_import(package, import_name=None, pip_name=None):
    if import_name is None:
        import_name = package
    if pip_name is None:
        pip_name = package
    spec = importlib.util.find_spec(import_name)
    if spec is None:
        print(f"Attempting to install missing package: {pip_name} ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            print(f"Package '{pip_name}' installed successfully.")
            globals()[import_name] = importlib.import_module(import_name)
        except (subprocess.CalledProcessError, ImportError) as e:
            print(f"Error: Failed to install and import '{pip_name}'. {e}")
            print("Please install it manually.")
            sys.exit(1)
    else:
        # print(f"Package '{import_name}' already available.")
        globals()[import_name] = importlib.import_module(import_name)


# --- Now the Imports (after potential installation) ---
# Use install_and_import OR rely on check_and_install_dependencies having run.
# If check_and_install_dependencies ran successfully, direct imports should work.
try:
    import stringcolor
    # Curses import needs to handle the windows-curses case
    if platform.system() == "Windows":
        # Check if it was installed; find_spec checks if it can be imported
        if importlib.util.find_spec("curses") is None:
             print("Error: 'windows-curses' is required on Windows but not found.")
             print("Please run the script again and choose 'yes' to install dependencies,")
             print("or install it manually ('pip install windows-curses').")
             sys.exit(1)
    # This import works for Linux/macOS directly, and for Windows if windows-curses is installed
    import curses
except ImportError as e:
    print(f"Error importing a required module: {e}")
    print("Please run the script again and choose 'yes' to install dependencies,")
    print("or install them manually from requirements.txt.")
    sys.exit(1)


# =========================
# Hilfsfunktionen
# =========================

# Use a constant for the JSON directory
JSON_DIR = "./JSON"
USERS_FILE = os.path.join(JSON_DIR, "stinky.json")

def get_user_file_path(user_id):
    """Gets the full path for a user's JSON file."""
    return os.path.join(JSON_DIR, f"{user_id}.json")

def colored_input(prompt, color="orange"):
    """Gets user input with a colored prompt."""
    # Ensure prompt is a string
    prompt_str = str(stringcolor.cs(prompt, color))
    return input(prompt_str)

def read_users(file_path):
    """Reads the main user database."""
    try:
        with open(file_path, 'r') as file:
            users = json.load(file)
        return users
    except (FileNotFoundError, json.JSONDecodeError):
        # Return empty dict if file missing or corrupt, it will be created/overwritten later
        return {}

def write_users(file_path, users):
    """Writes the main user database."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True) # Ensure directory exists
        with open(file_path, 'w') as file:
            json.dump(users, file, indent=4)
    except IOError as e:
        print(stringcolor.cs(f"Error writing user database {file_path}: {e}", "red"))

def create_user_json(user_id):
    """Creates an individual JSON file for a user's notes."""
    data = {
        "user_id": user_id,
        "notes": {}
    }
    os.makedirs(JSON_DIR, exist_ok=True)
    user_file = get_user_file_path(user_id)
    if not os.path.exists(user_file):
        try:
            with open(user_file, "w") as file:
                json.dump(data, file, indent=4)
        except IOError as e:
             print(stringcolor.cs(f"Error creating user file {user_file}: {e}", "red"))


def delete_user_json(user_id):
    """Deletes a user's individual JSON file."""
    user_file = get_user_file_path(user_id)
    try:
        os.remove(user_file)
        print(stringcolor.cs(f"User data file '{os.path.basename(user_file)}' deleted successfully.", "yellow"))
    except FileNotFoundError:
        # This might not be an error if the user never had notes
        # print(stringcolor.cs(f"User file '{os.path.basename(user_file)}' not found.", "red"))
        pass
    except OSError as e:
        print(stringcolor.cs(f"Error deleting user file '{os.path.basename(user_file)}': {e}", "red"))


def load_user_data(user_id):
    """Loads data (including notes) for a specific user."""
    user_file = get_user_file_path(user_id)
    try:
        with open(user_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(stringcolor.cs(f"User data file for {user_id} not found.", "yellow"))
        return None # Indicate user data doesn't exist
    except json.JSONDecodeError:
        print(stringcolor.cs(f"Error decoding JSON from {user_file}. File might be corrupt.", "red"))
        return None # Indicate error
    except IOError as e:
        print(stringcolor.cs(f"Error reading user file {user_file}: {e}", "red"))
        return None

def save_user_data(user_id, data):
    """Saves data (including notes) for a specific user."""
    user_file = get_user_file_path(user_id)
    try:
        with open(user_file, "w") as file:
            json.dump(data, file, indent=4)
        return True
    except IOError as e:
        print(stringcolor.cs(f"Error writing user file {user_file}: {e}", "red"))
        return False

# ProUser Features
PRO_USER_FEATURES = {
    "encryption": True,  # Advanced note encryption
    "cloud_sync": True,  # Cloud synchronization (mocked for now)
    "priority_support": True,  # Priority customer support
    "custom_themes": True,  # Customizable themes (mocked for now)
    "unlimited_storage": True  # Unlimited storage for notes
}

def is_pro_user(user_id):
    """Check if a user is a ProUser."""
    users = read_users(USERS_FILE)
    return users.get(user_id, {}).get("pro_user", False)

def encrypt_note_content(content):
    """Encrypt note content for ProUsers."""
    # Simple mock encryption (replace with real encryption logic)
    return f"ENCRYPTED({content})"

def decrypt_note_content(content):
    """Decrypt note content for ProUsers."""
    # Simple mock decryption (replace with real decryption logic)
    if content.startswith("ENCRYPTED(") and content.endswith(")"):
        return content[len("ENCRYPTED("):-1]
    return content

def create_note_entry(user_id, note_id, note_content, note_private):
    """Adds a note entry to a user's data file."""
    data = load_user_data(user_id)
    if data is None:
        print(stringcolor.cs(f"Cannot create note. User data for {user_id} not found or couldn't be loaded.", "red"))
        return

    if is_pro_user(user_id) and PRO_USER_FEATURES["encryption"]:
        note_content = encrypt_note_content(note_content)

    note_data = {
        "note_content": note_content,
        "note_private": note_private,
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    if "notes" not in data:
        data["notes"] = {}

    data["notes"][note_id] = note_data
    if save_user_data(user_id, data):
        print(stringcolor.cs(f"Note '{note_id}' created successfully for user {user_id}.", "green"))
    else:
        print(stringcolor.cs(f"Failed to save note '{note_id}' for user {user_id}.", "red"))

def get_user_notes(user_id):
    """Gets the notes dictionary for a user."""
    data = load_user_data(user_id)
    if data and "notes" in data:
        notes = data["notes"]
        if is_pro_user(user_id) and PRO_USER_FEATURES["encryption"]:
            for note_id, note_data in notes.items():
                note_data["note_content"] = decrypt_note_content(note_data["note_content"])
        return notes
    return {}

def toggle_pro_user_status(user_id):
    """Toggle the ProUser status for a user."""
    users = read_users(USERS_FILE)
    if user_id in users:
        current_status = users[user_id].get("pro_user", False)
        users[user_id]["pro_user"] = not current_status
        write_users(USERS_FILE, users)
        status = "enabled" if not current_status else "disabled"
        print(stringcolor.cs(f"ProUser status {status} for user '{user_id}'.", "green"))
    else:
        print(stringcolor.cs(f"User '{user_id}' not found.", "red"))

def print_user_notes(user_id): # Keep for potential debugging or direct display
    """Prints all notes for a given user."""
    notes = get_user_notes(user_id)
    if not notes:
        print(stringcolor.cs(f"User '{user_id}' has no notes.", "yellow"))
        return
    print(stringcolor.cs(f"Notes for user '{user_id}':", "yellow"))
    for note_id, note_data in notes.items():
        privacy = "Private" if note_data.get('note_private', False) else "Public"
        content = note_data.get('note_content', '[No Content]')
        print(stringcolor.cs(f"  ID: {note_id} ({privacy}) - Content: {content}", "cyan"))

# --- MODIFIED EDIT NOTE MENU ---
def edit_note_menu(user_id):
    """Presents a menu to edit notes for the logged-in user."""
    while True:
        user_data = load_user_data(user_id)
        if user_data is None:
            print(stringcolor.cs(f"Error loading notes for {user_id}. Cannot edit.", "red"))
            return # Exit editing if user data fails to load

        notes = user_data.get("notes", {})
        if not notes:
            print(stringcolor.cs("No notes to edit.", "yellow"))
            input(stringcolor.cs("Press Enter to go back...", "magenta")) # Pause before returning
            return

        note_ids = list(notes.keys())
        options = []
        for note_id in note_ids:
            content_preview = notes[note_id].get('note_content', '')[:40] # Show preview
            if len(notes[note_id].get('note_content', '')) > 40:
                content_preview += "..."
            privacy = "(Private)" if notes[note_id].get('note_private', False) else "(Public)"
            options.append(f"{note_id}: {content_preview} {privacy}")
        options.append("Back")

        idx = cursor_menu(options, title=f"--- Edit Notes for {user_id} ---")

        if idx == len(options) - 1:
            # "Back" selected
            break # Exit the edit menu loop

        selected_note_id = note_ids[idx]
        current_content = notes[selected_note_id].get('note_content', '')
        current_privacy = notes[selected_note_id].get('note_private', False)

        print(stringcolor.cs(f"\n--- Editing Note ID: {selected_note_id} ---", "cyan"))
        print(stringcolor.cs(f"Current Content: {current_content}", "white"))
        new_content = colored_input("Enter new note content (leave blank to keep current): ", "green")
        if not new_content: # If user just presses Enter
            new_content = current_content # Keep old content
        else:
            print(stringcolor.cs("Content updated.", "light_green"))

        # Edit Privacy
        while True:
            privacy_str = "private" if current_privacy else "public"
            change_privacy = colored_input(f"Note is currently {privacy_str}. Change privacy? (yes/no, leave blank to keep): ", "green").strip().lower()
            if change_privacy in ('y', 'yes'):
                new_privacy = not current_privacy # Flip the privacy setting
                new_privacy_str = "private" if new_privacy else "public"
                print(stringcolor.cs(f"Privacy changed to {new_privacy_str}.", "light_green"))
                break
            elif change_privacy in ('n', 'no', ''):
                new_privacy = current_privacy # Keep old privacy
                print(stringcolor.cs("Privacy unchanged.", "yellow"))
                break
            else:
                print(stringcolor.cs("Invalid input. Please enter 'yes' or 'no'.", "red"))

        # Save changes
        # Update the note in the loaded data
        user_data["notes"][selected_note_id]['note_content'] = new_content
        user_data["notes"][selected_note_id]['note_private'] = new_privacy
        user_data["notes"][selected_note_id]['updated_at'] = datetime.datetime.now().isoformat() # Update timestamp

        # Save the entire user data back to the file
        if save_user_data(user_id, user_data):
            print(stringcolor.cs("Note updated successfully.", "green"))
        else:
            print(stringcolor.cs("Failed to save updated note.", "red"))
            # Keep the loop going, but the change wasn't saved

        input(stringcolor.cs("\nPress Enter to continue editing...", "magenta")) # Pause

# Unused function (from original prompt context, can be removed)
# def createNoteElement(note_id, note_content, note_private): ...

# =========================
# Cursor-Menü Function
# =========================

def cursor_menu(options, title="--- Menu ---"):
    """Displays a navigable menu using curses and returns the selected index."""
    # Input validation (remains the same)
    if not isinstance(options, list) or not options:
        raise ValueError("Options must be a non-empty list.")
    if not all(isinstance(opt, str) for opt in options):
        raise TypeError("All options must be strings.")

    def _draw_menu(stdscr, current_row, options, title):
        stdscr.clear()
        h, w = stdscr.getmaxyx() # Get window dimensions

        # --- Title ---
        # Title should now be a plain string, we apply curses attributes here
        title_str = str(title)
        x_title = max(0, (w // 2) - (len(title_str) // 2))
        y_title = 0
        # Apply curses attributes for the title
        try:
            stdscr.attron(curses.color_pair(2)) # Use color pair 2 for title
            stdscr.attron(curses.A_BOLD)       # Make it bold
            stdscr.addstr(y_title, x_title, title_str)
            stdscr.attroff(curses.A_BOLD)       # Turn off bold
            stdscr.attroff(curses.color_pair(2)) # Turn off title color
        except curses.error:
             # Fallback if colors/attributes fail for title
             stdscr.addstr(y_title, x_title, title_str)


        # --- Options --- (remains mostly the same)
        max_option_len = max(len(opt) for opt in options)
        x_options = max(1, (w // 2) - (max_option_len // 2) - 1)
        y_options_start = 2

        for idx, row in enumerate(options):
            y = y_options_start + idx
            if y >= h -1:
                 stdscr.addstr(h - 1, 0, "...")
                 break

            display_row = row[:w - x_options - 1]

            try:
                if idx == current_row:
                    stdscr.attron(curses.color_pair(1)) # Highlight color pair
                    stdscr.addstr(y, x_options, display_row.ljust(max_option_len))
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, x_options, display_row)
            except curses.error:
                 # Fallback if colors fail for options
                 prefix = "->" if idx == current_row else "  "
                 stdscr.addstr(y, x_options-2, prefix + display_row)


        stdscr.refresh()

    def _menu_logic(stdscr):
        curses.curs_set(0) # Hide cursor
        curses.start_color()
        # Use terminal's default background for transparency (-1)
        curses.use_default_colors()

        # Define Color Pairs:
        # Pair 1: Highlight for selected option (e.g., Black text on Yellow background)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        # Pair 2: Title color (e.g., Yellow text on default background)
        curses.init_pair(2, curses.COLOR_YELLOW, -1) # -1 uses default background

        current_row = 0
        _draw_menu(stdscr, current_row, options, title) # Initial draw

        while True:
            key = stdscr.getch() # Get user input

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options) - 1:
                current_row += 1
            elif key in [curses.KEY_ENTER, ord('\n'), ord(' ')]: # Enter or Space selects
                # Before returning, clear screen and optionally print selection
                # stdscr.clear()
                # stdscr.addstr(0, 0, f"Selected: {options[current_row]}")
                # stdscr.refresh()
                # time.sleep(0.5) # Optional pause
                return current_row
            elif key == curses.KEY_RESIZE: # Handle terminal resize
                 _draw_menu(stdscr, current_row, options, title) # Redraw immediately
                 continue
            elif key == 27: # Escape key
                 back_options = [i for i, opt in enumerate(options) if opt.lower() in ('back', 'exit', 'quit')]
                 if back_options:
                     return back_options[0]

            _draw_menu(stdscr, current_row, options, title)

    # Ensure curses environment is properly managed (remains the same)
    try:
        return curses.wrapper(_menu_logic)
    except curses.error as e:
        print(f"\nCurses error: {e}")
        print("Your terminal might not fully support curses features.")
        # Fallback menu (remains the same)
        print("\n--- Fallback Menu ---")
        print(str(title)) # Title is plain string here too
        for i, opt in enumerate(options):
            print(f"{i + 1}. {opt}")
        while True:
            try:
                choice = input(f"Enter choice (1-{len(options)}): ")
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return idx
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")
    except Exception as e:
         print(f"\nAn unexpected error occurred in the menu: {e}")
         return len(options) - 1 # Default to last option


# =========================
# Main Application Logic
# =========================

def main():
    """Main application function."""
    # Ensure base directory and users file exist
    os.makedirs(JSON_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        print(f"User database '{USERS_FILE}' not found. Creating empty database.")
        write_users(USERS_FILE, {}) # Create empty user file

    users = read_users(USERS_FILE) # Load main user dictionary

    menu_options = [
        "Add/Edit User",
        "Delete User",
        "Create Note",
        "Edit User Notes",
        "Toggle ProUser Status",
        "Exit"
    ]

    while True:
        try:
            # Pass the title as a PLAIN STRING
            choice_idx = cursor_menu(menu_options, title="--- StinkyNotes Menu ---")
        except Exception as e:
            print(stringcolor.cs(f"\nMenu display error: {e}. Exiting.", "red"))
            break # Exit loop on menu error

        # Map index back to logical choice (handle potential menu errors returning unexpected values)
        if not isinstance(choice_idx, int) or choice_idx < 0 or choice_idx >= len(menu_options):
            print(stringcolor.cs("Invalid menu selection received. Please try again.", "red"))
            continue

        selected_option = menu_options[choice_idx]

        print(f"\n--- {selected_option} ---") # More descriptive header

        if selected_option == "Add/Edit User":
            user_id = colored_input("Enter User ID: ", "green")
            if not user_id:
                print(stringcolor.cs("User ID cannot be empty.", "red"))
                continue

            if user_id in users:
                print(stringcolor.cs(f"User '{user_id}' already exists. You can update details.", "cyan"))
                current_fullname = users[user_id].get("fullname", "N/A")
                print(f"Current Full Name: {current_fullname}")
                fullname = colored_input(f"Enter new Full Name (leave blank to keep '{current_fullname}'): ", "green")
                password = colored_input("Enter new Password (leave blank to keep current): ", "green")

                if fullname:
                    users[user_id]["fullname"] = fullname
                if password:
                    users[user_id]["password"] = password
                print(stringcolor.cs(f"User '{user_id}' details updated.", "light_green"))

            else:
                fullname = colored_input("Enter Full Name: ", "green")
                while not fullname:
                    print(stringcolor.cs("Full Name cannot be empty.", "red"))
                    fullname = colored_input("Enter Full Name: ", "green")

                password = colored_input("Enter Password: ", "green")
                while not password:
                    print(stringcolor.cs("Password cannot be empty.", "red"))
                    password = colored_input("Enter Password: ", "green")

                users[user_id] = {
                    "fullname": fullname,
                    "password": password
                }
                create_user_json(user_id) # Create the user's note file
                print(stringcolor.cs(f"User '{user_id}' added successfully.", "green"))

            write_users(USERS_FILE, users) # Save changes to the main user file

        elif selected_option == "Delete User":
            user_id = colored_input("Enter user ID to delete: ", "red")
            if user_id in users:
                confirm = colored_input(f"Are you sure you want to delete user '{user_id}' and all their notes? (yes/no): ", "red").lower()
                if confirm in ('y', 'yes'):
                    try:
                        del users[user_id] # Remove from main dictionary
                        write_users(USERS_FILE, users) # Save updated user list
                        delete_user_json(user_id) # Delete the user's notes file
                        print(stringcolor.cs(f"User '{user_id}' deleted successfully.", "green"))
                    except Exception as e:
                        print(stringcolor.cs(f"An error occurred during deletion: {e}", "red"))
                else:
                    print(stringcolor.cs("User deletion cancelled.", "yellow"))
            else:
                print(stringcolor.cs(f"User '{user_id}' not found.", "red"))

        elif selected_option == "Create Note":
            user_id = colored_input("Enter User ID to create note for: ", "green")
            if user_id not in users:
                print(stringcolor.cs(f"User '{user_id}' not found. Cannot create note.", "red"))
                continue # Go back to main menu

            password = colored_input(f"Enter password for '{user_id}': ", "green")
            if users[user_id].get("password") == password:
                print(stringcolor.cs("Login successful.", "green"))
                note_id = str(uuid.uuid4()) # Generate a robust unique ID
                note_content = colored_input("Enter note content: ", "blue")
                while not note_content:
                     print(stringcolor.cs("Note content cannot be empty.", "red"))
                     note_content = colored_input("Enter note content: ", "blue")

                # Input loop for private/public
                note_private = False # Default to public
                while True:
                    note_private_input = colored_input("Is this note private? (yes/no, default=no): ", "blue").strip().lower()
                    if note_private_input in ("yes", "y"):
                        note_private = True
                        break
                    elif note_private_input in ("no", "n", ""): # Empty input defaults to no
                        note_private = False
                        break
                    else:
                        print(stringcolor.cs("Please enter 'yes' or 'no'.", "red"))

                create_note_entry(user_id, note_id, note_content, note_private)
                # Success/failure message is printed within create_note_entry

            else:
                print(stringcolor.cs("Incorrect password.", "red"))
                # No 'continue' here, loop will naturally go back to menu

        # --- MODIFIED FLOW for Edit User Notes ---
        elif selected_option == "Edit User Notes":
            user_id = colored_input("Enter User ID whose notes you want to edit: ", "green")
            if user_id not in users:
                print(stringcolor.cs(f"User '{user_id}' not found.", "red"))
                continue # Back to main menu

            password = colored_input(f"Enter password for '{user_id}': ", "green")
            if users[user_id].get("password") == password:
                print(stringcolor.cs(f"Login successful. Accessing notes for '{user_id}'...", "green"))
                edit_note_menu(user_id) # Call the dedicated edit menu function
            else:
                print(stringcolor.cs("Incorrect password.", "red"))
                # No 'continue' needed, will loop back to main menu naturally

        elif selected_option == "Toggle ProUser Status":
            user_id = colored_input("Enter User ID to toggle ProUser status: ", "green")
            toggle_pro_user_status(user_id)

        elif selected_option == "Exit":
            print(stringcolor.cs("Exiting the program. Goodbye!", "yellow"))
            break # Exit the main while loop

        # Pause at the end of each action before showing the menu again
        input(stringcolor.cs("\nPress Enter to return to the main menu...", "magenta"))


if __name__ == "__main__":
    # The dependency check prompt happens earlier now
    try:
        main()
    except KeyboardInterrupt:
        print(stringcolor.cs("\nOperation cancelled by user. Exiting.", "yellow"))
    except Exception as e:
        # General fallback error catcher
        print(stringcolor.cs(f"\nAn unexpected error occurred: {e}", "red"))
        # Optionally print traceback for debugging
        # import traceback
        # traceback.print_exc()
    finally:
         # Clean up curses terminal state if it was used and exited unexpectedly
         if 'curses' in sys.modules and not sys.stdout.isatty(): # Check if curses likely ran
             try:
                  curses.endwin()
             except:
                  pass # Ignore errors during cleanup
         print("\nStinkyNotes finished.")

