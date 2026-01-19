# CLAUDE.md - Saikei Civil Context for IfcOpenShell Contributions

> This document provides context for Claude Code when working on Saikei Civil contributions to IfcOpenShell, specifically horizontal alignment visualization.

---

## Project Overview

**Saikei Civil** (formerly BlenderCivil) is an open-source Blender extension for native IFC 4.3 infrastructure design. The project aims to democratize professional civil engineering tools by providing free alternatives to expensive commercial software like Civil 3D ($2,500/year) and OpenRoads ($4,000/year).

### Mission
- **Bonsai BIM** = Buildings (vertical construction)
- **Saikei Civil** = Infrastructure (horizontal construction: roads, earthwork, drainage)

> "While Bonsai crafts the buildings, Saikei shapes the world around them."

### Key Differentiator
**Native IFC Philosophy**: IFC files serve as the primary database rather than export targets. We're not converting TO IFC - we ARE IFC from the start.

---

## Architecture Principles

### Three-Layer Architecture (Matches Bonsai)

Saikei follows Bonsai's proven architecture with `core/` and `tool/` at the **package root level**:

```
saikei/
├── core/                      # Layer 1: Pure Python - NO bpy imports
│   └── alignment.py           # Business logic, math, validation
├── tool/                      # Layer 2: Blender implementations - HAS bpy
│   └── alignment.py           # Blender object creation, linking
└── civil/                     # Layer 3: UI (like Bonsai's bim/)
    └── module/
        └── alignment/
            ├── __init__.py    # Registration
            ├── operator.py    # Blender operators
            ├── ui.py          # UI panels
            ├── prop.py        # PropertyGroups
            └── data.py        # UI data caching
```

**Layer Responsibilities:**

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: civil/module/{name}/ (UI Layer)                   │
│  - operator.py: User actions (bpy.types.Operator)           │
│  - ui.py: Interface panels (bpy.types.Panel)                │
│  - prop.py: UI state (bpy.types.PropertyGroup)              │
│  - Calls core functions, passing tool implementations       │
└─────────────────────────────────────────────────────────────┘
                           │ calls
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: core/ (Pure Python - NO bpy imports)              │
│  - All business logic, algorithms, mathematics              │
│  - Receives tool classes as parameters (dependency inject)  │
│  - MUST be testable outside Blender                         │
└─────────────────────────────────────────────────────────────┘
                           │ receives as parameters
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: tool/ (Blender implementations)                   │
│  - Concrete implementations with bpy                        │
│  - Blender object creation, scene manipulation              │
│  - Wraps Bonsai's tool.Ifc, tool.Collector, etc.            │
└─────────────────────────────────────────────────────────────┘
```

### Bonsai's Dependency Injection Pattern

Core functions receive tool classes as parameters, enabling testability:

```python
# In core/alignment.py (NO bpy imports)
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ifcopenshell
    import saikei.tool as tool

def create_alignment_visualization(
    ifc: type[tool.Ifc],
    alignment_tool: type[tool.Alignment],
    alignment: ifcopenshell.entity_instance,
) -> list:
    """Pure business logic - tools passed as parameters."""
    segments = get_layout_segments(alignment)
    objects = []
    for segment in segments:
        obj = alignment_tool.create_segment_object(segment)
        ifc.link(obj, segment)
        objects.append(obj)
    return objects
```

```python
# In civil/module/alignment/operator.py (HAS bpy)
import bpy
import saikei.tool as tool
import saikei.core.alignment as core

class SAIKEI_OT_visualize_alignment(bpy.types.Operator):
    def execute(self, context):
        alignment = self.get_active_alignment()
        # Call core logic, passing tool implementations
        core.create_alignment_visualization(
            tool.Ifc, tool.Alignment, alignment
        )
        return {'FINISHED'}
```

### Golden Pattern for Native IFC

```python
# 1. GET IFC FILE
ifc = NativeIfcManager.get_file()

# 2. CREATE/MODIFY IFC ENTITY FIRST
entity = ifc.create_entity("IfcAlignment", ...)

