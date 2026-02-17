# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
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


# Batch Processor for Blender Operations
# Processes multiple objects in batches for maximum performance

import bpy
import time
from typing import List, Dict, Tuple, Any
from collections import defaultdict

class BlenderBatchProcessor:
    """Ultra-efficient batch processor for massive operations in Blender"""

    def __init__(self, batch_size: int = 500):
        self.batch_size = batch_size
        self.visibility_operations = []
        self.color_operations = []
        self.keyframe_operations = []

    def add_visibility_operation(self, obj, frame: int, hide_viewport: bool, hide_render: bool):
        """Adds a visibility operation to the batch"""
        self.visibility_operations.append({
            'obj': obj,
            'frame': frame,
            'hide_viewport': hide_viewport,
            'hide_render': hide_render
        })

    def add_color_operation(self, obj, frame: int, color: Tuple[float, float, float, float]):
        """Adds a color operation to the batch"""
        self.color_operations.append({
            'obj': obj,
            'frame': frame,
            'color': color
        })

    def add_keyframe_operation(self, obj, frame: int, data_path: str, value: Any):
        """Adds a keyframe operation to the batch"""
        self.keyframe_operations.append({
            'obj': obj,
            'frame': frame,
            'data_path': data_path,
            'value': value
        })

    def execute_visibility_batch(self):
        """Executes all visibility operations in a batch"""
        if not self.visibility_operations:
            return

        start_time = time.time()

        # Group by frame to minimize context switches
        operations_by_frame = defaultdict(list)
        for op in self.visibility_operations:
            operations_by_frame[op['frame']].append(op)

        total_ops = 0
        for frame, ops in operations_by_frame.items():
            bpy.context.scene.frame_set(frame)

            # Process in batches
            for i in range(0, len(ops), self.batch_size):
                batch = ops[i:i + self.batch_size]

                for op in batch:
                    obj = op['obj']
                    obj.hide_viewport = op['hide_viewport']
                    obj.hide_render = op['hide_render']
                    # CRITICAL: Insert keyframes to create animation
                    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
                    obj.keyframe_insert(data_path="hide_render", frame=frame)

                total_ops += len(batch)

        elapsed = time.time() - start_time
        print(f"[INFO] BATCH: {total_ops} visibility ops in {elapsed:.2f}s")
        self.visibility_operations.clear()

    def execute_color_batch(self):
        """Executes all color operations in a batch"""
        if not self.color_operations:
            return

        start_time = time.time()

        # Group by frame
        operations_by_frame = defaultdict(list)
        for op in self.color_operations:
            operations_by_frame[op['frame']].append(op)

        total_ops = 0
        for frame, ops in operations_by_frame.items():
            bpy.context.scene.frame_set(frame)

            for i in range(0, len(ops), self.batch_size):
                batch = ops[i:i + self.batch_size]

                for op in batch:
                    op['obj'].color = op['color']
                    # CRITICAL: Insert keyframes to create animation
                    op['obj'].keyframe_insert(data_path="color", frame=frame)

                total_ops += len(batch)

        elapsed = time.time() - start_time
        print(f"[INFO] BATCH: {total_ops} color ops in {elapsed:.2f}s")
        self.color_operations.clear()

    def execute_keyframe_batch(self):
        """Executes all keyframe operations in a batch"""
        if not self.keyframe_operations:
            return

        start_time = time.time()

        # Group by object and data_path for consecutive keyframes
        grouped_ops = defaultdict(lambda: defaultdict(list))
        for op in self.keyframe_operations:
            obj_key = op['obj'].name
            grouped_ops[obj_key][op['data_path']].append(op)

        total_ops = 0
        for obj_name, data_paths in grouped_ops.items():
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                continue

            for data_path, ops in data_paths.items():
                # Sort by frame for efficient sequential keyframing
                ops.sort(key=lambda x: x['frame'])

                for op in ops:
                    frame = op['frame']
                    value = op['value']

                    # Set value
                    try:
                        if data_path == 'color':
                            obj.color = value
                        elif data_path == 'hide_viewport':
                            obj.hide_viewport = value
                        elif data_path == 'hide_render':
                            obj.hide_render = value

                        # Insert keyframe
                        obj.keyframe_insert(data_path=data_path, frame=frame)
                        total_ops += 1
                    except Exception as e:
                        print(f"[WARNING] Keyframe error {obj_name}.{data_path}@{frame}: {e}")

        elapsed = time.time() - start_time
        print(f"[INFO] BATCH: {total_ops} keyframes in {elapsed:.2f}s")
        self.keyframe_operations.clear()

    def execute_all_batches(self):
        """Executes all pending batches"""
        self.execute_visibility_batch()
        self.execute_color_batch()
        self.execute_keyframe_batch()

    def clear_all(self):
        """Clears all pending batches"""
        self.visibility_operations.clear()
        self.color_operations.clear()
        self.keyframe_operations.clear()


class VisibilityBatchOptimizer:
    """Specific optimizer for massive visibility operations"""

    @staticmethod
    def batch_hide_objects(objects_to_hide: List, objects_to_show: List):
        """Hides/shows objects in an ultra-efficient batch"""
        start_time = time.time()

        # Hide in batch
        for obj in objects_to_hide:
            obj.hide_viewport = True
            obj.hide_render = True

        # Show in batch
        for obj in objects_to_show:
            obj.hide_viewport = False
            obj.hide_render = False

        elapsed = time.time() - start_time
        total = len(objects_to_hide) + len(objects_to_show)
        print(f"[INFO] VISIBILITY BATCH: {total} objects in {elapsed:.2f}s")

    @staticmethod
    def batch_set_colors(objects_with_colors: List[Tuple]):
        """Sets colors in batch (obj, color)"""
        start_time = time.time()

        for obj, color in objects_with_colors:
            obj.color = color

        elapsed = time.time() - start_time
        print(f"[INFO] COLOR BATCH: {len(objects_with_colors)} colors set in {elapsed:.2f}s")