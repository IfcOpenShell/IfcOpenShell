APPLY_DEFAULT_MATERIALS
-----------------------

Given the command invocation:

    Duplex_A_20110907_optimized.ifc d.dae -yv --include attribute GlobalId 3bXiCStxP6Fgxdej$yc50U

You will find log messages along the lines of

    [Warning] {3bXiCStxP6Fgxdej$yc50U} No material and surface styles for:
    #333=IfcCovering('3bXiCStxP6Fgxdej$yc50U',#1,'Compound Ceiling:Gypsum Board:187483',$,'Compound Ceiling:Gypsum Board',#17840,#17052,'187483',.CEILING.)

This means that there is no IfcStyledItem associated to the representation items and that the element does not have an IfcMaterial association with IfcMaterialRepresentation from which we can derive a style (colour) for the element.

The interactive session below shows how with this setting enabled you will get a default generated material from the IFC element entity type and material indices of 0 pointing to that. With this setting disabled the material index would be -1 to indicate a missing style. Note that there is one material index for every triangle in the list of `shp.geometry.faces`.

    >>> import ifcopenshell, ifcopenshell.geom
    >>> f = ifcopenshell.open("Duplex_A_20110907_optimized.ifc")
    >>> s = ifcopenshell.geom.settings()
    >>> c = f["3bXiCStxP6Fgxdej$yc50U"]
    >>>
    >>> shp = ifcopenshell.geom.create_shape(s, c)
    >>> shp.geometry.material_ids
    (-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1)
    >>> [(m.name, m.diffuse) for m in shp.geometry.materials]
    []
    >>>
    >>> s.set(s.APPLY_DEFAULT_MATERIALS, True)
    >>> shp = ifcopenshell.geom.create_shape(s, c)
    >>> shp.geometry.material_ids
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    >>> [(m.name, m.diffuse) for m in shp.geometry.materials]
    [('IfcCovering', (0.7, 0.7, 0.7))]

This is enabled by default for the IfcConvert serializers as they will not gracefully handle -1 material indices and allows users to quickly assign colours based on entity types in their modelling applications.

APPLY_LAYERSETS
---------------

This setting is available in IfcConvert as `--enable-layerset-slicing`.

For IfcWall and IfcSlab elements, takes the associated IfcMaterialLayerSet and builds a set of surfaces to segment the building element geometry.

Note that enabling this settings is computationally intensive as it involves 3D Boolean operations.

    Duplex_A_20110907_optimized.ifc d1.dae -yv --include attribute GlobalId 2O2Fr$t4X7Zf8NOew3FNr2
    
![Image of d1.dae](settings-1.png)
    
    Duplex_A_20110907_optimized.ifc d2.dae --enable-layerset-slicing -yv --include attribute GlobalId 2O2Fr$t4X7Zf8NOew3FNr2
    
![Image of d2.dae](settings-2.png)

BUILDING_LOCAL_PLACEMENT
------------------------

This setting is available in IfcConvert using `--building-local-placement`.

In the typical IfcSite > IfcBuilding > IfcBuildingStorey > ... hierarchy of elements, don't incorporate the ObjectPlacement of the IfcBuilding and above in the placement of elements in the output. This is useful when there is a large offset in this placement that reduces precision in further processing.

CONVERT_BACK_UNITS
------------------

This setting is available in IfcConvert using `--convert-back-units`.

Internally IfcOpenShell uses meters as the global length unit to do calculations. This setting restores the coordinate positions after conversion by multiplying the factor of the IfcUnit with UnitType=LENGTHUNIT into the output geometry coordinate values.

DISABLE_OPENING_SUBTRACTIONS
----------------------------

This setting is available in IfcConvert using `--disable-opening-subtraction`.

As in most viewer applications, IfcOpeningElement geometry is subtracted from their host elements. This setting disables this behavior.

    Duplex_A_20110907_optimized.ifc d1.dae -yv --include attribute GlobalId 2O2Fr$t4X7Zf8NOew3FNr2
    
![Image of d1.dae](settings-1.png)
    
    Duplex_A_20110907_optimized.ifc d3.dae --disable-opening-subtraction -yv --include attribute GlobalId 2O2Fr$t4X7Zf8NOew3FNr2
    
![Image of d3.dae](settings-3.png)

Note that disabling this settings will reduce processing time and improve robustness as it involves 3D Boolean operations.

DISABLE_TRIANGULATION
---------------------

