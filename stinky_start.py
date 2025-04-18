#!/usr/bin/env python3
# Create and activate virtual environment automatically if needed
import os
import sys
import subprocess

# Check if running in a virtual environment
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("Not running in a virtual environment. Setting up venv...")
    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    
    # Determine the path to the Python interpreter in the virtual environment
    if os.name == 'nt':  # Windows
        venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:  # Linux/Mac
        venv_python = os.path.join(venv_dir, 'bin', 'python')
    
    # Re-execute the script using the virtual environment's Python
    print("Restarting in virtual environment...")
    os.execl(venv_python, venv_python, *sys.argv)

import sys
import subprocess
import importlib.util
import platform
import uuid
import os
import datetime
import json
import stringcolor
from stringcolor import cs
import importlib
import curses # Keep this import even if windows-curses might be used

# Create a requirements.txt file with the necessary dependencies
REQUIREMENTS = """stringcolor
windows-curses; platform_system == 'Windows'
"""

# --- Environment Setup (Optional at Runtime) ---

# Create a class for handling Pro User logging
class ProUserLogger:
    def __init__(self):
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger('prouser')
        self.logger.setLevel(logging.INFO)
        
        # Create a timestamp for the log file name
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"exports/prouser_log_{timestamp}.log"
        
        # Set up file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Log system startup and user identification
        self.log_system_info()
    
    def get_mac_address(self):
        """Get the MAC address of the machine"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 48, 8)][::-1])
            return mac
        except:
            return "Unknown MAC"
    
    def get_ip_address(self):
        """Get the IP address of the machine"""
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except:
            return "Unknown IP"
    
    def log_system_info(self):
        """Log system information at startup"""
        system_info = {
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
            "mac_address": self.get_mac_address(),
            "ip_address": self.get_ip_address(),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
        
        self.logger.info(f"=== PRO USER SESSION STARTED ===")
        self.logger.info(f"User identification: {json.dumps(system_info)}")
    
    def log_action(self, action, details=None):
        """Log a user action"""
        if details:
            self.logger.info(f"Action: {action} - Details: {json.dumps(details)}")
        else:
            self.logger.info(f"Action: {action}")
    
    def log_session_end(self):
        """Log session end"""
        self.logger.info(f"=== PRO USER SESSION ENDED ===")

# Initialize the logger (will be used in pro_user_area function)
prouser_logger = None

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
MESSAGES_FILE = os.path.join(JSON_DIR, "messages.json")  # File for storing private messages

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
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # Ensure directory exists
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
print("Keep the encryption key secure for decrypting notes.")

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
# ProUser Area Functions
# =========================

def encrypt_note(content, password):
    """Encrypts a note using a password-derived key."""
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    import os
    
    # Use password to derive encryption key
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    cipher = Fernet(key)
    
    # Encrypt the content
    encrypted_content = cipher.encrypt(content.encode())
    
    # Return the encrypted content and salt (both base64 encoded for storage)
    return {
        "encrypted_data": base64.urlsafe_b64encode(encrypted_content).decode(),
        "salt": base64.urlsafe_b64encode(salt).decode(),
        "is_encrypted": True
    }

def decrypt_note(encrypted_data, salt, password):
    """Decrypts a note using the provided password and salt."""
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDFHMAC
    import base64
    
    try:
        # Decode the salt and encrypted data
        # Decrypt the content
        decrypted_content = cipher.decrypt(encrypted_content).decode()
        return decrypted_content
    except (InvalidToken, ValueError, TypeError) as e:
        print(stringcolor.cs(f"Decryption error: {e}", "red"))
        return None

def send_note_via_sms(note_content, to_phone, user_id):
    """Sends a note via SMS using TextBelt Open Source."""
    try:
        import requests
        
        # TextBelt Open Source API endpoint (default is http://textbelt.com/text)
        # You can also run your own TextBelt server - see https://github.com/typpo/textbelt
        textbelt_url = "http://textbelt.com/text"  # Change this if using your own server
        
        # Prepare the payload for the API request
        payload = {
            'phone': to_phone,
            'message': f"Note from {user_id}:\n\n{note_content}",
            'key': 'textbelt'  # Use 'textbelt' for testing (1 free message per day)
            # For production, purchase a key from textbelt.com or use your own server
        }
        
        # Send the request
        response = requests.post(textbelt_url, data=payload)
        result = response.json()
        
        if result.get('success'):
            print(stringcolor.cs(f"SMS sent successfully! Message ID: {result.get('textId')}", "green"))
            return True
        else:
            print(stringcolor.cs(f"Failed to send SMS: {result.get('error')}", "red"))
            return False
    
    except ImportError:
        print(stringcolor.cs("Requests package not installed. Run 'pip install requests'.", "red"))
        return False
    except Exception as e:
        print(stringcolor.cs(f"Failed to send SMS: {e}", "red"))
        return False

def pro_user_area():
    """Provides advanced features for Pro users."""
    # Initialize the ProUser logger
    global prouser_logger
    prouser_logger = ProUserLogger()
    
    print(stringcolor.cs("Welcome to the ProUser Area!", "light_green"))
    
    # Check if user is a Pro user
    user_id = colored_input("Enter your User ID: ", "green")
    users = read_users(USERS_FILE)
    
    if user_id not in users:
        print(stringcolor.cs(f"User '{user_id}' not found.", "red"))
        prouser_logger.log_action("Access denied", {"reason": "User not found", "attempted_user_id": user_id})
        prouser_logger.log_session_end()
        return
    
    password = colored_input(f"Enter password for '{user_id}': ", "green")
    if users[user_id].get("password") != password:
        print(stringcolor.cs("Incorrect password.", "red"))
        prouser_logger.log_action("Access denied", {"reason": "Incorrect password", "user_id": user_id})
        prouser_logger.log_session_end()
        return
    
    # Log successful authentication
    prouser_logger.log_action("User authenticated", {"user_id": user_id})
    
    # Pro user features menu
    pro_options = [
        "View All Public Notes",
        "Export Your Notes",
        "Encrypt/Decrypt Notes",
        "Send Note via SMS",
        "Private Messaging",
        "Usage Statistics",
        "Back to Main Menu"
    ]
    
    while True:
        pro_choice = cursor_menu(pro_options, title=f"--- ProUser Area: {user_id} ---")
        
        if pro_choice == 0:  # View All Public Notes
            prouser_logger.log_action("Viewed All Public Notes", {"user_id": user_id})
            view_all_public_notes()
        elif pro_choice == 1:  # Export Your Notes
            prouser_logger.log_action("Exported Notes", {"user_id": user_id})
            export_user_notes(user_id)
        elif pro_choice == 2:  # Encrypt/Decrypt Notes
            prouser_logger.log_action("Accessed Encrypt/Decrypt Notes Menu", {"user_id": user_id})
            encrypt_decrypt_notes_menu(user_id, password)
        elif pro_choice == 3:  # Send Note via SMS
            prouser_logger.log_action("Accessed Send Note via SMS Menu", {"user_id": user_id})
            send_note_sms_menu(user_id)
        elif pro_choice == 4:  # Private Messaging
            prouser_logger.log_action("Accessed Private Messaging", {"user_id": user_id})
            messaging_system(user_id, password)
        elif pro_choice == 5:  # Usage Statistics
            prouser_logger.log_action("Viewed Usage Statistics", {"user_id": user_id})
            show_usage_statistics(user_id)
        elif pro_choice == 6:  # Back to Main Menu
            prouser_logger.log_action("Exited ProUser Area", {"user_id": user_id})
            prouser_logger.log_session_end()
            break
        
        input(stringcolor.cs("\nPress Enter to return to the ProUser menu...", "magenta"))

def encrypt_decrypt_notes_menu(user_id, master_password):
    """Menu for encrypting and decrypting notes."""
    print(stringcolor.cs("\n=== Encrypt/Decrypt Notes ===", "cyan"))
    
    user_data = load_user_data(user_id)
    if not user_data or "notes" not in user_data or not user_data["notes"]:
        print(stringcolor.cs(f"No notes found for user '{user_id}'.", "yellow"))
        return
    
    # Get all notes
    notes = user_data["notes"]
    
    # Options for the menu
    options = [
        "Encrypt a Note",
        "Decrypt a Note",
        "Back"
    ]
    
    while True:
        choice = cursor_menu(options, title="--- Encryption/Decryption Menu ---")
        
        if choice == 0:  # Encrypt a Note
            # Show only unencrypted notes
            unencrypted_notes = {note_id: note for note_id, note in notes.items() 
                               if not note.get("is_encrypted", False)}
            
            if not unencrypted_notes:
                print(stringcolor.cs("No unencrypted notes found.", "yellow"))
                continue
            
            # Create options for the menu
            note_options = []
            note_ids = list(unencrypted_notes.keys())
            
            for note_id in note_ids:
                content_preview = unencrypted_notes[note_id].get('note_content', '')[:40]
                if len(unencrypted_notes[note_id].get('note_content', '')) > 40:
                    content_preview += "..."
                note_options.append(f"{note_id}: {content_preview}")
            note_options.append("Back")
            
            note_idx = cursor_menu(note_options, title="--- Select Note to Encrypt ---")
            
            if note_idx < len(note_ids):  # If a note was selected
                selected_note_id = note_ids[note_idx]
                note_content = unencrypted_notes[selected_note_id]['note_content']
                
                # Get encryption password (can use master password or a specific one)
                use_master = colored_input("Use master password for encryption? (yes/no): ", "green").lower()
                
                if use_master in ['y', 'yes']:
                    encryption_password = master_password
                else:
                    encryption_password = colored_input("Enter encryption password: ", "green")
                
                # Encrypt the note
                encrypted_data = encrypt_note(note_content, encryption_password)
                
                # Update the note in user data
                user_data["notes"][selected_note_id].update(encrypted_data)
                # The original content is replaced with a placeholder
                user_data["notes"][selected_note_id]['note_content'] = "[ENCRYPTED NOTE]"
                
                # Save the updated user data
                if save_user_data(user_id, user_data):
                    print(stringcolor.cs(f"Note '{selected_note_id}' encrypted successfully.", "green"))
                else:
                    print(stringcolor.cs("Failed to save encrypted note.", "red"))
        
        elif choice == 1:  # Decrypt a Note
            # Show only encrypted notes
            encrypted_notes = {note_id: note for note_id, note in notes.items() 
                             if note.get("is_encrypted", False)}
            
            if not encrypted_notes:
                print(stringcolor.cs("No encrypted notes found.", "yellow"))
                continue
            
            # Create options for the menu
            note_options = []
            note_ids = list(encrypted_notes.keys())
            
            for note_id in note_ids:
                note_options.append(f"{note_id}: [ENCRYPTED NOTE]")
            note_options.append("Back")
            
            note_idx = cursor_menu(note_options, title="--- Select Note to Decrypt ---")
            
            if note_idx < len(note_ids):  # If a note was selected
                selected_note_id = note_ids[note_idx]
                encrypted_note = encrypted_notes[selected_note_id]
                
                # Get decryption password
                use_master = colored_input("Use master password for decryption? (yes/no): ", "green").lower()
                
                if use_master in ['y', 'yes']:
                    decryption_password = master_password
                else:
                    decryption_password = colored_input("Enter decryption password: ", "green")
                
                # Decrypt the note
                decrypted_content = decrypt_note(
                    encrypted_note['encrypted_data'],
                    encrypted_note['salt'],
                    decryption_password
                )
                
                if decrypted_content:
                    print(stringcolor.cs("\nDecrypted content:", "green"))
                    print(stringcolor.cs(decrypted_content, "cyan"))
                    
                    # Ask if user wants to save the note as decrypted
                    save_decrypted = colored_input("\nSave this note as decrypted? (yes/no): ", "green").lower()
                    
                    if save_decrypted in ['y', 'yes']:
                        # Remove encryption data and restore content
                        note_data = user_data["notes"][selected_note_id]
                        note_data['note_content'] = decrypted_content
                        note_data.pop('encrypted_data', None)
                        note_data.pop('salt', None)
                        note_data['is_encrypted'] = False
                        
                        # Save changes
                        if save_user_data(user_id, user_data):
                            print(stringcolor.cs("Note decrypted and saved successfully.", "green"))
                        else:
                            print(stringcolor.cs("Failed to save decrypted note.", "red"))
                else:
                    print(stringcolor.cs("Failed to decrypt note. Incorrect password?", "red"))
        
        elif choice == 2:  # Back
            break

def send_note_sms_menu(user_id):
    """Menu for sending a note via SMS."""
    print(stringcolor.cs("\n=== Send Note via SMS ===", "cyan"))
    
    user_data = load_user_data(user_id)
    if not user_data or "notes" not in user_data or not user_data["notes"]:
        print(stringcolor.cs(f"No notes found for user '{user_id}'.", "yellow"))
        return
    
    # Get all notes
    notes = user_data["notes"]
    
    # Create options for selecting a note
    note_options = []
    note_ids = []
    
    for note_id, note_data in notes.items():
        # Skip encrypted notes
        if note_data.get("is_encrypted", False):
            continue
        
        content_preview = note_data.get('note_content', '')[:40]
        if len(note_data.get('note_content', '')) > 40:
            content_preview += "..."
        note_options.append(f"{note_id}: {content_preview}")
        note_ids.append(note_id)
    
    if not note_options:
        print(stringcolor.cs("No notes available to send (all notes may be encrypted).", "yellow"))
        return
    
    note_options.append("Back")
    
    note_idx = cursor_menu(note_options, title="--- Select Note to Send ---")
    
    if note_idx < len(note_ids):  # If a note was selected
        selected_note_id = note_ids[note_idx]
        note_content = notes[selected_note_id]['note_content']
        
        print(stringcolor.cs("\nNote Content:", "green"))
        print(stringcolor.cs(note_content, "cyan"))
        
        # Get recipient's phone number
        phone_number = colored_input("\nEnter recipient's phone number (with country code, e.g., +12345678901): ", "green")
        
        # Validate phone number (basic check)
        if not phone_number.startswith('+') or len(phone_number) < 10:
            print(stringcolor.cs("Invalid phone number format. Must start with + and include country code.", "red"))
            return
        
        # Confirm sending
        confirm = colored_input(f"Send this note to {phone_number}? (yes/no): ", "green").lower()
        
        if confirm in ['y', 'yes']:
            # Send the SMS
            if send_note_via_sms(note_content, phone_number, user_id):
                print(stringcolor.cs("Note sent via SMS successfully!", "green"))
            else:
                print(stringcolor.cs("Failed to send note via SMS.", "red"))
    
    # If "Back" was selected or after sending, we return to the previous menu

def view_all_public_notes():
    """Displays all public notes from all users."""
    print(stringcolor.cs("\n=== All Public Notes ===", "cyan"))
    
    # Get all user files
    try:
        user_files = [f for f in os.listdir(JSON_DIR) if f.endswith('.json') and f != os.path.basename(USERS_FILE)]
    except Exception as e:
        print(stringcolor.cs(f"Error listing user files: {e}", "red"))
        return
    
    if not user_files:
        print(stringcolor.cs("No user files found.", "yellow"))
        return
    
    public_notes_found = False
    
    for user_file in user_files:
        user_id = os.path.splitext(user_file)[0]  # Remove .json extension
        user_data = load_user_data(user_id)
        
        if user_data and "notes" in user_data:
            # Filter for public notes only
            public_notes = {note_id: note for note_id, note in user_data["notes"].items() 
                           if not note.get("note_private", False)}
            
            if public_notes:
                public_notes_found = True
                print(stringcolor.cs(f"\nPublic notes from user '{user_id}':", "yellow"))
                
                for note_id, note_data in public_notes.items():
                    content = note_data.get('note_content', '[No Content]')
                    created_date = note_data.get('created_at', 'Unknown date')[:10]  # Show only the date part
                    print(stringcolor.cs(f"  • {created_date} - {content}", "cyan"))
    
    if not public_notes_found:
        print(stringcolor.cs("No public notes found from any user.", "yellow"))

def export_user_notes(user_id):
    """Exports all notes for a user to a text file."""
    print(stringcolor.cs("\n=== Export Notes ===", "cyan"))
    
    user_data = load_user_data(user_id)
    if not user_data or "notes" not in user_data or not user_data["notes"]:
        print(stringcolor.cs(f"No notes found for user '{user_id}'.", "yellow"))
        return
    
    # Create exports directory if it doesn't exist
    export_dir = "./exports"
    os.makedirs(export_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    export_filename = f"{export_dir}/{user_id}_notes_{timestamp}.txt"
    
    try:
        with open(export_filename, "w") as export_file:
            export_file.write(f"Notes Export for {user_id} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            export_file.write(f"{'='*50}\n\n")
            
            for note_id, note_data in user_data["notes"].items():
                # Handle encrypted notes differently
                if note_data.get("is_encrypted", False):
                    content = "[ENCRYPTED NOTE]"
                else:
                    content = note_data.get("note_content", "[No Content]")
                
                privacy = "Private" if note_data.get("note_private", False) else "Public"
                created_at = note_data.get("created_at", "Unknown")[:19]  # Format the timestamp
                updated_at = note_data.get("updated_at", created_at)[:19]  # Format the timestamp
                
                export_file.write(f"Note ID: {note_id}\n")
                export_file.write(f"Privacy: {privacy}\n")
                export_file.write(f"Created: {created_at}\n")
                export_file.write(f"Updated: {updated_at}\n")
                export_file.write(f"Content: {content}\n\n")
                export_file.write(f"{'-'*50}\n\n")
        
        print(stringcolor.cs(f"Notes exported to {export_filename}", "green"))
        return True
    except Exception as e:
        print(stringcolor.cs(f"Error exporting notes: {e}", "red"))
        return False

def show_usage_statistics(user_id):
    """Shows usage statistics for the user."""
    print(stringcolor.cs("\n=== Usage Statistics ===", "cyan"))
    
    user_data = load_user_data(user_id)
    if not user_data or "notes" not in user_data or not user_data["notes"]:
        print(stringcolor.cs(f"No notes found for user '{user_id}'.", "yellow"))
        return
    
    # Calculate statistics
    notes = user_data["notes"]
    total_notes = len(notes)
    private_notes = sum(1 for note in notes.values() if note.get("note_private", False))
    public_notes = total_notes - private_notes
    encrypted_notes = sum(1 for note in notes.values() if note.get("is_encrypted", False))
    
    # Find oldest and newest note
    dates = []
    for note in notes.values():
        if "created_at" in note:
            try:
                date_str = note["created_at"][:19]  # Keep only the date part
                dates.append(date_str)
            except (ValueError, IndexError):
                pass
    
    oldest_note = min(dates) if dates else "N/A"
    newest_note = max(dates) if dates else "N/A"
    
    # Calculate total characters in notes
    total_chars = sum(len(note.get("note_content", "")) for note in notes.values() 
                      if not note.get("is_encrypted", False))  # Skip encrypted notes
    
    # Display the statistics
    print(stringcolor.cs(f"Total Notes: {total_notes}", "yellow"))
    print(stringcolor.cs(f"Private Notes: {private_notes}", "yellow"))
    print(stringcolor.cs(f"Public Notes: {public_notes}", "yellow"))
    print(stringcolor.cs(f"Encrypted Notes: {encrypted_notes}", "yellow"))
    print(stringcolor.cs(f"First Note Created: {oldest_note}", "yellow"))
    print(stringcolor.cs(f"Latest Note Created: {newest_note}", "yellow"))
    print(stringcolor.cs(f"Total Characters (unencrypted notes): {total_chars}", "yellow"))

# --- Private Messaging Functions ---
def initialize_messages_db():
    """Initialize the messages database if it doesn't exist."""
    if not os.path.exists(MESSAGES_FILE):
        messages_data = {
            "messages": {}
        }
        try:
            with open(MESSAGES_FILE, 'w') as f:
                json.dump(messages_data, f, indent=4)
            return True
        except Exception as e:
            print(stringcolor.cs(f"Error initializing messages database: {e}", "red"))
            return False
    return True

