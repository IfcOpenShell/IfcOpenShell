# Please update REPO_PATH, BLENDER_PATH, PACKAGE_PATH, BONSAI_PATH in the script below.
# Default BLENDER_PATH on Mac: "/Users/$USER/Library/Application Support/Blender/4.2/"
# Default BLENDER_PATH on Linux: "$HOME/.config/blender/4.2/"
# REPO_PATH="/path/to/where/your/git/repository/is/cloned/IfcOpenShell"
REPO_PATH="/home/dion/Projects/ifcopenshell/"
BLENDER_PATH="${HOME}/.config/blender/4.2"
PACKAGE_PATH="${BLENDER_PATH}/extensions/.local/lib/python3.11/site-packages"
BONSAI_PATH="${BLENDER_PATH}/extensions/user_default/bonsai"

# Changing to the Git repository directory
cd $REPO_PATH

# Copy over compiled IfcOpenShell files
cp $PACKAGE_PATH/ifcopenshell/*_wrapper* $PWD/src/ifcopenshell-python/ifcopenshell/

# Remove extension and link to Git
rm $BONSAI_PATH/__init__.py
rm -r $PACKAGE_PATH/bonsai
rm -r $PACKAGE_PATH/ifcopenshell
rm -r $PACKAGE_PATH/ifccsv.py
rm -r $PACKAGE_PATH/ifcdiff.py
rm -r $PACKAGE_PATH/bsdd.py
rm -r $PACKAGE_PATH/bcf
rm -r $PACKAGE_PATH/ifc4d
rm -r $PACKAGE_PATH/ifc5d
rm -r $PACKAGE_PATH/ifccityjson
rm -r $PACKAGE_PATH/ifcclash
rm -r $PACKAGE_PATH/ifcpatch
rm -r $PACKAGE_PATH/ifctester
rm -r $PACKAGE_PATH/ifcfm

ln -s $PWD/src/bonsai/bonsai/__init__.py $BONSAI_PATH/__init__.py
ln -s $PWD/src/bonsai/bonsai $PACKAGE_PATH/bonsai
ln -s $PWD/src/ifcopenshell-python/ifcopenshell $PACKAGE_PATH/ifcopenshell
ln -s $PWD/src/ifccsv/ifccsv.py $PACKAGE_PATH/ifccsv.py
ln -s $PWD/src/ifcdiff/ifcdiff.py $PACKAGE_PATH/ifcdiff.py
ln -s $PWD/src/bsdd/bsdd.py $PACKAGE_PATH/bsdd.py
ln -s $PWD/src/bcf/bcf $PACKAGE_PATH/bcf
ln -s $PWD/src/ifc4d/ifc4d $PACKAGE_PATH/ifc4d
ln -s $PWD/src/ifc5d/ifc5d $PACKAGE_PATH/ifc5d
ln -s $PWD/src/ifccityjson/ifccityjson $PACKAGE_PATH/ifccityjson
ln -s $PWD/src/ifcclash/ifcclash $PACKAGE_PATH/ifcclash
ln -s $PWD/src/ifcpatch/ifcpatch $PACKAGE_PATH/ifcpatch
ln -s $PWD/src/ifctester/ifctester $PACKAGE_PATH/ifctester
ln -s $PWD/src/ifcfm/ifcfm $PACKAGE_PATH/ifcfm

# Manually download some third party dependencies
cd $PACKAGE_PATH/bonsai/bim/data/gantt
wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js
wget https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css
cd $PACKAGE_PATH/bonsai/bim/schema
wget https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl
