import datetime
import os


def get_repo_tag_names():
    git_return = os.popen("git tag -l").read()
    return [tag_name for tag_name in git_return.split("\n") if tag_name]


def set_github_env_var(key: str, value: str):
    env_file_path = os.getenv('GITHUB_ENV')
    with open(env_file_path, "a") as env_file:
        _ = env_file.write(f"{key}={value}" + "\n")


blenderbim_date_yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%y%m%d")

for tag_name in get_repo_tag_names():
    if blenderbim_date_yesterday in tag_name:
        set_github_env_var(key="choco_release", value="do_choco_release")
        set_github_env_var(key="target_release_tag", value=tag_name)
        print("do_choco_release", end="")
        break