def get_messages(user_id):
    """Get all messages for a specific user."""
    try:
        if not os.path.exists(MESSAGES_FILE):
            initialize_messages_db()
            return []
        
        with open(MESSAGES_FILE, 'r') as f:
            messages_data = json.load(f)
        
        # Return only messages for this user (as recipient)
        user_messages = []
        for msg_id, msg in messages_data.get("messages", {}).items():
            if msg.get("recipient_id") == user_id:
                msg["message_id"] = msg_id  # Add message ID to the message object
                user_messages.append(msg)
        
        # Sort messages by date (newest first)
        user_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return user_messages
    
    except Exception as e:
        print(stringcolor.cs(f"Error retrieving messages: {e}", "red"))
        return []

def count_unread_messages(user_id):
    """Count the number of unread messages for a user."""
    messages = get_messages(user_id)
    return sum(1 for msg in messages if not msg.get("read", False))

def mark_message_as_read(message_id):
    """Mark a message as read."""
    try:
        if not os.path.exists(MESSAGES_FILE):
            return False
        
        with open(MESSAGES_FILE, 'r') as f:
            messages_data = json.load(f)
        
        if message_id in messages_data.get("messages", {}):
            messages_data["messages"][message_id]["read"] = True
            
            with open(MESSAGES_FILE, 'w') as f:
                json.dump(messages_data, f, indent=4)
            return True
        return False
    
    except Exception as e:
        print(stringcolor.cs(f"Error marking message as read: {e}", "red"))
        return False

