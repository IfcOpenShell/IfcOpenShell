# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

"""Render-only exposure/gamma override for IFC elements selected by a filter query.

Blender's ``view_settings.exposure`` and ``view_settings.gamma`` are global
colour-management settings and cannot be assigned per object. This module
reproduces the effect for a subset of elements (selected via the shared Search
filter system, e.g. ``EPset_Status.Status=EXISTING``) using a Cryptomatte object
mask plus a small compositor graph, so the override only shows up in the final
render and the viewport is untouched.

Cryptomatte (not the Object Index pass) is used because EEVEE Next always renders
the Object Index pass as 0 (Blender bug #121690); Cryptomatte works in both EEVEE
and Cycles.
"""

import bpy
from bpy.app.handlers import persistent
import json
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.selector
import bonsai.tool as tool

# Marker stored on every node we create so re-running can clean up its own work
# without touching the user's other compositor nodes.
MARKER = "bim_status_render_override"

# TEMP DEBUG: tracing why the live transparency is not re-applied after a
# representation reload (profile edit round trip). Set False to silence.
DEBUG = True


def _dbg(message):
    if DEBUG:
        print(f"[transp-debug] {message}")


def _brief(names, limit=3):
    """Format a name list for logging without dumping thousands of entries."""
    names = list(names)
    head = ', '.join(str(n) for n in names[:limit])
    extra = len(names) - limit
    return f"[{head}{f', +{extra} more' if extra > 0 else ''}] ({len(names)})"


def get_filtered_elements(filter_groups):
    """Resolve a rule's filter groups to a set of IFC elements.

    Mirrors bim.search so behaviour matches the shared filter UI under both the
    legacy query and the set-operations preference.
    """
    ifc = tool.Ifc.get()
    if not ifc or not len(filter_groups):
        return set()

    if tool.Blender.get_addon_preferences().chain_filter_with_set_operations:
        # Migrate old "!" prefix filters to the filter_mode system, as bim.search does.
        for filter_group in filter_groups:
            for ifc_filter in filter_group.filters:
                if ifc_filter.type in ("entity", "instance") and ifc_filter.value.startswith("!"):
                    ifc_filter.value = ifc_filter.value[1:]
                    ifc_filter.filter_mode = "SUBTRACT"
        return tool.Search.execute_filter_groups(filter_groups)

    query = tool.Search.export_filter_query(filter_groups)
    if not query:
        return set()
    return ifcopenshell.util.selector.filter_elements(ifc, query)


def get_rule_objects(rule):
    """Return the Blender mesh objects for the IFC elements a rule's filter matches."""
    return [
        obj
        for element in get_filtered_elements(rule.filter_groups)
        if isinstance(obj := tool.Ifc.get_object(element), bpy.types.Object) and obj.type == "MESH"
    ]


def clear_marked_nodes(tree):
    for node in list(tree.nodes):
        if node.get(MARKER):
            tree.nodes.remove(node)


def get_or_create(tree, bl_idname):
    """Reuse an existing user node of this type, or create a fresh one."""
    for node in tree.nodes:
        if node.bl_idname == bl_idname and not node.get(MARKER):
            return node
    return tree.nodes.new(bl_idname)


# --- Blender 5 compositor compatibility ------------------------------------
# Blender 5.0 reworked the compositor and broke every API this module used:
#   * the scene's embedded node tree became a standalone CompositorNodeTree ID
#     (``scene.compositing_node_group``); ``scene.node_tree`` is gone and
#     ``scene.use_nodes`` is a deprecated no-op,
#   * the Composite output node was replaced by the node group's output,
#   * Gamma and MixRGB moved to the unified shader node types.
# Render Layers, Exposure and Cryptomatte are unchanged. Everything below funnels
# through these helpers so the graph-building code stays version agnostic.


def find_socket(sockets, identifier):
    """Look a socket up by ``identifier`` -- socket collections key by identifier, and
    the unified 5.x nodes carry several same-named sockets (one per data type)."""
    return next(socket for socket in sockets if socket.identifier == identifier)


def get_compositor_tree(scene, create=False):
    """Return the scene's compositor node tree, optionally creating it. None if absent."""
    if tool.Blender.BLENDER_5:
        tree = scene.compositing_node_group
        if tree is None and create:
            tree = bpy.data.node_groups.new("Compositor Nodes", "CompositorNodeTree")
            tree[MARKER] = True  # ours -- torn down again in clear_compositor
            scene.compositing_node_group = tree
        return tree
    if create:
        scene.use_nodes = True
    return scene.node_tree if scene.use_nodes else None


def get_output_socket(tree, create=False):
    """Return the socket that receives the tree's final image, or None.

    Pre-5.0 that is the Composite node's Image input; from 5.0 it is the first input
    of the group output node, backed by an interface socket.
    """
    if not tool.Blender.BLENDER_5:
        composite = next((n for n in tree.nodes if n.bl_idname == "CompositorNodeComposite"), None)
        if composite is None:
            if not create:
                return None
            composite = tree.nodes.new("CompositorNodeComposite")
        return composite.inputs["Image"]
    output = next((n for n in tree.nodes if n.bl_idname == "NodeGroupOutput"), None)
    if output is None:
        if not create:
            return None
        output = tree.nodes.new("NodeGroupOutput")
    if not any(i.item_type == "SOCKET" and i.in_out == "OUTPUT" for i in tree.interface.items_tree):
        if not create:
            return None
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    return output.inputs[0]  # the trailing "__extend__" virtual socket is always last


def add_gamma_node(tree, gamma):
    """Create a Gamma node and return ``(node, image_in, image_out)``.

    ShaderNodeGamma names its image sockets "Color", so they are addressed positionally.
    """
    node = tree.nodes.new("ShaderNodeGamma" if tool.Blender.BLENDER_5 else "CompositorNodeGamma")
    node.inputs["Gamma"].default_value = gamma
    return node, node.inputs[0], node.outputs[0]


def add_mix_node(tree):
    """Create a colour Mix node and return ``(node, fac_in, a_in, b_in, result_out)``."""
    if tool.Blender.BLENDER_5:
        node = tree.nodes.new("ShaderNodeMix")
        node.data_type = "RGBA"
        node.blend_type = "MIX"
        return (
            node,
            find_socket(node.inputs, "Factor_Float"),
            find_socket(node.inputs, "A_Color"),
            find_socket(node.inputs, "B_Color"),
            find_socket(node.outputs, "Result_Color"),
        )
    node = tree.nodes.new("CompositorNodeMixRGB")
    node.blend_type = "MIX"
    return node, node.inputs[0], node.inputs[1], node.inputs[2], node.outputs[0]


# Transparency is a real material effect (so geometry behind shows through), applied
# before the render and restored after. These hold the swap state between the render
# handlers. Only one render runs at a time, so module-level state is safe.
_transparency_restore = []  # (object, slot_index, original_material, temp_material, amount)
_temp_material_cache = {}  # (source material name, amount) -> shared temp material
_tracked_objects = set()  # names the rules WANT transparent, for depsgraph filtering

# Recorded on each temp material so an orphan (one left on a mesh rebuilt behind our
# back) can still be traced to what it replaced.
SOURCE_KEY = "bim_status_render_source"


def make_transparent_material(material, amount):
    """Copy a material and mix a Transparent BSDF into its surface by ``amount``."""
    dup = material.copy()
    dup[MARKER] = True
    dup[SOURCE_KEY] = material.name
    tool.Style.set_use_nodes(dup, True)  # deprecated no-op on Blender 5+, where it is always on
    tree = dup.node_tree
    output = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None)
    output = output or next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if output and output.inputs["Surface"].links:
        surface = output.inputs["Surface"].links[0].from_socket
        transparent = tree.nodes.new("ShaderNodeBsdfTransparent")
        mix = tree.nodes.new("ShaderNodeMixShader")
        mix.inputs["Fac"].default_value = amount  # 0 = opaque, 1 = fully transparent
        tree.links.new(surface, mix.inputs[1])
        tree.links.new(transparent.outputs[0], mix.inputs[2])
        tree.links.new(mix.outputs[0], output.inputs["Surface"])
    # Enable real alpha blending (EEVEE Next; fall back to the legacy property name).
    if hasattr(dup, "surface_render_method"):
        dup.surface_render_method = "BLENDED"
    elif hasattr(dup, "blend_method"):
        dup.blend_method = "BLEND"
    return dup


def get_temp_material(material, amount):
    """A transparent copy of ``material``, shared by every slot that needs it.

    Copying per slot meant one material datablock -- and one node tree -- per
    occurrence, so thousands on a real model. Keyed by source material and amount
    instead, which is a handful. Sharing stays safe for user_remap because every user
    of a given temp material had the same original.
    """
    key = (material.name, round(amount, 4))
    temp = _temp_material_cache.get(key)
    if temp is not None:
        try:
            temp.name  # liveness probe; raises if it was deleted behind our back
            return temp
        except ReferenceError:
            pass
    temp = make_transparent_material(material, amount)
    _temp_material_cache[key] = temp
    return temp


def release_unused_temp_materials():
    """Drop cached temp materials nothing references any more."""
    in_use = {entry[3] for entry in _transparency_restore}
    for key, temp in list(_temp_material_cache.items()):
        try:
            if temp in in_use or temp.users:
                continue
            bpy.data.materials.remove(temp)
        except (ReferenceError, RuntimeError):
            pass
        _temp_material_cache.pop(key, None)


def restore_transparency():
    """Put every original material back and drop the temporary copies.

    Full teardown, for saving and for switching the override off. sync_live_effects
    does the incremental version.
    """
    for obj, index, material, temp, _amount in _transparency_restore:
        try:
            slot = obj.material_slots[index]
            if slot.material is temp:
                slot.material = material
        except (IndexError, ReferenceError):
            pass
    _transparency_restore.clear()
    _tracked_objects.clear()
    for temp in list(_temp_material_cache.values()):
        try:
            # Anything still pointing at a temp material must be remapped back before
            # deletion -- a representation reload can carry one onto the rebuilt mesh,
            # or onto a replacement object our (obj, index) no longer names.
            # bpy.data.materials.remove unlinks from every user, so without this it
            # leaves those slots EMPTY and the element ends up with no material.
            if temp.users:
                source = bpy.data.materials.get(temp.get(SOURCE_KEY, "") or "")
                if source is not None:
                    temp.user_remap(source)
            if not temp.users:
                bpy.data.materials.remove(temp)
        except (ReferenceError, RuntimeError, AttributeError) as e:
            _dbg(f"temp material cleanup failed: {type(e).__name__}: {e}")
    _temp_material_cache.clear()


def live_state_is_stale(names=None):
    """True if the live state no longer matches what the rules ask for.

    ``names`` limits the check to the objects a depsgraph update actually touched --
    walking every swapped slot on every update is wasted work when thousands match.
    """
    applied = set()
    for obj, index, _original, temp, _amount in _transparency_restore:
        try:
            name = obj.name
            applied.add(name)
            if names is not None and name not in names:
                continue
            if obj.material_slots[index].material is not temp:
                return True
        except (IndexError, ReferenceError):
            return True
    # A wanted object carrying none of our materials is stale too -- its mesh may have
    # just been rebuilt. Objects with nothing swappable (no slots, or only empty ones)
    # deliberately do NOT count, or they would request a resync forever.
    for name in names or ():
        if name in applied:
            continue
        obj = bpy.data.objects.get(name)
        if obj is None:
            continue
        try:
            for slot in obj.material_slots:
                if slot.material is not None and not slot.material.get(MARKER):
                    return True
        except ReferenceError:
            continue
    return False


def build_color_rule(tree, scene, view_layer, rule, objects, input_socket, x, y):
    """Append one rule's exposure/gamma sub-graph to the compositor chain.

    Applies the colour effects to ``input_socket`` only where the rule's Cryptomatte
    matte covers, and returns ``(output_image_socket, matte_socket)``.
    """
    links = tree.links

    def node(bl_idname, loc):
        n = tree.nodes.new(bl_idname)
        n[MARKER] = True
        n.location = loc
        return n

    crypto = node("CompositorNodeCryptomatteV2", (x, y - 320))
    crypto.label = f"Matte: {rule.name}"
    crypto.source = "RENDER"
    crypto.scene = scene
    try:
        crypto.layer_name = f"{view_layer.name}.CryptoObject"
    except TypeError:
        pass  # Keep the node's default layer; the enum item isn't available yet.
    crypto.matte_id = ", ".join(obj.name for obj in objects)
    links.new(input_socket, crypto.inputs["Image"])
    matte = crypto.outputs["Matte"]

    exposure = node("CompositorNodeExposure", (x, y))
    exposure.label = f"Exposure: {rule.name}"
    exposure.inputs["Exposure"].default_value = rule.exposure
    links.new(input_socket, exposure.inputs["Image"])

    gamma, gamma_in, gamma_out = add_gamma_node(tree, rule.gamma)
    gamma[MARKER] = True
    gamma.location = (x + 180, y)
    gamma.label = f"Gamma: {rule.name}"
    links.new(exposure.outputs["Image"], gamma_in)

    mix, fac_in, base_in, effect_in, mix_out = add_mix_node(tree)
    mix[MARKER] = True
    mix.location = (x + 360, y)
    mix.label = f"Apply: {rule.name}"
    links.new(matte, fac_in)
    links.new(input_socket, base_in)
    links.new(gamma_out, effect_in)
    return mix_out, matte


def build_compositor(scene, props):
    """Build the compositor (exposure/gamma) chain for a render.

    Transparency is NOT handled here -- it is a live material effect managed by
    sync_live_effects so it also shows in the viewport. This only adds the colour
    nodes layered per rule.
    """
    tree = get_compositor_tree(scene, create=True)
    # The node tree is only applied to renders when compositing is enabled.
    scene.render.use_compositing = True
    clear_marked_nodes(tree)

    render_layers = get_or_create(tree, "CompositorNodeRLayers")
    if render_layers.scene is None:
        # A 5.x compositing group is a standalone ID, so a fresh Render Layers node in
        # one isn't implicitly bound to the scene we are rendering.
        render_layers.scene = scene
    output_socket = get_output_socket(tree, create=True)
    view_layer = scene.view_layers.get(render_layers.layer) or scene.view_layers[0]

    current = render_layers.outputs["Image"]
    x = render_layers.location.x + 320
    y = render_layers.location.y
    for rule in props.rules:
        objects = get_rule_objects(rule)
        if not objects:
            continue

        # Exposure/gamma stay in the compositor, masked by Cryptomatte. Only build the
        # sub-graph when there is a colour change to make.
        if rule.exposure != 0.0 or rule.gamma != 1.0:
            # Cryptomatte reads object IDs from the render's CryptoObject passes, so the
            # pass must be enabled on the view layer the node samples.
            view_layer.use_pass_cryptomatte_object = True
            current, _ = build_color_rule(tree, scene, view_layer, rule, objects, current, x, y)
            x += 700

    output_socket.node.location = (x, y)
    tree.links.new(current, output_socket)


def get_camera_override_props(camera):
    """Per-drawing override props live on the camera datablock; None if not a camera."""
    if camera and camera.type == "CAMERA":
        return camera.data.BIMRenderOverrideProperties
    return None


# --- IFC persistence -------------------------------------------------------
# The camera props are the working/edit copy; the rules are mirrored into the IFC
# model at EPset_Drawing.RenderOverrides (JSON) so they travel with the drawing.
# Coarse auto-sync: written on add/remove and on save, read on file load. Each
# rule's filter reuses the same query serialization as the drawing Include/Exclude
# filters (tool.Search.export/import_filter_query).

PSET_PROP = "RenderOverrides"


def serialize_rules(props):
    return [
        {
            "name": rule.name,
            "query": tool.Search.export_filter_query(rule.filter_groups),
            "exposure": round(rule.exposure, 6),
            "gamma": round(rule.gamma, 6),
            "transparency": round(rule.transparency, 6),
        }
        for rule in props.rules
    ]


def deserialize_rules(props, data):
    props.rules.clear()
    for entry in data:
        rule = props.rules.add()
        rule.name = entry.get("name", "Rule")
        # Direct id-property writes bypass the update callback so we don't trigger a
        # live re-sync for every rule mid-load (the caller syncs once at the end).
        rule["exposure"] = float(entry.get("exposure", 0.0))
        rule["gamma"] = float(entry.get("gamma", 1.0))
        rule["transparency"] = float(entry.get("transparency", 0.0))
        if query := (entry.get("query") or ""):
            try:
                tool.Search.import_filter_query(query, rule.filter_groups)
            except Exception:
                pass  # Tolerate an unparseable stored query rather than failing the load.
    props.active_rule_index = min(props.active_rule_index, max(len(props.rules) - 1, 0))


