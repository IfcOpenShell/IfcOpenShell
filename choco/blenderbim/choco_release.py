# commands to run it on a generic ubuntu 2404 oci container:
"""
apt update && apt install git wget curl ptpython mono-devel micro
mkdir -p /home/runner/work/IfcOpenShell && cd /home/runner/work/IfcOpenShell
git clone https://github.com/IfcOpenShell/IfcOpenShell
cd /home/runner/work/IfcOpenShell/IfcOpenShell/choco/blenderbim/
micro choco_release.py # paste this script, comment out push command
export CHOCO_TOKEN="secret_choco_release_token"
python3 choco_release.py
"""
import datetime
import hashlib
import os
import pathlib
import re
from urllib import request
from github import Github
from typing import NoReturn


def get_repo_tag_names() -> list[str]:
    git_return = os.popen("git tag -l").read()
    tag_names = [tag_name for tag_name in git_return.split("\n") if tag_name]
    print(f"{len(tag_names)} tag_names found in repo")
    return tag_names


def request_repo_info(url: str):
    req  = request.Request(url)
    resp = request.urlopen(req)
    if not resp.status == 200:
        print(f"[ERROR] could not contact server: {url}")
        quit(1)
    return resp


def get_choco_package_info() -> str:
    resp = request_repo_info(URL_CHOCO_PACKAGE)
    html_txt = str(resp.read())
    return html_txt


def get_latest_choco_blender_version() -> list:
    html_txt = get_choco_package_info()
    return re.findall(RE_BLENDER_VERSION_MIN_MAJ_PAT, html_txt)


def get_file_sha256_hash(file_path: str) -> str:
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()

    with open(file_path, "rb") as input_file:
        buffer = input_file.read(BLOCKSIZE)
        while len(buffer) > 0:
            hasher.update(buffer)
            buffer = input_file.read(BLOCKSIZE)

    return hasher.hexdigest()


def quit_with_error_message(message: str) -> NoReturn:
    print(f"ERROR: {message}")
    quit(0)


def get_release_zip(tag: str) -> tuple[str, str]:
    g = Github()
    repo = g.get_repo("IfcOpenShell/IfcOpenShell")
    release = repo.get_release(tag)
    for asset in release.get_assets():
        asset_name = asset.name
        if python_version not in asset_name:
            continue
        if TARGET_OS not in asset_name:
            continue
        return (asset_name, asset.browser_download_url)
    raise Exception(f"Couldn't find the release matching '{python_version}' and '{TARGET_OS}' in tag '{tag}'.")


start = datetime.datetime.now()

URL_CHOCO_PACKAGE  = "https://community.chocolatey.org/packages/blender"
URL_BLENDER_CMAKE  = "https://raw.githubusercontent.com/blender/blender/{}/build_files/cmake/Modules/FindPythonLibsUnix.cmake"
RE_BLENDER_VERSION_MIN_MAJ        = r"Latest Version.+<span>Blender (\d+\.\d+)\..+</span>"
RE_BLENDER_VERSION_MIN_MAJ_PAT    = r"Latest Version.+<span>Blender (\d+\.\d+\.\d+)</span>"
RE_BLENDER_PYTHON_VERSION_MAJ_MIN = r"\(_PYTHON_VERSION_SUPPORTED (\d+\.\d+)\)"

BLENDERBIM_DIR = pathlib.Path("/home/runner/work/IfcOpenShell/IfcOpenShell/choco/blenderbim/")

print("_____ check choco release needed?")

os.chdir(BLENDERBIM_DIR)

blenderbim_date_yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%y%m%d")
should_release = False
target_release_tag = ""
TARGET_OS = "windows-x64"

git_status = os.popen("git status").read()
print(git_status)

for tag_name in get_repo_tag_names():
    print(tag_name)
    if blenderbim_date_yesterday in tag_name:
        should_release = True
        target_release_tag = tag_name
        print(f"found {tag_name=} - {should_release=}")
        break

if not should_release:
    print(f"INFO: no blenderbim release tags found for {blenderbim_date_yesterday} -> no choco release today.")
    quit(0)
print(f"{should_release=}")

if not os.environ.get("CHOCO_TOKEN"):
    quit_with_error_message("could retrieve CHOCO_TOKEN env var")
choco_token = os.environ["CHOCO_TOKEN"]

print("\n_____ get blender info")
# blender_version_min_maj_pat - from chocolatey.org
latest_blender_release_maj_min_pat = get_latest_choco_blender_version()
if not latest_blender_release_maj_min_pat:
    quit_with_error_message("could not determine blender_version_min_maj_pat")