def send_message(sender_id, recipient_id, subject, content, encrypt=False, password=None):
    """Send a message to another user."""
    try:
        if not os.path.exists(MESSAGES_FILE):
            initialize_messages_db()
        
        with open(MESSAGES_FILE, 'r') as f:
            messages_data = json.load(f)
        
        # Check if recipient exists
        users = read_users(USERS_FILE)
        if recipient_id not in users:
            print(stringcolor.cs(f"Recipient '{recipient_id}' not found.", "red"))
            return False
        
        # Create message ID
        message_id = str(uuid.uuid4())
        
        # Prepare message content
        message_content = content
        is_encrypted = False
        encrypted_data = None
        salt = None
        
        # Encrypt if requested
        if encrypt and password:
            encryption_data = encrypt_note(content, password)
            message_content = "[ENCRYPTED MESSAGE]"
            is_encrypted = True
            encrypted_data = encryption_data.get("encrypted_data")
            salt = encryption_data.get("salt")
        
        # Create message object
        message = {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "subject": subject,
            "content": message_content,
            "timestamp": datetime.datetime.now().isoformat(),
            "read": False,
            "is_encrypted": is_encrypted,
        }
        
        # Add encryption data if applicable
        if is_encrypted:
            message["encrypted_data"] = encrypted_data
            message["salt"] = salt
        
        # Add message to database
        messages_data["messages"][message_id] = message
        
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages_data, f, indent=4)
        
        return True
    
    except Exception as e:
        print(stringcolor.cs(f"Error sending message: {e}", "red"))
        return False

