# IfcDiff

Compare IFC models for changes to geometry, properties, and structure. Compares the differences between two IFC models, including changes to geometry, properties, relationships, and spatial structure. Outputs differences in JSON format for further processing or reporting.

## Features

- **Element tracking**: Identify added and deleted elements between models
- **Relationship comparison**: Track changes in multiple relationship types:
  - Geometry
  - Attributes
  - Type assignments
  - Properties
  - Spatial containers
  - Aggregations
  - Classifications
- **Flexible filtering**: Compare only specific element types using IFC selectors
- **Configurable depth**: Choose between shallow (first difference only) or deep (all differences) comparison
- **JSON export**: Export comparison results in JSON format for further processing
- **Precision control**: Configure geometric comparison precision