def save_rules_to_ifc(camera):
    """Mirror a drawing camera's rules into EPset_Drawing.RenderOverrides."""
    drawing = tool.Ifc.get_entity(camera)
    props = get_camera_override_props(camera)
    if not drawing or props is None:
        return
    data = serialize_rules(props)
    existing = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", PSET_PROP)
    if not data and existing is None:
        return  # Nothing to store and nothing stored -- don't dirty unconfigured drawings.
    pset = tool.Pset.get_element_pset(drawing, "EPset_Drawing")
    if pset is None:
        return
    ifcopenshell.api.pset.edit_pset(
        tool.Ifc.get(), pset=pset, properties={PSET_PROP: json.dumps(data) if data else None}
    )


def load_rules_from_ifc(camera):
    """Populate a drawing camera's rules from EPset_Drawing.RenderOverrides."""
    drawing = tool.Ifc.get_entity(camera)
    props = get_camera_override_props(camera)
    if not drawing or props is None:
        return
    raw = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", PSET_PROP)
    if not raw:
        return
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return
    deserialize_rules(props, data)


def ensure_rules_loaded(camera):
    """Load rules from IFC only when the camera props are empty (i.e. freshly imported).

    The empty guard means this never clobbers rules being edited in-session: once a
    drawing has rules in its props, IFC is no longer read back into them.
    """
    props = get_camera_override_props(camera)
    if props is None or len(props.rules):
        return
    load_rules_from_ifc(camera)


def drawing_cameras():
    """Yield every camera object linked to an IFC drawing."""
    for obj in bpy.data.objects:
        if obj.type == "CAMERA" and tool.Ifc.get_entity(obj):
            yield obj


# --- Apply / restore seam --------------------------------------------------
# Two layers, so each effect lives where it can actually be shown:
#   * Live material layer (transparency): applied persistently while the toggle is
#     on, so it shows in the Rendered viewport (WYSIWYG). Driven by sync_live_effects.
#   * Render compositor layer (exposure/gamma): built just before a render and
#     removed just after, because the viewport compositor can't read Cryptomatte.
# The same enable toggle drives both.


def desired_transparency(scene):
    """{object: amount} that the active drawing's rules currently ask to be transparent."""
    props = get_camera_override_props(getattr(scene, "camera", None))
    if not props or not props.enabled:
        return {}
    desired = {}
    for rule in props.rules:
        if rule.transparency > 0:
            for obj in get_rule_objects(rule):
                desired[obj] = rule.transparency  # a later rule wins, as before
    return desired


def sync_live_effects(scene):
    """Bring the live (viewport) material state in line with the active drawing's rules.

    Incremental: slots already carrying the right temp material are left untouched, so a
    re-sync on a model where thousands of objects match does not tear everything down and
    rebuild it. That also means it can no longer destroy a working preview it is unable to
    restore. Idempotent; safe to call any time.
    """
    if scene is None:
        return
    desired = desired_transparency(scene)

    # Pass 1 -- keep what is already right, undo what is no longer wanted.
    kept, covered, restored = [], set(), 0
    for entry in _transparency_restore:
        obj, index, original, temp, amount = entry
        try:
            slot = obj.material_slots[index]
        except (IndexError, ReferenceError):
            continue  # object or slot is gone; nothing of ours left to undo
        if slot.material is not temp:
            continue  # replaced behind our back (e.g. a representation reload)
        if desired.get(obj) == amount:
            kept.append(entry)
            covered.add((obj.name, index))
            continue
        slot.material = original  # no longer wanted, or the amount changed
        restored += 1
    _transparency_restore[:] = kept

    # Pass 2 -- apply to anything wanted that is not already covered.
    applied, no_slots, empty_slots = 0, [], []
    for obj, amount in desired.items():
        try:
            slots = obj.material_slots
            if not len(slots):
                no_slots.append(obj.name)
                continue
            for index, slot in enumerate(slots):
                if (obj.name, index) in covered:
                    continue
                material = slot.material
                if material is None:
                    empty_slots.append(obj.name)
                    continue
                if material.get(MARKER):
                    # An orphan of ours, left by a rebuild we never saw. Adopt it via the
                    # source recorded on it, so it is tracked (and undone) again rather
                    # than silently baked into the file.
                    original = bpy.data.materials.get(material.get(SOURCE_KEY, "") or "")
                    if original is None:
                        continue
                else:
                    original = material
                temp = get_temp_material(original, amount)
                if slot.material is not temp:
                    slot.material = temp
                _transparency_restore.append((obj, index, original, temp, amount))
                applied += 1
        except ReferenceError:
            continue

    # Tracked = what the rules WANT, not just what we managed to apply, so an object whose
    # mesh is mid-rebuild is still watched and picked up when it comes back.
    _tracked_objects.clear()
    _tracked_objects.update(obj.name for obj in desired)
    release_unused_temp_materials()
    if DEBUG:
        _dbg(
            f"sync: wanted={len(desired)} applied={applied} kept={len(kept)} "
            f"restored={restored} temp_materials={len(_temp_material_cache)}"
        )
        if no_slots:
            _dbg(f"  no material slots (nothing to make transparent): {_brief(no_slots)}")
        if empty_slots:
            _dbg(f"  empty material slot: {_brief(empty_slots)}")


