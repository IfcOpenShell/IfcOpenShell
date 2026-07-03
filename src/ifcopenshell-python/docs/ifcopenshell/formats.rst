Formats
=======

IfcOpenShell supports several output formats, but they are not all meant
for the same job. Some are exchange formats for geometry, some are caches, and
some are specialised representations for downstream processing.

Summary
-------

There are two types of formats:

- lossless formats, where the goal is to preserve the IFC model itself so it
  can be read again without intentionally discarding semantic information. This
  is by design: IFC is a data standard that lets you choose the storage format
  you prefer.
- lossy formats, where the goal is to convert the model into another
  representation optimised for a different task, such as geometry caching,
  lazy access, or linked-data publishing.

It is possible to mix and match formats to choose the best tool for the job.

The ``.ifc`` format is known as the IFC-SPF (Step Physical File) format, and is
typically considered to be the baseline exchange format for IFC. It is a
plaintext file and can be read by all IFC tools.

.. warning::

    The pros and cons of formats are nuanced and the information on this page are just generalisations and may not always apply. For example, the size multiplier may vary significantly. If unsure, always test on your own datasets.

Lossless formats
^^^^^^^^^^^^^^^^

.. csv-table::
   :header: "Format", "Size", "Stores", "Strengths", "Trade-offs"

   "``.ifc`` / IFC-SPF", "1x (baseline)", "Lossless IFC model in STEP Physical File form", "Portable, standard, tool-friendly, the default reference format", "Large files can be slow to load and expensive to query repeatedly"
   "``.rdb`` / RocksDB", "0.4x (or 0.1x excluding geometry)", "Lossless or lossy (configurable) IFC model data in an IfcOpenShell-specific key-value encoding", "Supports partial reads and lazy streaming access to IFC data, good for memory-sensitive workflows for large datasets", "IfcOpenShell-specific and not a general interchange format"
   "``.ifcxml`` / IFCXML", "1.2x", "Everything in XML", "Increased readability and vast tool ecosystem for generically working with XML", "No longer supported and behaviour undefined"
   "``.ifcjson`` / IFCJSON", "1.5x", "Everything in JSON", "Increased readability and vast tool ecosystem for generically working with JSON", "Lack of industry support and authoring integration"
   "``.ifczip`` / IFCZIP", "0.2x", "ZIP compressed IFC data", "Decreased filesize for file transfer", "Overhead of compression and extraction"

Lossy formats
^^^^^^^^^^^^^

.. csv-table::
   :header: "Format", "Size", "Stores", "Strengths", "Trade-offs"

   "``.ifcview``", "0.5x", "Bonsai Viewer geometry, instances, bounds, and compact element metadata", "Very fast geometry loading, tuned for rendering rather than re-interpretation", "Viewer-specific, manually invalidated, and not intended as a general interchange format"
   "``.rdbview``", "varies", "ZIP package containing ``.ifcview`` render data and a lossy ``.rdb`` model without ``IfcRepresentationItem`` data", "Single-file Bonsai Viewer package with fast rendering and lazy semantic access", "IfcOpenShell-specific, lossy, and not intended as a general interchange or authoring format"
   "``.ttl`` / TTL-WKT", "10x", "RDF Turtle triples with WKT geometry literals and simple feature metadata", "Easy to integrate with linked data and geospatial tooling", "Geometry-focused export rather than full IFC authoring semantics"


How to choose
-------------

Use ``.ifc`` when you want the canonical, portable representation of the model.
Treat it as the benchmark that the other formats are compared against.

Choose ``.ifcview`` if your main problem is reopening the same model quickly in
the Bonsai Viewer. It is a viewer-oriented sidecar cache that
stores render-ready mesh, instance, and metadata structures so the viewer can
skip most of its geometry preparation work.

Choose ``.rdbview`` if you want a single file for the Bonsai Viewer. It
packages an ``.ifcview`` cache together with a compact, lossy
RocksDB model, so the viewer can load geometry quickly while still resolving
non-geometric IFC data lazily.

Choose ``.rdb`` if your main problem is the size of the IFC model itself and
you want more memory-efficient access to IFC data. It is always smaller than
IFC-SPF and has instant opens, and is a drop-in replacement for IFC-SPF.
RocksDB is a model-oriented storage format. The only downside is that it is not
internationally standardised.

Choose ``.ttl`` if you want to publish or analyse geometry in RDF semantic web
or GIS-style spatial querying systems, especially where WKT and GeoSPARQL-style
patterns are expected.

IFC-SPF
-------

IFC-SPF is the standard STEP Physical File representation of IFC. It is a plain
text ``.ifc`` file and is the baseline format that the others on this page are
best compared against. It's best used for:

- Exchanging IFC models between BIM tools
- Archiving a full IFC model in a broadly understood form
- Keeping the canonical source model alongside derived caches or exports

IFCVIEW
-------

``.ifcview`` is a binary sidecar cache used by the Bonsai Viewer. It stores
prepared render data such as quantised vertex and index buffers, per-instance
placements, world-space bounds, compact element lookup data, and enough
georeferencing state to reopen the cache consistently.

