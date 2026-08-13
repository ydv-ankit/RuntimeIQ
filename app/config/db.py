import psycopg2

connection = None
def get_connection():
    try:
        global connection
        if connection is None:
            connection = psycopg2.connect(
                database="runtimeiq",
                user="postgres",
                password="postgres",
                host="127.0.0.1",
                port=5432,
            )
        return connection
    except Exception as e:
        print("connection error", e)
        connection = None
        return connection

def close_connection():
    print("Closing db connection")
    global connection
    if connection:
        connection.close()
        connection = None