def clear_compositor(scene):
    """Remove the override compositor nodes and reconnect Render Layers -> Composite.

    Leaves live materials untouched (those are managed by sync_live_effects).
    """
    tree = get_compositor_tree(scene)
    if tree is None:
        return
    clear_marked_nodes(tree)
    if tree.get(MARKER):
        # A 5.x group we created just for the override -- remove it wholesale rather than
        # leaving the scene compositing through a passthrough graph it never had.
        scene.compositing_node_group = None
        bpy.data.node_groups.remove(tree)
        return
    rlayers = next((n for n in tree.nodes if n.bl_idname == "CompositorNodeRLayers"), None)
    output_socket = get_output_socket(tree)
    if rlayers and output_socket and not output_socket.links:
        tree.links.new(rlayers.outputs["Image"], output_socket)


# --- Handlers --------------------------------------------------------------


@persistent
def render_init_handler(scene, *args):
    # Ensure live materials match the current rules, then add the render-only compositor.
    ensure_rules_loaded(scene.camera)
    sync_live_effects(scene)
    props = get_camera_override_props(scene.camera)
    if props and props.enabled and len(props.rules):
        build_compositor(scene, props)


@persistent
def render_end_handler(scene, *args):
    # Remove the compositor; live materials persist for continued viewport preview.
    clear_compositor(scene)


# Switching the active drawing reassigns scene.camera, but no handler fires for that.
# A msgbus subscription re-syncs the live materials so the previous drawing's
# transparency is removed and the new drawing's applied. msgbus subscriptions are
# cleared on file load, so we re-subscribe in load_post.
_msgbus_owner = object()


def _deferred_camera_sync():
    scene = bpy.context.scene
    props = get_camera_override_props(scene.camera if scene else None)
    # Activating a drawing that already has rules auto-enables its overrides.
    if props and len(props.rules) and not props.enabled:
        props.enabled = True  # the update callback runs sync_live_effects
    else:
        sync_live_effects(scene)
    return None  # run once


def _on_active_camera_changed(*args):
    # Defer out of the msgbus notification context before touching material datablocks.
    if not bpy.app.timers.is_registered(_deferred_camera_sync):
        bpy.app.timers.register(_deferred_camera_sync, first_interval=0.0)


def subscribe_camera_change():
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Scene, "camera"),
        owner=_msgbus_owner,
        args=(),
        notify=_on_active_camera_changed,
    )


def _deferred_live_resync():
    scene = bpy.context.scene
    if scene is None:
        return None
    # The mode is re-checked HERE, not only when the timer was scheduled: entering edit
    # mode happens in between, and an object mid-edit has its slots in flux.
    if bpy.context.mode != "OBJECT":
        _dbg("deferred resync: not in OBJECT mode -- waiting")
        return 0.2
    if not live_state_is_stale():
        return None
    sync_live_effects(scene)
    return None  # run once


