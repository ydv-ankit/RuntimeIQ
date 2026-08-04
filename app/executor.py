class Executor:
    def execute(self, task: str):
        execution = {}
        if task == "metrics":
            execution["latency"] = "424ms"
        if task == "repository":
            execution["last_commit_sha"] = "akhd7f7uywe8dfuh3q"
        if task == "summary":
            execution["summary"] = "this is the task summary"
        return execution
