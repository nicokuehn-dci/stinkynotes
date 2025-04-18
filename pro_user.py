#!/usr/bin/env python3

import os
import json
import base64
from cryptography.fernet import Fernet
from stringcolor import cs
import sys

# Import menu functions from stinky_start.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from stinky_start import (
        cursor_menu, colored_input, load_user_data, save_user_data,
        get_user_notes, create_note_entry, USERS_FILE, MESSAGES_FILE
    )
except ImportError as e:
    print(f"Error importing from stinky_start.py: {e}")
    sys.exit(1)

def generate_key(password):
    """Generates a Fernet key based on a password."""
    password_bytes = password.encode()
    salt = b'stinkynotes_salt'  # Use a fixed salt for simplicity
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key

def encrypt_message(message, password):
    """Encrypts a message using a password."""
    key = generate_key(password)
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return encrypted_message.decode()

def decrypt_message(encrypted_message, password):
    """Decrypts a message using a password."""
    key = generate_key(password)
    fernet = Fernet(key)
    try:
        decrypted_message = fernet.decrypt(encrypted_message.encode())
        return decrypted_message.decode()
    except Exception as e:
        return None

def pro_user_menu(user_id):
    """Main menu for pro users."""
    options = [
        "Encrypt a Note",
        "Decrypt a Note",
        "View Encrypted Notes",
        "Back to Main Menu"
    ]

    while True:
        choice = cursor_menu(options, title=f"--- Pro User Area: {user_id} ---")

        if choice == 0:  # Encrypt a Note
            encrypt_note_menu(user_id)
        elif choice == 1:  # Decrypt a Note
            decrypt_note_menu(user_id)
        elif choice == 2:  # View Encrypted Notes
            view_encrypted_notes(user_id)
        elif choice == 3:  # Back to Main Menu
            break

def encrypt_note_menu(user_id):
    """Encrypts a note and saves it."""
    print(cs("\n=== Encrypt a Note ===", "cyan"))
    note_content = colored_input("Enter the note to encrypt: ", "green")
    if not note_content:
        print(cs("Encryption cancelled. Empty notes are not allowed.", "yellow"))
        return

    password = colored_input("Enter a password for encryption: ", "green")
    encrypted_note = encrypt_message(note_content, password)

    note_id = f"encrypted_note_{uuid.uuid4().hex[:8]}"
    create_note_entry(user_id, note_id, encrypted_note, True)

    print(cs(f"Encrypted note saved with ID: {note_id}", "green"))
    input(cs("\nPress Enter to continue...", "magenta"))

def decrypt_note_menu(user_id):
    """Decrypts a note."""
    print(cs("\n=== Decrypt a Note ===", "cyan"))
    notes = get_user_notes(user_id)
    encrypted_notes = {k: v for k, v in notes.items() if v.get('note_private', False)}

    if not encrypted_notes:
        print(cs("No encrypted notes found.", "yellow"))
        input(cs("\nPress Enter to continue...", "magenta"))
        return

    options = [f"{note_id}: {note_data.get('note_content', '')[:40]}..." for note_id, note_data in encrypted_notes.items()]
    options.append("Cancel")

    idx = cursor_menu(options, title="--- Select Note to Decrypt ---")
    if idx == len(options) - 1:  # Cancel option
        return

    selected_note_id = list(encrypted_notes.keys())[idx]
    encrypted_message = encrypted_notes[selected_note_id]['note_content']

    password = colored_input("Enter the password to decrypt: ", "green")
    decrypted_message = decrypt_message(encrypted_message, password)

    if decrypted_message:
        print(cs("\nDecrypted Message:", "cyan"))
        print(cs(decrypted_message, "green"))
    else:
        print(cs("Failed to decrypt the message. Incorrect password or corrupted data.", "red"))

    input(cs("\nPress Enter to continue...", "magenta"))

def view_encrypted_notes(user_id):
    """Displays all encrypted notes."""
    print(cs("\n=== Encrypted Notes ===", "cyan"))
    notes = get_user_notes(user_id)
    encrypted_notes = {k: v for k, v in notes.items() if v.get('note_private', False)}

    if not encrypted_notes:
        print(cs("No encrypted notes found.", "yellow"))
        input(cs("\nPress Enter to continue...", "magenta"))
        return

    for note_id, note_data in encrypted_notes.items():
        print(cs(f"\nNote ID: {note_id}", "yellow"))
        print(cs(f"Encrypted Content: {note_data.get('note_content', '[No Content]')}", "cyan"))
        print(cs("-" * 50, "white"))

    input(cs("\nPress Enter to continue...", "magenta"))

if __name__ == "__main__":
    print("This module should be imported from stinky_start.py, not run directly.")
    sys.exit(1)