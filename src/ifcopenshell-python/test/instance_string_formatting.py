import pytest
import ifcopenshell

def test_file_gc():
    f = ifcopenshell.file()
    inst = f.createIfcWall(ifcopenshell.guid.new(), Name=chr(0x1F37A))
    # 0x1F37A should be encoded using X4
    assert '\\X4\\' in inst.to_string()
    # to_string() should use upper case entity names
    assert 'IFCWALL' in inst.to_string()
    # __str__ uses camel case entity names
    assert 'IfcWall' in str(inst)
    # in fact, __str__ is equal to to_string(False)
    assert str(inst) == inst.to_string(False)

if __name__ == "__main__":
    pytest.main(["-sx", __file__])
