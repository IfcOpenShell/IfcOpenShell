IfcView format
==============

``.ifcview`` is a lossy binary geometry cache used by the Bonsai Viewer and
IfcViewer. It is a geometry cache, not an IFC exchange format. It stores
quantised, compressed, spatially sorted streamable chunks of tessellated
geometry, instancing, LODs, georeferencing, and basic element identifiers.

The format is optimised for three requirements:

- fast load and reuse of model geometry for analysis or visualisation
- direct upload to a viewer's GPU-facing mesh and instance layout
- compressed chunked streaming, especially for web loading by byte range

It intentionally does not store non-geometric IFC data or original IFC
parametric geometry. It is recommended to be combined with the original
``.ifc`` file, a ``.ifcdb``/``.rdb`` model store, or an ``.rdbview`` package
when additional data is needed.

The format writes native C++ structs directly for several tables. This makes it
compact and cheap to load, but it also means that ``.ifcview`` should not be
treated as a stable, language-neutral interchange specification.

The source of truth for the format is the C++ sidecar implementation in
``src/ifcviewer``. The current on-disk version is version 17.

Top-level layout
----------------

.. csv-table::
   :header: "Section", "Description"

   "SidecarHeader", "Versioning and format metadata"
   "uint64 geometry_section_size", "Number of bytes from start of geometry section to byte immediately before the geometry metadata block. May be used by streaming readers to skip bulk geometry and first fetch metadata."
   "Geometry section", "Streamable compressed chunks of geometry"
   "Geometry metadata block", "Mesh records, instance records, georeferencing data, and chunk frame offsets"
   "Element metadata block", "Element IDs, GUIDs, names, and IFC classes"

Both metadata blocks use the same compressed block wrapper:

.. code-block:: text

   uint64 compressed_size
   uint64 raw_size
   byte[compressed_size] zstd_frame

The geometry section is also compressed with zstd, but it is not one large
frame. Each streaming chunk has its own vertex frame and index frame so a
loader can fetch and decompress only the chunks it needs.

For web streaming, the loader would read:

1. the 20-byte head, consisting of the 12-byte header and 8-byte geometry size
2. the geometry metadata block header and compressed payload
3. the element metadata block header, so it can remember where the UI metadata
   lives

After that, visible chunks are loaded asynchronously by byte range. The
element metadata payload is fetched only when UI code asks for element
metadata.


Sidecar header
--------------

``SidecarHeader`` is 12 bytes:

.. code-block:: c

   struct SidecarHeader {
       uint32 magic;
       uint32 version;
       uint32 endian;
   };

The current values are:

.. list-table::
   :header-rows: 1

   * - Field
     - Value
     - Purpose
   * - Magic
     - ``0x49465657``
     - Identifies an ``IFVW`` sidecar.
   * - Version
     - ``17``
     - Selects the current layout version. Versions may not be compatible.
   * - Endian marker
     - ``0x01020304``
     - Rejects files written with a different byte order.

If any of these values do not match, the ifcview cache must be rejected.

Geometry section
----------------

The geometry section is the streamable part of the file. It contains, for each
chunk, two zstd frames:

.. code-block:: text

   chunk 0 vertex frame
   chunk 0 index frame
   chunk 1 vertex frame
   chunk 1 index frame
   ...

The metadata does not discover these frames by scanning. Instead, the geometry
metadata block stores the ``SidecarChunk`` table that locates each chunk's
compressed vertex and index frames.

Inside a decompressed chunk, data is chunk-local:

.. code-block:: text

   vertices for mesh first_mesh
   vertices for mesh first_mesh + 1
   ...
   LOD0 indices for mesh first_mesh
   LOD0 indices for mesh first_mesh + 1
   ...
   LOD1 indices for mesh first_mesh
   LOD1 indices for mesh first_mesh + 1
   ...

This order matches the renderer's streamed chunk upload path. Vertex offsets
and index offsets in ``MeshInfo`` describe the whole-model logical layout, but
the chunk upload path computes chunk-local offsets when it builds runtime chunk
state.

Vertex format
-------------

