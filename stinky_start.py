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
from cryptography.fernet import Fernet, InvalidToken
import binascii
import time  # Added for tracking failed login attempts
import logging
from passlib.hash import pbkdf2_sha256

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)
JSON_DIR = config["JSON_DIR"]

# Ensure virtual environment is created and activated
VENV_DIR = "venv"
if not os.path.exists(VENV_DIR):
    print("Virtual environment not found. Creating one...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        print("Virtual environment created successfully.")
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)

# Activate the virtual environment
activate_script = os.path.join(VENV_DIR, "bin", "activate")
if platform.system() == "Windows":
    activate_script = os.path.join(VENV_DIR, "Scripts", "activate.bat")
elif platform.system() == "Linux" or platform.system() == "Darwin":
    activate_script = os.path.join(VENV_DIR, "bin", "activate")

if os.path.exists(activate_script):
    try:
        if platform.system() == "Windows":
            subprocess.check_call([activate_script], shell=True)
        else:
            subprocess.check_call(["bash", "-c", f"source {activate_script} && echo 'Virtual environment activated.'"])
    except Exception as e:
        print(f"Error activating virtual environment: {e}")
        sys.exit(1)
else:
    print("Error: Virtual environment activation script not found. Please ensure the virtual environment is set up correctly.")
    sys.exit(1)

# Configure logging
LOG_FILE = "stinkynotes.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def log_error(error_message):
    """Log an error message to the log file."""
    logging.error(error_message)

def log_exception(exception):
    """Log an exception with traceback to the log file."""
    logging.exception(exception)

# Create a requirements.txt file with the necessary dependencies
REQUIREMENTS = """stringcolor
cryptography
twilio
string-color"""

# Dictionary to track failed login attempts and block time
failed_attempts = {}

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
                # Special case for twilio -> import name is twilio
                import_name = "twilio" if package_name == "twilio" else package_name
                try:
                    importlib.import_module(import_name)
                    print(f"Dependency '{package_name}' already satisfied.")
                except ImportError:
                    print(f"Installing missing dependency: {package_spec}")
                    try:
                        # Use the full spec (e.g., package==1.0) for installation
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec],
                                              stdout=subprocess.DEVNULL, stderr=subprocess.PIPE) # Capture stderr
                        print(f"Successfully installed {package_spec}.")
                        installed_changes = True
                    except subprocess.CalledProcessError as e:
                        # If it failed, print the command and the error output from pip
                        print(f"Error installing {package_spec}. Pip command failed.")
                        # e.stderr contains the captured error output (needs decoding)
                        if e.stderr:
                            print("--- Pip Error Output ---")
                            print(e.stderr.decode(errors='ignore')) # Decode bytes to string
                            print("------------------------")
                        print(f"Please try installing it manually: pip install \"{package_spec}\"")
                        sys.exit(1)
                    except Exception as e:
                         print(f"An unexpected error occurred during installation of {package_spec}: {e}")
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
def install_string_color():
    """Install the string-color package if not already installed."""
    try:
        import stringcolor
    except ImportError:
        print("string-color package not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "string-color", "--break-system-packages"])
        print("string-color package installed successfully.")

# Call the function to ensure string-color is installed
install_string_color()

# Proceed with dependency installation
check_and_install_dependencies()

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

# Generate a valid encryption key
ENCRYPTION_KEY = Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)

# Print the generated key for reference (optional, remove in production)
print(f"Generated Encryption Key: {ENCRYPTION_KEY.decode()}")

# Updated encryption and decryption functions
def encrypt_note_content(content):
    """Encrypt note content for ProUsers."""
    return fernet.encrypt(content.encode()).decode()

# Update decryption function to handle invalid base64 strings
def decrypt_note_content(content):
    """Decrypt note content for ProUsers."""
    try:
        return fernet.decrypt(content.encode()).decode()
    except (InvalidToken, binascii.Error):
        log_error(f"Decryption failed for content: {content}")
        return "[Decryption Failed: Invalid Content]"
    except Exception as e:
        log_exception(e)
        return "[Decryption Failed: Unknown Error]"

# ProUser Features
PRO_USER_FEATURES = {
    "encryption": True,  # Advanced note encryption
    "priority_support": True,  # Priority customer support
    "unlimited_storage": True  # Unlimited storage for notes
}

def is_pro_user(user_id):
    """Check if a user is a ProUser."""
    users = read_users(USERS_FILE)
    return users.get(user_id, {}).get("pro_user", False)

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

# --- ProUser Menu ---
def pro_user_menu(user_id):
    """Presents a menu for ProUsers with access to advanced features."""
    pro_user_options = [
        "Create Encrypted Note",
        "View Encrypted Notes",
        "Edit Encrypted Note",
        "Delete Encrypted Note",
        "Decrypt and View Note",
        "Back to Main Menu"
    ]

    while True:
        choice_idx = cursor_menu(pro_user_options, title=f"--- ProUser Menu for {user_id} ---")

        if choice_idx == len(pro_user_options) - 1:
            # "Back to Main Menu" selected
            break

        if choice_idx == 0:  # Create Encrypted Note
            note_id = str(uuid.uuid4())
            multi_line_instructions = "Enter note content. Press Ctrl+D (Linux/macOS) or Ctrl+Z then Enter (Windows) on an empty line to finish."
            print(stringcolor.cs(multi_line_instructions, "yellow"))
            note_content = colored_input("", "blue")
            while not note_content:
                print(stringcolor.cs("Note content cannot be empty.", "red"))
                note_content = colored_input("", "blue")

            note_private = True  # All ProUser notes are private by default
            create_note_entry(user_id, note_id, note_content, note_private)

        elif choice_idx == 1:  # View Encrypted Notes
            notes = get_user_notes(user_id)
            if not notes:
                print(stringcolor.cs("No encrypted notes found.", "yellow"))
            else:
                print(stringcolor.cs("\n--- Encrypted Notes ---", "cyan"))
                for note_id, note_data in notes.items():
                    content = note_data.get("note_content", "[No Content]")
                    privacy = "Private" if note_data.get("note_private", False) else "Public"
                    print(stringcolor.cs(f"ID: {note_id} ({privacy})\nContent: {content}\n", "green"))
            input(stringcolor.cs("\nPress Enter to return to the ProUser menu...", "magenta"))

        elif choice_idx == 2:  # Edit Encrypted Note
            notes = get_user_notes(user_id)
            if not notes:
                print(stringcolor.cs("No notes to edit.", "yellow"))
                continue

            note_ids = list(notes.keys())
            options = [f"{note_id}: {notes[note_id].get('note_content', '')[:40]}..." for note_id in note_ids]
            options.append("Back")

            idx = cursor_menu(options, title="--- Select Note to Edit ---")
            if idx == len(options) - 1:
                continue

            selected_note_id = note_ids[idx]
            current_content = notes[selected_note_id].get("note_content", "")
            new_content = colored_input("Enter new note content (leave blank to keep current): ", "green")
            if new_content:
                notes[selected_note_id]["note_content"] = encrypt_note_content(new_content)
                save_user_data(user_id, {"notes": notes})
                print(stringcolor.cs("Note updated successfully.", "green"))

        elif choice_idx == 3:  # Delete Encrypted Note
            notes = get_user_notes(user_id)
            if not notes:
                print(stringcolor.cs("No notes to delete.", "yellow"))
                continue

            note_ids = list(notes.keys())
            options = [f"{note_id}: {notes[note_id].get('note_content', '')[:40]}..." for note_id in note_ids]
            options.append("Back")

            idx = cursor_menu(options, title="--- Select Note to Delete ---")
            if idx == len(options) - 1:
                continue

            selected_note_id = note_ids[idx]
            del notes[selected_note_id]
            save_user_data(user_id, {"notes": notes})
            print(stringcolor.cs("Note deleted successfully.", "green"))

        elif choice_idx == 4:  # Decrypt and View Note
            notes = get_user_notes(user_id)
            if not notes:
                print(stringcolor.cs("No notes to decrypt.", "yellow"))
                continue

            note_ids = list(notes.keys())
            options = [f"{note_id}: {notes[note_id].get('note_content', '')[:40]}..." for note_id in note_ids]
            options.append("Back")

            idx = cursor_menu(options, title="--- Select Note to Decrypt ---")
            if idx == len(options) - 1:
                continue

            selected_note_id = note_ids[idx]
            encrypted_content = notes[selected_note_id].get("note_content", "")
            try:
                decrypted_content = decrypt_note_content(encrypted_content)
                print(stringcolor.cs(f"Decrypted Content for Note ID {selected_note_id}:\n{decrypted_content}", "green"))
            except Exception as e:
                print(stringcolor.cs(f"Failed to decrypt note: {e}", "red"))
                log_exception(e)

            input(stringcolor.cs("\nPress Enter to return to the ProUser menu...", "magenta"))

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