# 3. CREATE BLENDER VISUALIZATION SECOND
obj = create_blender_object(...)

# 4. LINK THEM (minimal storage in Blender)
NativeIfcManager.link_object(obj, entity)
# obj["ifc_definition_id"] = entity.id()
# obj["ifc_class"] = entity.is_a()
# obj["GlobalId"] = entity.GlobalId

# 5. SAVE = WRITE IFC FILE
NativeIfcManager.save_file("project.ifc")
```

### Key Principles
1. **IFC-First Design**: ALL civil engineering data lives in the IFC file
2. **Minimal Blender Storage**: Only 3 properties stored in Blender objects
3. **Separation of Concerns**: Core logic has NO bpy imports
4. **IfcStore Pattern**: Following Bonsai's proven pattern for IFC file management

---

## IFC 4.3 Alignment Structure

### Entity Hierarchy

```
IfcProject
└── IfcSite
    └── IfcRoad (via IfcRelAggregates)
        └── IfcAlignment (via IfcRelContainedInSpatialStructure)
            ├── IfcAlignmentHorizontal (via IfcRelNests)
            │   └── [IfcAlignmentSegment → IfcAlignmentHorizontalSegment]*
            ├── IfcAlignmentVertical (via IfcRelNests)
            │   └── [IfcAlignmentSegment → IfcAlignmentVerticalSegment]*
            └── IfcAlignmentCant (via IfcRelNests) [Future]
                └── [IfcAlignmentSegment → IfcAlignmentCantSegment]*
```

### Critical IFC Rules

1. **Zero-Length Terminal Segments**: The last `IfcAlignmentSegment.DesignParameters` in each layout MUST be zero length to provide the end point
2. **Ordered Collections**: `IfcRelNests.RelatedObjects` maintains segment order (start to end)
3. **Nesting Order**: Horizontal precedes Vertical precedes Cant in `IfcRelNests`

### Semantic vs Geometric Representation

The IFC 4.3 alignment model has TWO parallel structures:

**Semantic (Business Logic)**:
- `IfcAlignmentHorizontalSegment` with `PredefinedType` (LINE, CIRCULARARC, CLOTHOID, etc.)
- Contains design parameters (radius, length, direction)

**Geometric (Shape)**:
- `IfcCurveSegment` → `ParentCurve` (IfcLine, IfcCircle, IfcClothoid)
- Combined into `IfcCompositeCurve` (horizontal) or `IfcGradientCurve` (vertical)

**Mapping Table:**
| Business Logic (Semantic) | Geometric ParentCurve |
|---------------------------|----------------------|
| LINE                      | IfcLine              |
| CIRCULARARC               | IfcCircle            |
| CLOTHOID                  | IfcClothoid          |
| CUBIC                     | IfcPolynomialCurve   |
| PARABOLICARC              | IfcPolynomialCurve   |
| CONSTANTGRADIENT          | IfcLine              |

### The 2.5D Layered Model

IFC alignments use a "2.5D" approach - combining multiple 2D curves:

1. **Layer 1 - Horizontal**: `IfcCompositeCurve` in X-Y (Easting-Northing) plane
2. **Layer 2 - Vertical**: `IfcGradientCurve` in "Distance Along, Elevation" coordinate system
   - `BaseCurve` attribute points to horizontal `IfcCompositeCurve`
3. **Layer 3 - Cant**: `IfcSegmentedReferenceCurve` for superelevation
   - `BaseCurve` typically points to `IfcGradientCurve`

---

## Horizontal Alignment Implementation

### PI-Driven Design Approach

Saikei Civil uses the **Point of Intersection (PI)** method, matching professional workflows in Civil 3D and OpenRoads:

```
    PI● is just an intersection point
         ╲
          ╲ Tangent
           BC (Begin Curve)
            ╲  ╱
             ●   Curve (R=150m)
            ╱  ╲
           EC (End Curve)
          ╱ Tangent
         ╱
