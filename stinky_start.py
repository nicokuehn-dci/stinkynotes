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
            "notes": []
        }
    with open(f"./JSON/{user_id}.json", "w") as file:
        json.dump(data, file, indent=4)
    
def show_menu():
    print("\n--- Menu ---")
    print("1. Add/Edit Userinfo")
    print("2. Delete User")
    print("2. Leave Note")
    print("3. Publish Note") #dont forget to add datetime stuff
    print("4. Edit Notes")
    print("5. Delete Notes")
    
    print("6. Exit")

users = read_users('./JSON/stinky.json') #main dictionary with all users

while True:
    show_menu()
    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("You selected: Add/Edit User")
        user_id = input("Add user ID: ")
        fullname = input("Add Full Name: ")
        password = input("Add Password: ")
        users[user_id] = {
            "fullname": fullname,
            "password": password
        }
        write_users('./JSON/stinky.json', users)
        create_user_json(user_id)
        print(f"User {user_id} added successfully.")
        # Add/Edit User logic here
    elif choice == "2":
        print("You selected: Leave Note")
        # Leave Note logic here
    elif choice == "3":
        print("You selected: Publish Note")
        # Publish Note logic here
    elif choice == "4":
        print("You selected: Edit Notes")
        # Edit Notes logic here
    elif choice == "5":
        print("You selected: Delete Notes")
        # Delete Notes logic here
    elif choice == "6":
        print("Exiting the program. Goodbye!")
        break
    else:
        print("Invalid option. Please try again.")

print(users)