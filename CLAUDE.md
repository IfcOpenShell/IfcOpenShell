# CLAUDE.md - Saikei (Civil Engineering) Module Context

## Project Identity

**Name:** Saikei (Civil Engineering module for Bonsai)
**Pronunciation:** "SIGH-kay" (盆景 - Japanese for "planted landscape")
**Tagline:** "The landscape around the buildings"
**Repository:** `IfcOpenShell/IfcOpenShell` (branch: `saikei`)
**Location in repo:** `src/bonsai/bonsai/` (integrated into Bonsai)

### Brand Philosophy
Saikei is the civil engineering complement to Bonsai in the open-source IFC ecosystem:
- **Bonsai** = Buildings (vertical construction)
- **Saikei** = Infrastructure (horizontal construction: roads, earthwork, drainage)

> "While Bonsai crafts the buildings, Saikei shapes the world around them."

---

## Current Status

**Saikei has been merged into Bonsai** as of January 2026. It is no longer a separate extension but is now part of the core Bonsai codebase, following Bonsai's architecture patterns.

### Code Locations
| Component | Path |
|-----------|------|
| Core logic (business rules) | `src/bonsai/bonsai/core/alignment.py` |
| Tool layer (implementations) | `src/bonsai/bonsai/tool/alignment.py` |
| UI module | `src/bonsai/bonsai/bim/module/alignment/` |
| GPU decorators | `src/bonsai/bonsai/bim/module/alignment/decorator.py` |

---

## Mission & Vision

### Mission
Democratize professional civil engineering tools by providing free, open-source alternatives to expensive commercial software like Civil 3D and OpenRoads.

### Target Users
- Small engineering firms seeking cost-effective tools
- Engineers in developing countries without software budgets
- Students and educators
- Land surveyors and GIS professionals

### Core Philosophy: Native IFC
**"We're not converting TO IFC. We ARE IFC."**

Unlike traditional CAD software that exports to IFC, Saikei works **IN** IFC format from the very first action. The IFC file is the single source of truth, and Blender is the visualization/interaction layer.

---

## Architecture (Bonsai Pattern)

Saikei follows Bonsai's three-layer architecture:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BONSAI                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  bim/module/alignment/     (UI Layer)                         │ │
│  │  ├── ui.py                 Panels, UILists                    │ │
│  │  ├── operator.py           Blender operators                  │ │
│  │  ├── prop.py               PropertyGroups                     │ │
│  │  ├── data.py               Cached data for UI                 │ │
│  │  └── decorator.py          GPU drawing for visual feedback    │ │
│  │                                                                │ │
│  │  WHO: User interaction, visual feedback                       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  tool/alignment.py         (Tool Layer)                       │ │
│  │                                                                │ │
│  │  HOW: ALL implementations including:                          │ │
│  │  • Math and calculations (geometry, vectors, stations)        │ │
│  │  • Algorithms (curve fitting, segment generation)             │ │
│  │  • IFC entity creation and manipulation                       │ │
│  │  • Blender object creation and management                     │ │
│  │  • Coordinate transformations                                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  core/alignment.py         (Core Layer)                       │ │
│  │                                                                │ │
│  │  WHAT: Business logic and workflow orchestration ONLY         │ │
│  │  • NO math, calculations, or algorithms                       │ │
│  │  • NO IFC entity creation (delegates to Tool)                 │ │
│  │  • NO bpy imports                                             │ │
│  │  • Defines business rules and validation                      │ │
│  │  • Orchestrates workflow (calls Tool methods)                 │ │
│  │  • Testable outside Blender                                   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. Core Layer (`core/alignment.py`) — WHAT happens

**Purpose:** Business logic and workflow orchestration ONLY

**Contains:**
- Business rules ("an alignment must have at least 2 PIs")
- Validation logic ("radius must be positive")
- Workflow orchestration ("when PI moves, regenerate segments")
- Decision-making about what should happen

