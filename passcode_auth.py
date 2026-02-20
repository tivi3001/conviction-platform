import os
import sys
from getpass import getpass

CORRECT_PASSCODE = "241117"
MAX_ATTEMPTS = 3

def authenticate():
    """Prompt user for passcode, return True if correct."""
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        passcode = getpass("Enter passcode to start monitoring: ")

        if passcode == CORRECT_PASSCODE:
            print("✅ Authentication successful")
            return True
        else:
            attempts += 1
            remaining = MAX_ATTEMPTS - attempts
            if remaining > 0:
                print(f"❌ Incorrect passcode. {remaining} attempts remaining.")
            else:
                print("❌ Authentication failed. Exiting.")
                return False

    return False

def require_auth():
    """Require authentication or exit."""
    if not authenticate():
        sys.exit(1)

if __name__ == "__main__":
    if authenticate():
        print("Authentication passed")
    else:
        print("Authentication failed")
        sys.exit(1)