To be used in conjunction with `USE_BREP_DATA`. Do not apply the triangulation and - when `USE_BREP_DATA` is set - return a OpenCASCADE serialized TopoDS_Shape from `create_shape()` and `iterator`.

    >>> import ifcopenshell, ifcopenshell.geom
    >>> s = ifcopenshell.geom.settings()
    >>> s.set(s.DISABLE_TRIANGULATION, True)
    >>> s.set(s.USE_BREP_DATA, True)
    >>> f = ifcopenshell.open("Duplex_A_20110907_optimized.ifc")
    >>> c = f["3bXiCStxP6Fgxdej$yc50U"]
    >>> shp = ifcopenshell.geom.create_shape(s, c)
    >>> print(shp.geometry.brep_data)

    CASCADE Topology V1, (c) Matra-Datavision
    Locations 0
    Curve2ds 0
    Curves 12
    1 4.6750000000000034 -8.0749999999999904 2.657 -2.0455514041918775e-15 -1 0
    1 4.6750000000000034 -8.0749999999999904 2.657 1 -3.435893306383461e-15 0
    1 6.2260000000000044 -8.0749999999999957 2.657 -2.0455514041918724e-15 -1 0
    1 6.226 -10.246000000000031 2.657 -1 6.8717866127669219e-15 0
    ...

EDGE_ARROWS
-----------

When `INCLUDE_CURVES` is true and geometric elements include curves (such as the wall axis), add arrow heads to the edges to indicate direction of the curve.

    Duplex_A_20110907_optimized.ifc d4.dae --model --plan --edge-arrows -yv --include attribute GlobalId 2O2Fr$t4X7Zf8NOew3FNr2
    
![Image of d4.dae](settings-4.png)

EXCLUDE_SOLIDS_AND_SURFACES
---------------------------

Exclude faces, shells and solids from geometrical output. Implied when using `--plan` without `--model` in IfcConvert.

FASTER_BOOLEANS
---------------

NOTE: Only applicable when using OCCT 6.9 and earlier.

This setting is available in IfcConvert using `--merge-boolean-operands`.

Fuse the collection of all boolean operands into a single union before applying the boolean subtraction, as opposed to doing individual subtractions. This likely improves performance. From OCCT 7.0 onwards the boolean operations with multiple arguments is used.

GENERATE_UVS
------------

This setting is available in IfcConvert using `--generate-uvs`.

Applies a box projection on the generated geometry for the element to obtain UV coordinates. This is purely generated, it does not involve texture coordinates stored in the IFC model.

    Duplex_A_20110907_optimized.ifc d5.dae --generate-uvs -yv --include attribute GlobalId 2O2Fr$t4X7Zf8NOew3FNr2

![Image of d5.dae with a UV grid applied in Blender](settings-5.png)

INCLUDE_CURVES
--------------

This setting is available in IfcConvert using `--plan`.

Include edge and wire geometries in the geometric output.

LAYERSET_FIRST
--------------

This setting is available in IfcConvert using `--layerset-first`.

When not using APPLY_LAYERSETS, take the first material layer from the set to use as the material for the overall element.

NO_NORMALS
----------

This setting is available in IfcConvert using `--no-normals`.

Do not emit normals on geometric output

SEARCH_FLOOR
------------

Note: Only applicable to Collada .DAE output when used from IfcConvert.

This setting is available in IfcConvert using `--use-element-hierarchy`.

Include the spatial hierarchy in the elements.

SEW_SHELLS
----------

This setting is available in IfcConvert using `--orient-shells`.

Re-orient or sew connected face sets to have a consistent outwards orientation.

SITE_LOCAL_PLACEMENT
--------------------

This setting is available in IfcConvert using `--site-local-placement`.

See `BUILDING_LOCAL_PLACEMENT`, but exclude also the ObjectPlacement of the IfcSite.

USE_BREP_DATA
-------------

See `DISABLE_TRIANGULATION`.

USE_PYTHON_OPENCASCADE
----------------------

Note: Only available when an import of `OCC.Core.BRepTools` or `OCC.BRepTools` succeeds.

This implies `USE_WORLD_COORDS` `USE_BREP_DATA` and `DISABLE_TRIANGULATION`. The serialized TopoDS_Shape of `USE_BREP_DATA` is deserialized by Python OpenCASCADE.

USE_WORLD_COORDS
----------------

Apply the ObjectPlacement of the building elements to the geometric output. This is implied when using the Wavefront .OBJ output in IfcConvert. Note that this also eliminates the possibility for geometric elements to point to the same interpreted geometry result.

VALIDATE_QUANTITIES
-------------------

This setting is available in IfcConvert using `--validate`.

