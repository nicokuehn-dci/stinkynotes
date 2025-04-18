#!/usr/bin/env python3

import os
import json
import datetime
import uuid
import stringcolor
from stringcolor import cs
import sys

# Import menu functions from stinky_start.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from stinky_start import (
        cursor_menu, colored_input, read_users, write_users,
        load_user_data, save_user_data, get_user_notes,
        create_note_entry, edit_note_menu, USERS_FILE, JSON_DIR, 
        get_user_file_path, create_user_json
    )
except ImportError as e:
    print(f"Error importing from stinky_start.py: {e}")
    sys.exit(1)

def main_user_menu(user_id):
    """Main menu for normal users."""
    options = [
        "Create New Note",
        "View Your Notes",
        "Edit Notes",
        "Delete Note",
        "Account Settings",
        "Logout"
    ]
    
    while True:
        choice = cursor_menu(options, title=f"--- StinkyNotes: {user_id} ---")
        
        if choice == 0:  # Create New Note
            create_new_note(user_id)
        elif choice == 1:  # View Your Notes
            view_user_notes(user_id)
        elif choice == 2:  # Edit Notes
            edit_note_menu(user_id)
        elif choice == 3:  # Delete Note
            delete_note(user_id)
        elif choice == 4:  # Account Settings
            account_settings(user_id)
        elif choice == 5:  # Logout
            print(stringcolor.cs("Logging out...", "yellow"))
            break


def create_new_note(user_id):
    """Creates a new note for the user."""
    print(stringcolor.cs("\n=== Create New Note ===", "cyan"))
    
    note_content = colored_input("Enter your note: ", "green")
    if not note_content:
        print(stringcolor.cs("Note creation cancelled. Empty notes are not allowed.", "yellow"))
        return
    
    privacy_choice = colored_input("Make this note private? (yes/no): ", "green").lower()
    note_private = privacy_choice in ('y', 'yes')
    
    note_id = f"note_{uuid.uuid4().hex[:8]}"  # Generate a unique note ID
    create_note_entry(user_id, note_id, note_content, note_private)
    
    print(stringcolor.cs(f"Note created with ID: {note_id}", "green"))
    input(stringcolor.cs("\nPress Enter to continue...", "magenta"))


def view_user_notes(user_id):
    """Shows all notes for the current user."""
    print(stringcolor.cs("\n=== Your Notes ===", "cyan"))
    
    notes = get_user_notes(user_id)
    if not notes:
        print(stringcolor.cs("You don't have any notes yet.", "yellow"))
        input(stringcolor.cs("\nPress Enter to continue...", "magenta"))
        return
    
    # Sort notes by date (newest first) if they have timestamps
    sorted_notes = []
    for note_id, note_data in notes.items():
        note_with_id = note_data.copy()
        note_with_id['note_id'] = note_id
        sorted_notes.append(note_with_id)
    
    try:
        sorted_notes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    except Exception:
        # If sorting fails, just use the original order
        pass
    
    for note in sorted_notes:
        note_id = note['note_id']
        privacy = "Private" if note.get('note_private', False) else "Public"
        content = note.get('note_content', '[No Content]')
        created_at = note.get('created_at', 'Unknown date')[:19]  # Format timestamp
        
        print(stringcolor.cs(f"\nNote ID: {note_id}", "yellow"))
        print(stringcolor.cs(f"Created: {created_at}", "white"))
        print(stringcolor.cs(f"Privacy: {privacy}", "white"))
        print(stringcolor.cs(f"Content: {content}", "cyan"))
        print(stringcolor.cs("-" * 50, "white"))
    
    input(stringcolor.cs("\nPress Enter to continue...", "magenta"))


