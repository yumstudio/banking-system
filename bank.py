import random
import re
import sqlite3

# Database Setup
conn = sqlite3.connect("banking_system.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    account_number TEXT UNIQUE NOT NULL,
    dob TEXT NOT NULL,
    city TEXT NOT NULL,
    password TEXT NOT NULL,
    balance REAL NOT NULL,
    contact_number TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    address TEXT NOT NULL,
    active INTEGER DEFAULT 1
)''')
cursor.execute("""
ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1
""")


cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_number) REFERENCES users (account_number)
)''')

conn.commit()

# Utility Functions
def validate_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

def validate_contact(contact):
    return re.match(r"^\d{10}$", contact)

def validate_password(password):
    return re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

def generate_account_number():
    return str(random.randint(1000000000, 9999999999))

def add_user():
    name = input("Enter name: ")
    dob = input("Enter date of birth (YYYY-MM-DD): ")
    city = input("Enter city: ")

    while True:
        password = input("Enter password (at least 8 characters)")
        if validate_password(password):
             break
        else:
            print("Invalid password format!")

    while True:
      try:
        balance = float(input("Enter initial balance (minimum 2000): "))
        if balance < 2000:
            print("Balance must be at least 2000.")
        else:
          break
      except ValueError:
            print("Invalid input!")

    while True:
        contact_number = input("Enter contact number: ")
        if validate_contact(contact_number):
            break
        else:
            print("Invalid contact number!")

    while True:
        email = input("Enter email: ")
        if validate_email(email):
            break
        else:
            print("Invalid email format!")

    address = input("Enter address: ")
    account_number = generate_account_number()

    try:
        cursor.execute('''INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email, address)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (name, account_number, dob, city, password, balance, contact_number, email, address))
        conn.commit()
        print(f"User created successfully! Account Number: {account_number}")
    except sqlite3.IntegrityError:
        print("Error: Email or contact number already exists.")

def show_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"\nID: {user[0]}\nName: {user[1]}\nAccount Number: {user[2]}\nBalance: {user[6]}\nEmail: {user[8]}")

def login():
    account_number = input("Enter account number: ")
    password = input("Enter password: ")

    cursor.execute("SELECT * FROM users WHERE account_number = ? AND password = ? AND active = 1", (account_number, password))
    user = cursor.fetchone()

    if user:
        print("Login successful!")
        user_dashboard(user)
    else:
        print("Invalid credentials or inactive account.")

def user_dashboard(user):
    while True:
        print("\n1. Show Balance\n2. Show Transactions\n3. Credit\n4. Debit\n5. Transfer\n6. Change Password\n7. Logout")
        choice = input("Enter choice: ")

        if choice == "1":
            print(f"Current Balance: {user[6]}")
        elif choice == "2":
            cursor.execute("SELECT * FROM transactions WHERE account_number = ?", (user[2],))
            for t in cursor.fetchall():
                print(f"Transaction ID: {t[0]}, Type: {t[2]}, Amount: {t[3]}, Date: {t[4]}")
        elif choice == "3":
            amount = float(input("Enter amount to credit: "))
            cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, user[2]))
            cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (?, 'Credit', ?)", (user[2], amount))
            conn.commit()
            print("Amount credited.")
        elif choice == "4":
            amount = float(input("Enter amount to debit: "))
            if amount > user[6]:
                print("Insufficient funds.")
            else:
                cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number = ?", (amount, user[2]))
                cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (?, 'Debit', ?)", (user[2], amount))
                conn.commit()
                print("Amount debited.")
        elif choice == "5":
            target_account = input("Enter target account: ")
            amount = float(input("Enter amount to transfer: "))
            if amount > user[6]:
                print("Insufficient funds.")
            else:
                cursor.execute("UPDATE users SET balance = balance - ? WHERE account_number = ?", (amount, user[2]))
                cursor.execute("UPDATE users SET balance = balance + ? WHERE account_number = ?", (amount, target_account))
                cursor.execute("INSERT INTO transactions (account_number, transaction_type, amount) VALUES (?, 'Transfer', ?)", (user[2], amount))
                conn.commit()
                print("Transfer complete.")
        elif choice == "6":
            new_password = input("Enter new password: ")
            if validate_password(new_password):
                cursor.execute("UPDATE users SET password = ? WHERE account_number = ?", (new_password, user[2]))
                conn.commit()
                print("Password updated.")
            else:
                print("Invalid password format.")
        elif choice == "7":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

def main():
    while True:
        print("\n1. Add User\n2. Show Users\n3. Login\n4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_user()
        elif choice == "2":
            show_users()
        elif choice == "3":
            login()
        elif choice == "4":
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
