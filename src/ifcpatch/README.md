# IfcPatch

Utility for applying modification recipes to IFC files. IfcPatch enables programmatic editing and correction of IFC models through a collection of patches that can fix common issues, migrate data, or transform models.

## Available Recipes

### Alignment and Linear Placement
- **AddGeometricRepresentationToAlignment** - Add geometric representations to alignment elements
- **AddLinearPlacementFallbackPosition** - Add fallback positions for linear placements
- **AddZeroLengthSegmentToAlignment** - Add zero-length segments to alignments
- **PatchStationReferentPosition** - Patch station referent positions

### Data Conversion and Migration
- **AGS2IFC** - Convert AGS (geotechnical) data to IFC
- **ConvertLengthUnit** - Convert between length units
- **ConvertNestToAggregate** - Convert nesting relationships to aggregations
- **ConvertPropertiesToQuantities** - Convert properties to quantities
- **Migrate** - Migrate between IFC schema versions

### Element Extraction and Manipulation
- **ExtractElements** - Extract specific elements into a new model
- **ExtractPropertiesToSQLite** - Export properties to SQLite database
- **Ifc2Sql** - Convert IFC to SQL database
- **TessellateElements** - Tessellate elements into triangulated geometry

### Fixing Software-Specific Issues
- **FixArchiCADToRevitDoorSwings** - Fix door swing orientation from ArchiCAD for Revit
- **FixArchiCADToRevitSpaces** - Fix space data from ArchiCAD for Revit
- **FixRevit2025TINs** - Fix TIN (Triangulated Irregular Network) issues from Revit 2025
- **FixRevitClassificationCodeTypes** - Fix classification code data types from Revit
- **FixRevitTINs** - Fix TIN issues from Revit

### Geometry and Representation
- **AssignConstituentFractions** - Assign fractions to material constituents
- **DowngradeIndexedPolyCurve** - Convert indexed poly curves to simpler representations
- **RemoveSiteRepresentation** - Remove geometric representation from site elements

### Merging and Optimization
- **MergeDuplicateTypes** - Merge duplicate element types
- **MergeProjects** - Merge multiple IFC projects
- **MergeStyles** - Merge duplicate styles
- **Optimise** - Optimize file size and structure
- **PurgeData** - Remove unused data from model

### Spatial and Coordinate Systems
- **OffsetObjectPlacements** - Offset object placement coordinates
- **OffsetStoreyElevations** - Offset storey elevations
- **ResetAbsoluteCoordinates** - Reset absolute coordinates to origin
- **ResetSpatialElementLocations** - Reset spatial element locations
- **SetFalseOrigin** - Set a false origin for coordinates
- **SetRefElevation** - Set reference elevation
- **SetWorldCoordinateSystem** - Set world coordinate system
- **SplitByBuildingStorey** - Split model by building storeys

### Utilities
- **RecycleNonRootedElements** - Remove or recycle non-rooted elements
- **RegenerateGlobalIds** - Regenerate GlobalId values for elements
- **RemoveRevitUniformatClassification** - Remove Revit Uniformat classification
- **UnsharePsets** - Unshare property sets between elements