```

**Key Distinction**: 
- PIs are just intersection points (NO radius property)
- Curves are separate entities inserted between tangents (Curves HAVE radius)

### Core Classes

```python
class HorizontalAlignmentManager:
    """Core engine for horizontal alignment"""
    def add_pi(self, x: float, y: float) -> PI
    def insert_curve(self, pi_index: int, radius: float) -> Curve
    def generate_segments(self) -> List[Segment]
    
class PI:
    """Point of Intersection - just a position"""
    position: Tuple[float, float]
    # NO radius property
    
class Curve:
    """Curve inserted at a PI"""
    radius: float
    bc: Tuple[float, float]  # Begin Curve point
    ec: Tuple[float, float]  # End Curve point
    at_pi: int               # Which PI this curve is at
```

### Civil Engineering Mathematics

**Deflection Angle:**
```
Δ = arccos(t₁ · t₂)
```
Where t₁ and t₂ are normalized incoming/outgoing tangent vectors.

**Tangent Length:**
```
T = R × tan(Δ/2)
```

**Arc Length:**
```
L = R × Δ  (radians)
```

**BC/EC Points:**
```
BC = PI - t₁ × T
EC = PI + t₂ × T
```

### Segment Generation

```python
def regenerate_segments(self):
    """Auto-generate tangent and curve segments from PIs"""
    segments = []
    
    for i, pi in enumerate(self.pis[:-1]):
        next_pi = self.pis[i + 1]
        
        # Check if curve at this PI
        curve = self.get_curve_at_pi(i)
        
        if curve:
            # Add incoming tangent (trimmed to BC)
            segments.append(create_line_segment(prev_end, curve.bc))
            # Add curve
            segments.append(create_arc_segment(curve))
            prev_end = curve.ec
        else:
            # Add full tangent
            segments.append(create_line_segment(prev_end, next_pi.position))
            prev_end = next_pi.position
    
    return segments
```

---

## Visualization Layer

### AlignmentVisualizer Class

```python
class AlignmentVisualizer:
    """Create Blender visualization of IFC alignment"""
    
    def __init__(self, native_alignment):
        self.alignment = native_alignment
        self.collection = None
        self.pi_objects = []
        self.segment_objects = []
    
    def visualize_all(self):
        """Generate complete visualization"""
        self.setup_collection()
        self.create_pi_markers()
        self.create_segment_curves()
```

### Color Coding Convention

**PI Markers (Empties):**
- 🟢 Green = Tangent points (no curve)
- 🟠 Orange = Curve PIs (curve inserted)

**Segment Objects (Curves):**
- 🔵 Blue = Tangent segments (LINE)
- 🔴 Red = Circular arcs (CIRCULARARC)

### Object Linking Pattern

```python
# Every Blender object stores only 3 properties
obj["ifc_definition_id"] = entity.id()
obj["ifc_class"] = entity.is_a()
obj["GlobalId"] = entity.GlobalId

# All other data comes from IFC
entity = NativeIfcManager.get_entity(obj)
params = entity.DesignParameters  # Real data from IFC!
```

---

## Rick Brice's IfcOpenShell Alignment API

Rick Brice's alignment API was merged into IfcOpenShell v0.8.0 (PR #6234, March 14, 2025). This API provides comprehensive Python functions for IFC alignment creation.

### Key Functions

**Creation:**
```python
import ifcopenshell.api.alignment as align_api

# Create alignment with PI method
alignment = align_api.create_by_pi_method(
    ifc_file, 
    name='Main Alignment',
    hpoints=[(0,0), (100,50), (200,100)],  # Horizontal PI coordinates
    radii=[0, 150, 200],                    # Curve radii at PIs
    start_station=0.0
)

# Create alignment structure
alignment = align_api.create(
    ifc_file,
    name="Highway 101",
    horizontal_layout=horiz,
    vertical_layout=vert  # Optional
)
```

**Layout Functions:**
```python
# Add to existing horizontal
align_api.layout_horizontal_alignment_by_pi_method(
    ifc_file, horiz_alignment, hpoints, radii
)

