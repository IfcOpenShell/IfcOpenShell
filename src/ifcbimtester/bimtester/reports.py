import datetime
import json
import os
import pystache
import sys
from bimtester.lang import _


class ReportGenerator:
    def __init__(self):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.dirname(os.path.realpath(__file__))

    def generate(self, report_json, output_file):
        print("# Generating HTML reports.")

        report = json.loads(open(report_json).read())
        for feature in report:
            self.generate_feature_report(feature, output_file)

    def generate_feature_report(self, feature, output_file):
        # file_name = os.path.basename(feature["location"]).split(":")[0]
        data = {
            # "file_name": file_name,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": feature["name"],
            "description": feature.get("description", ""),
            "is_success": feature["status"] == "passed",
            "scenarios": [],
        }

        if "elements" not in feature:
            if "status" in feature and feature["status"] == "skipped":
                print("Feature was skipped. No html report will be created.")
            else:
                print("For a unknown reason no html report well be created.")
            # happens if the feature file does not consist of any valid Scenario
            return

        for scenario in feature["elements"]:
            scenario_data = self.process_scenario(scenario, feature)
            if scenario_data:
                data["scenarios"].append(scenario_data)

        data["total_passes"] = sum([s["total_passes"] for s in data["scenarios"]])
        data["total_steps"] = sum([s["total_steps"] for s in data["scenarios"]])
        try:
            data["pass_rate"] = round((data["total_passes"] / data["total_steps"]) * 100)
        except ZeroDivisionError:
            data["pass_rate"] = 0

        # get language and switch locale
        the_lang = self.get_feature_lang(feature["keyword"])
        from bimtester.lang import switch_locale
        switch_locale(os.path.join(self.base_path, "locale"), the_lang)
        data["_lang"] = the_lang

        data.update(self.get_template_strings())

        with open(output_file, "w", encoding="utf8") as out:
            with open(
                os.path.join(self.base_path, "resources", "reports", "template.html"), encoding="utf8"
            ) as template:
                out.write(pystache.render(template.read(), data))

    def process_scenario(self, scenario, feature):
        if len(scenario["steps"]) == 0:
            print("Scenario '{}' in feature '{}' has no steps.".format(scenario["name"], feature["name"]))
            return

        steps = []
        total_duration = 0

        for step in scenario["steps"]:
            step_data = self.process_step(step)
            total_duration += step_data["time_raw"]
            steps.append(step_data)

        total_passes = len([s for s in steps if s["is_success"] is True])
        total_steps = len(steps)
        pass_rate = round((total_passes / total_steps) * 100)

        return {
            "name": scenario["name"],
            # on behave < 1.2.6 there is no 'status' thus report fails
            "is_success": scenario["status"] == "passed",
            "time": round(total_duration, 2),
            "steps": steps,
            "total_passes": total_passes,
            "total_steps": total_steps,
            "pass_rate": pass_rate,
        }

    def process_step(self, step):
        name = step["name"]
        if "match" in step and "arguments" in step["match"]:
            for a in step["match"]["arguments"]:
                name = name.replace(a["value"], "<b>" + a["value"] + "</b>")
        if "result" not in step:
            step["result"] = {}
            step["result"]["status"] = "skipped"
            step["result"]["duration"] = 0
            step["result"]["error_message"] = "This requirement has been skipped due to a previous failing step."
        elif step["result"]["status"] == "undefined":
            step["result"] = {}
            step["result"]["status"] = "undefined"
            step["result"]["duration"] = 0
            step["result"]["error_message"] = "This requirement has not yet been specified."
        data = {
            "name": name,
            "time_raw": step["result"]["duration"],
            "time": round(step["result"]["duration"], 2),
            "is_success": step["result"]["status"] == "passed",
            "is_unspecified": step["result"]["status"] == "undefined",
            "is_skipped": step["result"]["status"] == "skipped",
            "error_message": None if step["result"]["status"] == "passed" else step["result"]["error_message"],
        }

        # Remove the first "Assertion Failed" message
        if isinstance(data["error_message"], list) and data["error_message"]:
            data["error_message"].pop(0)
        return data

    def get_template_strings(self):
        return {
            # "_lang": _("en"),
            "_success": _("Success"),
            "_failure": _("Failure"),
            "_tests_passed": _("Tests passed"),
            "_duration": _("Duration"),
            "_auditing": _("OpenBIM auditing is a feature of"),
            "_and": _("and"),
        }

    def get_feature_lang(self, feature_key):
        # I do not know any better ATM
        print(feature_key)
        if feature_key == "Feature":
            return "en"
        elif feature_key == "Funktionalität":
            return "de"
        elif feature_key == "Fonctionnalité":
            return "fr"
        elif feature_key == "Funzionalità":
            return "it"
        elif feature_key == "Functionaliteit":
            return "nl"
        else:
            # standard English
            return "en"
