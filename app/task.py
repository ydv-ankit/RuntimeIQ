class Task:
    name: str
    executor: str
    depends_on: list[str]

    def __init__(
        self,
        name: str,
        executor: str,
        depends_on: list[str] | None = None,
    ):
        self.name = name
        self.executor = executor
        self.depends_on = depends_on or []