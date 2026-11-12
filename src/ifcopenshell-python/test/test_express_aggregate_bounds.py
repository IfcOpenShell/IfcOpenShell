import os
import sys
import tempfile
import unittest

import ifcopenshell.express

sys.path.insert(0, os.path.dirname(ifcopenshell.express.__file__))


def _parse(schema_text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".exp", delete=False) as f:
        f.write(schema_text)
        path = f.name
    try:
        return ifcopenshell.express.parse(path)
    finally:
        os.unlink(path)
        cache = path + ".cache.dat"
        if os.path.exists(cache):
            os.unlink(cache)


class TestAggregateBounds(unittest.TestCase):
    def test_literal_bounds_preserved(self):
        """After loading [1;3] -> (1, 3)?"""
        s = _parse("SCHEMA t; ENTITY E; v : ARRAY [1:3] OF REAL; END_ENTITY; END_SCHEMA;")
        agg = (
            next(d for d in s.schema.declarations() if d.name() == "E")
            .attributes()[0]
            .type_of_attribute()
            .as_aggregation_type()
        )
        self.assertEqual((agg.bound1(), agg.bound2()), (1, 3))
        s.disown()

    def test_unbounded_marker(self):
        """[0:?] -> (0, -1)?"""
        s = _parse("SCHEMA t; ENTITY E; v : LIST [0:?] OF REAL; END_ENTITY; END_SCHEMA;")
        agg = (
            next(d for d in s.schema.declarations() if d.name() == "E")
            .attributes()[0]
            .type_of_attribute()
            .as_aggregation_type()
        )
        # import pdb; pdb.set_trace()
        self.assertEqual((agg.bound1(), agg.bound2()), (0, -1))
        s.disown()

    def test_voxel_grid_with_dynamic_bound_loads(self):
        """
        Array that is an expression :  [1:dim_x*dim_y*dim_z]
        Parsing must not crash, Bbund must be (1, -1)
        """
        s = _parse("""
            SCHEMA t;
            TYPE IfcBoolean = BOOLEAN; END_TYPE;

            ENTITY IfcVoxelHolder;
              NumberOfVoxelsX : INTEGER;
              NumberOfVoxelsY : INTEGER;
              NumberOfVoxelsZ : INTEGER;
              Voxels : ARRAY [1:NumberOfVoxelsX*NumberOfVoxelsY*NumberOfVoxelsZ] OF IfcBoolean;
            END_ENTITY;
            END_SCHEMA;
            """)
        holder = next(d for d in s.schema.declarations() if d.name() == "IfcVoxelHolder")
        voxels = holder.attributes()[-1].type_of_attribute().as_aggregation_type()
        self.assertEqual((voxels.bound1(), voxels.bound2()), (1, -1))
        s.disown()


if __name__ == "__main__":
    unittest.main()