**Does NOT contain:**
- Math or calculations (no `T = R × tan(Δ/2)`)
- Algorithms (no curve fitting, no geometry)
- IFC entity creation (no `ifc.create_entity()`)
- Blender operations (no `bpy` imports)

**Example (CORRECT):**
```python
# core/alignment.py - Business logic ONLY
def add_curve_at_pi(ifc, alignment_tool, alignment_id, pi_index, radius):
    """Orchestrates adding a curve - delegates math to Tool."""
    alignment = ifc.get_entity(alignment_id)
    
    # Business rule validation
    if not alignment_tool.can_add_curve_at_pi(alignment, pi_index):
        raise ValueError("Cannot add curve at this PI")
    
    if radius <= 0:
        raise ValueError("Radius must be positive")
    
    # Delegate ALL math and IFC creation to Tool layer
    curve_data = alignment_tool.create_curve_at_pi(alignment, pi_index, radius)
    
    # Business rule: trigger regeneration
    alignment_tool.regenerate_segments(alignment)
    
    return curve_data
```

#### 2. Tool Layer (`tool/alignment.py`) — HOW it happens

**Purpose:** All implementations - math, algorithms, IFC, Blender

**Contains:**
- Mathematical calculations (tangent length, arc length, deflection angles)
- Geometric algorithms (curve geometry, vector operations)
- IFC entity creation and manipulation
- Blender object creation and management
- Coordinate transformations
- Station calculations

**Example (CORRECT):**
```python
# tool/alignment.py - ALL implementations here
class Alignment:
    @classmethod
    def create_curve_at_pi(cls, alignment, pi_index, radius):
        """Tool layer - math and IFC creation happens here."""
        pis = cls.get_pis(alignment)
        p1, p2, p3 = pis[pi_index-1], pis[pi_index], pis[pi_index+1]
        
        # Math calculations (THIS BELONGS IN TOOL)
        t1 = (p2 - p1).normalized()
        t2 = (p3 - p2).normalized()
        deflection = math.acos(t1.dot(t2))
        tangent_length = radius * math.tan(deflection / 2)
        
        bc = p2 - t1 * tangent_length
        ec = p2 + t2 * tangent_length
        arc_length = radius * deflection
        
        # IFC creation (THIS BELONGS IN TOOL)
        ifc_file = tool.Ifc.get()
        segment = ifc_file.create_entity("IfcAlignmentSegment", ...)
        
        return {'bc': bc, 'ec': ec, 'arc_length': arc_length, 'segment': segment}
```

#### 3. UI Layer (`bim/module/alignment/`) — WHO interacts

**Purpose:** User interaction and visual feedback

**Contains:**
- Blender operators (button handlers)
- UI panels
- Property groups
- Cached data for UI performance

### Quick Reference: What Goes Where?

| Code Type | Layer | Example |
|-----------|-------|---------|
| Math formula | **Tool** | `T = R × tan(Δ/2)` |
| Vector operations | **Tool** | `v1.dot(v2)`, `v.normalized()` |
| IFC creation | **Tool** | `ifc.create_entity("IfcAlignment")` |
| Blender objects | **Tool** | `bpy.data.objects.new()` |
| Station calculations | **Tool** | `get_station_at_point()` |
| Coordinate transforms | **Tool** | `pyproj.transform()` |
| Mesh generation | **Tool** | `bmesh.ops.create_*()` |
| "Should we do X?" | **Core** | `can_add_pi(alignment)` |
| "When X, do Y" | **Core** | workflow orchestration |
| Validation rules | **Core** | `validate_minimum_radius()` |
| Button handler | **UI** | `class CIVIL_OT_add_pi` |
| Panel layout | **UI** | `class CIVIL_PT_alignment` |

**Simple Test:** If code contains a math formula or creates an IFC entity, it belongs in **Tool**, not **Core**.

---

## Code Patterns

### 1. IFC File Access

