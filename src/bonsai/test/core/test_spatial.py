# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bonsai.core.spatial as subject
from test.core.bootstrap import collector, ifc, spatial


class TestReferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run("spatial.reference_structure", products=["element"], relating_structure="structure").should_be_called()
        subject.reference_structure(ifc, spatial, structure="structure", element="element")


class TestDereferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run(
            "spatial.dereference_structure", products=["element"], relating_structure="structure"
        ).should_be_called()
        subject.dereference_structure(ifc, spatial, structure="structure", element="element")


class TestAssignContainer:
    def test_run(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_root_element("element").should_be_called().will_return("aggregate")
        spatial.get_decomposition("aggregate").should_be_called().will_return(["element", "element2"])
        spatial.can_contain("container", "aggregate").should_be_called().will_return(True)
        ifc.run("spatial.assign_container", products=["aggregate"], relating_structure="container").should_be_called()
        spatial.disable_editing("obj").should_be_called()
        ifc.get_object("aggregate").should_be_called().will_return("aggregate_obj")
        ifc.get_object("element").should_be_called().will_return("obj")
        ifc.get_object("element2").should_be_called().will_return("obj2")
        collector.assign("aggregate_obj").should_be_called()
        collector.assign("obj").should_be_called()
        collector.assign("obj2").should_be_called()
        subject.assign_container(ifc, collector, spatial, container="container", objs=["obj"])


class TestEnableEditingContainer:
    def test_run(self, spatial):
        spatial.set_target_container_as_default().should_be_called()
        spatial.enable_editing("obj").should_be_called()
        subject.enable_editing_container(spatial, obj="obj")


class TestDisableEditingContainer:
    def test_run(self, spatial):
        spatial.disable_editing("obj").should_be_called()
        subject.disable_editing_container(spatial, obj="obj")


class TestRemoveContainer:
    def test_run(self, ifc, collector):
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("spatial.unassign_container", products=["element"]).should_be_called()
        collector.assign("obj").should_be_called()
        subject.remove_container(ifc, collector, obj="obj")


class TestCopyToContainer:
    def test_run(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.get_relative_object_matrix("obj", "container_obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(container="to_container", objs=["new_obj"]).should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, collector, spatial, obj="obj", containers=["to_container"])

    def test_using_an_absolute_matrix_if_there_is_no_from_container(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return(None)
        spatial.get_object_matrix("obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(container="to_container", objs=["new_obj"]).should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, collector, spatial, obj="obj", containers=["to_container"])


class TestSelectContainer:
    def test_run(self, ifc, spatial):
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.set_active_object("container_obj", selection_mode="ADD").should_be_called()
        subject.select_container(ifc, spatial, container="container", selection_mode="ADD")


class TestSelectSimilarContainer:
    def test_run(self, ifc, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        spatial.get_decomposed_elements("container", True).should_be_called().will_return(["contained_element"])
        spatial.select_products(["contained_element"]).should_be_called()
        subject.select_similar_container(ifc, spatial, obj="obj")


class TestDeleteContainer:
    def test_run_cascades_container_and_dependent_annotations(self, monkeypatch):
        class FakeElement:
            def __init__(self, element_id, ifc_class, object_type=None):
                self._id = element_id
                self._ifc_class = ifc_class
                self.ObjectType = object_type
                self.IsDecomposedBy = []

            def id(self):
                return self._id

            def is_a(self, ifc_class):
                if self._ifc_class == ifc_class:
                    return True
                spatial_classes = {
                    "IfcSpatialElement",
                    "IfcSpatialStructureElement",
                    "IfcExternalSpatialStructureElement",
                }
                if ifc_class in spatial_classes and self._ifc_class in {
                    "IfcProject",
                    "IfcSite",
                    "IfcBuilding",
                    "IfcBuildingStorey",
                    "IfcSpace",
                }:
                    return True
                return False

        class FakeRelAssignsToProduct:
            def __init__(self, relating_product, related_objects):
                self.RelatingProduct = relating_product
                self.RelatedObjects = tuple(related_objects)

            def is_a(self, ifc_class):
                return ifc_class == "IfcRelAssignsToProduct"

        class FakeRelAggregates:
            def __init__(self, related_objects):
                self.RelatedObjects = tuple(related_objects)

        class FakeIfcFile:
            def __init__(self, elements, inverse_map):
                self.elements = elements
                self.inverse_map = inverse_map

            def by_id(self, element_id):
                return self.elements[element_id]

            def get_inverse(self, element):
                return self.inverse_map.get(element.id(), [])

        container = FakeElement(1, "IfcBuilding")
        storey = FakeElement(2, "IfcBuildingStorey")
        wall = FakeElement(3, "IfcWall")
        section_level = FakeElement(4, "IfcAnnotation", object_type="SECTION_LEVEL")
        container.IsDecomposedBy = [FakeRelAggregates([storey])]

        fake_file = FakeIfcFile(
            {1: container, 2: storey, 3: wall, 4: section_level},
            {2: [FakeRelAssignsToProduct(storey, [section_level])]},
        )

        monkeypatch.setattr(
            subject.ifcopenshell.util.element,
            "get_decomposition",
            lambda element, is_recursive=True: {storey, wall},
        )
        monkeypatch.setattr(
            subject.ifcopenshell.util.element,
            "get_container",
            lambda element: storey if element == wall else None,
        )

        deleted_objects = []
        run_calls = []
        imported = []

        class FakeIfc:
            @staticmethod
            def get():
                return fake_file

            @staticmethod
            def get_object(element):
                return None if element.id() == 3 else f"obj-{element.id()}"

            @staticmethod
            def run(usecase, **kwargs):
                run_calls.append((usecase, kwargs))

        class FakeGeometry:
            @staticmethod
            def delete_ifc_object(
                obj, allow_auto_annotation_deletion=False, suppress_spatial_import=False
            ):
                deleted_objects.append((obj, allow_auto_annotation_deletion, suppress_spatial_import))

        class FakeSpatial:
            @staticmethod
            def import_spatial_decomposition():
                imported.append(True)

        subject.delete_container(FakeIfc, FakeSpatial, FakeGeometry, container=container)

        assert deleted_objects == [
            ("obj-4", True, True),  # dependent SECTION_LEVEL annotation
            ("obj-1", False, True),  # container
            ("obj-2", False, True),  # decomposed storey
        ]
        assert run_calls == [("root.remove_product", {"product": wall})]
        assert imported == [True]

    def test_does_not_delete_elements_outside_spatial_subtree(self, monkeypatch):
        class FakeElement:
            def __init__(self, element_id, ifc_class):
                self._id = element_id
                self._ifc_class = ifc_class
                self.IsDecomposedBy = []

            def id(self):
                return self._id

            def is_a(self, ifc_class):
                if self._ifc_class == ifc_class:
                    return True
                spatial_classes = {
                    "IfcSpatialElement",
                    "IfcSpatialStructureElement",
                    "IfcExternalSpatialStructureElement",
                }
                if ifc_class in spatial_classes and self._ifc_class in {"IfcBuilding", "IfcBuildingStorey"}:
                    return True
                return False

        class FakeRelAggregates:
            def __init__(self, related_objects):
                self.RelatedObjects = tuple(related_objects)

        class FakeIfcFile:
            def __init__(self, elements):
                self.elements = elements

            def by_id(self, element_id):
                return self.elements[element_id]

            def get_inverse(self, element):
                return []

        container = FakeElement(1, "IfcBuilding")
        own_storey = FakeElement(2, "IfcBuildingStorey")
        other_storey = FakeElement(3, "IfcBuildingStorey")
        own_wall = FakeElement(4, "IfcWall")
        outside_wall = FakeElement(5, "IfcWall")
        container.IsDecomposedBy = [FakeRelAggregates([own_storey])]

        fake_file = FakeIfcFile({1: container, 2: own_storey, 3: other_storey, 4: own_wall, 5: outside_wall})

        monkeypatch.setattr(
            subject.ifcopenshell.util.element,
            "get_decomposition",
            lambda element, is_recursive=True: {own_storey, own_wall, outside_wall},
        )
        monkeypatch.setattr(
            subject.ifcopenshell.util.element,
            "get_container",
            lambda element: own_storey if element == own_wall else (other_storey if element == outside_wall else None),
        )

        deleted_objects = []
        run_calls = []
        imported = []

        class FakeIfc:
            @staticmethod
            def get():
                return fake_file

            @staticmethod
            def get_object(element):
                return f"obj-{element.id()}"

            @staticmethod
            def run(usecase, **kwargs):
                run_calls.append((usecase, kwargs))

        class FakeGeometry:
            @staticmethod
            def delete_ifc_object(
                obj, allow_auto_annotation_deletion=False, suppress_spatial_import=False
            ):
                deleted_objects.append((obj, allow_auto_annotation_deletion, suppress_spatial_import))

        class FakeSpatial:
            @staticmethod
            def import_spatial_decomposition():
                imported.append(True)

        subject.delete_container(FakeIfc, FakeSpatial, FakeGeometry, container=container)

        assert deleted_objects == [
            ("obj-1", False, True),  # container
            ("obj-2", False, True),  # own storey
            ("obj-4", False, True),  # own wall
        ]
        assert run_calls == []
        assert imported == [True]

    def test_reassigns_default_container_after_cascade_if_deleted(self, monkeypatch):
        class FakeElement:
            def __init__(self, element_id, ifc_class):
                self._id = element_id
                self._ifc_class = ifc_class
                self.IsDecomposedBy = []

            def id(self):
                return self._id

            def is_a(self, ifc_class):
                if self._ifc_class == ifc_class:
                    return True
                if ifc_class in {"IfcSpatialElement", "IfcSpatialStructureElement"} and self._ifc_class in {
                    "IfcBuilding",
                    "IfcBuildingStorey",
                }:
                    return True
                return False

        class FakeRelAggregates:
            def __init__(self, related_objects):
                self.RelatedObjects = tuple(related_objects)

        class FakeIfcFile:
            def __init__(self, elements):
                self.elements = elements

            def by_id(self, element_id):
                return self.elements[element_id]

            def get_inverse(self, element):
                return []

        container = FakeElement(1, "IfcBuilding")
        storey = FakeElement(2, "IfcBuildingStorey")
        replacement_storey = FakeElement(3, "IfcBuildingStorey")
        container.IsDecomposedBy = [FakeRelAggregates([storey])]

        fake_file = FakeIfcFile({1: container, 2: storey, 3: replacement_storey})

        monkeypatch.setattr(
            subject.ifcopenshell.util.element, "get_decomposition", lambda element, is_recursive=True: {storey}
        )
        monkeypatch.setattr(subject.ifcopenshell.util.element, "get_container", lambda element: None)

        class FakeIfc:
            @staticmethod
            def get():
                return fake_file

            @staticmethod
            def get_object(element):
                return f"obj-{element.id()}"

            @staticmethod
            def run(usecase, **kwargs):
                return None

        class FakeGeometry:
            @staticmethod
            def delete_ifc_object(
                obj, allow_auto_annotation_deletion=False, suppress_spatial_import=False
            ):
                return None

        imported = []
        set_default_calls = []

        class FakeSpatialProps:
            default_container = 2

        class FakeSpatial:
            @staticmethod
            def get_spatial_props():
                return FakeSpatialProps

            @staticmethod
            def guess_default_container():
                return replacement_storey

            @staticmethod
            def set_default_container(container):
                set_default_calls.append(container)

            @staticmethod
            def import_spatial_decomposition():
                imported.append(True)

        class FakeRoot:
            @staticmethod
            def get_default_container():
                return storey

        subject.delete_container(FakeIfc, FakeSpatial, FakeGeometry, container=container, root=FakeRoot)

        assert set_default_calls == [replacement_storey]
        assert imported == [True]

    def test_keeps_default_container_if_not_deleted(self, monkeypatch):
        class FakeElement:
            def __init__(self, element_id, ifc_class):
                self._id = element_id
                self._ifc_class = ifc_class
                self.IsDecomposedBy = []

            def id(self):
                return self._id

            def is_a(self, ifc_class):
                if self._ifc_class == ifc_class:
                    return True
                if ifc_class in {"IfcSpatialElement", "IfcSpatialStructureElement"} and self._ifc_class in {
                    "IfcBuilding",
                    "IfcBuildingStorey",
                }:
                    return True
                return False

        class FakeRelAggregates:
            def __init__(self, related_objects):
                self.RelatedObjects = tuple(related_objects)

        class FakeIfcFile:
            def __init__(self, elements):
                self.elements = elements

            def by_id(self, element_id):
                return self.elements[element_id]

            def get_inverse(self, element):
                return []

        container = FakeElement(1, "IfcBuilding")
        deleted_storey = FakeElement(2, "IfcBuildingStorey")
        surviving_storey = FakeElement(3, "IfcBuildingStorey")
        container.IsDecomposedBy = [FakeRelAggregates([deleted_storey])]

        fake_file = FakeIfcFile({1: container, 2: deleted_storey, 3: surviving_storey})

        monkeypatch.setattr(
            subject.ifcopenshell.util.element, "get_decomposition", lambda element, is_recursive=True: {deleted_storey}
        )
        monkeypatch.setattr(subject.ifcopenshell.util.element, "get_container", lambda element: None)

        class FakeIfc:
            @staticmethod
            def get():
                return fake_file

            @staticmethod
            def get_object(element):
                return f"obj-{element.id()}"

            @staticmethod
            def run(usecase, **kwargs):
                return None

        class FakeGeometry:
            @staticmethod
            def delete_ifc_object(
                obj, allow_auto_annotation_deletion=False, suppress_spatial_import=False
            ):
                return None

        set_default_calls = []

        class FakeSpatial:
            @staticmethod
            def guess_default_container():
                return deleted_storey

            @staticmethod
            def set_default_container(container):
                set_default_calls.append(container)

            @staticmethod
            def import_spatial_decomposition():
                return None

        class FakeRoot:
            @staticmethod
            def get_default_container():
                return surviving_storey

        subject.delete_container(FakeIfc, FakeSpatial, FakeGeometry, container=container, root=FakeRoot)

        assert set_default_calls == []

    def test_clears_default_container_if_deleted_and_no_replacement(self, monkeypatch):
        class FakeElement:
            def __init__(self, element_id, ifc_class):
                self._id = element_id
                self._ifc_class = ifc_class
                self.IsDecomposedBy = []

            def id(self):
                return self._id

            def is_a(self, ifc_class):
                if self._ifc_class == ifc_class:
                    return True
                if ifc_class in {"IfcSpatialElement", "IfcSpatialStructureElement"} and self._ifc_class in {
                    "IfcBuilding",
                    "IfcBuildingStorey",
                }:
                    return True
                return False

        class FakeRelAggregates:
            def __init__(self, related_objects):
                self.RelatedObjects = tuple(related_objects)

        class FakeIfcFile:
            def __init__(self, elements):
                self.elements = elements

            def by_id(self, element_id):
                return self.elements[element_id]

            def get_inverse(self, element):
                return []

        container = FakeElement(1, "IfcBuilding")
        storey = FakeElement(2, "IfcBuildingStorey")
        container.IsDecomposedBy = [FakeRelAggregates([storey])]

        fake_file = FakeIfcFile({1: container, 2: storey})

        monkeypatch.setattr(
            subject.ifcopenshell.util.element, "get_decomposition", lambda element, is_recursive=True: {storey}
        )
        monkeypatch.setattr(subject.ifcopenshell.util.element, "get_container", lambda element: None)

        class FakeIfc:
            @staticmethod
            def get():
                return fake_file

            @staticmethod
            def get_object(element):
                return f"obj-{element.id()}"

            @staticmethod
            def run(usecase, **kwargs):
                return None

        class FakeGeometry:
            @staticmethod
            def delete_ifc_object(
                obj, allow_auto_annotation_deletion=False, suppress_spatial_import=False
            ):
                return None

        class FakeSpatialProps:
            default_container = 2

        class FakeSpatial:
            @staticmethod
            def get_spatial_props():
                return FakeSpatialProps

            @staticmethod
            def guess_default_container():
                return None

            @staticmethod
            def set_default_container(container):
                raise AssertionError("set_default_container should not be called when no replacement exists")

            @staticmethod
            def import_spatial_decomposition():
                return None

        class FakeRoot:
            @staticmethod
            def get_default_container():
                return storey

        subject.delete_container(FakeIfc, FakeSpatial, FakeGeometry, container=container, root=FakeRoot)

        assert FakeSpatialProps.default_container == 0
