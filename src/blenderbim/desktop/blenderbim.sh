#!/bin/bash

# Wrapper script to launch BlenderBIM.

# If the `blender` executable can't be found in your PATH environment, set
# BLENDER_EXE to the location of your preferred `blender` executable.

#BLENDER_EXE=/opt/blender-3.3/blender

: ${BLENDER_EXE:=blender}

if [[ $# -eq 1 && -f "$@" ]]; then
    "${BLENDER_EXE}" --python-expr 'import bpy; bpy.data.collections.remove(bpy.data.collections[0]); bpy.ops.bim.load_project(filepath="'"$@"'")'
else
    "${BLENDER_EXE}" --python-expr 'import bpy; bpy.data.collections.remove(bpy.data.collections[0]); bpy.ops.bim.create_project()'
fi;