Each stored vertex is 12 bytes:

.. list-table::
   :header-rows: 1

   * - Byte offset
     - Type
     - Meaning
   * - ``0``
     - ``uint16[3]``
     - Quantised local position.
   * - ``6``
     - ``int8[2]``
     - Octahedral-encoded normal.
   * - ``8``
     - ``uint8[4]``
     - RGBA colour.

The position is quantised against the mesh's local axis-aligned bounding box,
stored in ``MeshInfo.local_aabb_min`` and ``MeshInfo.local_aabb_max``. This
bounding box is the quantisation basis. In other words, the format stores each
coordinate as a normalised integer within the mesh-local min/max range, rather
than storing the original float coordinate.

Conceptually, encoding does this per axis:

.. code-block:: text

   t = (position - local_aabb_min) / (local_aabb_max - local_aabb_min)
   stored = round(clamp(t, 0, 1) * 65535)

Decoding does the inverse:

.. code-block:: text

   t = stored / 65535
   position = mix(local_aabb_min, local_aabb_max, t)

The implementation stores ``extent_recip`` while encoding, which is simply
``1 / (local_aabb_max - local_aabb_min)`` for each axis. Degenerate axes use
``0`` so all coordinates on that axis quantise to the same value.

Normals use two signed bytes with octahedral encoding. This is less precise
than storing three floats, but is small and adequate for typical BIM geometry,
which is dominated by planar and axis-aligned surfaces. Colour is stored as the
four bytes used by the viewer's packed RGBA path.

Geometry metadata block
-----------------------

The geometry metadata block is the minimum metadata required to create the
runtime model and begin painting geometry. Its raw, decompressed order is:

.. code-block:: text

   vector<MeshInfo> meshes
   vector<InstanceInfo> instances
   uint32 has_coordinate_operation
   double[16] coordinate_operation_meters
   double project_length_to_meters
   double map_unit_to_meters
   vector<SidecarChunk> chunks

``MeshInfo`` is 56 bytes and describes one reusable mesh:

.. list-table::
   :header-rows: 1

   * - Field
     - Meaning
   * - ``vbo_byte_offset``
     - Byte offset of the mesh's vertices in the logical whole-model vertex buffer.
   * - ``vertex_count``
     - Number of 12-byte vertices.
   * - ``ebo_byte_offset``
     - Byte offset of the mesh's LOD0 indices in the logical index buffer.
   * - ``index_count``
     - Number of LOD0 ``uint32`` indices.
   * - ``local_aabb_min`` / ``local_aabb_max``
     - Mesh-local bounds and the quantisation basis for vertex positions.
   * - ``first_instance`` / ``instance_count``
     - Range of instances that reference this mesh after sidecar layout.
   * - ``lod1_ebo_byte_offset`` / ``lod1_index_count``
     - Optional decimated index range for LOD1. A count of ``0`` means LOD1 is unavailable.

``InstanceInfo`` is 232 bytes and records one placed occurrence of a mesh. The
important fields are:

.. list-table::
   :header-rows: 1

   * - Field
     - Meaning
   * - ``mesh_id``
     - Index into the mesh table.
   * - ``object_id``
     - Viewer object identifier used for selection and lookup.
   * - ``color_override_rgba8``
     - Optional per-instance colour override. ``0`` means use the baked vertex colour.
   * - ``model_id``
     - Source model identifier within the viewer.
   * - ``placement_transformation``
     - Double-precision placement emitted by the geometry streamer, before final federation and false-origin composition.
   * - ``transform``
     - Float render transform for the default stage state. Loaders may recompute it from ``placement_transformation`` and current stage matrices.
   * - ``world_aabb_min`` / ``world_aabb_max``
     - World-space instance bounds used for chunk bounds, culling, and view fitting.

Both transform forms are stored for precision and reuse. The double placement
keeps large IFC coordinates intact until the viewer has applied coordinate
operation, model transformation, and false-origin matrices. The float transform
is the GPU-facing result for the default composition.

The georeferencing fields cache enough of the model's coordinate operation and
unit scale to load a sidecar without reparsing the IFC source solely to recover
map conversion state. If the source map conversion changes, the sidecar must be
deleted and rebuilt.

