KEYWORD_TO_TASK = {
    "latency": "metrics",
    "deployment": "repository",
    "logs": "logs",
    "error": "logs",
    "database": "database",
}

class Planner:    
    def plan(self, goal: str) -> list[str]:
        tasks = list()
        for key in KEYWORD_TO_TASK:
            if key in goal:
                tasks.append(KEYWORD_TO_TASK[key])
        tasks.append("summary")
        return tasks