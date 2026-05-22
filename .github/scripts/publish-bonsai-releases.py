#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "PyGithub",
#     "requests",
# ]
# ///

import os
from pathlib import Path

import requests
from github import Github
from github.GitReleaseAsset import GitReleaseAsset

EXTENSION_ID = "bonsai"
CURRENT_PYTHON_VERSION = "py313"
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
    response.raise_for_status()

    temp_path.unlink()

    print(f"✓ Published {asset.name}")


def main() -> None:
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
        if CURRENT_PYTHON_VERSION not in asset.name:
            continue
        for platform in CURRENT_PLATFORMS:
            if platform in asset.name:
                asset_platform_map[asset.name] = (asset, platform)
                break

    if len(asset_platform_map) != len(CURRENT_PLATFORMS):
        found_platforms = {platform for _, (_, platform) in asset_platform_map.items()}
        missing_platforms = set(CURRENT_PLATFORMS) - found_platforms
        raise Exception(
            f"Expected {len(CURRENT_PLATFORMS)} assets but found {len(asset_platform_map)}. "
            f"Missing: {', '.join(sorted(missing_platforms))}"
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
