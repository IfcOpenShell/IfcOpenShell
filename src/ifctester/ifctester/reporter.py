# IfcTester - IDS based model auditing
# Copyright (C) 2021 Artur Tomczak <artomczak@gmail.com>, Thomas Krijnen <mail@thomaskrijnen.com>, Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcTester.
#
# IfcTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcTester.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import math
import logging
import datetime

cwd = os.path.dirname(os.path.realpath(__file__))

class Reporter:
    def __init__(self, ids):
        self.ids = ids

    def report(self, ids):
        pass

    def to_string(self):
        return ""

    def write(self, filepath):
        pass


class Console(Reporter):
    def __init__(self, ids, use_colour=True):
        super().__init__(ids)
        self.use_colour = use_colour
        self.colours = {
            "red": "\033[1;31m",
            "blue": "\033[1;34m",
            "cyan": "\033[1;36m",
            "green": "\033[0;32m",
            "yellow": "\033[0;33m",
            "purple": "\033[0;95m",
            "grey": "\033[0;90m",
            "reset": "\033[0;0m",
            "bold": "\033[;1m",
            "reverse": "\033[;7m",
        }

    def report(self):
        self.set_style("bold", "blue")
        print(self.ids.info.get("title", "Untitled IDS"))
        for specification in self.ids.specifications:
            self.report_specification(specification)
        self.set_style("reset")

    def report_specification(self, specification):
        if specification.status is True:
            self.set_style("bold", "green")
            print("[PASS] ", end="")
        elif specification.status is False:
            self.set_style("bold", "red")
            print("[FAIL] ", end="")
        elif specification.status is None:
            self.set_style("bold", "yellow")
            print("[UNTESTED] ", end="")

        self.set_style("bold")
        total = len(specification.applicable_entities)
        total_successes = total - len(specification.failed_entities)
        print(f"({total_successes}/{total}) ", end="")

        if specification.minOccurs != 0:
            print(f"*", end="")

        print(specification.name)

        self.set_style("cyan")
        print(" " * 4 + "Applies to:")
        self.set_style("reset")

        for applicability in specification.applicability:
            print(" " * 8 + applicability.to_string("applicability"))

        if not total and specification.status is False:
            return

        self.set_style("cyan")
        print(" " * 4 + "Requirements:")
        self.set_style("reset")

        for requirement in specification.requirements:
            self.set_style("reset")
            self.set_style("red") if requirement.failed_entities else self.set_style("green")
            print(" " * 8 + requirement.to_string("requirement"))
            self.set_style("reset")
            for i, element in enumerate(requirement.failed_entities[0:10]):
                print(" " * 12, end="")
                self.report_reason(requirement.failed_reasons[i], element)
            if len(requirement.failed_entities) > 10:
                print(" " * 12 + f"... {len(requirement.failed_entities)} in total ...")
        self.set_style("reset")

    def report_reason(self, reason, element):
        is_bold = False
        for substring in reason.split('"'):
            if is_bold:
                self.set_style("purple")
            else:
                self.set_style("reset")
            print(substring, end="")
            is_bold = not is_bold
        self.set_style("grey")
        print(" - " + str(element))
        self.set_style("reset")

    def set_style(self, *colours):
        if self.use_colour:
            sys.stdout.write("".join([self.colours[c] for c in colours]))


class Json(Reporter):
    def __init__(self, ids):
        super().__init__(ids)
        self.results = {}

    def report(self):
        self.results["title"] = self.ids.info.get("title", "Untitled IDS")
        self.results["specifications"] = []
        for specification in self.ids.specifications:
            self.results["specifications"].append(self.report_specification(specification))
        return self.results

    def report_specification(self, specification):
        requirements = []
        for requirement in specification.requirements:
            requirements.append(
                {
                    "description": requirement.to_string("requirement"),
                    "status": requirement.status,
                    "failed_entities": [
                        {"reason": requirement.failed_reasons[i], "element": str(e)}
                        for i, e in enumerate(requirement.failed_entities[0:10])
                    ],
                }
            )
        total = len(specification.applicable_entities)
        total_successes = total - len(specification.failed_entities)
        percentage = math.floor((total_successes / total) * 100) if total else "N/A"
        return {
            "name": specification.name,
            "status": specification.status,
            "total_successes": total_successes,
            "total": total,
            "percentage": percentage,
            "required": specification.minOccurs != 0,
            "requirements": requirements,
        }

    def to_string(self):
        import json

        return json.dumps(self.results)

    def to_file(self, filepath):
        import json

        with open(filepath, "w") as outfile:
            return json.dump(self.results, outfile)


