import os
import datetime
import json
import random
from stringcolor import cs
from prompt_toolkit import prompt
from os import system
from datetime import datetime

filepath = "./stinkies/"

def read_users(file_path):
    """Reads the user data from the main JSON file.(stinky.json)"""
    with open(file_path, 'r') as file:
        users = json.load(file)
    return users

def write_users(file_path, users):
    """Writes the user data to the main JSON file.(stinky.json)"""
    with open(file_path, 'w') as file:
        json.dump(users, file, indent=4)

def create_user_json(user_id):
    """Creates a JSON file for the user with an empty notes dictionary. Uses the user_id as the filename."""
    data = {
            "user_id": user_id,
            "notes": {}
        }
    with open(f"{filepath}{user_id}.json", "w") as file:
        json.dump(data, file, indent=4)

def delete_user_json(user_id):
    """Deletes the user's JSON file."""
    try:
        os.remove(f"{filepath}{user_id}.json")
        print(f"User {user_id}.json file deleted successfully.")
    except FileNotFoundError:
        print(f"User {user_id}.json file not found.")

def is_password_correct(user_id, password):
    """Checks if the provided password matches the stored password for the user."""
    if password == users[user_id]["password"]:
            print("Logged in successfully.")  
            return True
    else: 
        print("Incorrect password.")
        return False

def print_user_notes(user_id):
    """Prints all notes for the given user ID."""
    with open(f"{filepath}{user_id}.json", "r") as file:
        data = json.load(file)
        notes = data["notes"]
    print(f"{user_id} has notes:")
    for note_id, note_data in notes.items():
        print(f"Note ID: {note_id} Content: {note_data['note_content']}")

def create_note_json(user_id, note_id, note_content, note_private):
    """Creates a note for the user with the given ID and stores it in the user's JSON file."""
    note_data = {
    "note_content": note_content,
    "note_private": note_private}
    with open(f"{filepath}{user_id}.json", "r") as file:
        data = json.load(file)
    data["notes"][note_id] = note_data
    with open(f"{filepath}{user_id}.json", "w") as file:
        json.dump(data, file, indent=4)

def bool_to_yes_no(b):
    return "Yes" if b else "No"

def yes_no_to_bool(text):
    lookup = {"yes": True, "no": False}
    return lookup.get(text.lower(), None)


def edit_note_per_id(note_id, user_id):
    """Edits the content of a note for the user with the given ID."""
    with open(f"{filepath}{user_id}.json", "r") as file:
        data = json.load(file)
    notes = data["notes"]
    original = notes[note_id]["note_content"]
    edited = prompt("Edit your note: ", default=original)
    print("Your new note: ", edited)
    notes[note_id]["note_content"] = edited
    
    original = bool_to_yes_no(notes[note_id]["note_private"])
    edited = prompt("Edit your note status: ", default=original)
    if edited.lower() != ("yes" or "no"):
        edited = "Yes"
        input("Invalid note status! Status set to private!")
    print("Your new status: ", edited)
    notes[note_id]["note_private"] = yes_no_to_bool(edited)
    
    data["notes"] = notes
    with open(f"{filepath}{user_id}.json", "w") as file:
        json.dump(data, file, indent=4)

def delete_note_per_id(note_id, user_id):
    """Deletes a note for the user with the given ID."""
    with open(f"{filepath}{user_id}.json", "r") as file:
        data = json.load(file)
    notes = data["notes"]
    del notes[note_id]
    data["notes"] = notes
    with open(f"{filepath}{user_id}.json", "w") as file:
        json.dump(data, file, indent=4)

def edit_user_notes(user_id):
    """Allows the user to edit their notes."""
    with open(f"{filepath}{user_id}.json", "r") as file:
        data = json.load(file)
    notes = data["notes"]
    
    system("clear")
    print(f"Which note from '{user_id}' would you like to edit?\n\n")

    notes_list = list(notes.items())
    for index, (key, value) in enumerate(notes_list, start=1):
        timestamp_dt = datetime.strptime(key, "%Y%m%d%H%M%S")
        formatted_date = timestamp_dt.strftime("%d.%m.%Y - %H:%M:%S")    
        print(f"Note #{index}:\n--------\n{formatted_date}\n{value['note_content']}\n")

    try:
        counter = int(input("\nEnter Note-# please: ")) - 1
    except:
        counter = -1

    if 0 <= counter < len(notes_list):
        selected_key, selected_note = notes_list[counter]
        edit_note_per_id(selected_key, user_id)
    else:
        print("Invalid note number.")

def delete_user_note(user_id):
    """Allows the user to delete their notes."""
    with open(f"{filepath}{user_id}.json", "r") as file:
        data = json.load(file)
    notes = data["notes"]
    
    system("clear")
    print(f"Which note from '{user_id}' would you like to delete?\n\n")

    notes_list = list(notes.items())
    for index, (key, value) in enumerate(notes_list, start=1):
        timestamp_dt = datetime.strptime(key, "%Y%m%d%H%M%S")
        formatted_date = timestamp_dt.strftime("%d.%m.%Y - %H:%M:%S")    
        print(f"Note #{index}:\n--------\n{formatted_date}\n{value['note_content']}\n")

    try:
        counter = int(input("\nEnter Note-# please: ")) - 1
    except:
        counter = -1

    if 0 <= counter < len(notes_list):
        selected_key, selected_note = notes_list[counter]
        delete_note_per_id(selected_key, user_id)
        print(f"Note deleted successfully.")
    else:    
        print("Invalid note number.")    

