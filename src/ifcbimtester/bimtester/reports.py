import datetime
import gettext  # noqa
import json
import os
import pystache

from .features.steps.utils import switch_locale


def generate_report(
    report_dir=".",
    use_report_folder=True,
    report_file_name="report.json",
    html_template_file_path=""
):

    print("# Generating HTML reports now.")

    # get locale path
    localedir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "locale"
    )

    # get html template path
    report_template_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "resources",
        "reports"
    )

    if html_template_file_path:
        report_template_path = html_template_file_path

    # get report file and report dir
    if use_report_folder:
        report_dir = os.path.join(report_dir, "report")
    report_file = os.path.join(report_dir, report_file_name)
    # print(report_file)
    if not os.path.isdir(report_dir):
        return print("Report directory does not exist.")
    if not os.path.isfile(report_file):
        return print("Report file does not exist.")

    # read json report and create html report for each feature
    report = json.loads(open(report_file).read())
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
                steps.append(
                    {
                        "name": name,
                        "time": round(step["result"]["duration"], 2),
                        "is_success": step["result"]["status"] == "passed",
                        "is_unspecified": step["result"]["status"] == "undefined",
                        "is_skipped": step["result"]["status"] == "skipped",
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

        # translate report
        # json.dump(mydict, myfile, indent=4)
        # workaround for retrieving the feature file language
        print(feature["keyword"])
        if feature["keyword"] == "Feature":
            switch_locale(localedir, "en")
        elif feature["keyword"] == "Funktionalität":
            switch_locale(localedir, "de")
        elif feature["keyword"] == "Fonctionnalité":
            switch_locale(localedir, "fr")
        else:
            # standard English
            switch_locale(localedir, "en")
        strings_report = get_html_template_strings()
        # print(strings_report)
        data.update(strings_report)
        # print(data)

        html_report = os.path.join(report_dir, "{}.html".format(file_name))
        html_tmpl = os.path.join(report_template_path, "template.html")
        with open(html_report, "w", encoding="utf8") as out:
            with open(html_tmpl, encoding="utf8") as template:
                out.write(pystache.render(template.read(), data))


def get_html_template_strings():

    return {
        "tr_lang": _("en"),
        "tr_success": _("Success"),
        "tr_failure": _("Failure"),
        "tr_tests_passed": _("Tests passed"),
        "tr_duration": _("Duration"),
        "tr_auditing": _("OpenBIM auditing is a feature of"),
        "tr_and": _("and")
    }
