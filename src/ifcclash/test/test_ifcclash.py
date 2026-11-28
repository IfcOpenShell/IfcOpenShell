# This file was generated with the assistance of an AI coding tool.

import logging
from unittest import mock

import ifcclash.ifcclash as subject


def process(clash_set):
    settings = subject.ClashSettings()
    settings.logger = logging.getLogger("test")
    clasher = subject.Clasher(settings)
    with (
        mock.patch.object(subject.ifcopenshell.geom, "tree") as tree,
        mock.patch.object(clasher, "load_ifc"),
        mock.patch.object(clasher, "add_collision_objects"),
    ):
        tree.return_value.clash_intersection_many.return_value = []
        tree.return_value.clash_collision_many.return_value = []
        tree.return_value.clash_clearance_many.return_value = []
        clasher.process_clash_set(clash_set)
    return tree.return_value


class TestProcessClashSet:
    def test_intersection_defaults_when_optional_keys_are_omitted(self):
        tree = process({"name": "Set", "a": [{"file": "a.ifc"}], "mode": "intersection"})
        assert tree.clash_intersection_many.call_args.kwargs == {"tolerance": 0.002, "check_all": True}

    def test_collision_defaults_when_optional_keys_are_omitted(self):
        tree = process({"name": "Set", "a": [{"file": "a.ifc"}], "mode": "collision"})
        assert tree.clash_collision_many.call_args.kwargs == {"allow_touching": False}

    def test_clearance_defaults_when_optional_keys_are_omitted(self):
        tree = process({"name": "Set", "a": [{"file": "a.ifc"}], "mode": "clearance"})
        assert tree.clash_clearance_many.call_args.kwargs == {"clearance": 0.05, "check_all": False}

    def test_explicit_keys_are_passed_through(self):
        clash_set = {"name": "Set", "a": [{"file": "a.ifc"}], "mode": "collision", "allow_touching": True}
        tree = process(clash_set)
        assert tree.clash_collision_many.call_args.kwargs == {"allow_touching": True}
