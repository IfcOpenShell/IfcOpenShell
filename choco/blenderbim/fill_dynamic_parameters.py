import os
from pathlib import Path


print("[INFO] inserting dynamic chocolatey package parameters")
HERE_DIR = Path(__file__).parent.absolute()
# print(f"[INFO] HERE_DIR: {HERE_DIR}")

topics = {
    "spec": {
        "path": HERE_DIR / "blenderbim.nuspec",
        "env_vars": {
            "latest_blender_version_maj_min_pat",
            "blenderbim_build_version",
        },
    },
    "install": {
        "path": HERE_DIR / "tools" / "chocolateyinstall.ps1",
        "env_vars": {
            "url_blenderbim_py310_win_zip",
            "sha256sum_blenderbim_py310_win_zip",
            "latest_blender_version_maj_min",
        },
    },
    "uninstall": {
        "path": HERE_DIR / "tools" / "chocolateyuninstall.ps1",
        "env_vars": {
            "latest_blender_version_maj_min",
        },
    },
}

for topic, info in topics.items():
    print(f"[INFO] {topic}:")
    for env_var_name in info["env_vars"]:
        print(f"[INFO] {env_var_name} exists?: {os.environ[env_var_name]}")

    with open(info["path"], encoding="utf-8") as txt:
        content = txt.read()

    for env_var_name in info["env_vars"]:
        # print(f"[INFO] replace: {env_var_name}")
        content = content.replace(env_var_name, os.environ[env_var_name])

    with open(info["path"], "w", encoding="utf-8") as txt:
        txt.write(content)
        print(f"[INFO] written: {info['path']}")

print("[INFO] inserting dynamic chocolatey package parameters successful")
