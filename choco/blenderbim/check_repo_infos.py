import datetime
import re
import sys
from urllib import request


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


def get_latest_blender_version() -> list:
    html_txt = get_choco_package_info()
    return re.findall(RE_BLENDER_VERSION_MIN_MAJ_PAT, html_txt)


URL_IFCOS_RELEASES = "https://github.com/IfcOpenShell/IfcOpenShell/releases"
URL_CHOCO_PACKAGE  = "https://community.chocolatey.org/packages/blender"
URL_BLENDER_CMAKE  = "https://raw.githubusercontent.com/blender/blender/{}/build_files/cmake/Modules/FindPythonLibsUnix.cmake"
RE_BLENDER_VERSION_MIN_MAJ        = r"Latest Version.+<span>Blender (\d+\.\d+)\..+</span>"
RE_BLENDER_VERSION_MIN_MAJ_PAT    = r"Latest Version.+<span>Blender (\d+\.\d+\.\d+)</span>"
RE_BLENDER_PYTHON_VERSION_MAJ_MIN = r"SET\(_PYTHON_VERSION_SUPPORTED (\d+\.\d+)\)"


if sys.argv[1] == "--do_choco_release?":
    now = datetime.datetime.now()
    blenderbim_date = (now - datetime.timedelta(days=1)).strftime("%y%m%d")
    resp = request_repo_info(URL_IFCOS_RELEASES)
    text = str(resp.read())
    if blenderbim_date in text:
        print("do_choco_release", end="")


elif sys.argv[1] == "--latest_blender_release_maj_min_pat?":
    latest_blender_version = get_latest_blender_version()
    if latest_blender_version:
        print(latest_blender_version[0], end="")
    else:
        print("[ERROR] could not determine blender_version_min_maj_pat")
        quit(1)


elif sys.argv[1] == "--latest_blender_release_maj_min?":
    html_txt = get_choco_package_info()
    blender_version_min_maj = re.findall(RE_BLENDER_VERSION_MIN_MAJ, html_txt)
    if blender_version_min_maj:
        print(blender_version_min_maj[0], end="")
    else:
        print("[ERROR] could not determine blender_version_min_maj")
        quit(1)


elif sys.argv[1] == "--latest_blender_python_version_maj_min?":
    latest_blender_version = get_latest_blender_version()
    if latest_blender_version:
        latest_blender_version_tag = f"v{latest_blender_version[0]}"
        resp = request_repo_info(URL_BLENDER_CMAKE.format(latest_blender_version_tag))
        html_txt = str(resp.read())
        found = re.findall(RE_BLENDER_PYTHON_VERSION_MAJ_MIN, html_txt)
        if found:
            print(found[0], end="")
        else:
            print("[ERROR] could not determine blender_python_version_maj_min")
            quit(1)


elif sys.argv[1] == "--pyver?":
    latest_blender_version = get_latest_blender_version()
    if latest_blender_version:
        latest_blender_version_tag = f"v{latest_blender_version[0]}"
        resp = request_repo_info(URL_BLENDER_CMAKE.format(latest_blender_version_tag))
        html_txt = str(resp.read())
        found = re.findall(RE_BLENDER_PYTHON_VERSION_MAJ_MIN, html_txt)
        if found:
            print(f"py{found[0].replace('.', '')}", end="")
        else:
            print("[ERROR] could not determine pyver")
            quit(1)

