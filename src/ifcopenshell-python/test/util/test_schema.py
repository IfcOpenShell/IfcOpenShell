# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import pytest

import ifcopenshell
import ifcopenshell.api.project
import ifcopenshell.util.schema as subject
import test.bootstrap


class TestMigrator(test.bootstrap.IFC4):
    def test_migrate_element_using_attribute_mapping_ifc4_ifc4x3(self):
        ifc4_file = ifcopenshell.api.project.create_file()
        original_element = ifc4_file.createIfcWorkTime(Start="2024-01-01", Finish="2024-01-01")
        ifc4x3_file = ifcopenshell.api.project.create_file(version="IFC4X3")

        migrator = subject.Migrator()
        for element in ifc4_file:
            migrator.migrate(element, ifc4x3_file)

        new_element = ifc4x3_file.by_type(original_element.is_a())[0]
        assert original_element.Start == new_element.StartDate
        assert original_element.Finish == new_element.FinishDate

    def test_migrate_element_using_attribute_mapping_ifc4x3_ifc4(self):
        ifc4x3_file = ifcopenshell.api.project.create_file(version="IFC4X3")
        original_element = ifc4x3_file.createIfcWorkTime(StartDate="2024-01-01", FinishDate="2024-01-01")
        ifc4_file = ifcopenshell.api.project.create_file()

        migrator = subject.Migrator()
        for element in ifc4x3_file:
            migrator.migrate(element, ifc4_file)

        new_element = ifc4_file.by_type(original_element.is_a())[0]
        assert original_element.StartDate == new_element.Start
        assert original_element.FinishDate == new_element.Finish

    def test_migrate_element_using_attribute_mapping_ifc2x3_ifc4(self):
        ifc2x3_file = ifcopenshell.api.project.create_file(version="IFC2X3")
        original_element = ifc2x3_file.createIfcImageTexture(TextureType="SPECULAR")
        ifc4_file = ifcopenshell.api.project.create_file()

        migrator = subject.Migrator()
        for element in ifc2x3_file:
            migrator.migrate(element, ifc4_file)

        new_element = ifc4_file.by_type(original_element.is_a())[0]
        assert original_element.TextureType == new_element.Mode

    def test_migrate_element_using_attribute_mapping_ifc4_ifc2x3(self):
        ifc4_file = ifcopenshell.api.project.create_file()
        original_element = ifc4_file.createIfcImageTexture(Mode="SPECULAR")
        ifc2x3_file = ifcopenshell.api.project.create_file(version="IFC2X3")

        migrator = subject.Migrator()
        for element in ifc4_file:
            migrator.migrate(element, ifc2x3_file)

        new_element = ifc2x3_file.by_type(original_element.is_a())[0]
        assert original_element.Mode == new_element.TextureType

    def test_migrate_ifccountmeasure_to_ifc4x3(self):
        ifc_str = """
ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition[DesignTransferView]'),'2;1');
FILE_NAME('count.ifc','2024-11-18T12:44:20+05:00',(''),(''),'','','Nobody');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROPERTYSINGLEVALUE('PropCountInt',$,IFCCOUNTMEASURE(232),$);
#2=IFCPROPERTYSINGLEVALUE('PropCountFloat',$,IFCCOUNTMEASURE(232.),$);
#3=IFCQUANTITYCOUNT('QuantityCountInt',$,$,723,$);
#4=IFCQUANTITYCOUNT('QuantityCountFloat',$,$,723.,$);
ENDSEC;
END-ISO-10303-21;
"""
        ifc4_file = ifcopenshell.file.from_string(ifc_str)
        ifc4x3_file = ifcopenshell.api.project.create_file(version="IFC4X3")

        migrator = subject.Migrator()

        prop_int_count_measure = ifc4_file.by_id(1)
        prop_int_count_measure_ifc4x3 = migrator.migrate(prop_int_count_measure, ifc4x3_file)
        value = prop_int_count_measure_ifc4x3.NominalValue
        assert value.is_a("IfcCountMeasure")
        assert isinstance(value.wrappedValue, int)
        assert value.wrappedValue == 232

        float_count_measure = ifc4_file.by_id(2)
        float_count_measure_ifc4x3 = migrator.migrate(float_count_measure, ifc4x3_file)
        value = float_count_measure_ifc4x3.NominalValue
        assert value.is_a("IfcNumericMeasure")
        assert isinstance(value.wrappedValue, float)
        assert value.wrappedValue == 232.0

        qt_int_count_measure = ifc4_file.by_id(3)
        qt_int_count_measure_ifc4x3 = migrator.migrate(qt_int_count_measure, ifc4x3_file)
        assert qt_int_count_measure_ifc4x3.is_a("IfcQuantityCount")
        assert isinstance(qt_int_count_measure_ifc4x3[3], int)
        assert qt_int_count_measure_ifc4x3[3] == 723

        qt_float_count_measure = ifc4_file.by_id(4)
        qt_float_count_measure_ifc4x3 = migrator.migrate(qt_float_count_measure, ifc4x3_file)
        assert qt_float_count_measure_ifc4x3.is_a("IfcQuantityNumber")
        assert isinstance(qt_float_count_measure_ifc4x3[3], float)
        assert qt_float_count_measure_ifc4x3[3] == 723.0

    def test_migrate_class_raises_clear_error_for_ifc4_only_non_element_class_to_ifc2x3(self):
        """IFC4-only non-element classes (geometry items, etc.) have no
        IfcBuildingElementProxy fallback and must surface a clear error naming
        the failing class — not the cryptic 'Entity name not found in schema'."""
        ifc4_file = ifcopenshell.api.project.create_file()
        point_list = ifc4_file.create_entity("IfcCartesianPointList2D", CoordList=((0.0, 0.0), (1.0, 0.0)))
        ifc2x3_file = ifcopenshell.api.project.create_file(version="IFC2X3")

        migrator = subject.Migrator()
        with pytest.raises(NotImplementedError) as exc_info:
            migrator.migrate(point_list, ifc2x3_file)

        message = str(exc_info.value)
        assert "IfcCartesianPointList2D" in message
        assert "IFC2X3" in message

    def test_migrate_class_falls_back_to_ifcbuildingelementproxy_when_opt_in(self):
        """With ``fallback_element_to_proxy=True``, IFC4-only IfcElement
        subclasses (IfcLamp, IfcPipeSegment, IfcGeographicElement, …) migrate
        as IfcBuildingElementProxy instead of raising. Default behavior
        (no opt-in) raises so non-recipe callers keep the strict contract."""
        ifc4_file = ifcopenshell.api.project.create_file()
        lamp = ifc4_file.create_entity("IfcLamp", GlobalId="2K6Z3DR8X37AS9XFvX8GcW")
        ifc2x3_file = ifcopenshell.api.project.create_file(version="IFC2X3")

        # Default migrator raises (strict contract preserved).
        with pytest.raises(NotImplementedError, match="IfcLamp"):
            subject.Migrator().migrate(lamp, ifc2x3_file)

        # Opt-in migrator substitutes IfcBuildingElementProxy.
        ifc2x3_file = ifcopenshell.api.project.create_file(version="IFC2X3")
        new_lamp = subject.Migrator(fallback_element_to_proxy=True).migrate(lamp, ifc2x3_file)
        assert new_lamp.is_a("IfcBuildingElementProxy")