def list_all_public_notes(users):
    """Lists all public notes from all users."""
    notes = {}
    for user_id in users.keys():
        print(cs(f"{user_id}: ", "orange"))
        with open(f"{filepath}{user_id}.json", "r") as file:
            data = json.load(file)
        user_notes = data["notes"]
        for key, value in user_notes.items():
            if value["note_private"] == False:
                timestamp_dt = datetime.strptime(key, "%Y%m%d%H%M%S")
                formatted_date = timestamp_dt.strftime("%d.%m.%Y - %H:%M:%S")    
                print(f"{formatted_date} Note: {cs(value['note_content'], 'blue')}\n")
                notes[key] = value
    input()
    
def show_menu():
    """Displays the main menu."""
    print("\n--- Menu ---")
    print("1. Add/Edit User")
    print("2. Delete User")
    print("3. Create Note") 
    print("4. Edit User Notes")
    print("5. Delete Note")
    print("6. Print All Public Notes")
    print("7. ProUser Area")
    print("0. Exit")

def pro_user_area():
    """ProUser Area Menu Comming Soon ..."""
    print("\n--- ProUser Area ---\n Showing later by Nico")
    input()
    # print("1. Advanced Note Management")
    # print("2. Premium Support")
    # print("3. Customizable Themes")
    # print("4. Cloud Sync")
    # print("0. Back to Main Menu")
    # choice = input("\nEnter your choice: ")
    # if choice == "1":
    #     print("Advanced Note Management selected.")
    #     # Implement advanced note management features here
    # elif choice == "2":
    #     print("Premium Support selected.")
    #     # Implement premium support features here
    # elif choice == "3":
    #     print("Customizable Themes selected.")
    #     # Implement customizable themes features here
    # elif choice == "4":
    #     print("Cloud Sync selected.")
    #     # Implement cloud sync features here
    # elif choice == "0":
    #     return
    # else:
    #     print("Invalid option. Please try again.")

users = read_users(f'{filepath}stinky.json') # main dictionary with all users

while True:
    show_menu() # Display the menu
    choice = input("\nEnter your choice: ") 
    if choice == "1": # Add/Edit User
        print("You selected: Add/Edit User")
        user_id = input("Add user ID: ")
        if user_id in users:
            password = input(f"User {user_id} already exists. Please enter your password:")
            if is_password_correct(user_id, password):
                fullname = input("Change Full Name: ")
                password = input("Change Password: ")
        else:          
            fullname = input("Add Full Name: ")
            password = input("Add Password: ")
            create_user_json(user_id)
        users[user_id] = {
            "fullname": fullname,
            "password": password
        }
        write_users(f'{filepath}stinky.json', users)
        print(f"User {user_id} added successfully.")

    elif choice == "2": # Delete User
        print("You selected: Delete User")
        user_id = input("Enter user ID to delete: ")
        if user_id in users:
            password = input(f"Please enter your password:")
            if is_password_correct(user_id, password):
                delete_user_json(user_id)
                users.pop(user_id)
                write_users(f'{filepath}stinky.json', users)
                print(f"User {user_id} deleted successfully.")
            else:
                print("Incorrect password.")
                continue
        else:
            print(f"User {user_id} not found.")

    elif choice == "3": # Create Note
        print("You selected: Create Note")
        user_id = input("Log in to create a note for: ")
        if user_id not in users:
            print(f"User {user_id} not found.")
            input()
            continue
        else:
            password = input("Enter password: ")
            if password == users[user_id]["password"]:
                print("Logged in successfully.")
                note_id = datetime.now().strftime("%Y%m%d%H%M%S")
                note_content = input("Enter note content: ")
                note_private = input("Is this note private? (yes/no): ").lower()
                if note_private == "yes" or note_private == "y":
                    note_private = True
                elif note_private == "no" or note_private == "n":
                    note_private = False
                else:
                    print("Invalid input. Defaulting to public.")
                    note_private = True
                create_note_json(user_id, note_id, note_content, note_private)
            else:
                print("Incorrect password.")
                continue

    elif choice == "4": # Edit User Notes
        print("You selected: Edit Notes")
        user_id = input("Log in to edit notes for: ")
        password = input("Enter password: ")
        if is_password_correct(user_id, password):
            edit_user_notes(user_id)
        else:
            continue
        
    elif choice == "5": # Delete Note
        print("Delete a Note")
        user_id = input("Log in to delete a note for: ")
        if user_id not in users:
            print(f"User {user_id} not found.")
            input()
            continue
        else:
            password = input("Enter password: ")
            if is_password_correct(user_id, password):
                delete_user_note(user_id)
            else:
                print("Incorrect password.")
                continue

    elif choice == "6": # Print All Public Notes
        system("clear")
        print(f"A list of all public notes:\n")
        list_all_public_notes(users)

    elif choice == "7": # ProUser Area
        pro_user_area()

    elif choice == "0":
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid option. Please try again.")
