import datetime
import json
import os
import pystache


def generate_report(adir="."):
    print("# Generating HTML reports now.")

    # get html template
    html_template_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "features/template.html"
    )

    # get report file
    report_dir = os.path.join(adir, "report")
    if not os.path.exists(report_dir):
        return print("No report directory was found.")
    report_path = os.path.join(report_dir, "report.json")
    # print(report_path)
    if not os.path.exists(report_path):
        return print("No report data was found.")

    # read json report and create html report for each feature
    report = json.loads(open(report_path).read())
    for feature in report:
        file_name = os.path.basename(feature["location"]).split(":")[0]
        data = {
            "file_name": file_name,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": feature["name"],
            "description": feature["description"],
            "is_success": feature["status"] == "passed",
            "scenarios": [],
        }
        if "elements" not in feature:
            if "status" in feature and feature["status"] == "skipped":
                print("Feature was skipped. No html report will be created.")
            else:
                print("For a unknown reason no html report well be created.")
            # happens if the feature file does not consist of any valid Scenario
            continue
        for scenario in feature["elements"]:
            steps = []
            total_duration = 0
            if len(scenario["steps"]) == 0:
                print(
                    "Scenario '{}' in feature '{}' has no steps. "
                    "Thus skipped in report."
                    .format(scenario["name"], feature["name"])
                )
                continue
            for step in scenario["steps"]:
                if "result" in step:
                    total_duration += step["result"]["duration"]
                name = step["name"]
                if "match" in step and "arguments" in step["match"]:
                    for a in step["match"]["arguments"]:
                        name = name.replace(a["value"], "<b>" + a["value"] + "</b>")
                if "result" not in step or step["result"]["status"] == "undefined":
                    step["result"] = {}
                    step["result"]["status"] = "undefined"
                    step["result"]["duration"] = 0
                    step["result"]["error_message"] = "This requirement has not yet been specified."
                steps.append(
                    {
                        "name": name,
                        "time": round(step["result"]["duration"], 2),
                        "is_success": step["result"]["status"] == "passed",
                        "is_unspecified": "result" not in step or step["result"]["status"] == "undefined",
                        "error_message": None
                        if step["result"]["status"] == "passed"
                        else step["result"]["error_message"],
                    }
                )
            total_passes = len([s for s in steps if s["is_success"] is True])
            total_steps = len(steps)
            pass_rate = round((total_passes / total_steps) * 100)
            data["scenarios"].append(
                {
                    "name": scenario["name"],
                    # on behave < 1.2.6 there is no 'status' thus report fails
                    "is_success": scenario["status"] == "passed",
                    "time": round(total_duration, 2),
                    "steps": steps,
                    "total_passes": total_passes,
                    "total_steps": total_steps,
                    "pass_rate": pass_rate,
                }
            )
        data["total_passes"] = sum([s["total_passes"] for s in data["scenarios"]])
        data["total_steps"] = sum([s["total_steps"] for s in data["scenarios"]])
        data["pass_rate"] = round((data["total_passes"] / data["total_steps"]) * 100)

        html_report_file = os.path.join(report_dir, "{}.html".format(file_name))
        with open(html_report_file, "w") as out:
            with open(html_template_file) as template:
                out.write(pystache.render(template.read(), data))
