import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "objective": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        metric = self.file.create_entity(
            "IfcMetric",
            **{
                "Name": "Unnamed",
                "ConstraintGrade": "NOTDEFINED",
                "Benchmark": "EQUALTO",
            }
        )
        if self.settings["objective"]:
            benchmark_values = list(self.settings["objective"].BenchmarkValues or [])
            benchmark_values.append(metric)
        return metric
