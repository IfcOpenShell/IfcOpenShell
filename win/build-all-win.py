"""
It's not really a full version of nix/build-all.py for Windows,
but serves the similar purpose - build all packages during CI (though by using cmd scripts),
but also archives them to '~/outputs'.
"""

import os
import platform
import subprocess
import zipfile
from pathlib import Path
from zipfile import ZipFile


def is_arm64() -> bool:
    arch = os.environ.get("TARGET_ARCH", "").lower()
    if arch in ("arm64", "aarch64"):
        return True
    if arch in ("x64", "amd64", "x86_64"):
        return False
    return platform.machine().lower() in ("arm64", "aarch64")

assert Path.cwd() == Path(__file__).parent, "Run this script from the 'win' directory."

PYTHON_VERSIONS = ["3.10.3", "3.11.8", "3.12.1", "3.13.0", "3.14.0"]
REPO_PATH = Path(__file__).parent.parent
REPO_WIN = REPO_PATH / "win"
VERSION = (REPO_PATH / "VERSION").read_text().strip()
if "GITHUB_SHA" in os.environ:
    SHA = os.environ["GITHUB_SHA"][:7]
else:
    SHA = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
OUTPUT_DIR = Path.home() / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
print("Output directory:", OUTPUT_DIR)
ZIP_TEMPLATE = f"{{package_name}}-v{VERSION}-{SHA}-{'win-arm64' if is_arm64() else 'win64'}.zip"


def run(command: list[str]) -> None:
    print("Running:", command)
    subprocess.check_call(command)


def set_env(var_name: str, value: str) -> tuple[str, str | None]:
    """
    :return: Tuple of ``(var_name, old_value)`` to be passed to ``restore_env``.
    """
    old_value = os.getenv(var_name)
    os.environ[var_name] = value
    return var_name, old_value


def restore_env(var_name: str, old_value: str | None) -> None:
    if old_value is None:
        del os.environ[var_name]
    else:
        os.environ[var_name] = old_value


def build() -> None:
    for python_version in PYTHON_VERSIONS:
        os.environ["PYTHON_VERSION"] = python_version
        print(f"Building for Python {python_version}...")
        subprocess.run(
            [str(REPO_WIN / "build-deps.cmd"), "vs2022-ARM64" if is_arm64() else "vs2022-x64", "Release"],
            check=True,
            text=True,
            input="y\n",
        )
        OLD_ADD_COMMIT_SHA = set_env("ADD_COMMIT_SHA", "ON")
        run(
            [
                str(REPO_WIN / "run-cmake.bat"),
                "vs2022-ARM64" if is_arm64() else "vs2022-x64",
                "-DENABLE_BUILD_OPTIMIZATIONS=ON",
                "-DGLTF_SUPPORT=ON",
            ]
        )
        restore_env(*OLD_ADD_COMMIT_SHA)
        run([str(REPO_WIN / "install-ifcopenshell.bat"), "vs2022-ARM64" if is_arm64() else "vs2022-x64", "Release"])


def archive_executables() -> None:
    # Typically '_installed-vs2022-x64'.
    install_dir = next(d for d in REPO_PATH.iterdir() if d.is_dir() and d.name.startswith("_installed"))

    for file in (install_dir / "bin").iterdir():
        if file.suffix.lower() != ".exe":
            continue
        zip_name = ZIP_TEMPLATE.format(package_name=file.stem)
        with ZipFile(OUTPUT_DIR / zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file, arcname=file.name)
        print(f"{file} -> {zip_name}")


def archive_python_package(python_version: str, python_path: Path) -> None:
    python_version_major_minor = "".join(python_version.split(".")[:2])
    site_packages = python_path / "Lib" / "site-packages"
    package_path = site_packages / "ifcopenshell"

    # Clean cache.
    for file in package_path.rglob("*.pyc"):
        file.unlink()

    zip_name = ZIP_TEMPLATE.format(package_name=f"ifcopenshell-python-{python_version_major_minor}")
    with ZipFile(OUTPUT_DIR / zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for file in package_path.rglob("*"):
            arcname = file.relative_to(site_packages)
            zipf.write(file, arcname=arcname)
    print(f"{package_path} -> {zip_name}")


def archive_python_packages() -> None:
    deps_path = REPO_PATH / "_deps"
    python_versions: list[str] = []
    for d in deps_path.iterdir():
        if d.is_dir() and (d.name.startswith("python.") or d.name.startswith("pythonarm64.")):
            python_version = d.name.partition(".")[2]
            python_path = d / "tools"
            archive_python_package(python_version, python_path)
            python_versions.append(d.name.partition(".")[2])


def main() -> None:
    build()
    archive_executables()
    archive_python_packages()


if __name__ == "__main__":
    main()