```python
import bonsai.tool as tool

# Get IFC file
ifc_file = tool.Ifc.get()

# Get Blender object for IFC element
obj = tool.Ifc.get_object(ifc_element)

# Link IFC element to Blender object
tool.Ifc.link(ifc_element, blender_obj)
```

### 2. Operator Pattern

```python
class AddAlignment(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_alignment"
    bl_label = "Add Alignment"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        # Use core function with tool injection
        core.alignment.add_alignment(tool.Ifc, tool.Alignment)
        return {"FINISHED"}
```

### 3. Core Function Pattern

```python
# In core/alignment.py - NO bpy imports, NO math!
def add_alignment(ifc, alignment):
    """
    Business logic only - orchestrates alignment creation.
    
    Args:
        ifc: Tool class for IFC operations (injected)
        alignment: Tool class for alignment operations (injected)
    """
    # Business rule: check if we can add alignment
    if not alignment.can_create_alignment():
        raise ValueError("Cannot create alignment in current context")
    
    # Delegate actual creation to Tool layer
    result = alignment.create_alignment()
    
    return result
```

### 4. Tool Method Pattern

```python
# In tool/alignment.py - ALL implementations here
class Alignment:
    @classmethod
    def create_alignment(cls):
        """Tool layer - IFC creation and math happens here."""
        ifc_file = tool.Ifc.get()
        
        # IFC entity creation
        alignment = ifc_file.create_entity("IfcAlignment",
            GlobalId=ifcopenshell.guid.new(),
            Name="New Alignment"
        )
        
        # Blender object creation
        obj = bpy.data.objects.new("Alignment", None)
        tool.Ifc.link(alignment, obj)
        
        return alignment
```

### 5. Data Caching (for UI)

```python
# In bim/module/alignment/data.py
class AlignmentData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        # Load data from IFC
        cls.is_loaded = True

    @classmethod
    def refresh(cls):
        cls.is_loaded = False
```

### 6. GPU Decorator Pattern (Visual Feedback)

GPU decorators provide ephemeral visual feedback during modal operations. They draw directly to the viewport using Blender's GPU module and disappear automatically when the modal ends.

**Location:** `bim/module/alignment/decorator.py`

```python
# In decorator.py - GPU drawing for modal operations
class PIPickerDecorator:
    """Decorator for visualizing PI placement during modal picking."""

    # Class-level state (cleared on uninstall)
    is_installed = False
    handlers = []
    pi_points = []      # List of Vector - positions in Blender coords
    mouse_3d = None     # Current cursor position

    @classmethod
    def install(cls, context, region, rv3d):
        """Install GPU draw handlers."""
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_tangent_lines, (context,), "WINDOW", "POST_PIXEL")
        )
        cls.is_installed = True

    @classmethod
    def uninstall(cls):
        """Remove handlers and clear state."""
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.handlers = []
        cls.is_installed = False

    @classmethod
    def update(cls, pi_points_blender, mouse_3d):
        """Update state from modal operator."""
        cls.pi_points = pi_points_blender
        cls.mouse_3d = mouse_3d

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        """Standard Bonsai draw pattern - MUST call validate first."""
        if not tool.Blender.validate_shader_batch_data(content_pos, indices):
            return
        # ... shader drawing code
```

**Key Bonsai Utilities for Decorators:**

| Utility | Purpose |
|---------|---------|
| `tool.Blender.validate_shader_batch_data()` | **Required** - prevents crashes on empty batches |
| `tool.Blender.scale_font_size()` | DPI-aware font scaling for HUD text |
| `draw_circle_2d()` from `gpu_extras.presets` | Built-in circle drawing |
| `location_3d_to_region_2d()` | Convert 3D coords to screen coords |

**Modal Operator Integration:**

