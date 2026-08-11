from app.task import Task

KEYWORD_TO_TASK = {
    "latency": "metrics",
    "deployment": "repository",
    "logs": "logs",
    "error": "logs",
    "database": "database",
}

class Planner:
    def plan(self, goal: str) -> list[Task]:
        tasks: list[Task] = list()
        for key in KEYWORD_TO_TASK:
            if key in goal:
                tasks.append(Task(KEYWORD_TO_TASK[key]))
        tasks.append(Task("summary", depends_on=[x for x in tasks]))
        return tasks