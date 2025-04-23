Usage
=====

Example commands
----------------

For the most basic usage, specify an input and output file. The file extension
you provide for the output file determines what format the IFC is converted to.

.. code-block:: bash

    IfcConvert /path/to/input.ifc /path/to/output.obj

.. tip::

    On Windows, you can drag and drop a ``.ifc`` file on the ``IfcConvert.exe``
    file to automatically convert it to an ``.obj`` file.

For any conversion, it is recommended to use multiple cores to speed up
processing:

.. code-block:: bash

    # Change "7" to the number of CPU cores you have then plus one.
    IfcConvert -j 7 /path/to/input.ifc /path/to/output.dae

By default, units are converted to meters. If you want to retain the original units:

.. code-block:: bash

    IfcConvert --convert-back-units /path/to/input.ifc /path/to/output.stp

If your IFC uses large map coordinates and your desired format cannot handle it:

.. code-block:: bash

    IfcConvert --center-model /path/to/input.ifc /path/to/output.glb
    # Alternatively:
    IfcConvert --center-model-geometry /path/to/input.ifc /path/to/output.glb
    # Or you can specify a manual offset in X;Y;Z format
    IfcConvert --model-offset "10000;10000;0" /path/to/input.ifc /path/to/output.glb

IfcConvert can be used to convert only specific elements.

.. code-block:: bash

    # Convert only walls and slabs
    IfcConvert  --include entities IfcWall IfcSlab -v /path/to/input.ifc /path/to/output.glb
    # Convert only these two particular elements filtered by GlobalId
    IfcConvert  --include attribute GlobalId 1yETHMphv6LwABqR4Pbs5g attribute GlobalId 1yETHMphv6LwABqR0Pbs5g -v /path/to/input.ifc /path/to/output.glb
    # Convert all objects on level 1. Note how "+" is used.
    IfcConvert  --include+=attribute Name "Level 1" -v /path/to/input.ifc /path/to/output.glb

.. warning::

    The include (or exclude) arguments cannot be placed right before input file
    argument and only single of each argument supported for now.

IfcConvert can also be used to generate SVG floorplans:

.. code-block:: bash

    IfcConvert /path/to/input.ifc -yv /path/to/output.svg \
        -j 7 --exclude entities IfcOpeningElement IfcSpace

CLI Manual
----------