```python
# In operator.py
def invoke(self, context, event):
    # Install decorator for visual feedback
    alignment_decorator.PIPickerDecorator.install(context, self._region, self._rv3d)
    context.window_manager.modal_handler_add(self)
    return {"RUNNING_MODAL"}

def modal(self, context, event):
    if event.type == "MOUSEMOVE":
        # Update rubber band position
        alignment_decorator.PIPickerDecorator.update(pi_points, mouse_3d)
        self._area.tag_redraw()  # Trigger viewport redraw

    if event.type in {"RIGHTMOUSE", "ESC"}:
        alignment_decorator.PIPickerDecorator.uninstall()  # Cleanup
        return {"FINISHED"}
```

**Drawing Modes:**
- `POST_PIXEL` - 2D screen-space drawing (HUD text, lines in pixel coords)
- `POST_VIEW` - 3D world-space drawing (geometry in Blender coords)

---

## Property Naming Conventions

| Type | Prefix | Example |
|------|--------|---------|
| Scene PropertyGroup | `Civil*Properties` | `CivilAlignmentProperties` |
| Object PropertyGroup | `CivilObjectProperties` | - |
| Panel class | `CIVIL_PT_*` | `CIVIL_PT_alignments` |
| Operator class | `CIVIL_OT_*` | `CIVIL_OT_add_alignment` |
| UIList class | `CIVIL_UL_*` | `CIVIL_UL_alignments` |

**Note:** Use `Civil*` prefix, NOT `BIM*` or `BC_*` to avoid conflicts with Bonsai.

---

## IFC 4.3 Compliance

### Supported Entities
- `IfcAlignment`, `IfcAlignmentHorizontal`, `IfcAlignmentVertical`
- `IfcAlignmentSegment`, `IfcAlignmentHorizontalSegment`, `IfcAlignmentVerticalSegment`
- `IfcRoad`, `IfcSite`
- Segment types: LINE, CIRCULARARC, CLOTHOID, CONSTANTGRADIENT, PARABOLICARC

### Spatial Hierarchy
```
IfcProject
└── IfcSite
    └── IfcRoad
        └── IfcAlignment
            ├── IfcAlignmentHorizontal
            │   └── IfcAlignmentSegment(s)
            └── IfcAlignmentVertical
                └── IfcAlignmentSegment(s)
```

### Key API
```python
import ifcopenshell.api.alignment as align_api

# Create alignment using PI method
alignment = align_api.create_by_pi_method(
    ifc_file,
    name="Main Road",
    hpoints=[(0, 0), (100, 0), (200, 50)],
    radii=[0, 150, 0],
    start_station=0.0
)

# Get horizontal layout from alignment
h_layout = align_api.get_horizontal_layout(alignment)
```

---

## Development Setup

### Prerequisites
- Blender 5.0+
- Python 3.11
- Git

### Symlink for Development
```powershell
# Remove installed Bonsai extension
Remove-Item -Recurse "C:\Users\{USER}\AppData\Roaming\Blender Foundation\Blender\5.0\extensions\blender_org\bonsai"

# Create symlink to source
New-Item -ItemType SymbolicLink -Path "C:\Users\{USER}\AppData\Roaming\Blender Foundation\Blender\5.0\extensions\blender_org\bonsai" -Target "C:\GitHub\IfcOpenShell\src\bonsai\bonsai"
```

### Required Setup for Symlink
1. Update `blender_manifest.toml`: Change `platforms = ["os-arch"]` to `platforms = ["windows-x64"]`
2. Extract all wheels to site-packages (see Development Notes)
3. Mark manifest as skip-worktree: `git update-index --skip-worktree src/bonsai/bonsai/blender_manifest.toml`

---

## Development Progress

### Completed Features
- Horizontal alignment creation (PI method)
- All segment type visualization (LINE, CIRCULARARC, CLOTHOID, spirals via IfcOpenShell geometry engine)
- Individual segment selection (each segment is a selectable Blender curve)
- Alignment hierarchy in Blender (parent/child relationships)
- Stationing referents
- Zero-length terminator segment handling (invisible to users)
- Georeference/coordinate transformation support
- PI picker rubber band visualization (GPU decorator for visual feedback during modal picking)

