class Task:
    name: str
    depends_on: list[str]
    
    def __init__(self, name: str, depends_on: list[str] | None = None):
        self.name = name
        self.depends_on = depends_on or []