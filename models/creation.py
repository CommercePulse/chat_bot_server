import sqlite3

def TableCreation():
    # Define the database URI
    database_uri = 'bot_namespace.db'

    # Connect to the SQLite database
    conn = sqlite3.connect(database_uri)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Create the first table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_namespace_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            namespace_id TEXT NOT NULL,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create the second table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_vector_namespace (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_name TEXT NOT NULL,
            namespace_id TEXT NOT NULL,
            namespace_name TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()

print("Both tables created successfully.")
