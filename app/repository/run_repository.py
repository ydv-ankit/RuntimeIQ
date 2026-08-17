from app.models.run import Run, RunStatus
from app.config.db import get_db_connection
from datetime import datetime

class RunRepository:

    @staticmethod
    def create(run: Run):
        query = """
                INSERT INTO runs (id, goal, status, created_at)
                VALUES (%s, %s, %s, %s)
                """

        params = (str(run.id), run.goal, run.status.name, run.created_at)

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        cursor.close()
        connection.commit()
        
    @staticmethod
    def get(run_id: str):
        query = """
                SELECT * FROM runs
                WHERE id = %s
                """
        params = (str(run_id),)

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            raise Exception("run not found")
        cursor.close()
        return Run(
            id=row[0],
            goal=row[1],
            status=row[2],
            created_at=row[3]
        )

    @staticmethod
    def update_status(run_id: str, updated_status: RunStatus):
        query = """
                UPDATE runs
                SET status = %s
                where id = %s
                """
        params = (updated_status.name, str(run_id))
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        cursor.close()
        connection.commit()