import pathlib
import shutil

import requests
import zipfile
import os

# To test this locally, set these environment variables
REPO_OWNER = os.environ.get("REPO_OWNER", "IfcOpenShell/IfcOpenShell")
MY_WORKFLOW = os.environ.get("MY_WORKFLOW", "ci-ifcopenshell-conda-daily")
WORKFLOW_RUN_ID = os.environ.get("WORKFLOW_RUN_ID", None)
TOKEN = os.environ.get("GITHUB_TOKEN", None)
# To test this locally create a fine-grained personal access token for this repo with permissions "actions:read"
# See https://github.com/settings/tokens?type=beta

# This is a list of strings that indicate that a job has stopped abruptly.
SIGNS_OF_STOPPAGE = [
    "Error: The operation was canceled.",
    "fatal error C1060: compiler is out of heap space",
]


def start_request_session():
    s = requests.Session()
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    s.headers = headers
    return s


def get_ci_run(repo_name, run_id):
    url = f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}"
    s = start_request_session()
    response = s.get(url)
    return response.json()


def evaluate_log_file_for_abrupt_stop(log_file):
    with open(log_file) as f:
        for i, line in enumerate(f):
            for sign in SIGNS_OF_STOPPAGE:
                if sign in line:
                    print(f"Found sign of abrupt stoppage in [line {i}]: '{sign}'")
                    return True
    return False


def get_ci_specific_run_specific_failure_details(repo_name, run_id):
    url = f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/attempts/1/logs"
    s = start_request_session()
    response = s.get(url)

    # SAVE zip file
    with open("logs.zip", "wb") as f:
        f.write(response.content)

    # unzip file
    with zipfile.ZipFile("logs.zip", "r") as zip_ref:
        zip_ref.extractall("logs")

    failed_logs = []
    for file in pathlib.Path("logs").iterdir():
        if file.is_dir():
            continue

        if evaluate_log_file_for_abrupt_stop(file):
            failed_logs.append(file)

    return failed_logs


def restart_job(repo_name, job_id):
    url = f"https://api.github.com/repos/{repo_name}/actions/runs/{job_id}/rerun-failed-jobs"
    s = start_request_session()
    response = s.post(url)
    return response.json()


def eval_jobs():
    run = get_ci_run(REPO_OWNER, WORKFLOW_RUN_ID)
    if run["run_attempt"] > 1:
        print("This is not the first attempt. Exiting")
        return
    failed_logs = get_ci_specific_run_specific_failure_details(REPO_OWNER, WORKFLOW_RUN_ID)

    if len(failed_logs) == 0:
        print("No runs exhibit signs of abrupt stoppage")
        return

    print("restarting job", WORKFLOW_RUN_ID)
    r = restart_job(REPO_OWNER, WORKFLOW_RUN_ID)
    print(r)

    shutil.rmtree("logs")
    os.remove("logs.zip")


if __name__ == "__main__":
    eval_jobs()