@persistent
def depsgraph_handler(scene, depsgraph):
    """Re-apply the live transparency after something rebuilt an object we swapped.

    Nothing notifies this module when a representation is reloaded, so without this the
    preview is silently lost after a geometry edit until the toggle is cycled.

    This runs on every depsgraph update, so it stays cheap: it returns immediately unless
    the update names an object the rules want, and the staleness check is scoped to just
    those names. Material writes are deferred out of the notification, as with the msgbus
    camera subscription.
    """
    if not _tracked_objects:
        return
    matched = {
        name
        for name in (getattr(update.id, "name", None) for update in depsgraph.updates)
        if name in _tracked_objects
    }
    if not matched:
        return
    if bpy.context.mode != "OBJECT":
        return  # mid-edit; leaving edit mode fires another update
    if not live_state_is_stale(matched):
        return  # nothing to do -- do not churn a timer on every update
    if not bpy.app.timers.is_registered(_deferred_live_resync):
        if DEBUG:
            _dbg(f"depsgraph: stale after {_brief(matched)} -- scheduling resync")
        bpy.app.timers.register(_deferred_live_resync, first_interval=0.0)


@persistent
def load_post_handler(*args):
    # IFC is the source of truth: fill any empty drawing camera from its pset. (For a
    # .blend reopen the props already came from the file; for IFC import the cameras
    # don't exist yet here -- that case is covered by data.refresh / refresh_ui_data.)
    for camera in drawing_cameras():
        ensure_rules_loaded(camera)
    subscribe_camera_change()  # msgbus is cleared on file load; re-subscribe
    # Files are saved without the temp materials (see save_pre), so re-apply on load.
    sync_live_effects(bpy.context.scene)


@persistent
def save_pre_handler(*args):
    # Never write the temporary transparent materials into the .blend.
    restore_transparency()
    # Flush each drawing's current rules into the IFC model before it is saved.
    for camera in drawing_cameras():
        save_rules_to_ifc(camera)


@persistent
def save_post_handler(*args):
    # Put the live preview back after the (clean) save.
    sync_live_effects(bpy.context.scene)


class AddRenderOverrideRule(bpy.types.Operator):
    bl_idname = "bim.add_render_override_rule"
    bl_label = "Add Render Override Rule"
    bl_description = "Add a new selection + effects rule"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return get_camera_override_props(context.scene.camera) is not None

    def execute(self, context):
        props = get_camera_override_props(context.scene.camera)
        rule = props.rules.add()
        rule.name = f"Rule {len(props.rules)}"
        props.active_rule_index = len(props.rules) - 1
        sync_live_effects(context.scene)
        save_rules_to_ifc(context.scene.camera)
        return {"FINISHED"}


class RemoveRenderOverrideRule(bpy.types.Operator):
    bl_idname = "bim.remove_render_override_rule"
    bl_label = "Remove Render Override Rule"
    bl_description = "Remove the active selection + effects rule"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        props = get_camera_override_props(context.scene.camera)
        return bool(props and props.rules)

    def execute(self, context):
        props = get_camera_override_props(context.scene.camera)
        props.rules.remove(props.active_rule_index)
        props.active_rule_index = min(props.active_rule_index, len(props.rules) - 1)
        sync_live_effects(context.scene)
        save_rules_to_ifc(context.scene.camera)
        return {"FINISHED"}


_HANDLERS = (
    ("render_init", "render_init_handler"),
    ("render_complete", "render_end_handler"),
    ("render_cancel", "render_end_handler"),
    ("depsgraph_update_post", "depsgraph_handler"),
    ("load_post", "load_post_handler"),
    ("save_pre", "save_pre_handler"),
    ("save_post", "save_post_handler"),
)


def register_handlers():
    unregister_handlers()
    for collection_name, func_name in _HANDLERS:
        getattr(bpy.app.handlers, collection_name).append(globals()[func_name])
    subscribe_camera_change()


def unregister_handlers():
    for collection_name, func_name in _HANDLERS:
        collection = getattr(bpy.app.handlers, collection_name)
        func = globals()[func_name]
        if func in collection:
            collection.remove(func)
    bpy.msgbus.clear_by_owner(_msgbus_owner)
