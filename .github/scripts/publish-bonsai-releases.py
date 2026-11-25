#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "PyGithub",
#     "requests",
# ]
# ///

import argparse
import os
from pathlib import Path

import requests
from github import Github
from github.GitReleaseAsset import GitReleaseAsset

EXTENSION_ID = "bonsai"
CURRENT_PLATFORMS = ["linux-x64", "macos-arm64", "windows-x64"]


def publish_asset(asset: GitReleaseAsset, token: str, repo_root: Path) -> None:
    """
    Publish an asset to Blender Extensions.
    Reference: https://extensions.blender.org/api/v1/swagger
    """
    temp_path = repo_root / asset.name

    response = requests.get(asset.browser_download_url)
    response.raise_for_status()
    temp_path.write_bytes(response.content)

    url = f"https://extensions.blender.org/api/v1/extensions/{EXTENSION_ID}/versions/upload/"
    headers = {"Authorization": f"Bearer {token}"}

    files = {"version_file": temp_path.read_bytes()}
    response = requests.post(url, headers=headers, files=files)
    if not response.ok:
        # E.g. a validation error or the new version upload cooldown.
        print(f"Failed to publish {asset.name}: {response.text}")
    response.raise_for_status()

    temp_path.unlink()

    print(f"✓ Published {asset.name}")


def get_python_versions() -> list[str]:
    parser = argparse.ArgumentParser(description="Publish Bonsai release zips to Blender Extensions.")
    parser.add_argument(
        "--python-version",
        action="append",
        required=True,
        help="Python version of the zips to publish (e.g. py313), can be repeated.",
    )
    args = parser.parse_args()
    return args.python_version


def main() -> None:
    python_versions = get_python_versions()

    token = os.getenv("BLENDER_EXTENSIONS_TOKEN")
    if not token:
        raise Exception("BLENDER_EXTENSIONS_TOKEN environment variable not set")

    # Get the repository root
    repo_root = Path(__file__).parent.parent.parent

    # Read VERSION file
    version_file = repo_root / "VERSION"
    version = version_file.read_text().strip()

    print(f"Current VERSION: {version}")

    tag_name = f"bonsai-{version}"

    # Get release from GitHub
    gh = Github()
    gh_repo = gh.get_repo("IfcOpenShell/IfcOpenShell")
    release = gh_repo.get_release(tag_name)

    assets = release.get_assets()

    asset_platform_map: dict[str, tuple[GitReleaseAsset, str]] = {}
    for asset in assets:
        for python_version in python_versions:
            for platform in CURRENT_PLATFORMS:
                if asset.name.startswith(f"bonsai_{python_version}-") and platform in asset.name:
                    asset_platform_map[asset.name] = (asset, f"{python_version}-{platform}")

    expected = {f"{python_version}-{platform}" for python_version in python_versions for platform in CURRENT_PLATFORMS}
    found = {key for _, key in asset_platform_map.values()}
    if len(asset_platform_map) != len(expected) or found != expected:
        raise Exception(
            f"Expected {len(expected)} assets but found {len(asset_platform_map)}. "
            f"Missing: {', '.join(sorted(expected - found)) or 'none'}"
        )

    print("\nRelease assets:")
    for asset_name in sorted(asset_platform_map.keys()):
        print(f"- {asset_name}")

    # https://extensions.blender.org/api/v1/swagger
    print("\nPublishing assets to Blender Extensions:")
    for asset_name, (asset, platform) in asset_platform_map.items():
        publish_asset(asset, token, repo_root)


if __name__ == "__main__":
    main()