def delete_note(user_id):
    """Deletes a note."""
    print(stringcolor.cs("\n=== Delete Note ===", "cyan"))
    
    user_data = load_user_data(user_id)
    if user_data is None or "notes" not in user_data or not user_data["notes"]:
        print(stringcolor.cs("No notes to delete.", "yellow"))
        input(stringcolor.cs("\nPress Enter to continue...", "magenta"))
        return
    
    notes = user_data["notes"]
    note_ids = list(notes.keys())
    options = []
    
    for note_id in note_ids:
        content_preview = notes[note_id].get('note_content', '')[:40]
        if len(notes[note_id].get('note_content', '')) > 40:
            content_preview += "..."
        privacy = "(Private)" if notes[note_id].get('note_private', False) else "(Public)"
        options.append(f"{note_id}: {content_preview} {privacy}")
    
    options.append("Cancel")
    
    idx = cursor_menu(options, title="--- Select Note to Delete ---")
    
    if idx == len(options) - 1:  # Cancel option
        return
    
    selected_note_id = note_ids[idx]
    confirm = colored_input(f"Are you sure you want to delete note '{selected_note_id}'? (yes/no): ", "red").lower()
    
    if confirm in ('y', 'yes'):
        # Remove the note from user data
        del user_data["notes"][selected_note_id]
        
        # Save updated user data
        if save_user_data(user_id, user_data):
            print(stringcolor.cs(f"Note '{selected_note_id}' deleted successfully.", "green"))
        else:
            print(stringcolor.cs("Failed to delete note.", "red"))
    else:
        print(stringcolor.cs("Note deletion cancelled.", "yellow"))
    
    input(stringcolor.cs("\nPress Enter to continue...", "magenta"))


def account_settings(user_id):
    """Manages user account settings."""
    print(stringcolor.cs("\n=== Account Settings ===", "cyan"))
    
    options = [
        "Change Password",
        "Delete Account",
        "Back"
    ]
    
    choice = cursor_menu(options, title="--- Account Settings ---")
    
    if choice == 0:  # Change Password
        change_password(user_id)
    elif choice == 1:  # Delete Account
        delete_account(user_id)
    # If Back is selected, we just return to the previous menu


def change_password(user_id):
    """Changes the user's password."""
    users = read_users(USERS_FILE)
    
    if user_id not in users:
        print(stringcolor.cs("User not found.", "red"))
        return
    
    current_password = colored_input("Enter current password: ", "green")
    if users[user_id].get("password") != current_password:
        print(stringcolor.cs("Incorrect current password.", "red"))
        return
    
    new_password = colored_input("Enter new password: ", "green")
    if not new_password:
        print(stringcolor.cs("Password cannot be empty.", "red"))
        return
    
    confirm_password = colored_input("Confirm new password: ", "green")
    if new_password != confirm_password:
        print(stringcolor.cs("Passwords don't match.", "red"))
        return
    
    # Update password
    users[user_id]["password"] = new_password
    write_users(USERS_FILE, users)
    print(stringcolor.cs("Password changed successfully.", "green"))


def delete_account(user_id):
    """Deletes the user's account."""
    print(stringcolor.cs("\n=== Delete Account ===", "red"))
    print(stringcolor.cs("WARNING: This will permanently delete your account and all your notes!", "red"))
    
    confirm = colored_input("Type your username to confirm deletion: ", "red")
    if confirm != user_id:
        print(stringcolor.cs("Account deletion cancelled.", "yellow"))
        return
    
    users = read_users(USERS_FILE)
    if user_id not in users:
        print(stringcolor.cs("User not found.", "red"))
        return
    
    # Delete user from main database
    del users[user_id]
    write_users(USERS_FILE, users)
    
    # Delete user's note file
    try:
        user_file = get_user_file_path(user_id)
        if os.path.exists(user_file):
            os.remove(user_file)
    except Exception as e:
        print(stringcolor.cs(f"Error removing user file: {e}", "red"))
    
    print(stringcolor.cs("Account deleted successfully.", "green"))
    return True  # Indicate account was deleted to trigger logout


if __name__ == "__main__":
    print("This module should be imported from stinky_start.py, not run directly.")
    sys.exit(1)