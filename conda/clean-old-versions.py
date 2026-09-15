# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anaconda-client==1.12.3",
# ]
# ///

import os

from binstar_client.errors import BinstarError
from binstar_client.utils import get_server_api

# Configuration
api_token = os.environ.get("ANACONDA_TOKEN")
pkg_name = "ifcopenshell"
channel_name = "ifcopenshell"
number_of_supported_versions = int(os.environ["NUM_SUPPORTED_VERSIONS"])

# Authenticate with Anaconda
aserver_api = get_server_api(token=api_token)


# Get the list of packages in the channel
def get_package(filter_package_name: str = None):
    try:
        user_packages = aserver_api.user_packages(channel_name)
        if filter_package_name:
            user_packages = [pkg for pkg in user_packages if pkg["name"] == filter_package_name]
        if len(user_packages) == 0:
            print(f"No packages found for {filter_package_name}.")
        if len(user_packages) > 1:
            raise ValueError(
                f"Found {len(user_packages)} package for {filter_package_name}. Will only support 1 package."
            )

        return user_packages[0]
    except BinstarError as err:
        raise ValueError(f"Failed to fetch packages: {err}")


# Delete a package version
def delete_package(package_name, version):
    try:
        aserver_api.remove_release(channel_name, package_name, version)
        print(f"Deleted {package_name} version {version}")
    except BinstarError as err:
        print(f"Failed to delete {package_name} version {version}: {err}")


# Main logic
def main():
    package = get_package(pkg_name)
    if not package:
        print("No packages found.")
        return

    package_name = package["name"]
    versions = package["versions"]
    if len(versions) <= number_of_supported_versions:
        print(f"Number of versions {len(versions)} is less than or equal to {number_of_supported_versions}.")
        return

    # sort the versions in descending order
    print(f"Before reversal: {versions=}")
    versions.reverse()
    print(f"After reversal: {versions=}")

    releases = versions[number_of_supported_versions:]

    for release in releases:
        delete_package(package_name, release)


main()