.. code-block:: console

    $ IfcConvert -h

    IfcOpenShell IfcConvert 0.8.1-c49ca69 (OCC 7.8.1)
    Usage: IfcConvert [options] <input.ifc> [<output>]

    Converts (the geometry in) an IFC file into one of the following formats:
      .obj   WaveFront OBJ  (a .mtl file is also created)
      .dae   Collada        Digital Assets Exchange
      .glb   glTF           Binary glTF v2.0
      .stp   STEP           Standard for the Exchange of Product Data
      .igs   IGES           Initial Graphics Exchange Specification
      .xml   XML            Property definitions and decomposition tree
      .svg   SVG            Scalable Vector Graphics (2D floor plan)
      .h5    HDF            Hierarchical Data Format storing positions, normals and indices
      .cityjson             City JSON format for geospatial data
      .ttl   TTL/WKT        RDF Turtle with Well-Known-Text geometry
      .ifc   IFC-SPF        Industry Foundation Classes

    If no output filename given, <input>.obj will be used as the output file.


    Command line options:
      -h [ --help ]                         display usage information
      --version                             display version information
      -v [ --verbose ]                      more verbose log messages. Use twice 
                                            (-vv) for debugging level.
      -q [ --quiet ]                        less status and progress output
      --cache                               cache geometry creation. Use 
                                            --cache-file to specify cache file 
                                            path.
      --stderr-progress                     output progress to stderr stream
      -y [ --yes ]                          answer 'yes' automatically to possible 
                                            confirmation queries (e.g. overwriting 
                                            an existing output file)
      --no-progress                         suppress possible progress bar type of 
                                            prints that use carriage return
      --log-format arg                      log format: plain or json
      --log-file arg                        redirect log output to file

    Geometry options:
      --kernel arg (=opencascade)           Geometry kernel to use (opencascade, 
                                            cgal, cgal-simple).
      -j [ --threads ] arg (=1)             Number of parallel processing threads 
                                            for geometry interpretation.
      --center-model                        Centers the elements by applying the 
                                            center point of all placements as an 
                                            offset.Can take several minutes on 
                                            large models.
      --center-model-geometry               Centers the elements by applying the 
                                            center point of all mesh vertices as an
                                            offset.
      --include arg                         Specifies that the instances that match
                                            a specific filtering criteria are to be
                                            included in the geometrical output:
                                            1) 'entities': the following list of 
                                            types should be included. SVG output 
                                            defaults to IfcSpace to be included. 
                                            The entity names are handled 
                                            case-insensitively.
                                            2) 'layers': the instances that are 
                                            assigned to presentation layers of 
                                            which names match the given values 
                                            should be included.
                                            3) 'attribute <AttributeName>': 
                                            products whose value for 
                                            <AttributeName> should be included
                                            . Currently supported arguments are 
                                            GlobalId, Name, Description, and Tag.
                                            
                                            The values for 'layers' and 'arg' are 
                                            handled case-sensitively (wildcards 
                                            supported).--include and --exclude 
                                            cannot be placed right before input 
                                            file argument and only single of each 
                                            argument supported for now. See also 
                                            --exclude.
      --include+ arg                        Same as --include but applies filtering
                                            also to the decomposition and/or 
                                            containment (IsDecomposedBy, 
                                            HasOpenings, FillsVoid, 
                                            ContainedInStructure) of the filtered 
                                            entity, e.g. --include+=arg Name "Level
                                            1" includes entity with name "Level 1" 
                                            and all of its children. See --include 
                                            for more information. 
      --exclude arg                         Specifies that the entities that match 
                                            a specific filtering criteria are to be
                                            excluded in the geometrical output.See 
                                            --include for syntax and more details. 
                                            The default value is 
                                            '--exclude=entities IfcOpeningElement 
                                            IfcSpace'.
      --exclude+ arg                        Same as --exclude but applies filtering
                                            also to the decomposition and/or 
                                            containment of the filtered entity. See
                                            --include+ for more details.
      --filter-file arg                     Specifies a filter file that describes 
                                            the used filtering criteria. Supported 
                                            formats are '--include=arg GlobalId 
                                            ...' and 'include arg GlobalId ...'. 
                                            Spaces and tabs can be used as 
                                            delimiters.Multiple filters of same 
                                            type with different values can be 
                                            inserted on their own lines. See 
                                            --include, --include+, --exclude, and 
                                            --exclude+ for more details.
      --default-material-file arg           Specifies a material file that 
                                            describes the material object types 
                                            will haveif an object does not have any
                                            specified material in the IFC file.
      --exterior-only [=arg(=minkowski-triangles)] (=none)
                                            Export only the exterior shell of the 
                                            building found by geometric analysis. 
                                            convex-decomposition, 
                                            minkowski-triangles or 
                                            halfspace-snapping
      --plan                                Specifies whether to include curves in 
                                            the output result. Typically these are 
                                            representations of type Plan or Axis. 
                                            Excluded by default.
      --model                               Specifies whether to include surfaces 
                                            and solids in the output result. 
                                            Typically these are representations of 
                                            type Body or Facetation. 
      --mesher-linear-deflection arg (= 0.001)
                                            Specifies the linear deflection of the 
                                            mesher. Controls the detail of curved 
                                            surfaces in triangulated output 
                                            formats.
      --mesher-angular-deflection arg (= 0.5)
                                            Sets the angular tolerance of the 
                                            mesher in radians 0.5 by default if not
                                            specified.
      --reorient-shells                     Specifies whether to orient the faces 
                                            of IfcConnectedFaceSets. This is a 
                                            potentially time consuming operation, 
                                            but guarantees a consistent orientation
                                            of surface normals, even if the faces 
                                            are not properly oriented in the IFC 
                                            file.
      --length-unit arg (= 1)
      --angle-unit arg (= 1)
      --precision arg (= 1e-05)
      --dimensionality arg (= 1)            Specifies whether to include curves 
                                            and/or surfaces and solids in the 
                                            output result. Defaults to only 
                                            surfaces and solids.
      --layerset-first                      Assigns the first layer material of the
                                            layerset to the complete product.
      --disable-boolean-result              Specifies whether to disable the 
                                            boolean operation within 
                                            representations such as clippings by 
                                            means of IfcBooleanResult and subtypes
      --no-wire-intersection-check          Skip wire intersection check.
      --no-wire-intersection-tolerance arg (= 0)
                                            Set wire intersection tolerance to 0.
      --precision-factor arg (= 1)          Option to increase linear tolerance for
                                            more permissive edge curves and fewer 
                                            artifacts after boolean operations at 
                                            the expense of geometric detail due to 
                                            vertex collapsing and wire intersection
                                            fuzziness.
      --debug                               write boolean operands to file in 
                                            current directory for debugging 
                                            purposes
      --boolean-attempt-2d                  Do not attempt to process boolean 
                                            subtractions in 2D.
      --surface-colour                      Prioritizes the surface color instead 
                                            of using diffuse.
      --weld-vertices                       Specifies whether vertices are welded, 
                                            meaning that the coordinates vector 
                                            will only contain unique xyz-triplets. 
                                            This results in a manifold mesh which 
                                            is useful for modelling applications, 
                                            but might result in unwanted shading 
                                            artefacts in rendering applications.
      --use-world-coords                    Specifies whether to apply the local 
                                            placements of building elements 
                                            directly to the coordinates of the 
                                            representation mesh rather than to 
                                            represent the local placement in the 
                                            4x3 matrix, which will in that case be 
                                            the identity matrix.
      --unify-shapes                        Unify adjacent co-planar and co-linear 
                                            subshapes (topological entities sharing
                                            the same geometric domain) before 
                                            triangulation or further processing
      --use-material-names                  Use material names instead of unique 
                                            IDs for naming materials upon 
                                            serialization. Applicable for OBJ and 
                                            DAE output.
      --convert-back-units                  Specifies whether to convert back 
                                            geometrical output back to the unit of 
                                            measure in which it is defined in the 
                                            IFC file. Default is to use meters.
      --context-ids arg
      --context-ids arg
      --context-ids arg
      --iterator-output arg (= 0)
      --disable-opening-subtractions        Specifies whether to disable the 
                                            boolean subtraction of 
                                            IfcOpeningElement Representations from 
                                            their RelatingElements.
      --apply-default-materials 
      --no-normals                          Disables computation of normals.Saves 
                                            time and file size and is useful in 
                                            instances where you're going to 
                                            recompute normals for the exported 
                                            model in other modelling application in
                                            any case.
      --generate-uvs                        Generates UVs (texture coordinates) by 
                                            using simple box projection. Requires 
                                            normals. Not guaranteed to work 
                                            properly if used with --weld-vertices.
      --enable-layerset-slicing             Specifies whether to enable the slicing
                                            of products according to their 
                                            associated IfcMaterialLayerSet.
      --element-hierarchy                   Assign the elements using their e.g 
                                            IfcBuildingStorey parent.Applicable to 
                                            DAE output.
      --validate                            Checks whether geometrical output 
                                            conforms to the included explicit 
                                            quantities.
      --edge-arrows                         Adds arrow heads to edge segments to 
                                            signify edge direction
      --building-local-placement            Similar to --site-local-placement, but 
                                            placing elements in locally in the 
                                            parent IfcBuilding coord system
      --site-local-placement                Place elements locally in the IfcSite 
                                            coordinate system, instead of placing 
                                            them in the IFC global coords. 
                                            Applicable for OBJ, DAE, and STP 
                                            output.
      --force-space-transparency arg        Overrides transparency of spaces in 
                                            geometry output.
      --circle-segments arg (= 16)          Number of segments to approximate full 
                                            circles in CGAL kernel.
      --keep-bounding-boxes                 Default is to removes IfcBoundingBox 
                                            from model prior to converting 
                                            geometry.Setting this option disables 
                                            that behaviour
      --function-step-type arg (= 0)        Indicates the method used for defining 
                                            step size when evaluating 
                                            function-based curves. Provides 
                                            interpretation of function-step-param
      --function-step-param arg (= 0.5)     Indicates the parameter value for 
                                            defining step size when evaluating 
                                            function-based curves.
      --no-parallel-mapping                 Perform mapping upfront 
                                            (single-threaded) as opposed to in 
                                            parallel. May decrease performance, but
                                            also decrease output size (in the 
                                            future)
      --model-offset arg                    Applies an arbitrary offset of form 
                                            'x,y,z' to all placements.
      --model-rotation arg                  Applies an arbitrary quaternion 
                                            rotation of form 'x,y,z,w' to all 
                                            placements.
      --triangulation-type arg (= 0)        Type of planar facet to be emitted

    Serialization options:
      --bounds arg                          Specifies the bounding rectangle, for 
                                            example 512x512, to which the output 
                                            will be scaled. Only used when 
                                            converting to SVG.
      --scale arg                           Interprets SVG bounds in mm, centers 
                                            layout and draw elements to scale. Only
                                            used when converting to SVG. Example 
                                            1:100.
      --center arg                          When using --scale, specifies the 
                                            location in the range [0 1]x[0 1] 
                                            around whichto center the drawings. 
                                            Example 0.5x0.5 (default).
      --section-ref arg                     Element at which cross sections should 
                                            be created
      --elevation-ref arg                   Element at which drawings should be 
                                            created
      --elevation-ref-guid arg              Element guids at which drawings should 
                                            be created
      --auto-section                        Creates SVG cross section drawings 
                                            automatically based on model extents
      --auto-elevation                      Creates SVG elevation drawings 
                                            automatically based on model extents
      --draw-storey-heights [=arg(=full)] (=none)
                                            Draws a horizontal line at the height 
                                            of building storeys in vertical 
                                            drawings
      --storey-height-line-length arg       Length of the line when 
                                            --draw-storey-heights=left
      --svg-xmlns                           Stores name and guid in a separate 
                                            namespace as opposed to data-name, 
                                            data-guid
      --svg-poly                            Uses the polygonal algorithm for hidden
                                            line rendering
      --svg-prefilter                       Prefilter faces and shapes before 
                                            feeding to HLR algorithm
      --svg-segment-projection              Segment result of projection wrt 
                                            original products
      --svg-write-poly                      Approximate every curve as polygonal in
                                            SVG output
      --svg-project                         Always enable hidden line rendering 
                                            instead of only on elevations
      --svg-without-storeys                 Don't emit drawings for building 
                                            storeys
      --svg-no-css                          Don't emit CSS style declarations
      --door-arcs                           Draw door openings arcs for IfcDoor 
                                            elements
      --section-height arg                  Specifies the cut section height for 
                                            SVG 2D geometry.
      --section-height-from-storeys         Derives section height from storey 
                                            elevation. Use --section-height to 
                                            override default offset of 1.2
      --print-space-names                   Prints IfcSpace LongName and Name in 
                                            the geometry output. Applicable for SVG
                                            output
      --print-space-areas                   Prints calculated IfcSpace areas in 
                                            square meters. Applicable for SVG 
                                            output
      --space-name-transform arg            Additional transform to the space 
                                            labels in SVG
      --use-element-names                   Use entity instance IfcRoot.Name 
                                            instead of unique IDs for naming 
                                            elements upon serialization. Applicable
                                            for OBJ, DAE, STP, and SVG output.
      --use-element-guids                   Use entity instance IfcRoot.GlobalId 
                                            instead of unique IDs for naming 
                                            elements upon serialization. Applicable
                                            for OBJ, DAE, STP, and SVG output.
      --use-element-step-ids                Use the numeric step identifier (entity
                                            instance name) for naming elements upon
                                            serialization. Applicable for OBJ, DAE,
                                            STP, and SVG output.
      --use-element-types                   Use element types instead of unique IDs
                                            for naming elements upon serialization.
                                            Applicable to DAE output.
      --y-up                                Change the 'up' axis to positive Y, 
                                            default is Z UP. Applicable to OBJ 
                                            output.
      --ecef                                Write glTF in Earth-Centered 
                                            Earth-Fixed coordinates. Requires PROJ.
      --digits arg (= 15)                   Sets the precision to be used to format
                                            floating-point values, 15 by default. 
                                            Use a negative value to use the 
                                            system's default precision (should be 6
                                            typically). Applicable for OBJ and DAE 
                                            output. For DAE output, value >= 15 
                                            means that up to 16 decimals are used, 
                                            and any other value means that 6 or 7 
                                            decimals are used.
      --base-uri arg                        Base URI for products to be used in 
                                            RDF-based serializations.
      --wkt-use-section                     Use a geometrical section rather than 
                                            full polyhedral output and footprint in
                                            TTL WKT
