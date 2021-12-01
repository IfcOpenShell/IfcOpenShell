import os
import sys
import json
import shutil
import logging
import tempfile
import ifcopenshell

try:
    import ifcopenshell.express
except:
    pass  # They are using an old version of IfcOpenShell. Gracefully degrade for now.
import behave.formatter.pretty  # Needed for pyinstaller to package it
from bimtester.ifc import IfcStore
from distutils.dir_util import copy_tree
from behave.__main__ import main as behave_main


# TODO: refactor when this isn't super experimental
from logging import StreamHandler

class IDSHandler(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self)
        self.results = {
            "name": "Specification name",
            "status": "passed",
            "location": "filename.xml",
            "elements": [
                {
                    "keyword": "Scenario",
                    "name": "Checking IDS specifications",
                    "status": "passed",
                    "steps": []
                }
            ]
        }

    def emit(self, record):
        msg = self.format(record)
        # Obviously, not a final product
        is_fail = "is compliant" not in msg
        if is_fail:
            self.results["status"] = "failed"
            self.results["elements"][0]["status"] = "failed"
        self.results["elements"][0]["steps"].append({
            "keyword": "*",
            "match": {},
            "name": msg,
            "result": {
                "duration": 0.0,
                "error_message": "Assertion Failed",
                "status": "failed" if is_fail else "passed"
            },
            "step_type": "given"
        })


class TestRunner:
    def __init__(self, ifc_path, schema_path=None, ifc=None):
        IfcStore.path = ifc_path

        # can't load the IFC file if the schema is not loaded before
        if schema_path:
            schema = ifcopenshell.express.parse(schema_path)
            ifcopenshell.register_schema(schema)

        IfcStore.file = ifc if ifc else ifcopenshell.open(ifc_path)

        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.dirname(os.path.realpath(__file__))

        self.locale_path = os.path.join(self.base_path, "locale")

    def run(self, args):
        if args["feature"][-4:].lower() == ".xml":
            return self.test_ids(args)
        return self.test_feature(args)

    def test_ids(self, args):
        # Local import whilst this is experimental
        import ifcopenshell.ids

        logger = logging.getLogger("IDS")
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        ids_handler = IDSHandler()
        logger.addHandler(ids_handler)
        ids_file = ifcopenshell.ids.ids.open(args["feature"])
        ids_file.validate(IfcStore.file, logger)

        tmpdir = tempfile.mkdtemp()
        report_json = os.path.join(tmpdir, "report.json")
        json.dump([ids_handler.results], open(report_json, "w"))
        return report_json

    def test_feature(self, args):
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