# Add vertical layout
align_api.add_vertical_layout(alignment, vertical_layout)

# Add zero-length terminator (required!)
align_api.add_zero_length_segment(layout)
```

**Getters:**
```python
horiz = align_api.get_horizontal_layout(alignment)
vert = align_api.get_vertical_layout(alignment)
segments = align_api.get_layout_segments(layout)
curve = align_api.get_layout_curve(layout)  # IfcCompositeCurve/IfcGradientCurve
```

### Integration Strategy

**Recommended architecture for Saikei contributions:**

| Layer | Rick's API Responsibility | Saikei's Responsibility |
|-------|--------------------------|------------------------|
| IFC Backend | All IFC entity creation, relationships, geometric representations | None - use Rick's API |
| Business Logic | Alignment math, segment generation, stationing | Design validation, AASHTO rules |
| UI Layer | None (Python API only) | Full Blender panels, operators |
| Visualization | None | Real-time 3D preview, PI markers |

### Example Integration Pattern

```python
# Saikei Civil operator using Rick's API backend
import ifcopenshell.api.alignment as align_api

class SAIKEI_OT_create_alignment(bpy.types.Operator):
    def execute(self, context):
        # Get PI data from Blender UI
        hpoints = [(pi.x, pi.y) for pi in context.scene.saikei_pis]
        radii = [pi.radius for pi in context.scene.saikei_pis]
        
        # Use Rick's API for IFC creation
        alignment = align_api.create_by_pi_method(
            self.ifc_file, 
            name='Main Alignment',
            hpoints=hpoints, 
            radii=radii,
            start_station=context.scene.saikei_start_station
        )
        
        # Saikei handles visualization
        self.visualizer.update_from_ifc(alignment)
        return {'FINISHED'}
```

---

## Validation and Compliance

### buildingSMART Validation

Saikei Civil has undergone extensive validation testing with buildingSMART International. Key compliance requirements:

1. **Zero-Length Terminal Segments**: Every layout must end with a zero-length segment
2. **Spatial Hierarchy**: Proper `IfcRelAggregates` and `IfcRelContainedInSpatialStructure`
3. **Segment Continuity**: End of segment N must match start of segment N+1 (< 0.001m tolerance)
4. **Ordered Nesting**: Segments in correct order via `IfcRelNests.RelatedObjects`

### Validation Code Pattern

```python
def validate_alignment(alignment):
    """Validate IFC alignment structure"""
    errors = []
    warnings = []
    
    # Check basic structure
    if not alignment:
        errors.append("No IfcAlignment entity")
        return errors, warnings
    
    # Get horizontal layout
    horiz = get_horizontal_layout(alignment)
    if not horiz:
        errors.append("No IfcAlignmentHorizontal")
        return errors, warnings
    
    # Check segments
    segments = get_layout_segments(horiz)
    if len(segments) < 2:
        warnings.append("Need at least 2 segments")
    
    # Check zero-length terminator
    last_seg = segments[-1].DesignParameters
    if last_seg.SegmentLength > 0.0001:
        errors.append("Missing zero-length terminal segment")
    
    # Check continuity
    for i in range(len(segments) - 1):
        gap = calculate_gap(segments[i], segments[i+1])
        if gap > 0.001:
            errors.append(f"Gap of {gap}m between segments {i} and {i+1}")
    
    return errors, warnings
```

---

## PR Focus: Horizontal Alignment Visualization

For your first PR focused on horizontal alignment visualization, focus on:

### Core Requirements

1. **Read IFC alignment data** using Rick's API getters
2. **Generate Blender visualization objects** (curves/empties)
3. **Link objects to IFC entities** with minimal storage
4. **Color-code by segment type** (LINE=blue, CIRCULARARC=red)
5. **Support real-time updates** via depsgraph handlers

### Key Files to Create/Modify

Following Bonsai's architecture with `core/` and `tool/` at package root:

```
saikei/
├── core/                          # NEW - Pure Python (NO bpy)
│   ├── __init__.py
│   └── alignment.py               # Business logic, math, validation
├── tool/                          # NEW - Blender implementations
│   ├── __init__.py
│   └── alignment.py               # Blender object creation, linking
└── civil/                         # EXISTING - UI layer
    └── module/
        └── alignment/
            ├── __init__.py        # Registration
            ├── operator.py        # Operators call core.*, passing tool.*
            ├── ui.py              # UI panels
            ├── prop.py            # PropertyGroups
            └── data.py            # UI data caching