### In Progress
- Vertical alignment support
- Corridor generation
- Cross-section profiles

### Planned
- Earthwork calculations
- Drainage design

---

## Testing

```python
# In Blender Python console:

# Test IFC access
import bonsai.tool as tool
ifc = tool.Ifc.get()
print(f"IFC loaded: {ifc is not None}")
print(f"Schema: {ifc.schema if ifc else 'N/A'}")

# Test alignments
if ifc:
    alignments = ifc.by_type("IfcAlignment")
    print(f"Alignments: {len(alignments)}")
```

---

## Resources

### Documentation
- IFC 4.3 Spec: https://ifc43-docs.standards.buildingsmart.org/
- IfcOpenShell: https://docs.ifcopenshell.org/
- Bonsai Docs: https://docs.bonsaibim.org/
- Bonsai Wiki: https://wiki.osarch.org/

### Community
- OSArch Forum: https://community.osarch.org/
- buildingSMART: https://www.buildingsmart.org/

---

## Contact & Ownership

**Primary Developer:** Michael Yoder (Desert Springs Civil Engineering PLLC)
**Project:** Part of IfcOpenShell/Bonsai (open-source, community-driven)
**License:** GPL v3

---

*Last Updated: February 2026*
*Saikei - Civil Engineering for Bonsai*

---

## Architecture Clarification Note

**Source:** Dion Moult (Bonsai founder), January 2026

The three-layer architecture follows this strict separation:

| Layer | Contains | Simple Rule |
|-------|----------|-------------|
| **Core** | Business logic ONLY | "Decides WHAT happens" |
| **Tool** | Math, algorithms, IFC, Blender | "Implements HOW it happens" |
| **UI** | User interaction | "Handles WHO interacts" |

**Key insight:** If code contains a math formula or creates an IFC entity, it belongs in **Tool**, not **Core**. Core only orchestrates and validates - it never calculates.

---

## Geometry Pipeline (Alignment Visualization)

This section documents how alignment segments are converted from IFC entities to visible Blender curves.

### Entity Hierarchy

```
IFC Semantic Layer (Business Logic)
├── IfcAlignment
│   └── IfcAlignmentHorizontal (nested via IfcRelNests)
│       └── IfcAlignmentSegment (nested via IfcRelNests)
│           └── DesignParameters: IfcAlignmentHorizontalSegment
│               • StartPoint, StartDirection
│               • SegmentLength, PredefinedType (LINE, CIRCULARARC, CLOTHOID, etc.)
│               • StartRadiusOfCurvature, EndRadiusOfCurvature

IFC Geometric Layer (Representation)
├── IfcCompositeCurve (for horizontal)
│   └── IfcCurveSegment (one per alignment segment)
│       • Placement: IfcAxis2Placement2D
│       • ParentCurve: IfcLine, IfcCircle, IfcClothoid, etc.
│       • SegmentStart, SegmentLength
```

### Geometry Flow

```
IfcAlignmentSegment
        │
        ▼
┌───────────────────────────────┐
│ align_api.get_mapped_segments │  (IfcOpenShell API)
│ Maps semantic → geometric     │
└───────────────────────────────┘
        │
        ▼
IfcCurveSegment (geometric representation)
        │
        ▼
┌───────────────────────────────┐
│ align_util.evaluate_segment   │  (IfcOpenShell geometry engine)
│ Returns 4x4 transform matrix  │
│ at distance along segment     │
└───────────────────────────────┘
        │
        ▼
Transform Matrix (4x4, TRANSPOSED)
┌                           ┐
│ Xx  Xy  Xz  0 │  Row 0: X-axis direction
│ Yx  Yy  Yz  0 │  Row 1: Y-axis direction
│ Zx  Zy  Zz  0 │  Row 2: Z-axis direction
│ Tx  Ty  Tz  1 │  Row 3: Translation (position)
└                           ┘
        │
        ▼
Blender CURVE object with vertices
```

