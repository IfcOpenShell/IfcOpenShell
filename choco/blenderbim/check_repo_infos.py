import sys
import re
import datetime
from urllib import request


def request_repo_info(url: str):
    req  = request.Request(url)
    resp = request.urlopen(req)
    if not resp.status == 200:
        print(f"[ERROR] could not contact server: {url}")
        quit(1)
    return resp


if sys.argv[1] == "--do_choco_release?":
    now = datetime.datetime.now()
    blenderbim_date = now.strftime("%y%m%d")
    url = "https://github.com/IfcOpenShell/IfcOpenShell/releases/latest"
    resp = request_repo_info(url)
    if blenderbim_date in resp.url:
        print("do_choco_release", end="")


elif sys.argv[1] == "--latest_blender_release_min_maj_pat?":
    re_blender_version_min_maj_pat = r"Latest Version.+<span>Blender (\d+\.\d+\.\d+)</span>"
    url = "https://community.chocolatey.org/packages/blender"
    resp = request_repo_info(url)
    html_txt = str(resp.read())
    found = re.findall(re_blender_version_min_maj_pat, html_txt)
    if found:
        print(found[0], end="")


elif sys.argv[1] == "--latest_blender_release_min_maj?":
    re_blender_version_min_maj = r"Latest Version.+<span>Blender (\d+\.\d+)\..+</span>"
    url = "https://community.chocolatey.org/packages/blender"
    resp = request_repo_info(url)
    html_txt = str(resp.read())
    found = re.findall(re_blender_version_min_maj, html_txt)
    if found:
        print(found[0], end="")

elif sys.argv[1] == "--latest_blender_python_version_maj_min?":
    # get latest blender version first
    re_blender_version_min_maj_pat = r"Latest Version.+<span>Blender (\d+\.\d+\.\d+)</span>"
    url = "https://community.chocolatey.org/packages/blender"
    resp = request_repo_info(url)
    html_txt = str(resp.read())
    found = re.findall(re_blender_version_min_maj_pat, html_txt)
    if found:
        latest_blender_version_tag = f"v{found[0]}"
        re_blender_python_version_maj_min = r"SET\(PYTHON_VERSION (\d+.\d+) "
        url = f"https://raw.githubusercontent.com/blender/blender/{latest_blender_version_tag}/build_files/cmake/Modules/FindPythonLibsUnix.cmake"
        resp = request_repo_info(url)
        html_txt = str(resp.read())
        found = re.findall(re_blender_python_version_maj_min, html_txt)
        if found:
            print(found[0], end="")


elif sys.argv[1] == "--pyver?":
    # get latest blender version first
    re_blender_version_min_maj_pat = r"Latest Version.+<span>Blender (\d+\.\d+\.\d+)</span>"
    url = "https://community.chocolatey.org/packages/blender"
    resp = request_repo_info(url)
    html_txt = str(resp.read())
    found = re.findall(re_blender_version_min_maj_pat, html_txt)
    if found:
        latest_blender_version_tag = f"v{found[0]}"
        re_blender_python_version_maj_min = r"SET\(PYTHON_VERSION (\d+.\d+) "
        url = f"https://raw.githubusercontent.com/blender/blender/{latest_blender_version_tag}/build_files/cmake/Modules/FindPythonLibsUnix.cmake"
        resp = request_repo_info(url)
        html_txt = str(resp.read())
        found = re.findall(re_blender_python_version_maj_min, html_txt)
        if found:
            print(f"py{found[0].replace('.', '')}", end="")

