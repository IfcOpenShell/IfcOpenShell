import os.path
import zipfile
import tempfile
from xml.dom import minidom


def load(filepath):
    filepath = extract_project(filepath)
    if os.path.isfile(os.path.join(filepath, "bcf.version")):
        version_path = os.path.join(filepath, "bcf.version")
        version_id = get_version(version_path)
        if version_id == "2.1":
            from bcf.v2.bcfxml import BcfXml

            bcfxml = BcfXml()
            bcfxml.filepath = filepath
            return bcfxml
        else:
            from bcf.v3.bcfxml import BcfXml

            bcfxml = BcfXml()
            bcfxml.filepath = filepath
            return bcfxml


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