### Key Implementation: `get_segment_vertices()`

Location: `src/bonsai/bonsai/tool/alignment.py`

This method extracts vertices from an IFC alignment segment using IfcOpenShell's geometry engine:

```python
@classmethod
def get_segment_vertices(
    cls, segment: "ifcopenshell.entity_instance", distance_interval: float = 1.0
) -> Optional[List[Tuple[float, float, float]]]:
    """Get vertices for a single alignment segment using IfcOpenShell's geometry engine."""
    import ifcopenshell.api.alignment as align_api
    from ifcopenshell.api.alignment import util as align_util

    # Get the mapped curve segment(s) for this alignment segment
    mapped_segments = align_api.get_mapped_segments(segment)
    # mapped_segments is tuple: (main_segment, spiral_in, spiral_out)

    for curve_segment in [s for s in mapped_segments if s is not None]:
        segment_length = curve_segment.SegmentLength.wrappedValue
        num_points = max(2, int(segment_length / distance_interval) + 1)

        for i in range(num_points):
            dist_along = (i / (num_points - 1)) * segment_length

            # Use IfcOpenShell geometry engine to evaluate position
            transform_matrix = align_util.evaluate_segment(curve_segment, dist_along)

            # CRITICAL: Matrix is transposed - position is in ROW 3, not column 3
            x = float(transform_matrix[3, 0]) / unit_scale
            y = float(transform_matrix[3, 1]) / unit_scale
            z = float(transform_matrix[3, 2]) / unit_scale

            vertices.append((x, y, z))

    return vertices
```

**Critical Note:** The transform matrix returned by `evaluate_segment()` is transposed compared to standard OpenGL/Blender conventions. Position values are in **row 3** (indices `[3, 0]`, `[3, 1]`, `[3, 2]`), not column 3.

### Key Implementation: `_create_segment_curve()`

Location: `src/bonsai/bonsai/tool/alignment.py`

Creates a Blender CURVE object from segment vertices:

```python
@classmethod
def _create_segment_curve(
    cls,
    segment: "ifcopenshell.entity_instance",
    segment_number: int,
    parent_obj: "bpy.types.Object",
) -> Optional["bpy.types.Object"]:
    """Create a Blender curve object for an alignment segment."""

    # Skip zero-length terminator segments
    if cls.is_zero_length_segment(segment):
        return None

    # Get vertices using IfcOpenShell geometry engine
    vertices = cls.get_segment_vertices(segment)
    if not vertices:
        return None

    # Create Blender curve
    curve_data = bpy.data.curves.new(name=curve_name, type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('POLY')
    spline.points.add(len(vertices) - 1)

    for i, (x, y, z) in enumerate(vertices):
        spline.points[i].co = (x, y, z, 1.0)  # w=1.0 for 3D

    obj = bpy.data.objects.new(curve_name, curve_data)
    obj.parent = parent_obj

    # Link to IFC element
    tool.Ifc.link(segment, obj)

    return obj
```

### Zero-Length Segment Handling

IFC alignments require a zero-length terminator segment at the end. These are handled invisibly:

```python
@classmethod
def is_zero_length_segment(cls, segment: "ifcopenshell.entity_instance") -> bool:
    """Check if segment is a zero-length terminator."""
    design_params = segment.DesignParameters
    if design_params.is_a("IfcAlignmentHorizontalSegment"):
        return design_params.SegmentLength == 0.0
    elif design_params.is_a("IfcAlignmentVerticalSegment"):
        return design_params.HorizontalLength == 0.0
    return False

@classmethod
def layout_has_real_segments(cls, layout: "ifcopenshell.entity_instance") -> bool:
    """Check if layout has segments beyond just the zero-length terminator."""
    for rel in layout.IsNestedBy:
        for segment in rel.RelatedObjects:
            if not cls.is_zero_length_segment(segment):
                return True
    return False
```