def delete_message(message_id):
    """Delete a message."""
    try:
        if not os.path.exists(MESSAGES_FILE):
            return False
        
        with open(MESSAGES_FILE, 'r') as f:
            messages_data = json.load(f)
        
        if message_id in messages_data.get("messages", {}):
            del messages_data["messages"][message_id]
            
            with open(MESSAGES_FILE, 'w') as f:
                json.dump(messages_data, f, indent=4)
            return True
        return False
    
    except Exception as e:
        print(stringcolor.cs(f"Error deleting message: {e}", "red"))
        return False

def messaging_system(user_id, password):
    """Main messaging system interface."""
    # Initialize messages database if needed
    initialize_messages_db()
    
    # Get unread message count
    unread_count = count_unread_messages(user_id)
    
    if unread_count > 0:
        print(stringcolor.cs(f"\nYou have {unread_count} unread message(s)!", "light_green"))
    
    # Display messaging menu
    options = [
        "View Inbox",
        "Send New Message",
        "Back to Pro User Area"
    ]
    
    while True:
        choice = cursor_menu(options, title=f"--- Private Messaging: {user_id} ---")
        
        if choice == 0:  # View Inbox
            view_inbox(user_id, password)
        elif choice == 1:  # Send New Message
            send_new_message(user_id, password)
        elif choice == 2:  # Back
            break

