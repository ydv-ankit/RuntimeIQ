from dataclasses import dataclass

class Planner:    
    def plan(self, goal: str) -> list[str]:
        tasks = list()
        if "latency" in goal:
            tasks.append("metrics")

        if "deployment" in goal:
            tasks.append("repository")

        if "logs" in goal:
            tasks.append("logs")

        tasks.append("summary")
        return tasks