latest_blender_release_maj_min_pat = latest_blender_release_maj_min_pat[0]
print(f"{latest_blender_release_maj_min_pat=}")

# blender_version_min_maj - from chocolatey.org
blender_version_min_maj = latest_blender_release_maj_min_pat.rsplit(".", 1)[0]
print(f"{blender_version_min_maj=}")

# blender_python_version_maj_min - from blender repo
python_version = ""
latest_blender_version_tag = f"v{latest_blender_release_maj_min_pat}"
resp = request_repo_info(URL_BLENDER_CMAKE.format(latest_blender_version_tag))
html_txt = str(resp.read())
found = re.findall(RE_BLENDER_PYTHON_VERSION_MAJ_MIN, html_txt)
if not found:
    quit_with_error_message("could not determine blender_python_version_maj_min")

blender_python_version_maj_min = found[0]
print(f"{blender_python_version_maj_min=}")
python_version = f"py{found[0].replace('.', '')}"
print(f"{python_version=}")

blenderbim_build_version = target_release_tag.replace("blenderbim-", "")

# url_blenderbim_py3x_win_zip
release_zip_file_name, url_blenderbim_py3x_win_zip = get_release_zip(target_release_tag)
os.popen(f"wget {url_blenderbim_py3x_win_zip} --no-verbose").read()

# sha256sum_blenderbim_py310_win_zip
sha256sum_blenderbim_py3x_win_zip = get_file_sha256_hash(release_zip_file_name)

print("\n_____ fill dynamic chocolatey package parameters")
HERE_DIR = pathlib.Path(__file__).parent.absolute()
# print(f"[INFO] HERE_DIR: {HERE_DIR}")

topics = {
    "spec": {
        "path": HERE_DIR / "blenderbim.nuspec",
        "key_values": {
            "latest_blender_version_maj_min_pat": latest_blender_release_maj_min_pat,
            "blenderbim_build_version"          : blenderbim_build_version,
        },
    },
    "install": {
        "path": HERE_DIR / "tools" / "chocolateyinstall.ps1",
        "key_values": {
            "url_blenderbim_py3x_win_zip"      : url_blenderbim_py3x_win_zip,
            "sha256sum_blenderbim_py3x_win_zip": sha256sum_blenderbim_py3x_win_zip,
            "latest_blender_version_maj_min"   : blender_version_min_maj,
        },
    },
    "uninstall": {
        "path": HERE_DIR / "tools" / "chocolateyuninstall.ps1",
        "key_values": {
            "latest_blender_version_maj_min": blender_version_min_maj,
        },
    },
}

for topic, info in topics.items():
    print(f"  {topic}:")
    with open(info["path"], encoding="utf-8") as txt:
        content = txt.read()

    for key, value in info["key_values"].items():
        # print(f"[INFO] replace: {env_var_name}")
        if not key in content:
            print(f"  {key=} not found in {info['path']}")
        content = content.replace(key, value)

    with open(info["path"], "w", encoding="utf-8") as txt:
        txt.write(content)
        print(f"  written: {info['path']}")

print("[INFO] inserting dynamic chocolatey package parameters successful")


print("\n_____ build choco.exe with mono")

choco_version = "1.1.0"
os.popen(f"wget https://github.com/chocolatey/choco/archive/refs/tags/{choco_version}.tar.gz --quiet").read()
os.popen(f"tar -xzf {choco_version}.tar.gz").read()
print("choco tar unpack successful")
os.chdir("choco-1.1.0")
os.popen("./build.sh").read()

os.popen("cp -r build_output/chocolatey /opt/chocolatey").read()
os.chdir(BLENDERBIM_DIR)

if pathlib.Path("/opt/chocolatey/choco.exe").exists():
    print("choco build successful")

print("\n_____ build choco pack")

os.popen("mono /opt/chocolatey/choco.exe pack --allow-unofficial").read()
os.popen('mono /opt/chocolatey/choco.exe setapikey --key="{choco_token}" --source="https://push.chocolatey.org/" --allow-unofficial').read()

print("\n_____ build choco push")
os.popen('mono /opt/chocolatey/choco.exe push --source="https://push.chocolatey.org/" --key="$CHOCO_TOKEN" --allow-unofficial --verbose').read()

print(f"choco push of version: {target_release_tag} successful!")
print(f"it took: {datetime.datetime.now() - start}")
