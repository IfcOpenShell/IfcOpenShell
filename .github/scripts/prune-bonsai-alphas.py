#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#     "PyGithub",
# ]
# ///

"""Delete Bonsai alpha releases and their tags, keeping only the newest ones."""

import argparse
import os
import re
from typing import NamedTuple

from github import Auth, Github
from github.GitRelease import GitRelease

REPO = "IfcOpenShell/IfcOpenShell"
ALPHA_TAG = re.compile(r"bonsai-.+-alpha\d+")


class Args(NamedTuple):
    keep: int
    dry_run: bool


def get_outdated_alphas(releases: list[GitRelease], keep: int) -> list[GitRelease]:
    # Skip drafts as they may not have tags. If drafts occur, first investigate why they occur.
    alphas = [r for r in releases if not r.draft and ALPHA_TAG.fullmatch(r.tag_name)]
    alphas.sort(key=lambda r: r.published_at, reverse=True)
    return alphas[keep:]


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", type=int, required=True, help="Number of newest alpha releases to keep.")
    parser.add_argument("--dry-run", action="store_true", help="Only print the releases that would be deleted.")
    args = parser.parse_args()
    return Args(keep=args.keep, dry_run=args.dry_run)


def main() -> None:
    args = parse_args()

    repo = Github(auth=Auth.Token(os.environ["GH_TOKEN"])).get_repo(REPO)
    outdated = get_outdated_alphas(list(repo.get_releases()), args.keep)

    for release in outdated:
        tag = release.tag_name
        if args.dry_run:
            print(f"Would delete {tag}")
            continue
        release.delete_release()
        repo.get_git_ref(f"tags/{tag}").delete()
        print(f"Deleted {tag}")

    print(f"{len(outdated)} alpha release(s) outdated, keeping the newest {args.keep}.")


if __name__ == "__main__":
    main()