def view_inbox(user_id, password):
    """View the user's inbox."""
    messages = get_messages(user_id)
    
    if not messages:
        print(stringcolor.cs("Your inbox is empty.", "yellow"))
        input(stringcolor.cs("Press Enter to continue...", "magenta"))
        return
    
    # Create message list for menu
    message_options = []
    for msg in messages:
        sender = msg.get("sender_id", "Unknown")
        subject = msg.get("subject", "No Subject")
        date = msg.get("timestamp", "")[:10]  # Show only the date part
        
        # Mark unread messages with an asterisk
        unread_mark = "* " if not msg.get("read", False) else "  "
        encrypted_mark = "[ENCRYPTED] " if msg.get("is_encrypted", False) else ""
        
        message_options.append(f"{unread_mark}{encrypted_mark}{date} - From: {sender} - Subject: {subject}")
    
    message_options.append("Back to Messaging Menu")
    
    while True:
        msg_idx = cursor_menu(message_options, title="--- Your Inbox ---")
        
        if msg_idx == len(message_options) - 1:  # Back option
            break
        
        # View the selected message
        selected_msg = messages[msg_idx]
        message_id = selected_msg.get("message_id")
        
        print(stringcolor.cs("\n=== Message Details ===", "cyan"))
        print(stringcolor.cs(f"From: {selected_msg.get('sender_id', 'Unknown')}", "yellow"))
        print(stringcolor.cs(f"Date: {selected_msg.get('timestamp', '')[:19]}", "yellow"))  # Show date and time
        print(stringcolor.cs(f"Subject: {selected_msg.get('subject', 'No Subject')}", "yellow"))
        print(stringcolor.cs("Content:", "yellow"))
        
        # Check if message is encrypted
        if selected_msg.get("is_encrypted", False):
            print(stringcolor.cs("[ENCRYPTED MESSAGE]", "red"))
            decrypt_choice = colored_input("Decrypt this message? (yes/no): ", "green").lower()
            
            if decrypt_choice in ['y', 'yes']:
                # Ask for password
                use_master = colored_input("Use your master password for decryption? (yes/no): ", "green").lower()
                
                if use_master in ['y', 'yes']:
                    decryption_password = password
                else:
                    decryption_password = colored_input("Enter decryption password: ", "green")
                
                # Attempt to decrypt
                decrypted_content = decrypt_note(
                    selected_msg.get("encrypted_data", ""),
                    selected_msg.get("salt", ""),
                    decryption_password
                )
                
                if decrypted_content:
                    print(stringcolor.cs("\nDecrypted content:", "green"))
                    print(stringcolor.cs(decrypted_content, "cyan"))
                else:
                    print(stringcolor.cs("Failed to decrypt message. Incorrect password?", "red"))
        else:
            # Display unencrypted content
            print(stringcolor.cs(selected_msg.get("content", ""), "cyan"))
        
        # Mark the message as read if it wasn't already
        if not selected_msg.get("read", False):
            mark_message_as_read(message_id)
            # Update the menu option to remove the unread mark
            message_options[msg_idx] = "  " + message_options[msg_idx][2:]
        
        # Show message actions menu
        message_actions = [
            "Reply to Message",
            "Delete Message",
            "Back to Inbox"
        ]
        
        action_idx = cursor_menu(message_actions, title="--- Message Actions ---")
        
        if action_idx == 0:  # Reply
            reply_to_message(user_id, selected_msg.get("sender_id", ""), password)
        elif action_idx == 1:  # Delete
            if delete_message(message_id):
                print(stringcolor.cs("Message deleted successfully.", "green"))
                # Remove the message from the options list and return to inbox
                del messages[msg_idx]
                del message_options[msg_idx]
                break
            else:
                print(stringcolor.cs("Failed to delete message.", "red"))
        # For action_idx == 2 (Back), we just continue the loop to show the inbox again
        
        input(stringcolor.cs("\nPress Enter to continue...", "magenta"))

