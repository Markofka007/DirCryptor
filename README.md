# DirCryptor
A tool for encrypting/decrypting directories using a password key. This works on Windows and Linux (and probably Mac too). I was tinkering with simple file encryption methods and decided to make a script that can recursively encrypt an entire directory, which could be useful for securing directories with sensitive information. Also, since I am kind of a noob with cryptography, ChatGPT did help me with some of this project.
Ideally, this is a script that you should keep on a flash drive and run it from the flash drive when you need encryption/decryption since I have a hardcoded salt in the script. But either way, even if the salt is known, it should still be secure enough from the password alone. Plus, the salt would still be an obstacle for anyone who tries to bruteforce the encryption with rainbow tables.

# Key Features
1. **Key Derivation**
   - You enter a password, which is run through PBKDF2-HMAC-SHA256 (with a fixed salt) to produce a symmetric key. This key is not stored anywhere, so you will need to remember that password for decryption later.

2. **Encryption and Integrity File**
   - Every file in the folder (and its subfolders) is encrypted. It also appends ".enc" to the file name to indicate it was encrypted.
   - A hidden `.integrity_check` file is created at the root of the chosen directory which contains the encrypted constant `INTEGRITY_OK`.

3. **Decryption**
   - Before touching any encrypted files, the script first decrypts `.integrity_check` and confirms it decrypts to `INTEGRITY_OK`. If that passes, then it continues to decrypt every `.enc` file and restore their original names.

4. **Integrity-Only Mode**
   - You can also choose “Integrity Check” mode to verify your password (and salt) without decrypting anything. This will only decrypt `.integrity_check` and confirms it decrypts to `INTEGRITY_OK`. This is useful for confirming that you have the right key without needing to actually decrypt all files (which can be time-consuming if there's a lot).

# Usage
1. Make sure that the cryptography library is installed with `pip install cryptography`.
2. TKinter should come with the Python standard library, but if you're on Linux and missing it for some reason (like I was) you can install it with `sudo apt install python3-tk`.
3. Run the script, and it will open a file explorer to have you choose a directory to encrypt/decrypt.
4. Choose "E" for Encrpyt, "D" for Decrypt, or "I" for a password check without decrypting the files.
5. Enter a password and watch it do its thing.

