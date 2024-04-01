import os
import sqlite3

connection = sqlite3.connect(os.environ.get('DATABASE_URL', 'chat/database/chat.sqlite'))
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS accounts (
address TEXT PRIMARY KEY,
display_name TEXT NOT NULL,
signature BLOB NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
message_id TEXT NOT NULL,
from_address TEXT NOT NULL,
message TEXT NOT NULL,
wrote_at TEXT NOT NULL,
signature TEXT NOT NULL,
PRIMARY KEY (message_id, from_address)
);
''')

connection.commit()
connection.close()
