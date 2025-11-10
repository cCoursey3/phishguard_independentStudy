import mysql.connector
import hashlib

def hash_pin(pin):
    """Hashes the PIN using SHA-256."""
    return hashlib.sha256(pin.encode()).hexdigest()

def signup(username, pin):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='manager',
            password='gl33bieWeedyK!tty',
            database='user_DB'
        )
        cursor = conn.cursor()
        hashed_pin = hash_pin(pin)
        cursor.execute('INSERT INTO users (username, pin) VALUES (%s, %s)', (username, hashed_pin))
        conn.commit()
        print("User signed up successfully!")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            print("Username already exists!")
        else:
            print(err)
    finally:
        conn.close()

def login(username, pin):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='manager',
            password='gl33bieWeedyK!tty',
            database='user_DB'
        )
        cursor = conn.cursor()
        hashed_pin = hash_pin(pin)
        cursor.execute('SELECT * FROM users WHERE username = %s AND pin = %s', (username, hashed_pin))
        user = cursor.fetchone()
        if user:
            print("Login successful!")
        else:
            print("Invalid username or PIN!")
    finally:
        conn.close()
