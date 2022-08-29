Usage
=====

Example commands
----------------

For the most basic usage, specify an input and output file. The file extension
you provide for the output file determines what format the IFC is converted to.

::

    $ IfcConvert /path/to/input.ifc /path/to/output.obj

.. tip::

    On Windows, you can drag and drop a ``.ifc`` file on the ``IfcConvert.exe``
    file to automatically convert it to an ``.obj`` file.

For any conversion, it is recommended to use multiple cores to speed up
processing:

::

    # Change "7" to the number of CPU cores you have then plus one.
    $ IfcConvert -j 7 /path/to/input.ifc /path/to/output.dae

By default, units are converted to meters. If you want to retain the original units:

::

    $ IfcConvert --convert-back-units /path/to/input.ifc /path/to/output.stp

If your IFC uses large map coordinates and your desired format cannot handle it:

::

    $ IfcConvert --center-model /path/to/input.ifc /path/to/output.glb
    # Alternatively:
    $ IfcConvert --center-model-geometry /path/to/input.ifc /path/to/output.glb
    # Or you can specify a manual offset in X;Y;Z format
    $ IfcConvert --model-offset "10000;10000;0" /path/to/input.ifc /path/to/output.glb

IfcConvert can also be used to generate SVG floorplans:

::

    $ IfcConvert /path/to/input.ifc -yv /path/to/output.svg \
        -j 7 --exclude entities IfcOpeningElement IfcSpace

CLI Manual
----------

