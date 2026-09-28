#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "PyGithub",
# ]
# ///
# This file was generated with the assistance of an AI coding tool.
"""Package a Bonsai nightly for Chocolatey and push it to chocolatey.org.

Takes the newest `bonsai-*-alpha<yymmdd>*` GitHub release of yesterday (UTC),
or the release named with --tag, fills the nuspec and the install script with
the release's Windows zips, runs `choco pack` and, unless --dry-run, `choco
push`. Meant for a Windows runner, where choco is preinstalled; the package
lands in dist/ next to this script.
"""

import argparse
import datetime
import hashlib
import itertools
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlretrieve

from github import Github
from github.GitRelease import GitRelease

HERE = Path(__file__).parent
REPO = "IfcOpenShell/IfcOpenShell"
NUSPEC = HERE / "bonsai-nightly.nuspec"
PLATFORM = "windows-x64"
PYTHON_VARIANTS = ("py311", "py313")
PUSH_SOURCE = "https://push.chocolatey.org/"


def find_nightly_release(releases, date: str) -> GitRelease | None:
    """The newest release of `date` (yymmdd); releases come newest first."""
    pattern = re.compile(rf"^bonsai-.+-alpha{date}\d*$")
    # A few nightlies a day: yesterday's are well within the newest hundred
    # releases, and paging through the whole history is refused past 1000.
    for release in itertools.islice(releases, 100):
        if pattern.match(release.tag_name):
            return release
    return None


def download(url: str, dest: Path) -> str:
    """Download `url` to `dest` and return its SHA-256."""
    print(f"Downloading {url}")
    urlretrieve(url, dest)
    return hashlib.sha256(dest.read_bytes()).hexdigest()


def fill(template: Path, dest: Path, values: dict[str, str]) -> None:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        placeholder = "{{" + key + "}}"
        if placeholder not in text:
            raise SystemExit(f"{placeholder} not found in {template}")
        text = text.replace(placeholder, value)
    dest.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="release tag to package instead of yesterday's newest nightly")
    parser.add_argument("--dry-run", action="store_true", help="pack, but do not push to chocolatey.org")
    args = parser.parse_args()

    repo = Github().get_repo(REPO)
    if args.tag:
        release = repo.get_release(args.tag)
    else:
        yesterday = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime("%y%m%d")
        release = find_nightly_release(repo.get_releases(), yesterday)
        if release is None:
            print(f"No bonsai nightly release for {yesterday}, nothing to publish.")
            return
    print(f"Packaging {release.tag_name}")

    token = os.environ.get("CHOCO_TOKEN")
    if not args.dry_run and not token:
        raise SystemExit("CHOCO_TOKEN is not set")

    build_dir = HERE / "build"
    dist_dir = HERE / "dist"
    shutil.rmtree(build_dir, ignore_errors=True)
    shutil.copytree(HERE / "tools", build_dir / "tools")
    dist_dir.mkdir(exist_ok=True)

    version = release.tag_name.removeprefix("bonsai-")
    values: dict[str, str] = {}
    assets = {asset.name: asset for asset in release.get_assets()}
    for variant in PYTHON_VARIANTS:
        name = next((n for n in assets if n.startswith(f"bonsai_{variant}-") and n.endswith(f"-{PLATFORM}.zip")), None)
        if name is None:
            raise SystemExit(f"{release.tag_name} has no bonsai_{variant}-*-{PLATFORM}.zip asset")
        url = assets[name].browser_download_url
        values[f"URL_{variant.upper()}"] = url
        values[f"SHA256_{variant.upper()}"] = download(url, build_dir / name)
        (build_dir / name).unlink()

    fill(NUSPEC, build_dir / NUSPEC.name, {"VERSION": version})
    fill(HERE / "tools" / "chocolateyinstall.ps1", build_dir / "tools" / "chocolateyinstall.ps1", values)

    subprocess.run(["choco", "pack", NUSPEC.name, "--outputdirectory", str(dist_dir)], cwd=build_dir, check=True)
    nupkg = next(dist_dir.glob("*.nupkg"))
    print(f"Packed {nupkg}")

    if args.dry_run:
        print("Dry run, not pushing.")
        return
    subprocess.run(
        ["choco", "push", str(nupkg), "--source", PUSH_SOURCE, "--api-key", token],
        check=True,
    )
    print(f"Pushed {nupkg.name} to {PUSH_SOURCE}")


if __name__ == "__main__":
    sys.exit(main())