Running IfcConvert with `--validate` will set a non-zero exit code when ever a log message with severity equal or greater than ERROR has been emitted.

Currently for internal use only. For every building element geometry converted, looks for an associated quantity set where the OwnerHistory's organization name is IfcOpenShell. And looks for the quantities "Total Surface Area", "Volume", "Shape Validation Properties.Surface Genus" and validates these according to the interpreted geometry definition. Emit Logger::Error when calculated values are outside of the tolerance range for the value stored in the model.

WELD_VERTICES
-------------

Note: In Python, this setting is *on* by default.

Note: This setting only affects triangulated output.

This setting is available in IfcConvert using `--weld-vertices`.

Discards normals and joins vertices solely based on position. This is useful when output is to be modified in a modeling application.

    >>> import ifcopenshell, ifcopenshell.geom
    >>> s = ifcopenshell.geom.settings()
    >>> s.set(s.WELD_VERTICES, False)
    >>> f = ifcopenshell.open("Duplex_A_20110907_optimized.ifc")
    >>> c = f["3bXiCStxP6Fgxdej$yc50U"]
    >>> shp = ifcopenshell.geom.create_shape(s, c)
    >>> shp.geometry.verts
    (4.675000000000003, -8.07499999999999, 2.657, 4.674999999999999, -10.24600000000002, 2.657, 6.226000000000004, -8.074999999999996, 2.657, 6.226, -10.24600000000003, 2.657, 4.675000000000003, -8.07499999999999, 2.6, 4.674999999999999, -10.24600000000002, 2.6, 6.226000000000004, -8.074999999999996, 2.6, 6.226, -10.24600000000003, 2.6, 4.674999999999999, -10.24600000000002, 2.657, 4.674999999999999, -10.24600000000002, 2.6, 4.675000000000003, -8.07499999999999, 2.657, 4.675000000000003, -8.07499999999999, 2.6, 6.226, -10.24600000000003, 2.657, 4.674999999999999, -10.24600000000002, 2.657, 6.226, -10.24600000000003, 2.6, 4.674999999999999, -10.24600000000002, 2.6, 6.226000000000004, -8.074999999999996, 2.657, 6.226, -10.24600000000003, 2.657, 6.226000000000004, -8.074999999999996, 2.6, 6.226, -10.24600000000003, 2.6, 4.675000000000003, -8.07499999999999, 2.657, 4.675000000000003, -8.07499999999999, 2.6, 6.226000000000004, -8.074999999999996, 2.657, 6.226000000000004, -8.074999999999996, 2.6)
    >>> shp.geometry.normals
    (3.059754518198021e-17, 0.0, -1.0, 3.059754518198021e-17, 0.0, -1.0, 3.059754518198021e-17, 0.0, -1.0, 3.059754518198021e-17, 0.0, -1.0, 2.110175529791737e-16, 0.0, -1.0, 2.110175529791737e-16, 0.0, -1.0, 2.110175529791737e-16, 0.0, -1.0, 2.110175529791737e-16, 0.0, -1.0, -1.0, 1.79434333701042e-15, 0.0, -1.0, 1.79434333701042e-15, 0.0, -1.0, 1.79434333701042e-15, 0.0, -1.0, 1.79434333701042e-15, 0.0, 6.8717866127669046e-15, 1.0, 0.0, 6.8717866127669046e-15, 1.0, 0.0, 6.8717866127669046e-15, 1.0, 0.0, 6.8717866127669046e-15, 1.0, 0.0, -1.0, 1.79434333701042e-15, 0.0, -1.0, 1.79434333701042e-15, 0.0, -1.0, 1.79434333701042e-15, 0.0, -1.0, 1.79434333701042e-15, 0.0, 3.4358933063834523e-15, 1.0, 0.0, 3.4358933063834523e-15, 1.0, 0.0, 3.4358933063834523e-15, 1.0, 0.0, 3.4358933063834523e-15, 1.0, 0.0)
    >>>
    >>> s.set(s.WELD_VERTICES, True)
    >>> shp = ifcopenshell.geom.create_shape(s, c)
    >>> shp.geometry.verts
    (4.675000000000003, -8.07499999999999, 2.657, 4.674999999999999, -10.24600000000002, 2.657, 6.226000000000004, -8.074999999999996, 2.657, 6.226, -10.24600000000003, 2.657, 4.675000000000003, -8.07499999999999, 2.6, 4.674999999999999, -10.24600000000002, 2.6, 6.226000000000004, -8.074999999999996, 2.6, 6.226, -10.24600000000003, 2.6)
    >>> shp.geometry.normals
    ()
