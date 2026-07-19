###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

# Some basic tests. Currently only covering basic I/O.

import os
import uuid

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid

f = ifcopenshell.open("input/acad2010_walls.ifc")

# Some operations on ifcopenshell.file
assert f[1].is_a("IfcCartesianPoint")
assert f[1].is_a("IfcRepresentationItem")
assert f[1].is_a() == "IfcCartesianPoint"
assert f.by_id(1).is_a("IfcCartesianPoint")
assert f["28pa2ppDf1IA$BaQrvAf48"].is_a("IfcProject")
assert f.by_guid("28pa2ppDf1IA$BaQrvAf48").is_a("IfcProject")
assert f.createIfcCartesianPoint((0.0, 0.0, 0.0)).is_a("IfcCartesianPoint")
assert f.by_type("IfcProject")[0].is_a("IfcProject")
assert f.traverse(f[16])[-1].is_a("IFCSIUNIT")
assert len(f.traverse(f[35], 1)) == 2
assert len(f.traverse(f[35])) == 3
assert f[16] in f.get_inverse(f[15])
assert f[16].UnitComponent is not None
f.remove(f[15])
assert f[16].UnitComponent is None
prop = f.by_type("IfcPropertySingleValue")[0]
assert prop.NominalValue.wrappedValue in str(prop)

# An instance added to a new file yields the same string
# representation, except for any instance name identifiers.
f2 = ifcopenshell.file(schema=f.schema)
prop2 = f2.add(prop)
assert str(prop) == str(prop2).replace(str(prop2.id()), str(prop.id()))
assert prop2.id() == 1

# A recursively obtained python dictionary representation
# matches for copied instances as well
app = f.by_type("IfcApplication")[0]
assert f2.add(app).get_info(False, True) == app.get_info(False, True)
assert "Version" in dir(app)

# Enumeration of entity type names
g = ifcopenshell.file(schema=f.schema)
p = g.createIfcCartesianPoint((0.0, 0.0))
assert len(g.types()) == 1
g.remove(p)
assert len(g.types()) == 0

# Some operations on ifcopenshell.entity_instance
assert f[22].Id == ""
assert f[22].Addresses is None
assert f[23] in f[22].EngagedIn
f[22].Id = "123"
assert "123" in str(f[22])
f[22].MiddleNames = "John", "Matthew"
assert "('John','Matthew')" in str(f[22])
assert ("Id", "123") in list(f[22].get_info().items())

# Assignment of instances and implications on inverse attributes
assert f[288].ConnectedTo[0].RelatingElement == f[288]
num_connections_1 = len(f[340].ConnectedTo + f[340].ConnectedFrom)
f[288].ConnectedTo[0].RelatingElement = f[340]
num_connections_2 = len(f[340].ConnectedTo + f[340].ConnectedFrom)
assert num_connections_2 == num_connections_1 + 1
assert f[288].ConnectedTo == ()
rel = f.createIfcRelConnectsPathElements(RelatingElement=f[288])
assert f[288].ConnectedTo == (rel,)

# Some operations on ifcopenshell.guid
assert len(ifcopenshell.guid.compress(uuid.uuid1().hex)) == 22

# reopen, because we messed with the units
f = ifcopenshell.open("input/acad2010_walls.ifc")

# Test the BVH tree
tree_settings = ifcopenshell.geom.settings()
tree_settings.set(tree_settings.DISABLE_OPENING_SUBTRACTIONS, True)
t = ifcopenshell.geom.tree(f, tree_settings)
# This wall is connected to two other walls
assert len(t.select_box(f[48], extend=0.1)) == 3

# Test serialization
f.write("output.ifc")
with open("output.ifc") as txt:
    assert "123" in txt.read()
os.unlink("output.ifc")

# IfcConvert --name-template: a generic printf/find-style template to derive
# per-entity identifiers/names upon serialization (see issue #413).
import shutil
import subprocess

ifcconvert = shutil.which("IfcConvert")
if ifcconvert is None:
    print("[Notice] IfcConvert not found on PATH, skipping --name-template tests")
else:
    fixture = "files/name_template_fixture.ifc"
    out_obj = "name_template_fixture.obj"

    def convert(*extra_args):
        if os.path.exists(out_obj):
            os.unlink(out_obj)
        subprocess.check_call([ifcconvert, fixture, out_obj, *extra_args])
        with open(out_obj) as f:
            return f.read()

    # %N (Name), %G (GlobalId), %T (entity class), %t (Tag)
    contents = convert("--name-template", "%T-%N (%G) tag=%t")
    assert "g IfcWall-Test Wall (27uW0y7Gr72R8yo2C4vBlV) tag=TAG-001" in contents

    # %g: the uncompressed/decoded UUID form of the GlobalId, distinct from %G
    contents = convert("--name-template", "%g")
    assert "g 87e2003c-1d0d-4709-b23c-c82304e4bbdf" in contents

    # %i: the numeric STEP instance id of the IfcWall instance (#40 in the fixture)
    contents = convert("--name-template", "%i")
    assert "g 40" in contents

    # literal %% is preserved as a single percent sign
    contents = convert("--name-template", "100%%")
    assert "g 100%" in contents

    # an unrecognized placeholder is emitted verbatim rather than silently dropped
    contents = convert("--name-template", "%Z-%N")
    assert "g %Z-Test Wall" in contents

    # --name-template takes priority over the older --use-element-guids flag
    contents = convert("--name-template", "%N", "--use-element-guids")
    assert "g Test Wall" in contents

    # the older flags keep working unchanged when --name-template isn't used
    contents = convert("--use-element-guids")
    assert "g 27uW0y7Gr72R8yo2C4vBlV" in contents

    os.unlink(out_obj)
    mtl = "name_template_fixture.mtl"
    if os.path.exists(mtl):
        os.unlink(mtl)
