import os
import datetime
import json
import random
import stringcolor

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
        "note_private": note_private}
        with open(f"./JSON/{user_id}.json", "r") as file:
            data = json.load(file)
        data["notes"][note_id] = note_data
        with open(f"./JSON/{user_id}.json", "w") as file:
            json.dump(data, file, indent=4)

        
    
    
    
def show_menu():
    print("\n--- Menu ---")
    print("1. Add/Edit User")
    print("2. Delete User")
    print("3. Create Note") #dont forget to add datetime stuff
    print("5. Edit Note")
    print("6. Delete Note")
    
    print("0. Exit")

users = read_users('./JSON/stinky.json') #main dictionary with all users

while True:
    show_menu()
    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("You selected: Add/Edit User")
        user_id = input("Add user ID: ")
        if user_id in users:
            print(f"User {user_id} already exists. You can change Fullname and Password.")
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
        if password == users[user_id]["password"]:
            print("Logged in successfully.")
            note_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
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
        # Publish Note logic here
    elif choice == "4":
        print("You selected: Edit Notes")
        # Edit Notes logic here
    elif choice == "5":
        print("You selected: Delete Notes")
        # Delete Notes logic here
    elif choice == "0":
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid option. Please try again.")

print(users)