class Data:
    is_loaded = False
    tasks = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.tasks = {}

    @classmethod
    def load(cls, file):
        cls.tasks = {}
        for task in file.by_type("IfcTask"):
            cls.tasks[task.id()] = {"Name": task.Name, "Identification": task.Identification or ""}
        cls.is_loaded=True