class Html(Json):
    def __init__(self, ids):
        super().__init__(ids)
        self.results = {}

    def report(self):
        self.results["title"] = self.ids.info.get("title", "Untitled IDS")
        self.results["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results["specifications"] = []
        for specification in self.ids.specifications:
            self.results["specifications"].append(self.report_specification(specification))
        return self.results

    def to_string(self):
        import pystache

        with open(os.path.join(cwd, "templates", "report.html"), "r") as file:
            return pystache.render(file.read(), self.results)

    def to_file(self, filepath):
        import pystache

        with open(os.path.join(cwd, "templates", "report.html"), "r") as file:
            with open(filepath, "w") as outfile:
                return outfile.write(pystache.render(file.read(), self.results))


class BcfHandler(logging.StreamHandler):
    """Logging handler for creation of BCF report files.

    :param project_name: defaults to "IDS Project"
    :type project_name: str, optional
    :param author: Email of the person creating the BCF report, defaults to "your@email.com"
    :type author: str, optional
    :param filepath: Path to save the BCF report, defaults to None
    :type filepath: str, optional
    :param report_valid: True if you want to list all the compliant cases as well, defaults to False
    :type report_valid: bool, optional

    Example::

        bcf_handler = BcfHandler(
            project_name="Default IDS Project",
            author="your@email.com",
            filepath="example.bcf",
        )
        logger = logging.getLogger("IDS_Logger")
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        logger.addHandler(bcf_handler)
    """

    def __init__(self, project_name="IDS Project", author="your@email.com", filepath=None, report_valid=False):
        import numpy as np
        import ifcopenshell.util.placement
        from bcf.v2.bcfxml import BcfXml
        from bcf.v2 import data as bcf

        logging.StreamHandler.__init__(self)
        if report_valid:
            self.setLevel(logging.INFO)
        else:
            self.setLevel(logging.ERROR)
        self.bcf = BcfXml()
        self.bcf.author = author
        self.bcf.new_project()
        self.bcf.project.name = project_name
        self.filepath = filepath
        self.bcf.edit_project()

    def emit(self, log_content):
        """Triggered on each use of logging with the BCF handler enabled.

        :param log_content: default logger message
        :type log_content: string|dict
        """
        topic = bcf.Topic()
        topic.title = log_content.msg["sentence"].split(".\n")[1]
        topic.description = log_content.msg["sentence"].split(".\n")[0]
        self.bcf.add_topic(topic)
        # try:  # Add viewpoint and link to ifc object
        viewpoint = bcf.Viewpoint()
        viewpoint.perspective_camera = bcf.PerspectiveCamera()
        ifc_elem = log_content.msg["ifc_element"]
        # ifc_elem = ifc_file.by_guid(log_content.msg["guid"])
        target_position = np.array(ifcopenshell.util.placement.get_local_placement(ifc_elem.ObjectPlacement))
        target_position = target_position[:, 3][0:3]
        camera_position = target_position + np.array((5, 5, 5))
        viewpoint.perspective_camera.camera_view_point.x = camera_position[0]
        viewpoint.perspective_camera.camera_view_point.y = camera_position[1]
        viewpoint.perspective_camera.camera_view_point.z = camera_position[2]
        camera_direction = camera_position - target_position
        camera_direction = camera_direction / np.linalg.norm(camera_direction)
        camera_right = np.cross(np.array([0.0, 0.0, 1.0]), camera_direction)
        camera_right = camera_right / np.linalg.norm(camera_right)
        camera_up = np.cross(camera_direction, camera_right)
        camera_up = camera_up / np.linalg.norm(camera_up)
        rotation_transform = np.zeros((4, 4))
        rotation_transform[0, :3] = camera_right
        rotation_transform[1, :3] = camera_up
        rotation_transform[2, :3] = camera_direction
        rotation_transform[-1, -1] = 1
        translation_transform = np.eye(4)
        translation_transform[:3, -1] = -camera_position
        look_at_transform = np.matmul(rotation_transform, translation_transform)
        mat = np.linalg.inv(look_at_transform)
        viewpoint.perspective_camera.camera_direction.x = mat[0][2] * -1
        viewpoint.perspective_camera.camera_direction.y = mat[1][2] * -1
        viewpoint.perspective_camera.camera_direction.z = mat[2][2] * -1
        viewpoint.perspective_camera.camera_up_vector.x = mat[0][1]
        viewpoint.perspective_camera.camera_up_vector.y = mat[1][1]
        viewpoint.perspective_camera.camera_up_vector.z = mat[2][1]
        viewpoint.components = bcf.Components()
        c = bcf.Component()
        c.ifc_guid = log_content.msg["guid"]
        viewpoint.components.selection.append(c)
        viewpoint.components.visibility = bcf.ComponentVisibility()
        viewpoint.components.visibility.default_visibility = True
        viewpoint.snapshot = None
        self.bcf.add_viewpoint(topic, viewpoint)

    def flush(self):
        """Saves the BCF report to file. Triggered at the end of the validation process."""
        if not self.filepath:
            self.filepath = os.getcwd() + r"\IDS_report.bcf"
        if not (self.filepath.endswith(".bcf") or self.filepath.endswith(".bcfzip")):
            self.filepath = self.filepath + r"\IDS_report.bcf"
        self.bcf.save_project(self.filepath)