```

### Minimal Visualization Implementation

```python
def visualize_horizontal_alignment(alignment, collection):
    """Create Blender visualization from IFC alignment"""
    
    # Get segments from IFC
    horiz = align_api.get_horizontal_layout(alignment)
    segments = align_api.get_layout_segments(horiz)
    
    objects = []
    for i, segment in enumerate(segments):
        params = segment.DesignParameters
        
        if params.PredefinedType == "LINE":
            obj = create_line_curve(params, name=f"Tangent_{i}")
            set_material_color(obj, BLUE)
        elif params.PredefinedType == "CIRCULARARC":
            obj = create_arc_curve(params, name=f"Curve_{i}")
            set_material_color(obj, RED)
        
        # Link to IFC
        obj["ifc_definition_id"] = segment.id()
        obj["ifc_class"] = segment.is_a()
        obj["GlobalId"] = segment.GlobalId
        
        collection.objects.link(obj)
        objects.append(obj)
    
    return objects
```

---

## Development Guidelines

### Code Style
- Follow PEP 8
- Type annotations for all public functions
- Docstrings with examples
- No `bpy` imports in `core/` modules

### Testing
- Unit tests for all core logic (outside Blender)
- Integration tests with sample IFC files
- Validation against buildingSMART checker

### Commit Messages
```
feat(alignment): Add horizontal alignment visualization

- Create AlignmentVisualizer class for Blender curve generation
- Support LINE and CIRCULARARC segment types
- Implement IFC entity linking pattern
- Add color coding by segment type

Refs: #123
```

---

## Resources

### Documentation
- IFC 4.3 Specification: https://ifc43-docs.standards.buildingsmart.org/
- IfcOpenShell Docs: https://docs.ifcopenshell.org/
- Bonsai Wiki: https://wiki.osarch.org/

### Community
- OSArch Forum: https://community.osarch.org/
- IfcOpenShell GitHub: https://github.com/IfcOpenShell/IfcOpenShell
- buildingSMART Forums: https://forums.buildingsmart.org/

### Key Contacts
- **Rick Brice** (WSDOT) - IfcOpenShell alignment API author
- **Dion Moult** - Bonsai BIM founder
- **Will Sharp** (HDR) - buildingSMART committee co-chair

---

## Quick Reference

### Entity Creation Pattern
```python
# Always create IFC first, then Blender, then link
entity = ifc.create_entity("IfcAlignmentSegment", ...)
obj = bpy.data.objects.new("Segment", curve_data)
obj["ifc_definition_id"] = entity.id()
```

### Segment Types
- `LINE` → IfcLine (blue visualization)
- `CIRCULARARC` → IfcCircle (red visualization)
- `CLOTHOID` → IfcClothoid (future)
- `CONSTANTGRADIENT` → IfcLine (vertical)
- `PARABOLICARC` → IfcPolynomialCurve (vertical)

### Required Terminal Segment
```python
# Last segment MUST be zero-length
align_api.add_zero_length_segment(layout)
```

### Minimal Object Storage
```python
# ONLY these 3 properties in Blender
obj["ifc_definition_id"] = entity.id()
obj["ifc_class"] = entity.is_a()
obj["GlobalId"] = entity.GlobalId
```

---

*Document Version: 1.1*
*Updated: January 2026*
*Changes: Updated architecture to match Bonsai's actual pattern (core/ and tool/ at package root)*
*For: Saikei Civil IfcOpenShell PR - Horizontal Alignment Visualization*