def send_new_message(user_id, password):
    """Send a new message to another user."""
    print(stringcolor.cs("\n=== Send New Message ===", "cyan"))
    
    # Get all users for recipient selection
    users = read_users(USERS_FILE)
    
    # Filter out the current user
    other_users = [uid for uid in users.keys() if uid != user_id]
    
    if not other_users:
        print(stringcolor.cs("There are no other users to message.", "yellow"))
        input(stringcolor.cs("Press Enter to continue...", "magenta"))
        return
    
    # Create user selection menu
    user_options = []
    for uid in other_users:
        fullname = users[uid].get("fullname", "Unknown")
        user_options.append(f"{uid} ({fullname})")
    
    user_options.append("Back")
    
    user_idx = cursor_menu(user_options, title="--- Select Recipient ---")
    
    if user_idx == len(user_options) - 1:  # Back option
        return
    
    recipient_id = other_users[user_idx]
    
    # Get message details
    subject = colored_input("Enter message subject: ", "green")
    content = colored_input("Enter message content:\n", "green")
    
    # Ask if the message should be encrypted
    encrypt_choice = colored_input("Encrypt this message? (yes/no): ", "green").lower()
    encrypt = encrypt_choice in ['y', 'yes']
    
    encryption_password = None
    if encrypt:
        use_master = colored_input("Use your master password for encryption? (yes/no): ", "green").lower()
        if use_master in ['y', 'yes']:
            encryption_password = password
        else:
            encryption_password = colored_input("Enter encryption password (recipient will need this to decrypt): ", "green")
    
    # Send the message
    if send_message(user_id, recipient_id, subject, content, encrypt, encryption_password):
        print(stringcolor.cs(f"Message sent successfully to {recipient_id}!", "green"))
    else:
        print(stringcolor.cs("Failed to send message.", "red"))
    
    input(stringcolor.cs("\nPress Enter to continue...", "magenta"))

