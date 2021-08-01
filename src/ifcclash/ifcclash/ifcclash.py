#!/usr/bin/env python3

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector
import multiprocessing
import numpy as np
import json
import sys
import argparse
import logging
from . import collider


class Clasher:
    def __init__(self, settings):
        self.settings = settings
        self.geom_settings = ifcopenshell.geom.settings()
        self.clash_sets = []
        self.collider = collider.Collider()
        self.selector = ifcopenshell.util.selector.Selector()
        self.ifcs = {}

    def clash(self):
        existing_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(100000)
        for clash_set in self.clash_sets:
            self.process_clash_set(clash_set)
        sys.setrecursionlimit(existing_limit)

    def process_clash_set(self, clash_set):
        print("proccessings", clash_set)
        self.collider.create_group("a")
        for source in clash_set["a"]:
            self.add_collision_objects(
                "a", self.load_ifc(source["file"]), source.get("mode", None), source.get("selector", None)
            )

        if "b" in clash_set:
            self.collider.create_group("b")
            for source in clash_set["b"]:
                self.add_collision_objects(
                    "b", self.load_ifc(source["file"]), source.get("mode", None), source.get("selector", None)
                )
            results = self.collider.collide_group("a", "b")
        else:
            results = self.collider.collide_internal("a")

        for result in results:
            print("*" * 10)
            print("Is Collision:", result["collision"].isCollision())
            print(result["id1"], result["id2"])
            print("Number of contacts:", result["collision"].numContacts())
            for contact in result["collision"].getContacts():
                print(contact)

    def load_ifc(self, path):
        ifc = self.ifcs.get(path, None)
        if not ifc:
            ifc = ifcopenshell.open(path)
            self.ifcs[path] = ifc
        return ifc

    def add_collision_objects(self, name, ifc_file, mode=None, selector=None):
        print('adding collision objects', name)
        if not mode:
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                exclude=(ifc_file.by_type("IfcSpatialStructureElement")),
            )
        elif mode == "e":
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                exclude=selector.parse(ifc_file, selector),
            )
        elif mode == "i":
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=selector.parse(ifc_file, selector),
            )
        valid_file = iterator.initialize()
        if not valid_file:
            return False
        old_progress = -1
        while True:
            shape = iterator.get()
            self.collider.create_object(name, shape.guid, shape)
            if not iterator.next():
                break

    def export(self):
        if len(self.settings.output) > 4 and self.settings.output[-4:] == ".bcf":
            return self.export_bcfxml()
        self.export_json()

    def export_bcfxml(self):
        import bcf
        import bcf.bcfxml

        for i, clash_set in enumerate(self.clash_sets):
            bcfxml = bcf.bcfxml.BcfXml()
            bcfxml.new_project()
            bcfxml.project.name = clash_set["name"]
            bcfxml.edit_project()
            for key, clash in clash_set["clashes"].items():
                topic = bcf.data.Topic()
                topic.title = "{}/{} and {}/{}".format(
                    clash["a_ifc_class"], clash["a_name"], clash["b_ifc_class"], clash["b_name"]
                )
                topic = bcfxml.add_topic(topic)
                viewpoint = bcf.data.Viewpoint()
                viewpoint.perspective_camera = bcf.data.PerspectiveCamera()
                position = np.array(clash["position"])
                point = position + np.array((5, 5, 5))  # Dumb, but works!
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
                viewpoint.components = bcf.data.Components()
                c1 = bcf.data.Component()
                c1.ifc_guid = clash["a_global_id"]
                c2 = bcf.data.Component()
                c2.ifc_guid = clash["b_global_id"]
                viewpoint.components.selection.append(c1)
                viewpoint.components.selection.append(c2)
                viewpoint.components.visibility = bcf.data.ComponentVisibility()
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
        results = self.clash_sets.copy()
        for result in results:
            del result["a_cm"]
            del result["b_cm"]
            for ab in ["a", "b"]:
                for data in result[ab]:
                    if "ifc" in data:
                        del data["ifc"]
        with open(self.settings.output, "w", encoding="utf-8") as clashes_file:
            json.dump(results, clashes_file, indent=4)

    def get_element(self, clash_group, global_id):
        for data in clash_group:
            try:
                element = data["ifc"].by_guid(global_id)
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
                print(f"Skipping clash set [{clash_set['name']}] since it contains no clash results.")
                continue
            clashes = clash_set["clashes"]
            if len(clashes) == 0:
                print(f"Skipping clash set [{clash_set['name']}] since it contains no clash results.")
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
        print(
            f"Took {count_of_input_clashes} clashes in {count_of_clash_sets} clash sets and turned",
            f"them into {count_of_smart_groups} smart groups in {count_of_final_clash_sets} clash sets",
        )

        return output_clash_sets


class ClashSettings:
    def __init__(self):
        self.logger = None
        self.output = "clashes.json"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clashes geometry between two IFC files")
    parser.add_argument("input", type=str, help="A JSON dataset describing a series of clashsets")
    parser.add_argument(
        "-o", "--output", type=str, help="The JSON diff file to output. Defaults to output.json", default="output.json"
    )
    args = parser.parse_args()

    settings = ClashSettings()
    settings.output = args.output
    settings.logger = logging.getLogger("Clash")
    settings.logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    settings.logger.addHandler(handler)
    ifc_clasher = Clasher(settings)
    with open(args.input, "r") as clash_sets_file:
        ifc_clasher.clash_sets = json.loads(clash_sets_file.read())
    ifc_clasher.clash()
    ifc_clasher.export()
