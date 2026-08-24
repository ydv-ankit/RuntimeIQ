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
                workflow_id UUID NULL
                created_at TIMESTAMPTZ NOT NULL
            )

            CREATE TABLE IF NOT EXISTS workflows (
                id UUID PRIMARY KEY,
                name TEXT NOT NULL,
                definition JSONB NOT NULL,
                created_at TIMESTAMPZ NOT NULL
            );
        """)

    connection.commit()