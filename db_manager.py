import sqlite3

DB_NAME = "bot.db"

def initialize_database():
    """
    Inicializa la base de datos SQLite creando las tablas si no existen.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                messages INTEGER DEFAULT 0,
                voice_time REAL DEFAULT 0.0,
                points REAL DEFAULT 0.0,
                vc_join_time TEXT
            )
        """)
        conn.commit()

def add_or_update_user(user_id, messages=0, voice_time=0.0, points=0.0, vc_join_time=None):
    """
    Añade un nuevo usuario o actualiza un usuario existente.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, messages, voice_time, points, vc_join_time)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                messages = messages + excluded.messages,
                voice_time = voice_time + excluded.voice_time,
                points = points + excluded.points,
                vc_join_time = excluded.vc_join_time
        """, (user_id, messages, voice_time, points, vc_join_time))
        conn.commit()

def get_user_points(user_id):
    """
    Obtiene los datos de un usuario, incluyendo los puntos.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(zip([d[0] for d in cursor.description], row)) if row else None

def get_all_users():
    """
    Devuelve todos los usuarios de la base de datos.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [dict(zip([d[0] for d in cursor.description], row)) for row in rows]

def update_user_points(user_id, points):
    """
    Actualiza los puntos de un usuario.
    """
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET points = ? WHERE user_id = ?
        """, (points, user_id))
        conn.commit()
