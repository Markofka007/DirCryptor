import os
import sys
import getpass
import base64
import tkinter as tk
from tkinter import filedialog

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# ---------------------------- CONFIG ---------------------------------
# You probably don't need to change any of these!!!
SALT = b"16_bytes_of_salt"  #Static salt (MUST BE EXACTLY 16 BYTES)
CHECK_NAME = ".integrity_check"  #Integrity check file name
CHECK_PLAINTEXT = b"INTEGRITY_OK"  #Integrity check flag
# ---------------------------------------------------------------------

#Target directory
TARGET_DIR = None


def choose_directory():
    """Ask user to choose a target directory with file explorer."""
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select directory to encrypt/decrypt")
    root.destroy()
    if not folder:
        print("No directory selected. Exiting.")
        pause()
        sys.exit(1)
    return folder


def derive_key(password: bytes, salt: bytes) -> bytes:
    """Create a base64-encoded key from password and salt using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


def encrypt_file(path: str, fernet: Fernet):
    data = open(path, "rb").read()
    token = fernet.encrypt(data)
    with open(path + ".enc", "wb") as f:
        f.write(token)
    os.remove(path)


def decrypt_file(path: str, fernet: Fernet):
    token = open(path, "rb").read()
    data = fernet.decrypt(token)
    orig = path[:-4]  #Remove .enc from files
    with open(orig, "wb") as f:
        f.write(data)
    os.remove(path)


def write_integrity_file(fernet: Fernet):
    token = fernet.encrypt(CHECK_PLAINTEXT)
    with open(os.path.join(TARGET_DIR, CHECK_NAME), "wb") as f:
        f.write(token)


def verify_integrity(fernet: Fernet) -> bool:
    path = os.path.join(TARGET_DIR, CHECK_NAME)
    try:
        token = open(path, "rb").read()
        return fernet.decrypt(token) == CHECK_PLAINTEXT
    except (FileNotFoundError, InvalidToken):
        return False


def process_directory(mode: str, fernet: Fernet):
    for root, _, files in os.walk(TARGET_DIR):
        for fname in files:
            fp = os.path.join(root, fname)
            try:
                if mode == "encrypt":
                    if fname == CHECK_NAME or fname.endswith(".enc"):
                        continue
                    encrypt_file(fp, fernet)
                    print(f"[+] Encrypted: {fp}")
                elif mode == "decrypt":
                    if not fname.endswith(".enc"):
                        continue
                    decrypt_file(fp, fernet)
                    print(f"[+] Decrypted: {fp}")
            except Exception as e:
                print(f"[!] Failed to {mode} {fp}: {e}")


def pause():
    """Pause before immediately exiting to give you a moment to see messages."""
    try:
        input("Press Enter to exit...")
    except EOFError:
        pass


def main():
    global TARGET_DIR
    TARGET_DIR = choose_directory()

    choice = input("Do you want to (E)ncrypt, (D)ecrypt, or (I)ntegrity Check? ").strip().lower()
    if choice.startswith("e"):
        mode = "encrypt"
    elif choice.startswith("d"):
        mode = "decrypt"
    elif choice.startswith("i"):
        mode = "check"
    else:
        print("Invalid choice; enter E, D, or I.")
        pause()
        sys.exit(1)

    #Encryption branch
    if mode == "encrypt":
        pwd = getpass.getpass("Enter new password: ").strip().encode()
        confirm = getpass.getpass("Confirm password: ").strip().encode()
        max_tries = 3
        tries = 1
        while pwd != confirm and tries < max_tries:
            print("✗ Passwords do not match, try again.")
            pwd = getpass.getpass("Enter new password: ").strip().encode()
            confirm = getpass.getpass("Confirm password: ").strip().encode()
            tries += 1
        if pwd != confirm:
            print("✗ Passwords still don’t match. Aborting.")
            pause()
            sys.exit(1)
        if len(pwd) < 8:
            print("⚠ Warning: Password is shorter than 8 characters.")
        key = derive_key(pwd, SALT)
        f = Fernet(key)

        integrity_path = os.path.join(TARGET_DIR, CHECK_NAME)
        if os.path.exists(integrity_path):
            print("✗ Directory already appears encrypted (integrity file exists). Aborting.")
            pause()
            sys.exit(1)

        write_integrity_file(f)
        process_directory("encrypt", f)
        print("✓ Encryption complete; integrity check created.")
        pause()

    #Decryption branch
    elif mode == "decrypt":
        pwd = getpass.getpass("Enter password: ").strip().encode()
        key = derive_key(pwd, SALT)
        f = Fernet(key)

        if not verify_integrity(f):
            print("✗ Wrong password (integrity check failed). Aborting.")
            pause()
            sys.exit(2)

        os.remove(os.path.join(TARGET_DIR, CHECK_NAME))
        process_directory("decrypt", f)
        print("✓ Decryption complete.")
        pause()

    #Integrity check branch (used to verify a password without decrypting)
    else:  # mode == "check"
        pwd = getpass.getpass("Enter password for integrity check: ").strip().encode()
        key = derive_key(pwd, SALT)
        f = Fernet(key)

        if verify_integrity(f):
            print("✓ Integrity check passed: correct password.")
        else:
            print("✗ Integrity check failed: wrong password or no integrity file.")
        pause()
        sys.exit(0)

if __name__ == "__main__":
    main()
