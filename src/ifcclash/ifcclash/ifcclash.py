#!/usr/bin/env python3

# IfcClash - IFC-based clash detection.
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcClash.
#
# IfcClash is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcClash is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcClash.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np
import json
import sys
import argparse
import logging
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector
from . import collider


class Clasher:
    def __init__(self, settings):
        self.settings = settings
        self.geom_settings = ifcopenshell.geom.settings()
        self.clash_sets = []
        self.collider = collider.Collider(self.settings.logger)
        self.selector = ifcopenshell.util.selector.Selector()
        self.ifcs = {}

    def clash(self):
        existing_limit = sys.getrecursionlimit()
        for clash_set in self.clash_sets:
            self.process_clash_set(clash_set)

    def process_clash_set(self, clash_set):
        self.collider.create_group("a")
        for source in clash_set["a"]:
            source["ifc"] = self.load_ifc(source["file"])
            self.add_collision_objects("a", source["ifc"], source.get("mode", None), source.get("selector", None))

        if "b" in clash_set:
            self.collider.create_group("b")
            for source in clash_set["b"]:
                source["ifc"] = self.load_ifc(source["file"])
                self.add_collision_objects("b", source["ifc"], source.get("mode", None), source.get("selector", None))
            results = self.collider.collide_group("a", "b")
        else:
            results = self.collider.collide_internal("a")

        processed_results = {}
        for result in results:
            element1 = self.get_element(clash_set["a"], result["id1"])
            if "b" in clash_set:
                element2 = self.get_element(clash_set["b"], result["id2"])
            else:
                element2 = self.get_element(clash_set["a"], result["id2"])

            contact = result["collision"].getContacts()[0]
            processed_results[f"{result['id1']}-{result['id2']}"] = {
                "a_global_id": result["id1"],
                "b_global_id": result["id2"],
                "a_ifc_class": element1.is_a(),
                "b_ifc_class": element2.is_a(),
                "a_name": element1.Name,
                "b_name": element2.Name,
                "normal": list(contact.normal),
                "position": list(contact.pos),
                "penetration_depth": contact.penetration_depth,
            }
        clash_set["clashes"] = processed_results

    def load_ifc(self, path):
        import time

        start = time.time()
        self.settings.logger.info(f"Loading IFC {path}")
        ifc = self.ifcs.get(path, None)
        if not ifc:
            ifc = ifcopenshell.open(path)
            self.ifcs[path] = ifc
        self.settings.logger.info(f"Loading finished {time.time() - start}")
        return ifc

    def add_collision_objects(self, name, ifc_file, mode=None, selector=None):
        import time

        start = time.time()
        self.settings.logger.info("Creating iterator")
        if not mode:
            elements = ifc_file.by_type("IfcElement")
        elif mode == "e":
            elements = set(ifc_file.by_type("IfcElement")) - set(self.selector.parse(ifc_file, selector))
        elif mode == "i":
            elements = self.selector.parse(ifc_file, selector)
        iterator = ifcopenshell.geom.iterator(
            self.geom_settings, ifc_file, multiprocessing.cpu_count(), include=elements
        )
        self.settings.logger.info(f"Iterator creation finished {time.time() - start}")
        self.collider.create_objects(name, ifc_file, iterator, elements)

    def export(self):
        if len(self.settings.output) > 4 and self.settings.output[-4:] == ".bcf":
            return self.export_bcfxml()
        self.export_json()

    def export_bcfxml(self):
        import bcf
        import bcf.v2.bcfxml

        for i, clash_set in enumerate(self.clash_sets):
            bcfxml = bcf.v2.bcfxml.BcfXml()
            bcfxml.new_project()
            bcfxml.project.name = clash_set["name"]
            bcfxml.edit_project()
            for key, clash in clash_set["clashes"].items():
                topic = bcf.v2.data.Topic()
                topic.title = "{}/{} and {}/{}".format(
                    clash["a_ifc_class"], clash["a_name"], clash["b_ifc_class"], clash["b_name"]
                )
                topic = bcfxml.add_topic(topic)
                viewpoint = bcf.v2.data.Viewpoint()
                viewpoint.perspective_camera = bcf.v2.data.PerspectiveCamera()
                position = np.array(clash["position"])
                point = position + np.array((5, 5, 5))  # Dumb, but works (for now)!
                viewpoint.perspective_camera.camera_view_point.x = point[0]
                viewpoint.perspective_camera.camera_view_point.y = point[1]
                viewpoint.perspective_camera.camera_view_point.z = point[2]
                mat = self.get_track_to_matrix(point, position)
                viewpoint.perspective_camera.camera_direction.x = mat[0][2] * -1
                viewpoint.perspective_camera.camera_direction.y = mat[1][2] * -1
                viewpoint.perspective_camera.camera_direction.z = mat[2][2] * -1
                viewpoint.perspective_camera.camera_up_vector.x = mat[0][1]
                viewpoint.perspective_camera.camera_up_vector.y = mat[1][1]
                viewpoint.perspective_camera.camera_up_vector.z = mat[2][1]
                viewpoint.components = bcf.v2.data.Components()
                c1 = bcf.v2.data.Component()
                c1.ifc_guid = clash["a_global_id"]
                c2 = bcf.v2.data.Component()
                c2.ifc_guid = clash["b_global_id"]
                viewpoint.components.selection.append(c1)
                viewpoint.components.selection.append(c2)
                viewpoint.components.visibility = bcf.v2.data.ComponentVisibility()
                viewpoint.components.visibility.default_visibility = True
                viewpoint.snapshot = self.get_viewpoint_snapshot(viewpoint, mat)
                bcfxml.add_viewpoint(topic, viewpoint)
            if i == 0:
                bcfxml.save_project(self.settings.output)
            else:
                bcfxml.save_project(self.settings.output + f".{i}")

    def get_viewpoint_snapshot(self, viewpoint, mat):
        return None  # Possible to overload this function in a GUI application if used as a library

    # https://blender.stackexchange.com/questions/68834/recreate-to-track-quat-with-two-vectors-using-python/141706#141706
    def get_track_to_matrix(self, camera_position, target_position):
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
        return np.linalg.inv(look_at_transform)

    def export_json(self):
        clash_sets = self.clash_sets.copy()
        for clash_set in clash_sets:
            for source in clash_set["a"]:
                del source["ifc"]
            for source in clash_set.get("b", []):
                del source["ifc"]
        with open(self.settings.output, "w", encoding="utf-8") as clashes_file:
            json.dump(clash_sets, clashes_file, indent=4)

    def get_element(self, clash_set, global_id):
        for source in clash_set:
            try:
                element = source["ifc"].by_guid(global_id)
                if element:
                    return element
            except:
                pass

    def smart_group_clashes(self, clash_sets, max_clustering_distance):
        from sklearn.cluster import OPTICS
        from collections import defaultdict

        count_of_input_clashes = 0
        count_of_clash_sets = 0
        count_of_smart_groups = 0
        count_of_final_clash_sets = 0

        count_of_clash_sets = len(clash_sets)

        for clash_set in clash_sets:
            if not "clashes" in clash_set.keys():
                self.settings.logger.info(
                    f"Skipping clash set [{clash_set['name']}] since it contains no clash results."
                )
                continue
            clashes = clash_set["clashes"]
            if len(clashes) == 0:
                self.settings.logger.info(
                    f"Skipping clash set [{clash_set['name']}] since it contains no clash results."
                )
                continue

            count_of_input_clashes += len(clashes)

            positions = []
            for clash in clashes.values():
                positions.append(clash["position"])

            data = np.array(positions)

            # INPUTS
            # set the desired maximum distance between the grouped points
            if max_clustering_distance > 0:
                max_distance_between_grouped_points = max_clustering_distance
            else:
                max_distance_between_grouped_points = 3

            model = OPTICS(min_samples=2, max_eps=max_distance_between_grouped_points)
            model.fit_predict(data)
            pred = model.fit_predict(data)

            # Insert the smart groups into the clashes
            if len(pred) == len(clashes.values()):
                i = 0
                for clash in clashes.values():
                    int_prediction = int(pred[i])
                    if int_prediction == -1:
                        # ungroup this clash since it's a single clash that we were not able to group.
                        new_clash_group_number = np.amax(pred).item() + 1 + i
                        clash["smart_group"] = new_clash_group_number
                    else:
                        clash["smart_group"] = int_prediction
                    i += 1

        # Create JSON with smart_groups that contain GlobalIDs
        output_clash_sets = defaultdict(list)
        for clash_set in clash_sets:
            if not "clashes" in clash_set.keys():
                continue
            smart_groups = defaultdict(list)
            for clash_id, content in clash_set["clashes"].items():
                if "smart_group" in content:
                    object_id_list = list()
                    # Clash has been grouped, let's extract it.
                    object_id_list.append(content["a_global_id"])
                    object_id_list.append(content["b_global_id"])
                    smart_groups[content["smart_group"]].append(object_id_list)
            count_of_smart_groups += len(smart_groups)
            output_clash_sets[clash_set["name"]].append(smart_groups)

        # Rename the clash groups to something more sensible
        for clash_set, smart_groups in output_clash_sets.items():
            clash_set_name = clash_set
            # Only select the clashes that correspond to the actively selected IFC Clash Set
            i = 1
            new_smart_group_name = ""
            for smart_group, global_id_pairs in list(smart_groups[0].items()):
                new_smart_group_name = f"{clash_set_name} - {i}"
                smart_groups[0][new_smart_group_name] = smart_groups[0].pop(smart_group)
                i += 1

        count_of_final_clash_sets = len(output_clash_sets)
        self.settings.logger.info(
            f"Took {count_of_input_clashes} clashes in {count_of_clash_sets} clash sets and turned them into {count_of_smart_groups} smart groups in {count_of_final_clash_sets} clash sets"
        )

        return output_clash_sets


class ClashSettings:
    def __init__(self):
        self.logger = None
        self.output = "clashes.json"
