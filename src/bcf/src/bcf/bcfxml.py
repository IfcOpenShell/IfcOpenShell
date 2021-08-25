import os.path
import zipfile
import tempfile
from xml.dom import minidom


def load(filepath):
    filepath = extract_project(filepath)
    if os.path.isfile(os.path.join(filepath, "bcf.version")):
        version_path = os.path.join(filepath, "bcf.version")
        version_id = get_version(version_path)
        # TODO: we actually coded it for 2.1, let's check the difference between 2.0 and 2.1
        if version_id == "2.1" or version_id == "2.0":
            from bcf.v2.bcfxml import BcfXml

            bcfxml = BcfXml()
            bcfxml.filepath = filepath
            return bcfxml
        elif version_id == "3.0":
            from bcf.v3.bcfxml import BcfXml

            bcfxml = BcfXml()
            bcfxml.filepath = filepath
            return bcfxml
        else:
            raise Exception(f"Version {version_id} not supported.")


def get_version(version_path):
    xmlparse = minidom.parse(version_path)
    version_el = xmlparse.getElementsByTagName("Version")[0]
    version = version_el.getAttribute("VersionId")
    return version


def extract_project(filepath):
    if not filepath:
        return
    zip_file = zipfile.ZipFile(filepath)
    filepath = tempfile.mkdtemp()
    zip_file.extractall(filepath)
    return filepath
