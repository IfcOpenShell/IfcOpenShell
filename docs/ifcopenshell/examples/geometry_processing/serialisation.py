# This file was generated with the assistance of an AI coding tool.
#
# Geometry processing (Python): serialising geometry to glTF.
#
# Requires IfcOpenShell 0.9, where the serialiser settings are part of the
# geometry settings.

import os
import sys

ifc_path = sys.argv[1]

# tag::example
import multiprocessing

import ifcopenshell
import ifcopenshell.geom

ifc_file = ifcopenshell.open(ifc_path)

settings = ifcopenshell.geom.settings()

# Settings for glTF / glb. Applying default materials is required in glTF.
settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
settings.set("apply-default-materials", True)

# Settings for obj
# settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
# settings.set("apply-default-materials", True)
# settings.set("use-world-coords", True)

# Setting element GUIDs is optional, but useful to uniquely identify objects in
# non-semantic formats.
settings.set("use-element-guids", True)

# Serialise to glTF / glb
serialiser = ifcopenshell.geom.serializers.gltf("output.glb", settings)

# Serialise to obj
# serialiser = ifcopenshell.geom.serializers.obj("output.obj", "output.mtl", settings)

serialiser.setFile(ifc_file)
serialiser.setUnitNameAndMagnitude("METER", 1.0)
serialiser.writeHeader()

iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
if iterator.initialize():
    while True:
        serialiser.write(iterator.get())
        if not iterator.next():
            break
serialiser.finalize()
# end::example

assert os.path.getsize("output.glb") > 0