Use it when the goal is to reopen the same model quickly in Bonsai Viewer
without repeating tessellation, packing, quantisation, and instance rebuilds.
It is not a general interchange format or a full semantic storage backend. For
model data, pair it with the original IFC file or with RocksDB.

.. toctree::
   :maxdepth: 1

   ifcview_format

RDBVIEW
-------

``.rdbview`` is a ZIP package used by the Bonsai Viewer. It combines the two
viewer-oriented outputs that are otherwise commonly kept next to each other:

- an ``.ifcview`` file for prepared render data
- a lossy ``.rdb`` database for IFC model data, excluding
  ``IfcRepresentationItem`` entities

The ``.ifcview`` member stores the geometry and viewer runtime data. The
``.rdb`` member stores the remaining model data in a compact RocksDB form so
the viewer can resolve entities, attributes, relationships, and properties
without keeping the full source IFC file alongside the cache.

Use it when you want a single viewer-ready file for Bonsai Viewer instead of
separate sidecar files. It is lossy, Bonsai Viewer-specific, and not intended
as a general interchange, editing, or standards-based archival format.

RocksDB
-------

RocksDB is an embedded key-value database. In IfcOpenShell, ``.rdb`` output is
typically a directory containing database files rather than a single plain text
document.

RocksDB output stores IFC model data in an IfcOpenShell-specific embedded
key-value store. Unlike HDF5, it is centered on the IFC model itself rather
than on precomputed geometry output.

RocksDB stores IFC data in a form suitable for IfcOpenShell to resolve entities,
attributes, and references on demand. In practice, this makes it better suited
to semantic and structural access than geometry caching. Use it for very large
IFC files, memory-sensitive workflows, or pipelines that need fast access to
IFC entities without keeping the whole model resident in memory. It is specific
to IfcOpenShell workflows, is not a general exchange format for other tools,
and by itself is not a geometry publication format.

TTL/WKT
-------

TTL is Turtle, a plain text RDF format. WKT is Well-Known Text, a plain
text geometry representation widely used in GIS. In IfcOpenShell, ``.ttl``
output is a text file containing RDF triples whose geometry is written as WKT
literals.

TTL output writes RDF Turtle with geometry expressed as WKT literals. In
IfcConvert this appears as ``.ttl`` output and is intended for linked-data and
geospatial workflows rather than CAD-style interchange.

IfcOpenShell's TTL output writes ``geo:Feature`` and ``geo:Geometry``
resources, ``geo:asWKT`` geometry literals, and identifiers and labels for
exported elements. Depending on the mode, the WKT geometry may be 3D
polyhedral surfaces, 2D or 3D linework, or section or footprint-like polygonal
output.

Use ``.ttl`` when your downstream stack is RDF, linked data, or
GeoSPARQL-oriented, and you want geometry in a spatially interoperable text
form. It is not "IFC as RDF"; it is a geometry-led RDF export. WKT is convenient
for interoperability, but it is a simplification compared with the full IFC
geometric model, so this format is best for publishing, querying, and
integration rather than round-tripping IFC authoring data.

Comparison with other formats
-----------------------------

Fragments (That Open Company), and XKT (Xeokit), are best understood as 
binary viewing formats. They are designed to load large BIM models quickly in a
viewer. Both are similar to IFCVIEW, because they are derived, lossy formats.
Fragments, XKT, and IFCVIEW do not preserve the full IFC (as opposed to RDB).
Like all the formats listed here, they are all bespoke and not internationally
standarised interchange formats.

- IFCVIEW and XKT is more aggressively optimised to a particular in-memory and
  GPU-facing data layout. Fragments uses a language neutral specification via
  Flatbuffers. If you want more flexibility, choose Fragments. If you want
  optimisation for loading and rendering, choose IFCVIEW or XKT.
- IFCVIEW is optimised to only store geometry and related viewing data (spatial
  trees, bounding boxes, instancing, georeferencing), and needs to be paired
  with another format for data (such as RDB for lossless data). XKT
  additionally can package properties, and Fragments can package both
  properties and relationships. If you want a single bundle, choose Fragments
  or XKT. If you want flexibility around data storage, or lossless data
  storage, you can use any format, and we recommend combining it with RDB (or
  SQL, JSON, XML, etc).
- Fragments and XKT has an ecosystem of tooling built for the web. IFCVIEW does not
  (yet) have this and so is not yet web-ready. If you are building web apps,
  choose Fragments or XKT.
- XKT has a much richer geometry description including textures, skyboxes,
  spheremaps, etc. If you need this, choose XKT.


Also note that IfcOpenShell historically supported HDF5 as both a `lossless IFC
storage format
<https://pure.tue.nl/ws/portalfiles/portal/28331562/icccbe_hdf5_krijnen_beetz.pdf>`_
(to ISO 10303-26) and a lossy geometry cache (for OCC BReps or triangles). This
did not deliver enough technical advantages to continue maintaining and has
been removed.
