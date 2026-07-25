# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import base64
from typing import Any

from ifcmcp.core import IfcSession

try:
    from mcp.server.fastmcp import FastMCP  # type: ignore
    from mcp.types import ImageContent  # type: ignore
except Exception:  # pragma: no cover
    FastMCP = None  # type: ignore
    ImageContent = None  # type: ignore


def build_server() -> Any:
    """Create the FastMCP server if the dependency is available."""
    if FastMCP is None:
        raise ImportError(
            "FastMCP is not installed. Install with: pip install ifcmcp[mcp] " "(or add 'mcp' to your environment)."
        )

    session = IfcSession()

    server = FastMCP(
        name="ifc-mcp",
        instructions=(
            "MCP server for querying and editing IFC building models. "
            "Load a file first with ifc_load, then use query/edit tools. "
            "Save changes with ifc_save."
        ),
    )

    # ---- Lifecycle ----
    @server.tool()
    def ifc_new(schema: str = "IFC4") -> dict[str, Any]:
        """Create a new empty IFC model in memory.

        Replaces the model currently held by the session, discarding any unsaved
        edits.  The new model has no file path of its own, so ``ifc_save`` must be
        given an explicit path.

        :param schema: IFC schema version — ``IFC2X3``, ``IFC4``, ``IFC4X1``,
            ``IFC4X2`` or ``IFC4X3`` — passed straight to
            ``ifcopenshell.file()`` (default ``IFC4``).  ``IFC4X3`` and
            ``IFC4X3_ADD2`` are both accepted and resolve to the same
            schema identifier, ``IFC4X3_ADD2``.
        """
        return session.ifc_new(schema=schema)

    @server.tool()
    def ifc_load(path: str) -> str:
        """Open an IFC file from disk into the session.

        Replaces the model currently held by the session, discarding any unsaved
        edits, and remembers the path so a later ``ifc_save`` can overwrite it.
        Call this before any query or edit tool.  Returns a confirmation string
        naming the schema version and entity count.

        :param path: Filesystem path of the IFC file to open.
        """
        return session.ifc_load(path)

    @server.tool()
    def ifc_save(path: str = "") -> str:
        """Write the in-memory model to disk.

        Overwrites the target file without further confirmation.  Edits made by
        ``ifc_edit``, ``ifc_shape`` and ``ifc_quantify`` exist only in memory
        until this is called.

        :param path: Destination path.  Omit to overwrite the file the model was
            loaded from; this fails for a model created by ``ifc_new``, which has
            no original path.
        """
        return session.ifc_save(path)

    @server.tool()
    def ifc_reset() -> dict[str, Any]:
        """Discard the in-memory model.

        Drops the model and its file path, throwing away any edits not already
        written with ``ifc_save``.  Succeeds even when no model is loaded.
        """
        return session.ifc_reset()

    # ---- Query ----
    @server.tool()
    def ifc_summary() -> dict[str, Any]:
        """Summarise the loaded model: schema, entity counts and project info.

        Returns the ``schema`` version, ``total_entities``, a ``types`` mapping of
        IFC class name to instance count in descending order, and a ``project``
        block with the id, name and description of the first ``IfcProject``.  The
        counts cover every entity in the file, not just physical elements.  This
        is usually the first tool to call after ``ifc_load``.
        """
        return session.ifc_summary()

    @server.tool()
    def ifc_tree() -> dict[str, Any] | list[dict[str, Any]]:
        """Return the spatial hierarchy of the model as a nested tree.

        Starts at ``IfcProject`` and descends through decomposition (site,
        building, storeys) and containment (the elements placed in each storey).
        Every node carries ``id``, ``type`` and ``name``; ``children`` holds
        decomposed sub-spaces and ``elements`` holds contained elements, and
        either key is omitted when empty.  Returns a list when the file contains
        several projects, or an ``error`` key when it contains none.
        """
        return session.ifc_tree()

    @server.tool()
    def ifc_info(element_id: int) -> dict[str, Any]:
        """Inspect a single entity in depth.

        Returns the entity's direct ``attributes`` plus, where present,
        ``property_sets``, ``element_type``, ``material``, ``container``,
        ``placement`` (a 4x4 transformation matrix) and ``geometry_summary``
        (profile dimensions, extrusion depth, face counts).  Keys are omitted
        when the information is unavailable.  Use ``ifc_select`` or ``ifc_tree``
        to find step IDs.

        :param element_id: Step ID of the entity to inspect.
        """
        return session.ifc_info(element_id)

    @server.tool()
    def ifc_select(query: str) -> list[dict[str, Any]]:
        """Find elements matching an ifcopenshell selector query.

        Returns one entry per match with ``id``, ``type``, ``repr`` and ``name``,
        ordered by step ID.  The step IDs returned are the input for
        ``ifc_info``, ``ifc_relations`` and ``ifc_clash``.

        :param query: ifcopenshell selector, for example ``'IfcWall'`` (all
            walls), ``'IfcWall, IfcColumn'`` (walls and columns), ``'! IfcWall'``
            (everything except walls), ``'IfcWall, Name = "My Wall"'``,
            ``'type = "Concrete Wall"'`` or ``'material = "Concrete"'``.
        """
        return session.ifc_select(query)

    @server.tool()
    def ifc_relations(element_id: int, traverse: str = "") -> dict[str, Any] | list[dict[str, Any]]:
        """Show how an element relates to the rest of the model.

        By default returns a dict whose optional blocks are ``hierarchy``
        (parent, container, aggregate, nest, filled void, voided element),
        ``children`` (contained, parts, components, openings),
        ``type_relationship``, ``groups``, ``systems``, ``zones``, ``material``,
        ``referenced_structures`` and ``connections`` (connected to/from, ports),
        plus a de-duplicated flat ``elements`` list of everything referenced.
        Blocks with nothing to report are omitted.

        :param element_id: Step ID of the element to examine.
        :param traverse: Set to ``'up'`` to instead return the chain of ancestors
            from the element to ``IfcProject`` as a flat list.  Any other value
            gives the default behaviour.
        """
        return session.ifc_relations(element_id, traverse=traverse)

    @server.tool()
    def ifc_clash(
        element_id: int,
        clearance: float = 0.0,
        tolerance: float = 0.002,
        scope: str = "storey",
    ) -> dict[str, Any]:
        """Check one element for geometric clashes against other elements.

        Reports hard intersections and, optionally, violations of a required
        clearance.  Returns the overall ``pass``, the ``scope`` actually used and
        a ``checks`` block in which each clash names the other ``element``, the
        clash ``type``, the ``distance`` and the two closest points ``p1`` and
        ``p2``.  Geometry is computed for every element in scope, so this is slow
        on large models; ``pass`` is null with an ``error`` when the element has
        no usable geometry.

        :param element_id: Step ID of the element to check.
        :param clearance: Required clearance in metres.  ``0.0`` (default) skips
            the clearance check and reports intersections only.
        :param tolerance: Intersection tolerance in metres (default ``0.002``).
        :param scope: ``storey`` (default) checks only elements sharing the same
            spatial container; ``all`` checks every ``IfcElement`` except feature
            elements such as openings.  ``storey`` falls back to ``all`` when the
            element has no spatial container.
        """
        return session.ifc_clash(
            element_id=element_id,
            clearance=clearance,
            tolerance=tolerance,
            scope=scope,
        )

    @server.tool()
    def ifc_contexts() -> list[dict[str, Any]]:
        """List the geometric representation contexts defined in the model.

        Returns every ``IfcGeometricRepresentationContext`` and subcontext with
        its ``id``, ``context_type`` and ``context_identifier``; subcontexts also
        carry ``target_view`` and ``parent_context_id``.  Use this to obtain the
        context step ID that geometry-creating ``ifc_edit`` calls require.
        """
        return session.ifc_contexts()

    @server.tool()
    def ifc_materials() -> list[dict[str, Any]]:
        """List the materials and material sets defined in the model.

        Returns a single list covering ``IfcMaterial`` (with its category),
        ``IfcMaterialLayerSet`` (each layer's name, thickness, material and
        ventilation flag), ``IfcMaterialConstituentSet`` (constituent names,
        materials and fractions) and ``IfcMaterialProfileSet`` (profile names and
        materials).  Every entry carries the step ID of the material entity.
        """
        return session.ifc_materials()

    # ---- Edit ----
    @server.tool()
    def ifc_list(module: str = "") -> list[dict]:
        """Discover the ifcopenshell.api functions available for editing.

        With no argument returns every API module with its description, function
        names and function count.  With a module name returns that module's
        functions, each with a one-line description and its parameters.  This is
        the starting point for ``ifc_docs`` and ``ifc_edit``; it inspects the
        installed ifcopenshell package and works without a model loaded.

        :param module: API module name, for example ``'root'``, ``'geometry'`` or
            ``'pset'``.  Omit to list all modules.
        """
        return session.ifc_list(module=module)

    @server.tool()
    def ifc_docs(function_path: str) -> dict:
        """Show the full documentation for one ifcopenshell.api function.

        Returns the summary and long description, every parameter with its type,
        default and description, and the return type.  Read this before calling
        ``ifc_edit`` so that parameter names and value types are correct.  Works
        without a model loaded.

        :param function_path: ``'module.function'``, for example
            ``'root.create_entity'``.
        """
        return session.ifc_docs(function_path=function_path)

    @server.tool()
    def ifc_edit(function_path: str, params: str = "{}") -> dict:
        """Run an ifcopenshell.api function to modify the model.

        This is the general-purpose edit tool; use ``ifc_list`` and ``ifc_docs``
        first to find the function and its parameters.  Changes are made to the
        in-memory model only, so ``ifc_save`` is needed to persist them.  Returns
        ``{"ok": True, "result": ...}``, or ``{"ok": False, "error": ...}`` when
        the function is unknown, a parameter cannot be converted, or the call
        raises.

        :param function_path: ``'module.function'``, for example
            ``'root.create_entity'``.
        :param params: JSON object of keyword arguments.  Pass entity references
            as integer step IDs, and arguments typed as an IFC file as a file
            path string.
        """
        return session.ifc_edit(function_path=function_path, params=params)

    # ---- Extended query + edit ----
    @server.tool()
    def ifc_validate(express_rules: bool = False) -> dict[str, Any]:
        """Validate the loaded model against the IFC schema.

        Returns ``valid`` together with a list of ``issues``, each carrying a
        ``level`` and a ``message``.  Worth running after a batch of ``ifc_edit``
        calls and before ``ifc_save``.

        :param express_rules: Also evaluate the schema's EXPRESS rules.  Catches
            more problems but is considerably slower (default ``False``).
        """
        return session.ifc_validate(express_rules=express_rules)

    @server.tool()
    def ifc_schedule(max_depth: int | None = None) -> list[dict[str, Any]]:
        """List the construction programme: work schedules and their task trees.

        Covers ``IfcWorkSchedule`` only — this is the time dimension of the
        model.  Use ``ifc_cost`` for cost schedules and ``ifc_quantify`` to
        compute element quantities.  Each schedule lists its tasks recursively,
        and each task carries its scheduled ``start`` and ``finish``, an
        ``is_milestone`` flag, the products it ``outputs`` and its ``subtasks``.
        Returns an empty list when the model has no work schedules.

        :param max_depth: Levels of subtask nesting to expand, counting root
            tasks as level 1.  Past the cutoff ``subtasks`` is replaced by a
            ``truncated`` marker with the number of tasks not expanded.  Omit for
            unlimited depth.
        """
        return session.ifc_schedule(max_depth=max_depth)

    @server.tool()
    def ifc_cost(max_depth: int | None = None) -> list[dict[str, Any]]:
        """List the cost schedules: bills of quantities and their cost items.

        Covers ``IfcCostSchedule`` only — this is the money dimension of the
        model.  Use ``ifc_schedule`` for the construction programme and
        ``ifc_quantify`` to compute element quantities.  Each cost item reports
        its cost ``values`` as ``formula`` label and ``category`` pairs, together
        with its nested ``subitems``.  Returns an empty list when the model has
        no cost schedules.

        :param max_depth: Levels of cost item nesting to expand, counting root
            items as level 1.  Past the cutoff ``subitems`` is replaced by a
            ``truncated`` marker with the number of items not expanded.  Omit for
            unlimited depth.
        """
        return session.ifc_cost(max_depth=max_depth)

    @server.tool()
    def ifc_schema(entity_type: str) -> dict[str, Any]:
        """Look up the IFC documentation for an entity class.

        Returns the class ``description``, its ``predefined_types``, per-attribute
        documentation and a ``spec_url``, resolved against the schema version of
        the loaded model — so a model must be loaded first.  Returns an ``error``
        key for an unknown class.  Use this to learn what an entity means, and
        ``ifc_docs`` to learn how to create one.

        :param entity_type: IFC class name, for example ``'IfcWall'``.
        """
        return session.ifc_schema(entity_type=entity_type)

    @server.tool()
    def ifc_quantify(rule: str, selector: str = "") -> dict[str, Any]:
        """Compute base quantities for elements and write them into the model.

        This is a write operation: it derives lengths, areas and volumes from
        element geometry and adds or updates their ``IfcElementQuantity`` sets,
        so ``ifc_save`` is needed to persist the result.  It does not report a
        schedule — use ``ifc_schedule`` for the construction programme and
        ``ifc_cost`` for cost schedules.  An unrecognised ``rule`` is reported as
        an error listing the rules that are available.

        :param rule: Quantity take-off rule set, for example
            ``'IFC4QtoBaseQuantities'`` or ``'IFC4X3QtoBaseQuantities'``.
        :param selector: ifcopenshell selector restricting which elements are
            measured, e.g. ``'IfcWall'``.  Omit to measure every ``IfcElement``
            and ``IfcSpace``.
        """
        return session.ifc_quantify(rule=rule, selector=selector)

    # ---- Shape builder ----
    @server.tool()
    def ifc_shape_list() -> list[dict]:
        """List the ShapeBuilder methods available for constructing geometry.

        Returns every public ``ifcopenshell.util.shape_builder.ShapeBuilder``
        method with a one-line description and its parameter names.  Use it to
        find a method, then ``ifc_shape_docs`` for the details and ``ifc_shape``
        to call it.  Works without a model loaded.
        """
        return session.ifc_shape_list()

    @server.tool()
    def ifc_shape_docs(method: str) -> dict:
        """Show the full documentation for one ShapeBuilder method.

        Returns the summary and long description, every parameter with its type
        and default, and the return type.  Read this before ``ifc_shape`` so that
        argument names and value shapes are correct.  Works without a model
        loaded.

        :param method: ShapeBuilder method name, for example ``'polyline'``,
            ``'rectangle'`` or ``'extrude'``.
        """
        return session.ifc_shape_docs(method=method)

    @server.tool()
    def ifc_shape(method: str, params: str = "{}") -> dict:
        """Call a ShapeBuilder method to build geometry in the model.

        The created entities are added to the in-memory model, so ``ifc_save`` is
        needed to persist them.  On success the result identifies the created
        entity by step ID and type; an unknown method or a failed call is
        reported as an error instead.  Keyword arguments the method does not
        accept are silently ignored.

        :param method: ShapeBuilder method name, as listed by ``ifc_shape_list``.
        :param params: JSON object of keyword arguments.  Pass entity references
            as integer step IDs and vectors as JSON arrays, e.g.
            ``[1.0, 0.0, 0.0]``.
        """
        return session.ifc_shape(method=method, params=params)

    @server.tool(structured_output=False)
    def ifc_plot(
        selector: str = "",
        element_ids: list[int] | None = None,
        view: str = "floorplan",
        width_mm: float = 297.0,
        height_mm: float = 420.0,
        scale: float = 1.0 / 100.0,
        png_width: int = 1024,
        png_height: int = 1024,
        output_path: str = "",
    ) -> list[ImageContent]:
        """Generate a 2D technical drawing of the loaded IFC model.

        Returns an inline PNG image (floor plan, elevation, or section) that the
        LLM can inspect to understand the 2D layout of the model.  If
        ``output_path`` is provided the drawing is also saved to disk — as SVG
        when the path ends in ``.svg``, otherwise as PNG.

        :param selector: ifcopenshell selector to restrict plotted elements
            (e.g. ``'IfcWall'``). Omit to plot the whole model.
        :param element_ids: Step IDs of elements to highlight. Other elements
            are faded so the subject stands out.
        :param view: Drawing view — ``floorplan`` (default), ``elevation``,
            ``section``, or ``auto``.
        :param width_mm: Paper width in mm (default 297 = A4 landscape width).
        :param height_mm: Paper height in mm (default 420 = A4 landscape height).
        :param scale: Model-to-paper scale ratio (default 0.01 = 1:100).
        :param png_width: Raster output width in pixels (default 1024).
        :param png_height: Raster output height in pixels (default 1024).
        :param output_path: Optional file path to save the drawing to disk.
        """
        png_bytes = session.ifc_plot(
            selector=selector,
            element_ids=element_ids,
            view=view,
            width_mm=width_mm,
            height_mm=height_mm,
            scale=scale,
            png_width=png_width,
            png_height=png_height,
            output_format="png",
        )
        if output_path:
            if output_path.endswith(".svg"):
                svg_bytes = session.ifc_plot(
                    selector=selector,
                    element_ids=element_ids,
                    view=view,
                    width_mm=width_mm,
                    height_mm=height_mm,
                    scale=scale,
                    output_format="svg",
                )
                with open(output_path, "wb") as f:
                    f.write(svg_bytes)
            else:
                with open(output_path, "wb") as f:
                    f.write(png_bytes)
        return [ImageContent(type="image", data=base64.b64encode(png_bytes).decode(), mimeType="image/png")]

    @server.tool(structured_output=False)
    def ifc_render(
        selector: str = "",
        element_ids: list[int] | None = None,
        view: str = "iso",
        output_path: str = "",
    ) -> list[ImageContent]:
        """Render the loaded IFC model to a PNG image.

        Returns an inline image the LLM can inspect to understand the spatial
        layout of the model or a specific element in context.  If
        ``output_path`` is provided the PNG is also saved to that file path.

        :param selector: ifcopenshell selector to restrict rendered elements
            (e.g. ``'IfcWall'``, ``'IfcBuildingStorey[Name="0"]'``).
            Omit to render the whole model.
        :param element_ids: Step IDs of elements to highlight. Other elements
            are rendered in translucent grey so the subject stands out.
        :param view: Camera angle — ``iso`` (default), ``top``, ``south``,
            ``north``, ``east``, or ``west``.
        :param output_path: Optional file path to save the PNG to disk.
        """
        png_bytes = session.ifc_render(selector=selector, element_ids=element_ids, view=view)
        if output_path:
            with open(output_path, "wb") as f:
                f.write(png_bytes)
        return [ImageContent(type="image", data=base64.b64encode(png_bytes).decode(), mimeType="image/png")]

    return server
