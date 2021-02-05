import os
import sys
import shutil
import tempfile
import ifcopenshell
try:
    import ifcopenshell.express
except:
    pass # They are using an old version of IfcOpenShell. Gracefully degrade for now.
import behave.formatter.pretty  # Needed for pyinstaller to package it
from bimtester.ifc import IfcStore
from distutils.dir_util import copy_tree
from behave.__main__ import main as behave_main


class TestRunner:
    def __init__(self, ifc_path, ifc=None):
        IfcStore.path = ifc_path
        IfcStore.file = ifc if ifc else ifcopenshell.open(ifc_path)

        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.dirname(os.path.realpath(__file__))

        self.locale_path = os.path.join(self.base_path, "locale")

    def run(self, args):
        if args["schema_file"]:
            schema = ifcopenshell.express.parse(args["schema_file"])
            ifcopenshell.register_schema(args["schema_name"])

        tmpdir = tempfile.mkdtemp()
        features_path = os.path.join(tmpdir, "features")
        steps_path = os.path.join(features_path, "steps")
        report_json = os.path.join(tmpdir, "report.json")
        shutil.copytree(os.path.join(self.base_path, "features"), features_path)
        shutil.copy(args["feature"], features_path)
        if args["steps"]:
            if os.path.isfile(args["steps"]):
                shutil.copy(args["steps"], steps_path)
            elif os.path.isdir(args["steps"]):
                copy_tree(args["steps"], steps_path)
        behave_main(self.get_behave_args(args, features_path, report_json))
        return report_json

    def get_behave_args(self, args, features_path, report_json):
        behave_args = [features_path]
        behave_args.extend(["--define", "localedir={}".format(self.locale_path)])
        if args["advanced_arguments"]:
            behave_args.extend(args["advanced_arguments"].split())
        if args["ifc"]:
            behave_args.extend(["--define", "ifc={}".format(args["ifc"])])
        if args["path"]:
            behave_args.extend(["--define", "path={}".format(args["path"])])
        if args["lang"]:
            behave_args.extend(["--lang={}".format(args["lang"])])
        if not args["console"]:
            # https://github.com/behave/behave/issues/346
            behave_args.extend(["--no-capture", "--format", "json.pretty", "--outfile", report_json])
        return behave_args
