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

"""
Construction Lines Tool for Bonsai BIM
=======================================

A tool for creating temporary reference geometry from selected edges.
Construction lines automatically extend, find intersections, and create
visual markers to aid in precise modeling.

Original Author: Julian "straaatooos" Hüther (Goliath Project)
https://github.com/straaatooos/goliath

Adapted for: Bonsai BIM Integration

Key Features:
- Extend selected edges into long construction lines
- Automatic intersection detection with existing construction lines
- Visual markers (empties) at intersection points
- Custom transform orientation based on selected geometry
- Prevents duplicate intersection markers at the same location
"""

import bpy
import bmesh
import mathutils



# Name of the container object for all construction lines
CONLINES_OBJECT_NAME = "ConstructionLines"
# Name of the root collection for all construction lines and intersection markers
CONLINES_COLLECTION_NAME = "ConstructionLines"

# Color for the construction lines object [R, G, B, Alpha]
CONLINES_COLOR = [1, 0.25, 0.1, 0.3]  # Orange-red with transparency

# Scale factor for extending construction lines from their midpoint
CONLINES_SCALE_FACTOR = 200

# Tolerance for intersection detection (larger = prevents near-duplicate intersections)
INTERSECTION_TOLERANCE = 0.001

# Tolerance for coplanarity detection (distance between closest points on two lines)
COPLANARITY_TOLERANCE = 0.001

# Visual properties for intersection marker empties
INTERSECTION_MARKER_NAME = "ConLine_Intersection"
INTERSECTION_MARKER_SIZE = 0.1
INTERSECTION_SHOW_IN_FRONT = True

# Name of the custom transform orientation
CUSTOM_ORIENTATION_NAME = "Cons_Line"

# Property name for storing construction line registry
CONLINES_REGISTRY_PROP = "conlines_registry"


def ensure_construction_lines_object():
    """
    Create or verify existence of the construction lines container object.
    
    This object stores all construction line geometry with special properties:
    - Cannot be selected (hide_select = True)
    - Orange-red color for visibility
    - Acts as parent for intersection marker empties
    - Stores registry of lines and their intersection points
    """
    if not bpy.context.scene:
        return
        
    root_coll = bpy.data.collections.get(CONLINES_COLLECTION_NAME)
    if not root_coll:
        root_coll = bpy.data.collections.new(CONLINES_COLLECTION_NAME)
        bpy.context.scene.collection.children.link(root_coll)

    if CONLINES_OBJECT_NAME not in bpy.context.scene.objects:
        mesh = bpy.data.meshes.new(CONLINES_OBJECT_NAME)
        obj = bpy.data.objects.new(CONLINES_OBJECT_NAME, mesh)
        root_coll.objects.link(obj)
        obj.hide_select = True
        obj.color = CONLINES_COLOR
        # Initialize empty registry for tracking lines
        obj[CONLINES_REGISTRY_PROP] = []


def calculate_shortest_distance_points(line1_p1, line1_p2, line2_p1, line2_p2):
    """
    Calculate the two closest points between two 3D line segments.
    
    This function finds the points on each line that are closest to each other,
    which represents the shortest distance between the two lines.
    
    For coplanar lines that intersect, both points will be at the same location.
    For non-coplanar (skew) lines, the two points will be different.
    
    Args:
        line1_p1: First point of line 1 (Vector)
        line1_p2: Second point of line 1 (Vector)
        line2_p1: First point of line 2 (Vector)
        line2_p2: Second point of line 2 (Vector)
        
    Returns:
        tuple: (point_on_line1, point_on_line2) or None if lines are parallel
    """
    return mathutils.geometry.intersect_line_line(line1_p1, line1_p2, line2_p1, line2_p2)


