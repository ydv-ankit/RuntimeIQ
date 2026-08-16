from app.config.db import get_db_connection

def seed_db_schema():
    connection = get_db_connection()
    print("connection", connection)
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id UUID PRIMARY KEY,
                goal TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL
            )
        """)

    connection.commit()