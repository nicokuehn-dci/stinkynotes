# StinkyNotes

## Overview
StinkyNotes is a Python-based note management application that allows users to create, edit, and manage notes. It supports both regular users and ProUsers with advanced features like encrypted notes.

## Features
- Add, edit, and delete user accounts.
- Create and manage notes.
- ProUser features:
  - Encrypted notes for added security.
  - Priority support.
  - Unlimited storage for notes.
- JSON-based storage for user data and notes.

## How to Run
1. Ensure you have Python 3 installed on your system.
2. Clone or download the repository.
3. Navigate to the project directory.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   python3 stinky_start.py
   ```

## JSON Storage Structure
- All user data and notes are stored in the `JSON` directory.
- Each user has a separate JSON file named `<user_id>.json`.
- The main user database is stored in `stinky.json`.

## Multi-line Input Instructions
When entering multi-line input (e.g., note content):
- On Linux/macOS: Press `Ctrl+D` on an empty line to finish.
- On Windows: Press `Ctrl+Z` then `Enter` on an empty line to finish.

## Dependencies
- `stringcolor`: For colored terminal output.
- `cryptography`: For encryption and decryption of notes.
- `twilio`: For potential SMS notifications (future feature).
- `windows-curses`: Provides curses support on Windows (built-in on Linux/macOS).

## Notes
- Ensure the `JSON` directory exists in the project root.
- The application generates an encryption key on each run. Keep it secure for decrypting notes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
