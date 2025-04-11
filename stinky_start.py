import os
import datetime
import json
import random
import stringcolor

def show_menu():
    print("\n--- Menu ---")
    print("1. Add/Edit User")
    print("2. Delete User")
    print("2. Leave Note")
    print("3. Publish Note")
    print("4. Edit Notes")
    print("5. Delete Notes")
    
    print("6. Exit")

while True:
    show_menu()
    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("You selected: Add/Edit User")
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
