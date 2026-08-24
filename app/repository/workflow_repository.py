from app.task import Task
from app.config.db import get_db_connection
from app.workflows.workflow import Workflow
import uuid
import json
from datetime import datetime, timezone

class WorkflowRepository:

    @staticmethod
    def create(workflow: Workflow) -> str:
        query = """
                INSERT INTO runs (id, name, definition, created_at)
                VALUES (%s, %s, %s, %s)
                """

        workflow_id = uuid.uuid4()
        params = (workflow_id, workflow.name, json.dumps(workflow.tasks), datetime.now(timezone.utc))

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        cursor.close()
        connection.commit()
        return str(workflow_id)
        
    @staticmethod
    def get(workflow_id: str):
        query = """
                SELECT * FROM workflows
                WHERE id = %s
                """
        params = (str(workflow_id),)

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            raise Exception("workflow not found")
        cursor.close()
        tasks = [
            Task(
                name=task["name"],
                executor=task["executor"],
                depends_on=task.get("depends_on", [])
            )
            for task in json.loads(row[2])
        ]
        return Workflow(
            id=row[0],
            name=row[1],
            tasks=tasks,
            created_at=row[3]
        )
