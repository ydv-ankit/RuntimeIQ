import psycopg2
from app.config.env import settings

connection = None
def get_db_connection():
    try:
        global connection
        if connection is None:
            connection = psycopg2.connect(
                database=settings.DB_DATABASE_NAME,
                user=settings.DB_USERNAME,
                password=settings.DB_PASSWORD,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
            )
        return connection
    except Exception as e:
        print("connection error", e)
        connection = None
        raise

def close_connection():
    print("Closing db connection")
    global connection
    if connection:
        connection.close()
        connection = None