``SidecarChunk`` is 56 bytes and records one streamable range of meshes. Each
chunk maps to two compressed geometry frames in the geometry section:

.. list-table::
   :header-rows: 1

   * - Field
     - Meaning
   * - ``first_mesh``
     - First mesh index covered by the chunk.
   * - ``mesh_count``
     - Number of consecutive meshes covered by the chunk.
   * - ``v_comp_off`` / ``v_comp_size``
     - Byte offset and compressed byte size of the chunk's vertex frame, relative to the start of the geometry section.
   * - ``v_raw_size``
     - Decompressed byte size of the chunk's vertex data.
   * - ``i_comp_off`` / ``i_comp_size``
     - Byte offset and compressed byte size of the chunk's index frame, relative to the start of the geometry section.
   * - ``i_raw_size``
     - Decompressed byte size of the chunk's index data.

The chunk table is part of the geometry metadata because the viewer needs it
before it can request geometry. On the web path, the loader reads the header
and geometry metadata block, creates a model with non-resident chunks, and then
starts fetching visible chunk frames by byte range.

Element metadata block
-----------------------

The element metadata block stores non-geometric element lookup data used by UI
features such as picking, tree display, object labels, and search.

Its raw, decompressed order is:

.. code-block:: text

   vector<ElementTableRecord> elements
   uint32 string_table_bytes
   char[string_table_bytes] string_table

Each ``ElementTableRecord`` is a fixed-size 36-byte record:

.. code-block:: c

   struct ElementTableRecord {
       uint32 object_id;
       uint32 model_id;
       int32  ifc_id;
       uint32 guid_offset;
       uint32 guid_length;
       uint32 name_offset;
       uint32 name_length;
       uint32 type_offset;
       uint32 type_length;
   };

Strings are stored once in the string table and referenced by offset and
length.

Splitting this block from geometry metadata is important for first paint. A
large model can have substantial names, GlobalIds, and type strings. The web
viewer can show geometry after the geometry metadata block is available, then
fetch this metadata later when the UI needs it.

Chunk planning
--------------

Chunks are spatial groups of meshes. During sidecar creation, the builder:

1. Computes a centroid for each mesh from the average of its instance
   world-AABB centres.
2. Sorts mesh ids by a 3D Morton code, also known as Z-order.
3. Greedily packs the sorted meshes into 4 MiB vertex-byte chunks. A single
   mesh larger than that limit is kept whole in an oversized chunk. Meshes are
   not split.
4. Reorders meshes, vertices, indices, and instances so each chunk is a
   consecutive mesh range.
5. Writes these offsets into the ``SidecarChunk`` table so that loaders can
   directly jump to the compressed chunk as needed.

How the file is produced
------------------------

When no usable sidecar is available, the viewer falls back to the geometry
streamer. The streamer emits:

- ``StreamedMesh`` once for each unique representation mesh
- ``StreamedInstance`` for every placed occurrence of a mesh
- ``ElementInfo`` records for viewer metadata

The sidecar builder consumes those streams. Mesh chunks are converted from the
streamer transfer layout, which is seven floats per vertex
(``position.xyz``, ``normal.xyz``, packed colour), into the 12-byte quantised
vertex layout. Instance chunks become ``InstanceInfo`` records. Element info
records become ``ElementTableRecord`` plus string table entries.

At finalisation, the builder adds LOD1 index buffers where useful, caches
georeferencing state, lays out meshes in streaming chunk order, builds the chunk
table, and writes the file.

Binary conventions
------------------

The current writer uses these conventions:

- Multi-byte scalar values are written in native byte order and validated by
  the endian marker.
- Counted vectors are written as ``uint32 count`` followed by
  ``count * sizeof(T)`` bytes of raw table entries.
- Metadata blocks are zstd-compressed as complete raw metadata buffers.
- Geometry chunks store vertex bytes and index bytes as separate zstd frames.
- Offsets stored in the chunk table are relative to the start of the geometry
  section, not relative to the start of the file.