class BIM_OT_construction_lines_clear(bpy.types.Operator):
    """Clear all construction lines and intersection markers"""
    bl_idname = "bim.construction_lines_clear"
    bl_label = "Clear Construction Lines"
    bl_description = "Remove all construction lines and intersection markers from the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """Only available when construction lines feature is enabled"""
        if not context.scene:
            return False
        model_props = getattr(context.scene, 'BIMModelProperties', None)
        if not model_props:
            return False
        return model_props.show_construction_lines
    
    def execute(self, context):
        """
        Clear all construction line data:
        1. Remove all geometry from container object
        2. Delete all intersection marker empties
        3. Delete custom transform orientation
        """

        obj = bpy.data.objects.get(CONLINES_OBJECT_NAME)
        if obj:
            me = obj.data
            
            bm = bmesh.new()
            bm.from_mesh(me)
            bm.clear()
            bm.to_mesh(me)
            bm.free()
            
            children_to_remove = list(obj.children)
            for child in children_to_remove:
                child.parent = None
                bpy.data.objects.remove(child)
            
            # Clear the registry
            if CONLINES_REGISTRY_PROP in obj:
                obj[CONLINES_REGISTRY_PROP] = []

        try:
            context.scene.transform_orientation_slots[0].type = CUSTOM_ORIENTATION_NAME
            bpy.ops.transform.delete_orientation()
        except (RuntimeError, TypeError):
            pass

        self.report({'INFO'}, "Construction lines cleared")
        return {'FINISHED'}


class BIM_OT_construction_lines_add(bpy.types.Operator):
    """Add construction lines from selected edges"""
    bl_idname = "bim.construction_lines_add"
    bl_label = "Add Construction Lines"
    bl_description = "Create extended construction lines from selected edge(s) with automatic intersection detection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Only available in Edit Mode when construction lines feature is enabled"""
        if not context.object or context.object.mode != "EDIT":
            return False
        if not context.scene:
            return False
        model_props = getattr(context.scene, 'BIMModelProperties', None)
        if not model_props:
            return False
        return model_props.show_construction_lines

    def execute(self, context):
        """
        Main execution flow:
        1. Ensure container object exists
        2. Track current intersection count
        3. Process selected edges into construction lines
        4. Report new intersections added
        """
        # Ensure container object exists
        ensure_construction_lines_object()
        
        # Count intersections before operation (for reporting)
        obj_container = bpy.data.objects.get(CONLINES_OBJECT_NAME)
        if obj_container:
            intersections_before = len(obj_container.children)
        else:
            intersections_before = 0

        # Process the selection and create construction lines
        success = self.duplicator()
        
        if not success:
            return {'CANCELLED'}

        # Calculate how many intersections were added
        obj_container = bpy.data.objects.get(CONLINES_OBJECT_NAME)
        if obj_container:
            intersections_after = len(obj_container.children)
            intersections_added = intersections_after - intersections_before
            
            # Report what was created
            if intersections_added > 0:
                msg = f"Added {intersections_added} intersection point{'s' if intersections_added != 1 else ''}"
                self.report({'INFO'}, msg)
        
        return {'FINISHED'}



    def edit_imaginary_mesh(self, newedges):
        """
        Add new construction line edges to the container object.
        
        Args:
            newedges: BMesh edge with two vertices representing the construction line
        """
        obj = bpy.data.objects.get(CONLINES_OBJECT_NAME)
        if not obj:
            return
            
        me = obj.data
        
        # Create BMesh from container object
        bm1 = bmesh.new()
        bm1.from_mesh(me)
        
        # Store edge index before adding
        edge_index_before = len(bm1.edges)
        
        # Find and create intersections with existing lines
        # Returns list of (marker, existing_edge_index) tuples
        intersection_data = self.intersector(bm1, newedges)
        
        # Add the new edge to the container
        newedge_coords = [newedges.verts[0].co, newedges.verts[1].co]
        newedge_verts = [bm1.verts.new(newedge_coords[0]), bm1.verts.new(newedge_coords[1])]
        new_edge = bm1.edges.new(newedge_verts)
        
        # Register this line with its intersection points (bidirectional tracking)
        self.register_construction_line(obj, newedge_coords, intersection_data)
        
        # Enforce max line count limit
        self.enforce_max_line_count(bm1, obj)
        
        # Update mesh
        bm1.to_mesh(me)
        bm1.free()
        
    def intersector(self, bm, newedge):
        """
        Find intersections between new construction line and existing ones.
        Creates geometry and visual markers for each valid intersection.
        
        For coplanar lines: Creates one marker at the intersection point
        For non-coplanar lines: Creates two markers at the points of shortest distance
        
        Only creates markers if there isn't already one at that location.
        
        Args:
            bm: BMesh data of the container object
            newedge: The new edge to check for intersections
            
        Returns:
            List of (marker, existing_edge_index) tuples for bidirectional tracking
        """
        obj = bpy.data.objects.get(CONLINES_OBJECT_NAME)
        if not obj:
            return []
            
        edges = [e for e in bm.edges]
        intersection_data = []  # List of (marker, edge_index) tuples
        intersection_verts = []  # For adding vertices to mesh

        # Get the two points of the new edge
        u1, u2 = [vertex.co for vertex in newedge.verts]
        
        # Check intersection with each existing edge
        for edge_index, edge in enumerate(edges):
            # Get the two points of the existing edge
            v1, v2 = [vertex.co for vertex in edge.verts]

            # Calculate closest points between the two lines using dedicated function
            closest_points = calculate_shortest_distance_points(u1, u2, v1, v2)
            
            if closest_points is not None:
                point_on_new_line, point_on_existing_line = closest_points
                
                # Calculate distance between the two closest points to check coplanarity
                distance_between_points = (point_on_new_line - point_on_existing_line).length
                
                # Check if lines are coplanar (distance between closest points is negligible)
                is_coplanar = distance_between_points < COPLANARITY_TOLERANCE
                
                if is_coplanar:
                    # Lines are coplanar - create one intersection marker
                    # Use average of the two points (they should be nearly identical)
                    iv = (point_on_new_line + point_on_existing_line) / 2
                    
                    # Validate that intersection is actually on both line segments
                    a = iv - u1
                    b = iv - u2
                    c = u1 - u2
                    d = iv - v1
                    e = iv - v2
                    f = v1 - v2
                    
                    # Check if point is on both segments using distance formula
                    on_segment_1 = a.length + b.length - c.length < INTERSECTION_TOLERANCE
                    on_segment_2 = d.length + e.length - f.length < INTERSECTION_TOLERANCE
                    
                    if on_segment_1 and on_segment_2:
                        # Check if there's already an intersection marker at this location
                        duplicate = False
                        for child in obj.children:
                            distance = (child.location - iv).length
                            if distance < INTERSECTION_TOLERANCE:
                                duplicate = True
                                break
                        
                        if not duplicate:
                            # Add vertex to container mesh
                            intersection_verts.append(bm.verts.new(iv))
                            # Create visual marker and track it
                            marker = self._create_intersection_marker(obj, iv)
                            intersection_data.append((marker, edge_index))
                
                else:
                    # Lines are NOT coplanar (skew lines) - create markers at both shortest distance points
                    points_to_mark = [point_on_new_line, point_on_existing_line]
                    
                    for point in points_to_mark:
                        # Check if there's already an intersection marker at this location
                        duplicate = False
                        for child in obj.children:
                            distance = (child.location - point).length
                            if distance < INTERSECTION_TOLERANCE:
                                duplicate = True
                                break
                        
                        if not duplicate:
                            # Add vertex to container mesh
                            intersection_verts.append(bm.verts.new(point))
                            # Create visual marker and track it
                            marker = self._create_intersection_marker(obj, point)
                            intersection_data.append((marker, edge_index))
                        
        return intersection_data
    
    def register_construction_line(self, obj, edge_coords, intersection_data):
        """
        Register a construction line with its associated intersection markers.
        Updates both the new line and existing lines with bidirectional marker tracking.
        
        Args:
            obj: The construction lines container object
            edge_coords: List of two vectors representing the line endpoints
            intersection_data: List of (marker, existing_edge_index) tuples
        """
        # Initialize registry if it doesn't exist
        if CONLINES_REGISTRY_PROP not in obj:
            obj[CONLINES_REGISTRY_PROP] = []
        
        # Get registry as list
        registry = list(obj[CONLINES_REGISTRY_PROP])
        
        # Extract markers from intersection_data
        marker_names = [marker.name for marker, _ in intersection_data]
        
        # Add new line entry
        line_entry = {
            "start": [edge_coords[0].x, edge_coords[0].y, edge_coords[0].z],
            "end": [edge_coords[1].x, edge_coords[1].y, edge_coords[1].z],
            "markers": marker_names
        }
        registry.append(line_entry)
        
        # Update existing lines' registries to include the shared markers (bidirectional tracking)
        for marker, edge_index in intersection_data:
            if edge_index < len(registry) - 1:  # -1 because we just added the new line
                # Add this marker to the existing line's marker list
                # Convert to list first (IDPropertyArray is immutable)
                existing_markers = list(registry[edge_index]["markers"])
                if marker.name not in existing_markers:
                    existing_markers.append(marker.name)
                    registry[edge_index]["markers"] = existing_markers
        
        # Save back to object
        obj[CONLINES_REGISTRY_PROP] = registry
    
    def enforce_max_line_count(self, bm, obj):
        """
        Enforce the maximum construction line count.
        Removes oldest lines and their associated intersection markers when limit is exceeded.
        
        Args:
            bm: BMesh data of the container object
            obj: The construction lines container object
        """
        model_props = bpy.context.scene.BIMModelProperties
        max_count = model_props.construction_lines_max_count if hasattr(model_props, 'construction_lines_max_count') else 10
        
        # 0 means no limit
        if max_count == 0:
            return
        
        # Get registry
        if CONLINES_REGISTRY_PROP not in obj:
            return
        
        registry = list(obj[CONLINES_REGISTRY_PROP])
        current_count = len(registry)
        
        if current_count > max_count:
            # Calculate how many to remove
            to_remove_count = current_count - max_count
            
            # Get edges list
            edges = [e for e in bm.edges]
            
            # Remove the oldest lines
            for i in range(to_remove_count):
                line_entry = registry[i]
                
                # Remove the edge that matches this line's coordinates
                start = mathutils.Vector(line_entry["start"])
                end = mathutils.Vector(line_entry["end"])
                
                for edge in edges:
                    v1 = edge.verts[0].co
                    v2 = edge.verts[1].co
                    
                    # Check if this edge matches the registered line
                    if ((v1 - start).length < INTERSECTION_TOLERANCE and (v2 - end).length < INTERSECTION_TOLERANCE) or \
                       ((v1 - end).length < INTERSECTION_TOLERANCE and (v2 - start).length < INTERSECTION_TOLERANCE):
                        # Remove the edge
                        bm.edges.remove(edge)
                        edges.remove(edge)
                        break
                
                # Remove associated intersection markers
                markers_to_remove = set(line_entry["markers"])
                for marker_name in markers_to_remove:
                    marker = bpy.data.objects.get(marker_name)
                    if marker:
                        marker.parent = None
                        bpy.data.objects.remove(marker)
                
                # Remove these markers from other lines' registries (cleanup bidirectional references)
                for other_line_entry in registry:
                    if other_line_entry != line_entry:
                        other_line_entry["markers"] = [
                            m for m in other_line_entry["markers"] if m not in markers_to_remove
                        ]
            
            # Update registry - remove the oldest entries
            registry = registry[to_remove_count:]
            obj[CONLINES_REGISTRY_PROP] = registry
            
            # Clean up orphaned vertices
            verts_to_remove = [v for v in bm.verts if len(v.link_edges) == 0]
            for vert in verts_to_remove:
                bm.verts.remove(vert)
    
    def _create_intersection_marker(self, parent_obj, location):
        """
        Create a visual marker (empty object) at the given location.
        
        Args:
            parent_obj: The parent object (ConstructionLines container)
            location: The 3D location for the marker (Vector)
            
        Returns:
            The created empty object marker
        """
        # Create visual marker (empty object)
        empty = bpy.data.objects.new(INTERSECTION_MARKER_NAME, None)
        
        # Link to the ConstructionLines root collection
        root_coll = bpy.data.collections.get(CONLINES_COLLECTION_NAME)
        if not root_coll:
            root_coll = bpy.data.collections.new(CONLINES_COLLECTION_NAME)
            bpy.context.scene.collection.children.link(root_coll)
        root_coll.objects.link(empty)
        
        # Configure marker
        empty.location = location
        empty.parent = parent_obj  # Parent to container for organization
        empty.empty_display_size = INTERSECTION_MARKER_SIZE
        empty.show_in_front = INTERSECTION_SHOW_IN_FRONT
        empty.hide_select = True  # Prevent selection
        
        return empty
    
    def _create_construction_line_from_points(self, v1_co, v2_co, world_matrix):
        """
        Helper function to create a construction line from two points.
        
        Args:
            v1_co: First vertex coordinate (local space)
            v2_co: Second vertex coordinate (local space)
            world_matrix: World transformation matrix
        """
        # Transform to world space
        v1_world = world_matrix @ v1_co
        v2_world = world_matrix @ v2_co
        
        # Scale from midpoint
        midpoint = (v1_world + v2_world) / 2
        mat_loc = mathutils.Matrix.Translation(-midpoint)
        
        # Create temporary BMesh with scaled edge
        bm_temp = bmesh.new()
        v1_temp = bm_temp.verts.new(v1_world)
        v2_temp = bm_temp.verts.new(v2_world)
        bm_temp.edges.new([v1_temp, v2_temp])
        bm_temp.edges.ensure_lookup_table()
        
        scale_vec = mathutils.Vector((1, 1, 1)) * CONLINES_SCALE_FACTOR
        bmesh.ops.scale(bm_temp, vec=scale_vec, space=mat_loc, verts=[v1_temp, v2_temp])
        
        # Add to container object
        self.edit_imaginary_mesh(bm_temp.edges[0])
        bm_temp.free()
                        
    def duplicator(self):
        """
        Core logic for creating construction lines from selected edges.
        
        Process:
        1. Save current selection state
        2. Switch to edge selection mode
        3. Get user's edge selection
        4. Create custom transform orientation
        5. Duplicate and extend selected edges
        6. Add to container object with intersection detection
        7. Clean up and restore original state
        
        Returns:
            bool: True if successful, False otherwise
        """
        me = bpy.context.object.data
        bm = bmesh.from_edit_mesh(me)

        # ========================================
        # SAVE STATE (to restore after operation)
        # ========================================
        prev_select_mode = bpy.context.tool_settings.mesh_select_mode[:]
        
        # Store all currently selected elements
        prev_selection = []
        prev_selection.extend([v for v in bm.verts if v.select])
        prev_selection.extend([e for e in bm.edges if e.select])
        prev_selection.extend([f for f in bm.faces if f.select])

        # ========================================
        # PREPARE FOR EDGE SELECTION
        # ========================================
        # Get current edge and face selection
        selected_edges = [e for e in bm.edges if e.select]
        selected_faces = [f for f in bm.faces if f.select]
        selected_verts = [v for v in bm.verts if v.select]
        
        # Check if anything is selected
        if not selected_edges and not selected_faces and len(selected_verts) < 2:
            self.report({'WARNING'}, "Select at least 2 vertices, 1 edge, or 1 face")
            return False

        # ========================================
        # CREATE CUSTOM TRANSFORM ORIENTATION
        # ========================================
        # Create new orientation from selected edge(s) (overwrite any existing)
        bpy.ops.transform.create_orientation(
            name=CUSTOM_ORIENTATION_NAME, 
            use=False, 
            overwrite=True
        )

        # ========================================
        # PROCESS SELECTION
        # ========================================
        # Get world matrix once
        world_matrix = bpy.context.object.matrix_world
        
        # 1. All pairs of selected vertices (only if no edges are selected)
        if len(selected_verts) >= 2 and not selected_edges:
            for i in range(len(selected_verts)):
                for j in range(i+1, len(selected_verts)):
                    v1 = selected_verts[i]
                    v2 = selected_verts[j]
                    self._create_construction_line_from_points(v1.co, v2.co, world_matrix)
            # Deselect original vertices
            for vertex in selected_verts:
                vertex.select = False
        
        # 2. Each selected edge
        if selected_edges:
            for edge in selected_edges:
                v1 = edge.verts[0]
                v2 = edge.verts[1]
                self._create_construction_line_from_points(v1.co, v2.co, world_matrix)
        
        # 3. Each edge of selected faces
        if selected_faces:
            for face in selected_faces:
                for edge in face.edges:
                    v1 = edge.verts[0]
                    v2 = edge.verts[1]
                    self._create_construction_line_from_points(v1.co, v2.co, world_matrix)
        
        # ========================================
        # RESTORE ORIGINAL STATE
        # ========================================
        # Restore previous selection
        bpy.ops.mesh.select_all(action='DESELECT')
        for ele in prev_selection:
            if ele.is_valid:
                ele.select = True
        
        # Update mesh
        bmesh.update_edit_mesh(me)

        # Restore selection mode
        bpy.context.tool_settings.mesh_select_mode = prev_select_mode
        
        return True

