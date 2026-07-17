import ifcopenshell

def test_skip_over_non_entity_instance():
    data = """
ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;
DATA;
#1=IFCLENGTHMEASURE(0.1);
#5=IFCCARTESIANPOINT((0.,0.));
ENDSEC;
END-ISO-10303-21;
"""
    f = ifcopenshell.file.from_string(data)
    print(ifcopenshell.get_log())
    f.by_id(5)


def test_reference_to_undefined_owning_instance():
    data = "ISO-10303-21;HEADER;FILE_DESCRIPTION();FILE_NAME();FILE_SCHEMA(('IFC4'));#=IFCRELAGGREGATES((#))#5=IFCPOINT)"
    ifcopenshell.file.from_string(data)
    print(ifcopenshell.get_log())


def test_reference_to_undefined_owning_instance_simple_type():
    data = "ISO-10303-21;HEADER;FILE_DESCRIPTION();FILE_NAME();FILE_SCHEMA(('IFC4'));#=IFCPROJECT((#))#4=IFCSIUNIT("
    ifcopenshell.file.from_string(data)
    print(ifcopenshell.get_log())