**Behavior:**
- Zero-length segments are never visualized (no Blender object created)
- Empty layouts (only zero-length segment) skip geometry generation silently
- Warnings are suppressed for expected empty-layout scenarios

### IfcOpenShell Alignment API Functions Used

| Function | Location | Purpose |
|----------|----------|---------|
| `get_mapped_segments(segment)` | `ifcopenshell.api.alignment` | Maps IfcAlignmentSegment → IfcCurveSegment(s) |
| `evaluate_segment(curve_seg, dist)` | `ifcopenshell.api.alignment.util` | Returns 4x4 transform matrix at distance |
| `get_horizontal_layout(alignment)` | `ifcopenshell.api.alignment` | Gets IfcAlignmentHorizontal from alignment |
| `get_curve(alignment)` | `ifcopenshell.api.alignment` | Gets geometric representation curve |
| `has_zero_length_segment(layout)` | `ifcopenshell.api.alignment` | Checks for terminator segment |

### Coordinate Transformation

When georeference data exists, coordinates are transformed:

```python
# In tool/alignment.py
georeference = tool.Georeference.get_georeference()
if georeference:
    vertices = [
        tool.Georeference.xyz2local(v, georeference)
        for v in vertices
    ]
```

This ensures alignment geometry displays correctly in Blender's coordinate system when the IFC file uses real-world coordinates.

---

## Troubleshooting & Debugging

### Common Issues and Solutions

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| All vertices at (0,0,0) | Matrix index wrong (column vs row) | Use `matrix[3, 0]` not `matrix[0, 3]` for position |
| No visualization | Zero-length segment only | Check `layout_has_real_segments()` before generating |
| Segment not selectable | Created as EMPTY, not CURVE | Ensure `_create_segment_curve()` creates curve data |
| Wrong position in viewport | Missing georeference transform | Apply `tool.Georeference.xyz2local()` to vertices |
| `generate_vertices failed` | Empty IfcCompositeCurve | Skip geometry generation for empty layouts |

### Debugging with Blender MCP

Use Blender MCP to execute Python in Blender for live debugging:

```python
# Check if segments exist
import bonsai.tool as tool
ifc = tool.Ifc.get()
alignments = ifc.by_type("IfcAlignment")
for a in alignments:
    for rel in a.IsNestedBy:
        for child in rel.RelatedObjects:
            if child.is_a("IfcAlignmentHorizontal"):
                for rel2 in child.IsNestedBy:
                    print(f"Segments: {len(rel2.RelatedObjects)}")

# Test geometry evaluation
import ifcopenshell.api.alignment as align_api
from ifcopenshell.api.alignment import util as align_util
segment = ifc.by_type("IfcAlignmentSegment")[0]
mapped = align_api.get_mapped_segments(segment)
if mapped[0]:
    matrix = align_util.evaluate_segment(mapped[0], 0.0)
    print(f"Start position: ({matrix[3,0]}, {matrix[3,1]}, {matrix[3,2]})")
```

### Key Files to Check When Debugging

1. **`tool/alignment.py`** - Main implementation (geometry, Blender objects)
2. **`ifcopenshell/api/alignment/util.py`** - Geometry engine functions
3. **`ifcopenshell/api/alignment/get_mapped_segments.py`** - Semantic to geometric mapping

### Rebuilding After Breaking Changes

If the alignment visualization breaks:

1. **Verify IFC structure**: Check that IfcAlignmentSegment has DesignParameters and is nested correctly
2. **Verify geometry mapping**: Confirm `get_mapped_segments()` returns valid IfcCurveSegments
3. **Verify matrix extraction**: Remember matrix is TRANSPOSED - position in row 3
4. **Verify unit scaling**: Apply `calculate_unit_scale(file)` to coordinates
5. **Verify Blender object creation**: Ensure curve has spline points and is linked to IFC element