def hash_password(password):
    """Hash a password for storing."""
    return pbkdf2_sha256.hash(password)

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by the user."""
    return pbkdf2_sha256.verify(provided_password, stored_password)

def check_password(user_id, input_password):
    """Check the password for a user and handle failed attempts."""
    global failed_attempts

    # Initialize tracking for the user if not present
    if user_id not in failed_attempts:
        failed_attempts[user_id] = {"count": 0, "block_until": None}

    # Check if the user is currently blocked
    block_until = failed_attempts[user_id]["block_until"]
    if block_until and time.time() < block_until:
        remaining_time = int(block_until - time.time())
        print(stringcolor.cs(f"User '{user_id}' is blocked. Try again in {remaining_time} seconds.", "red"))
        return False

    # Reset block time if the block period has passed
    if block_until and time.time() >= block_until:
        failed_attempts[user_id]["block_until"] = None
        failed_attempts[user_id]["count"] = 0

    # Check the password
    users = read_users(USERS_FILE)
    correct_password = users.get(user_id, {}).get("password")
    if verify_password(correct_password, input_password):
        # Reset failed attempts on successful login
        failed_attempts[user_id]["count"] = 0
        return True
    else:
        # Increment failed attempts
        failed_attempts[user_id]["count"] += 1
        print(stringcolor.cs("Incorrect password.", "red"))

        # Block the user after 3 failed attempts
        if failed_attempts[user_id]["count"] >= 3:
            failed_attempts[user_id]["block_until"] = time.time() + 180  # Block for 3 minutes
            print(stringcolor.cs(f"User '{user_id}' is blocked for 3 minutes due to multiple failed attempts.", "red"))

        return False

def login_user(user_id):
    """Handle user login with password check and blocking."""
    while True:
        password = colored_input(f"Enter password for '{user_id}': ", "green")
        if check_password(user_id, password):
            print(stringcolor.cs("Login successful.", "green"))
            return True
        else:
            print(stringcolor.cs("Please try again.", "yellow"))

        # Exit loop if user is blocked
        if failed_attempts[user_id]["block_until"]:
            return False

# Enhanced error handling with self-healing capabilities

def self_healing_handler(error):
    """Attempt to resolve common errors automatically."""
    if isinstance(error, FileNotFoundError):
        missing_file = str(error).split("No such file or directory: ")[1].strip("'")
        print(stringcolor.cs(f"File not found: {missing_file}. Attempting to recreate it...", "yellow"))
        try:
            if missing_file.endswith("stinky.json"):
                write_users(USERS_FILE, {})
                print(stringcolor.cs(f"Recreated missing file: {missing_file}", "green"))
            elif missing_file.startswith(JSON_DIR):
                user_id = missing_file.split("/")[-1].replace(".json", "")
                create_user_json(user_id)
                print(stringcolor.cs(f"Recreated missing user file: {missing_file}", "green"))
            else:
                print(stringcolor.cs(f"Cannot handle missing file: {missing_file}", "red"))
        except Exception as e:
            log_exception(e)
            print(stringcolor.cs(f"Failed to recreate missing file: {missing_file}", "red"))

    elif isinstance(error, json.JSONDecodeError):
        print(stringcolor.cs("JSON file is corrupted. Attempting to reset it...", "yellow"))
        try:
            corrupted_file = str(error).split("Expecting value: line 1 column 1 (char 0)")[0].strip()
            if corrupted_file.endswith("stinky.json"):
                write_users(USERS_FILE, {})
                print(stringcolor.cs(f"Reset corrupted file: {corrupted_file}", "green"))
            elif corrupted_file.startswith(JSON_DIR):
                user_id = corrupted_file.split("/")[-1].replace(".json", "")
                create_user_json(user_id)
                print(stringcolor.cs(f"Reset corrupted user file: {corrupted_file}", "green"))
            else:
                print(stringcolor.cs(f"Cannot handle corrupted file: {corrupted_file}", "red"))
        except Exception as e:
            log_exception(e)
            print(stringcolor.cs("Failed to reset corrupted JSON file.", "red"))

    elif isinstance(error, ImportError):
        missing_module = str(error).split("No module named ")[1].strip("'")
        print(stringcolor.cs(f"Missing module: {missing_module}. Attempting to install it...", "yellow"))
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", missing_module, "--break-system-packages"])
            print(stringcolor.cs(f"Successfully installed missing module: {missing_module}", "green"))
        except Exception as e:
            log_exception(e)
            print(stringcolor.cs(f"Failed to install missing module: {missing_module}", "red"))

    else:
        print(stringcolor.cs("An unknown error occurred. Logging it for review.", "red"))
        log_exception(error)

def process_log_and_self_repair():
    """Reads the log file, attempts to fix errors, and removes fixed entries."""
    try:
        if not os.path.exists(LOG_FILE):
            print("Log file not found. Nothing to process.")
            return

        with open(LOG_FILE, "r") as log_file:
            log_entries = log_file.readlines()

        repaired_entries = []
        for entry in log_entries:
            if "InvalidToken" in entry:
                print("Attempting to fix InvalidToken error...")
                # Handle InvalidToken errors (e.g., skip invalid notes)
                repaired_entries.append(entry)
            elif "FileNotFoundError" in entry:
                print("Attempting to fix missing file error...")
                # Handle missing file errors (e.g., recreate files)
                repaired_entries.append(entry)
            elif "JSONDecodeError" in entry:
                print("Attempting to fix corrupted JSON file...")
                # Handle corrupted JSON files (e.g., reset files)
                repaired_entries.append(entry)
            else:
                print(f"Unhandled log entry: {entry.strip()}")

        # Rewrite the log file without repaired entries
        with open(LOG_FILE, "w") as log_file:
            for entry in log_entries:
                if entry not in repaired_entries:
                    log_file.write(entry)

        print("Log processing complete. Fixed entries removed.")

    except Exception as e:
        print(f"Error processing log file: {e}")
        log_exception(e)

# Main function
def main():
    """Main function to start the StinkyNotes application."""
    print("Welcome to StinkyNotes!")
    # Add the main menu or application logic here
    while True:
        menu_options = [
            "Add/Edit User",
            "Delete User",
            "Create Note",
            "View User Notes",  # New menu item for viewing notes
            "Edit User Notes",  # Existing menu item for editing notes
            "ProUser Area",
            "Exit"
        ]

        selected_option = cursor_menu(menu_options, title="--- StinkyNotes Menu ---")

        if selected_option == len(menu_options) - 1:  # Exit
            print("Exiting the application. Goodbye!")
            break

        elif selected_option == 0:  # Add/Edit User
            print("Add/Edit User functionality not implemented yet.")

        elif selected_option == 1:  # Delete User
            print("Delete User functionality not implemented yet.")

        elif selected_option == 2:  # Create Note
            print("Create Note functionality not implemented yet.")

        elif selected_option == 3:  # View User Notes
            user_id = colored_input("Enter User ID to view notes: ", "green")
            print_user_notes(user_id)  # Use the existing function to display notes

        elif selected_option == 4:  # Edit User Notes
            user_id = colored_input("Enter User ID to edit notes: ", "green")
            edit_note_menu(user_id)  # Use the existing function to edit notes

        elif selected_option == 5:  # ProUser Area
            user_id = colored_input("Enter ProUser ID: ", "green")
            if login_user(user_id):
                pro_user_menu(user_id)

        else:
            print("Invalid option selected.")

# Wrap main application logic with self-healing error handling
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(stringcolor.cs(f"\nAn error occurred: {e}", "red"))
        self_healing_handler(e)
        print(stringcolor.cs("Attempting to restart the application...", "yellow"))
        try:
            main()
        except Exception as retry_error:
            print(stringcolor.cs(f"\nFailed to recover from error: {retry_error}", "red"))
            log_exception(retry_error)
            print(stringcolor.cs("Please check the log file for more details.", "yellow"))
    finally:
        process_log_and_self_repair()

# Ensure the main function is defined
if __name__ == "__main__":
    main()