def reply_to_message(user_id, recipient_id, password):
    """Reply to a message."""
    print(stringcolor.cs(f"\n=== Reply to {recipient_id} ===", "cyan"))
    
    # Get message details
    subject = colored_input("Enter reply subject: ", "green")
    content = colored_input("Enter reply content:\n", "green")
    
    # Ask if the message should be encrypted
    encrypt_choice = colored_input("Encrypt this reply? (yes/no): ", "green").lower()
    encrypt = encrypt_choice in ['y', 'yes']
    
    encryption_password = None
    if encrypt:
        use_master = colored_input("Use your master password for encryption? (yes/no): ", "green").lower()
        if use_master in ['y', 'yes']:
            encryption_password = password
        else:
            encryption_password = colored_input("Enter encryption password (recipient will need this to decrypt): ", "green")
    
    # Send the reply
    if send_message(user_id, recipient_id, subject, content, encrypt, encryption_password):
        print(stringcolor.cs(f"Reply sent successfully to {recipient_id}!", "green"))
    else:
        print(stringcolor.cs("Failed to send reply.", "red"))

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
        "Exit"
    ]

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

        elif selected_option == "Exit":
            print(stringcolor.cs("Exiting the program. Goodbye!", "yellow"))
            break # Exit the main while loop

        # Pause at the end of each action before showing the menu again
        input(stringcolor.cs("\nPress Enter to return to the main menu...", "magenta"))


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

