# StinkyNotes - Nico Branch

StinkyNotes is a feature-rich note-taking application designed for both regular and Pro users. This branch introduces advanced features, intelligent error handling, and a robust ProUser area.

## Features

### General Features
- **Add/Edit User**: Create or modify user profiles.
- **Delete User**: Remove user profiles and their associated data.
- **Create Note**: Add new notes to your account.
- **Edit User Notes**: Modify existing notes.
- **Exit**: Safely exit the application.

### ProUser Area Features
ProUsers have access to advanced features, including:
- **Create Encrypted Note**: Add notes with advanced encryption for enhanced security.
- **View Encrypted Notes**: View all encrypted notes.
- **Edit Encrypted Note**: Modify the content of encrypted notes.
- **Delete Encrypted Note**: Remove encrypted notes from your account.
- **Decrypt and View Note**: Decrypt and view the content of encrypted notes.

### Intelligent Error Handling
The application includes a self-healing mechanism to handle errors and ensure smooth operation:
- **Dependency Management**: Automatically checks and installs missing dependencies.
- **Virtual Environment Setup**: Ensures a virtual environment is created and activated before running the application.
- **Error Logging**: Logs all errors to `stinkynotes.log` for debugging.
- **Self-Repair**: Reads the log file on exit, attempts to fix errors, and removes fixed entries from the log.
- **Common Error Fixes**:
  - Recreates missing files.
  - Resets corrupted JSON files.
  - Skips invalid encrypted notes.

## How to Run
1. Clone the repository and navigate to the project directory.
2. Run the application:
   ```bash
   python3 stinky_start.py
   ```
3. Follow the on-screen instructions to set up dependencies and start using the application.

## Requirements
- Python 3.12 or higher
- Required Python packages (automatically installed):
  - `stringcolor`
  - `cryptography`
  - `twilio`
  - `string-color`

## File Structure
- `stinky_start.py`: Main application script.
- `requirements.txt`: Lists required Python packages.
- `stinkynotes.log`: Log file for error tracking and debugging.
- `JSON/`: Directory containing user data files.

## Notes
- Ensure Python is installed on your system.
- For ProUser features, you must log in with a ProUser account.
- The application automatically handles most errors and maintains a clean log file.

## License
This project is licensed under the terms of the LICENSE file included in the repository.