::

    $ IfcConvert -h

    IfcOpenShell IfcConvert v0.7.0-dc67287d (OCC 7.5.3)
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
      .ifc   IFC-SPF        Industry Foundation Classes

    If no output filename given, <input>.obj will be used as the output file.


    Command line options:
      -h [ --help ]                         display usage information
      --version                             display version information
      -v [ --verbose ]                      more verbose log messages. Use twice 
                                            (-vv) for debugging level.
      -d [ --debug ]                        write boolean operands to file in 
                                            current directory for debugging 
                                            purposes
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
      -j [ --threads ] arg (=1)             Number of parallel processing threads 
                                            for geometry interpretation.
      --plan                                Specifies whether to include curves in 
                                            the output result. Typically these are 
                                            representations of type Plan or Axis. 
                                            Excluded by default.
      --model                               Specifies whether to include surfaces 
                                            and solids in the output result. 
                                            Typically these are representations of 
                                            type Body or Facetation. Included by 
                                            default.
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
      --convert-back-units                  Specifies whether to convert back 
                                            geometrical output back to the unit of 
                                            measure in which it is defined in the 
                                            IFC file. Default is to use meters.
      --orient-shells                       Specifies whether to orient the faces 
                                            of IfcConnectedFaceSets. This is a 
                                            potentially time consuming operation, 
                                            but guarantees a consistent orientation
                                            of surface normals, even if the faces 
                                            are not properly oriented in the IFC 
                                            file.
      --center-model                        Centers the elements by applying the 
                                            center point of all placements as an 
                                            offset.Can take several minutes on 
                                            large models.
      --center-model-geometry               Centers the elements by applying the 
                                            center point of all mesh vertices as an
                                            offset.
      --model-offset arg                    Applies an arbitrary offset of form 
                                            'x;y;z' to all placements.
      --model-rotation arg                  Applies an arbitrary quaternion 
                                            rotation of form 'x;y;z;w' to all 
                                            placements.
      --disable-opening-subtractions        Specifies whether to disable the 
                                            boolean subtraction of 
                                            IfcOpeningElement Representations from 
                                            their RelatingElements.
      --disable-boolean-results             Specifies whether to disable the 
                                            boolean operation within 
                                            representations such as clippings by 
                                            means of IfcBooleanResult and subtypes
      --no-2d-boolean                       Do not attempt to process boolean 
                                            subtractions in 2D.
      --enable-layerset-slicing             Specifies whether to enable the slicing
                                            of products according to their 
                                            associated IfcMaterialLayerSet.
      --layerset-first                      Assigns the first layer material of the
                                            layerset to the complete product.
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
      --no-normals                          Disables computation of normals. Saves 
                                            time and file size and is useful in 
                                            instances where you're going to 
                                            recompute normals for the exported 
                                            model in other modelling application in
                                            any case.
      --deflection-tolerance arg (=0.001)   Sets the deflection tolerance of the 
                                            mesher, 1e-3 by default if not 
                                            specified.
      --force-space-transparency arg        Overrides transparency of spaces in 
                                            geometry output.
      --angular-tolerance arg (=0.5)        Sets the angular tolerance of the 
                                            mesher in radians 0.5 by default if not
                                            specified.
      --generate-uvs                        Generates UVs (texture coordinates) by 
                                            using simple box projection. Requires 
                                            normals. Not guaranteed to work 
                                            properly if used with --weld-vertices.
      --default-material-file arg           Specifies a material file that 
                                            describes the material object types 
                                            will haveif an object does not have any
                                            specified material in the IFC file.
      --validate                            Checks whether geometrical output 
                                            conforms to the included explicit 
                                            quantities.
      --no-wire-intersection-check          Skip wire intersection check.
      --no-wire-intersection-tolerance      Set wire intersection tolerance to 0.
      --strict-tolerance                    Use exact tolerance from model. Default
                                            is a 10 times increase for more 
                                            permissive edge curves and fewer 
                                            artifacts after boolean operations at 
                                            the expense of geometric detail due to 
                                            vertex collapsing and wire intersection
                                            fuzziness.

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
      --use-element-names                   Use entity instance IfcRoot.Name 
                                            instead of unique IDs for naming 
                                            elements upon serialization. Applicable
                                            for OBJ, DAE, and SVG output.
      --use-element-guids                   Use entity instance IfcRoot.GlobalId 
                                            instead of unique IDs for naming 
                                            elements upon serialization. Applicable
                                            for OBJ, DAE, and SVG output.
      --use-element-numeric-ids             Use the numeric step identifier (entity
                                            instance name) for naming elements upon
                                            serialization. Applicable for OBJ, DAE,
                                            and SVG output.
      --use-material-names                  Use material names instead of unique 
                                            IDs for naming materials upon 
                                            serialization. Applicable for OBJ and 
                                            DAE output.
      --use-element-types                   Use element types instead of unique IDs
                                            for naming elements upon serialization.
                                            Applicable for DAE output.
      --use-element-hierarchy               Order the elements using their 
                                            IfcBuildingStorey parent. Applicable 
                                            for DAE output.
      --site-local-placement                Place elements locally in the IfcSite 
                                            coordinate system, instead of placing 
                                            them in the IFC global coords. 
                                            Applicable for OBJ and DAE output.
      --y-up                                Change the 'up' axis to positive Y, 
                                            default is Z UP, Applicable for OBJ 
                                            output.
      --building-local-placement            Similar to --site-local-placement, but 
                                            placing elements in locally in the 
                                            parent IfcBuilding coord system
      --precision arg (=15)                 Sets the precision to be used to format
                                            floating-point values, 15 by default. 
                                            Use a negative value to use the 
                                            system's default precision (should be 6
                                            typically). Applicable for OBJ and DAE 
                                            output. For DAE output, value >= 15 
                                            means that up to 16 decimals are used, 
                                            and any other value means that 6 or 7 
                                            decimals are used.
      --print-space-names                   Prints IfcSpace LongName and Name in 
                                            the geometry output. Applicable for SVG
                                            output
      --print-space-areas                   Prints calculated IfcSpace areas in 
                                            square meters. Applicable for SVG 
                                            output
      --space-name-transform arg            Additional transform to the space 
                                            labels in SVG
      --edge-arrows                         Adds arrow heads to edge segments to 
                                            signify edge direction