class TestGetFallbackSchema:
    """Pins the schema-identifier normalisation contract relied on by callers
    that need to map upstream variants (IFC4X3_ADD2, IFC2X3_TC1, IFC4_ADD2, …)
    to a base schema name for compatibility tables / downgrade detection."""

    def test_ifc4x3_variants_collapse_to_ifc4x3(self):
        # Longest-prefix-first: IFC4X3_ADD2 must NOT be misclassified as IFC4
        # — the function checks IFC4X3 before IFC4.
        assert subject.get_fallback_schema("IFC4X3") == "IFC4X3"
        assert subject.get_fallback_schema("IFC4X3_ADD1") == "IFC4X3"
        assert subject.get_fallback_schema("IFC4X3_ADD2") == "IFC4X3"
        assert subject.get_fallback_schema("IFC4X3_RC1") == "IFC4X3"

    def test_ifc4_variants_collapse_to_ifc4(self):
        assert subject.get_fallback_schema("IFC4") == "IFC4"
        assert subject.get_fallback_schema("IFC4_ADD1") == "IFC4"
        assert subject.get_fallback_schema("IFC4_ADD2") == "IFC4"
        # IFC4X1 / IFC4X2 are draft schemas — collapse to IFC4 by design.
        assert subject.get_fallback_schema("IFC4X1") == "IFC4"
        assert subject.get_fallback_schema("IFC4X2") == "IFC4"

    def test_ifc2x3_variants_collapse_to_ifc2x3(self):
        assert subject.get_fallback_schema("IFC2X3") == "IFC2X3"
        assert subject.get_fallback_schema("IFC2X3_TC1") == "IFC2X3"
        assert subject.get_fallback_schema("IFC2X3_FINAL") == "IFC2X3"

    def test_unknown_version_asserts(self):
        # Asserts under non-optimised Python; in -O mode would return the
        # unmodified input. Caller should guard accordingly.
        with pytest.raises(AssertionError):
            subject.get_fallback_schema("IFC10")


