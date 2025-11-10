import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='manager',
        password='gl33bieWeedyK!tty',
        database='user_DB'
    )

    # Create a cursor object
    c = conn.cursor()

    # Create a table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        pin VARCHAR(255) NOT NULL
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    print("Database and table created successfully!")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if conn.is_connected():
        conn.close()
