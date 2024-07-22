git clone https://github.com/IfcOpenShell/IfcOpenShell.git
cd IfcOpenShell

# path to BlenderBIM addon
# default path on Mac: "/Users/$USER/Library/Application Support/Blender/X.X/scripts/addons/blenderbim"
# default path on Linux: "$HOME/.config/blender/X.X/"
BLENDER_ADDON_PATH="/path/to/blender/X.XX/scripts/addons/blenderbim"

# Remove the Blender add-on Python code
rm -r $BLENDER_ADDON_PATH/core/
rm -r $BLENDER_ADDON_PATH/tool/
rm -r $BLENDER_ADDON_PATH/bim/

# Replace them with links to the Git repository
ln -s $PWD/src/blenderbim/blenderbim/core $BLENDER_ADDON_PATH/core
ln -s $PWD/src/blenderbim/blenderbim/tool $BLENDER_ADDON_PATH/tool
ln -s $PWD/src/blenderbim/blenderbim/bim $BLENDER_ADDON_PATH/bim

# Copy over compiled IfcOpenShell files
cp $BLENDER_ADDON_PATH/libs/site/packages/ifcopenshell/*_wrapper* $PWD/src/ifcopenshell-python/ifcopenshell/

# Remove the IfcOpenShell dependency
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifcopenshell

# Replace them with links to the Git repository
ln -s $PWD/src/ifcopenshell-python/ifcopenshell $BLENDER_ADDON_PATH/libs/site/packages/ifcopenshell

# Remove and link other IfcOpenShell utilities
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifccsv.py
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifcdiff.py
rm -r $BLENDER_ADDON_PATH/libs/site/packages/bsdd.py
rm -r $BLENDER_ADDON_PATH/libs/site/packages/bcf
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifc4d
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifc5d
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifccityjson
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifcclash
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifcpatch
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifctester
rm -r $BLENDER_ADDON_PATH/libs/site/packages/ifcfm
rm -r $BLENDER_ADDON_PATH/libs/Desktop

ln -s $PWD/src/ifccsv/ifccsv.py $BLENDER_ADDON_PATH/libs/site/packages/ifccsv.py
ln -s $PWD/src/ifcdiff/ifcdiff.py $BLENDER_ADDON_PATH/libs/site/packages/ifcdiff.py
ln -s $PWD/src/bsdd/bsdd.py $BLENDER_ADDON_PATH/libs/site/packages/bsdd.py
ln -s $PWD/src/bcf/src/bcf $BLENDER_ADDON_PATH/libs/site/packages/bcf
ln -s $PWD/src/ifc4d/ifc4d $BLENDER_ADDON_PATH/libs/site/packages/ifc4d
ln -s $PWD/src/ifc5d/ifc5d $BLENDER_ADDON_PATH/libs/site/packages/ifc5d
ln -s $PWD/src/ifccityjson/ifccityjson $BLENDER_ADDON_PATH/libs/site/packages/ifccityjson
ln -s $PWD/src/ifcclash/ifcclash $BLENDER_ADDON_PATH/libs/site/packages/ifcclash
ln -s $PWD/src/ifcpatch/ifcpatch $BLENDER_ADDON_PATH/libs/site/packages/ifcpatch
ln -s $PWD/src/ifctester/ifctester $BLENDER_ADDON_PATH/libs/site/packages/ifctester
ln -s $PWD/src/ifcfm/ifcfm $BLENDER_ADDON_PATH/libs/site/packages/ifcfm
ln -s $PWD/src/blenderbim/blenderbim/libs/desktop $BLENDER_ADDON_PATH/libs/Desktop

# Manually download some third party dependencies
cd $BLENDER_ADDON_PATH/bim/data/gantt
wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js
wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css
cd $BLENDER_ADDON_PATH/bim/schema
wget https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl
