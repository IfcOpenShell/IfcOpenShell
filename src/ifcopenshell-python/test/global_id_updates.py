import pytest
import ifcopenshell

def test_global_id_updates():
    g1, g2, g3 = (ifcopenshell.guid.new() for i in range(3))
    f = ifcopenshell.file()
    
    f.createIfcWall(g1)
    f[g1].GlobalId = g2
    with pytest.raises(RuntimeError):
        f[g1]
    assert f[g2]
    
    inst = f.createIfcWall()
    inst.GlobalId = g3
    assert f[g3]
    
    # Non-unique guid, succeeds but logs an error
    ifcopenshell.get_log()
    inst = f.createIfcWall(g3)
    assert "Overwriting" in ifcopenshell.get_log()

if __name__ == "__main__":
    pytest.main(["-sx", __file__])