class TestIfc4OnlyGeometryClasses:
    def test_known_ifc4_only_classes_present(self):
        result = subject.ifc4_only_geometry_classes()
        # Classes that genuinely don't exist in IFC2X3 and inherit
        # IfcRepresentationItem in IFC4.
        for name in (
            "IfcPolygonalFaceSet",
            "IfcTriangulatedFaceSet",
            "IfcIndexedPolyCurve",
            "IfcCartesianPointList3D",
            "IfcAdvancedBrep",
        ):
            assert name in result, f"{name} should be classified as IFC4-only geometry"

    def test_ifc2x3_compatible_classes_absent(self):
        result = subject.ifc4_only_geometry_classes()
        # Classes that exist in both schemas — must NOT be flagged.
        for name in ("IfcPolyline", "IfcFacetedBrep", "IfcCartesianPoint", "IfcExtrudedAreaSolid"):
            assert name not in result, f"{name} exists in IFC2X3, should not be IFC4-only"

    def test_non_geometry_ifc4_only_classes_absent(self):
        result = subject.ifc4_only_geometry_classes()
        # IFC4-only but not IfcRepresentationItem subclasses — out of scope.
        for name in ("IfcEvent", "IfcWorkCalendar", "IfcLamp"):
            assert name not in result, f"{name} is not an IfcRepresentationItem subclass"

    def test_result_is_cached_frozenset(self):
        first = subject.ifc4_only_geometry_classes()
        second = subject.ifc4_only_geometry_classes()
        assert first is second  # @functools.cache returns the same object


class TestGeometryClassesIntroducedAfter:
    """Generalised version of ``ifc4_only_geometry_classes`` — pins the
    schema-aware contract that supports IFC4X3 → IFC2X3 downgrades, not just
    IFC4 → IFC2X3."""

    def test_ifc4_to_ifc2x3_matches_legacy_helper(self):
        # The legacy ``ifc4_only_geometry_classes`` is now a thin alias.
        assert subject.geometry_classes_introduced_after("IFC2X3", "IFC4") == subject.ifc4_only_geometry_classes()

    def test_ifc4x3_to_ifc2x3_is_superset_of_ifc4_to_ifc2x3(self):
        # IFC4X3 is a superset of IFC4 — every IFC4-only geometry class is
        # also missing from IFC2X3 when the source is IFC4X3, plus any new
        # IFC4X3-only geometry (alignment curves, distance expressions, …).
        ifc4_gap = subject.geometry_classes_introduced_after("IFC2X3", "IFC4")
        ifc4x3_gap = subject.geometry_classes_introduced_after("IFC2X3", "IFC4X3")
        assert ifc4_gap <= ifc4x3_gap

    def test_ifc4_to_ifc4x3_is_empty(self):
        # IFC4X3 contains every IFC4 IfcRepresentationItem subclass — no
        # IFC4 class is missing from IFC4X3.
        assert subject.geometry_classes_introduced_after("IFC4X3", "IFC4") == frozenset()


class TestEnumValueOutsideTarget:
    @staticmethod
    def _attr(class_name: str, attr_name: str):
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC2X3")
        decl = schema.declaration_by_name(class_name)
        return next(a for a in decl.all_attributes() if a.name() == attr_name)

    def test_enum_value_present_in_target_returns_false(self):
        # IfcCovering.PredefinedType is IfcCoveringTypeEnum — CEILING is valid.
        attr = self._attr("IfcCovering", "PredefinedType")
        assert subject._enum_value_outside_target(attr, "CEILING") is False

    def test_enum_value_missing_in_target_returns_true(self):
        # IfcCoveringTypeEnum has no COMPACTFLUORESCENT (an IfcLampTypeEnum value).
        attr = self._attr("IfcCovering", "PredefinedType")
        assert subject._enum_value_outside_target(attr, "COMPACTFLUORESCENT") is True

    def test_non_enum_attribute_returns_false(self):
        # IfcCovering.Name is IfcLabel — not an enum, so the helper must return False.
        attr = self._attr("IfcCovering", "Name")
        assert subject._enum_value_outside_target(attr, "anything") is False

    def test_non_string_value_returns_false(self):
        attr = self._attr("IfcCovering", "PredefinedType")
        assert subject._enum_value_outside_target(attr, 42) is False


class TestExtendedMaterialProperties(test.bootstrap.IFC4):
    def test_migrate_extended_material_properties_ifc2x3_ifc4(self):
        ifc2x3_file = ifcopenshell.api.project.create_file(version="IFC2X3")
        material = ifc2x3_file.createIfcMaterial(Name="Material")
        props = [ifc2x3_file.createIfcPropertySingleValue(Name="Foo")]
        original_element = ifc2x3_file.createIfcExtendedMaterialProperties(Material=material, ExtendedProperties=props)
        ifc4_file = ifcopenshell.api.project.create_file()

        migrator = subject.Migrator()
        for element in ifc2x3_file:
            migrator.migrate(element, ifc4_file)

        new_element = ifc4_file.by_type("IfcMaterialProperties")[0]
        assert new_element.Material.is_a("IfcMaterial")
        assert new_element.Material.Name == "Material"
        assert new_element.Properties[0].is_a("IfcPropertySingleValue")
        assert new_element.Properties[0].Name == "Foo"
