# This can be run using `blender -b -P headless_import.py`

import bpy
from bonsai.bim.ifc import IfcStore

# When federating, you may wish to manually specify the origin to ensure models
# with different or arbitrary origin conventions will turn up in the right spot.

props = bpy.context.scene.BIMGeoreferenceProperties

# A good idea it to test import a portion of the model (or grids only) and check
# georeferencing coordinates in the IFC Georeferencing panel before filling out
# these details.

# props.blender_eastings = '334134181.0'
# props.blender_northings = '6254570511.0'
# props.blender_orthogonal_height = '0.0'
# props.blender_x_axis_abscissa = '0.147487884244522'
# props.blender_x_axis_ordinate = '0.989063862448262'
# props.has_blender_offset = True

props = bpy.context.scene.BIMProjectProperties

# Generally recommended to disable caching for stability right now
props.should_cache = False

# If you are not authoring, it is recommended to enable this.
# When enabled, types, openings, and non geometric elements are not loaded.
props.is_coordinating = True

# Merging is a good strategy to keep object counts low in huge models.

# Leave it to none if you do not have a huge model.
props.merge_mode = "NONE"

# A good merge strategy when the type is significant
props.merge_mode = "IFC_TYPE"

# A good merge strategy to really get object counts low where types don't matter, like for structural models
props.merge_mode = "IFC_CLASS"

# If you want to import a range of elements, say the first 30k elements, set the
# offset and limit here. 30k is generally useful as a guideline to keep models
# responsive (though my computer can handle 80k).
props.element_offset = 0
props.element_limit = 30000

bpy.ops.bim.load_project(filepath="/path/to/your/model/input.ifc")

# In coordination mode, it is unnecessary to maintain a link to the IFC
bpy.ops.bim.unload_project()

# Save the processed file here
bpy.ops.wm.save_mainfile(filepath="/path/to/your/model/output.blend")
