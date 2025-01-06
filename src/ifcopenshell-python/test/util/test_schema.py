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

import test.bootstrap
import ifcopenshell.api.project
import ifcopenshell.util.schema as subject


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
