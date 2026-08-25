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

    def to_dict(self):
        return {
            "name": self.name,
            "executor": self.executor,
            "depends_on": self.depends_on,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            executor=data["executor"],
            depends_on=data.get("depends_on", []),
        )