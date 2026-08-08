import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id),
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_conversation(username, title="New Chat"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (username, title) VALUES (%s, %s) RETURNING id",
        (username, title)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id

def get_conversations(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title FROM conversations WHERE username = %s ORDER BY id DESC",
        (username,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": row[0], "title": row[1]} for row in rows]

def save_message(conversation_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
        (conversation_id, role, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

def load_messages(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE conversation_id = %s ORDER BY id ASC",
        (conversation_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"role": role, "content": content} for role, content in rows]

def delete_conversation(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE conversation_id = %s", (conversation_id,))
    cursor.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
    conn.commit()
    cursor.close()
    conn.close()

def rename_conversation(conversation_id, new_title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET title = %s WHERE id = %s",
        (new_title, conversation_id)
    )
    conn.commit()
    cursor.close()
    conn.close()