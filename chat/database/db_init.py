import os
import sqlite3

connection = sqlite3.connect(os.environ.get('DATABASE_URL', 'chat/database/chat.sqlite'))
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS accounts (
address TEXT NOT NULL PRIMARY KEY,
display_name TEXT NOT NULL,
signature BLOB NOT NULL,
state_index INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
message_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
from_address TEXT NOT NULL,
message TEXT NOT NULL,
wrote_at TEXT NOT NULL,
signature TEXT NOT NULL,
state_index INTEGER NOT NULL);
''')

connection.commit()
connection.close()
