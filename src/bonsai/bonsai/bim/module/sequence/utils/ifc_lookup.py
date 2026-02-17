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


# Ultra-Fast IFC Entity Lookup System
# Precomputed mappings for instant access

import time
from typing import Dict, List, Set, Optional, Any
import bonsai.tool as tool
import ifcopenshell.util.sequence

class IFCLookupOptimizer:
    """Ultra-fast lookup system for IFC entities and task relationships"""

    def __init__(self):
        self.product_to_output_tasks: Dict[int, List] = {}
        self.product_to_input_tasks: Dict[int, List] = {}
        self.task_to_outputs: Dict[int, List] = {}
        self.task_to_inputs: Dict[int, List] = {}
        self.task_hierarchy: Dict[int, List] = {}
        self.all_tasks_flat: List = []
        self.product_ids: Set[int] = set()
        self.lookup_built = False

    def build_lookup_tables(self, work_schedule):
        """Builds all lookup tables at once - 10x faster"""
        start_time = time.time()

        print("[INFO] Building IFC lookup tables...")

        # 1. Get all tasks at once
        root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)
        self.all_tasks_flat = []

        def collect_all_tasks(task):
            self.all_tasks_flat.append(task)
            nested = ifcopenshell.util.sequence.get_nested_tasks(task)
            for subtask in nested:
                collect_all_tasks(subtask)

        for root_task in root_tasks:
            collect_all_tasks(root_task)

        print(f"[INFO] Found {len(self.all_tasks_flat)} tasks")

        # 2. Pre-compute ALL relationships at once
        for task in self.all_tasks_flat:
            task_id = task.id()

            # Task Outputs
            try:
                outputs = list(ifcopenshell.util.sequence.get_task_outputs(task))
                self.task_to_outputs[task_id] = outputs

                for output in outputs:
                    product_id = output.id()
                    self.product_ids.add(product_id)

                    if product_id not in self.product_to_output_tasks:
                        self.product_to_output_tasks[product_id] = []
                    self.product_to_output_tasks[product_id].append(task)
            except:
                self.task_to_outputs[task_id] = []

            # Task Inputs
            try:
                inputs = tool.Sequence.get_task_inputs(task) if hasattr(tool.Sequence, 'get_task_inputs') else []
                if not inputs:
                    inputs = list(ifcopenshell.util.sequence.get_task_inputs(task))
                self.task_to_inputs[task_id] = inputs

                for input_prod in inputs:
                    product_id = input_prod.id()
                    self.product_ids.add(product_id)

                    if product_id not in self.product_to_input_tasks:
                        self.product_to_input_tasks[product_id] = []
                    self.product_to_input_tasks[product_id].append(task)
            except:
                self.task_to_inputs[task_id] = []

        self.lookup_built = True
        elapsed = time.time() - start_time
        print(f"[INFO] Lookup tables built in {elapsed:.2f}s")
        print(f"[INFO] {len(self.product_ids)} products, {len(self.all_tasks_flat)} tasks")

        # Debug: Show some details
        print(f"[DEBUG] task_to_outputs entries: {len(self.task_to_outputs)}")
        print(f"[DEBUG] task_to_inputs entries: {len(self.task_to_inputs)}")

        # Show first few tasks with their products
        tasks_with_products = 0
        for task in self.all_tasks_flat[:5]:  # Check first 5 tasks
            task_id = task.id()
            outputs = self.task_to_outputs.get(task_id, [])
            inputs = self.task_to_inputs.get(task_id, [])
            if outputs or inputs:
                tasks_with_products += 1
                task_name = getattr(task, 'Name', f'Task_{task_id}')
                print(f"[DEBUG] {task_name}: {len(outputs)} outputs, {len(inputs)} inputs")

        print(f"[DEBUG] Tasks with products (first 5): {tasks_with_products}/5")

    def get_tasks_for_product(self, product_id: int) -> tuple[List, List]:
        """Gets input/output tasks for a product instantly"""
        if not self.lookup_built:
            return [], []

        output_tasks = self.product_to_output_tasks.get(product_id, [])
        input_tasks = self.product_to_input_tasks.get(product_id, [])
        return input_tasks, output_tasks

    def get_outputs_for_task(self, task_id: int) -> List:
        """Gets outputs for a task instantly"""
        return self.task_to_outputs.get(task_id, [])

    def get_inputs_for_task(self, task_id: int) -> List:
        """Gets inputs for a task instantly"""
        return self.task_to_inputs.get(task_id, [])

    def get_all_products(self) -> Set[int]:
        """Gets all product IDs"""
        return self.product_ids.copy()

    def get_all_tasks(self) -> List:
        """Gets all tasks"""
        return self.all_tasks_flat.copy()

    def invalidate(self):
        """Invalidates the lookup"""
        self.product_to_output_tasks.clear()
        self.product_to_input_tasks.clear()
        self.task_to_outputs.clear()
        self.task_to_inputs.clear()
        self.task_hierarchy.clear()
        self.all_tasks_flat.clear()
        self.product_ids.clear()
        self.lookup_built = False


class TaskDateCache:
    """Ultra-efficient cache for task dates"""

    def __init__(self):
        self.date_cache: Dict[str, Optional[Any]] = {}

    def get_date(self, task, date_type: str, is_earliest: bool = False, is_latest: bool = False):
        """Gets date with cache"""
        cache_key = f"{task.id()}_{date_type}_{is_earliest}_{is_latest}"

        if cache_key not in self.date_cache:
            try:
                if is_earliest:
                    date = ifcopenshell.util.sequence.derive_date(task, date_type, is_earliest=True)
                elif is_latest:
                    date = ifcopenshell.util.sequence.derive_date(task, date_type, is_latest=True)
                else:
                    date = ifcopenshell.util.sequence.derive_date(task, date_type)
                self.date_cache[cache_key] = date
            except:
                self.date_cache[cache_key] = None

        return self.date_cache[cache_key]

    def invalidate(self):
        """Clears the cache"""
        self.date_cache.clear()


# Global singleton instances
_ifc_lookup = IFCLookupOptimizer()
_date_cache = TaskDateCache()

def get_ifc_lookup() -> IFCLookupOptimizer:
    """Gets the global lookup optimizer"""
    return _ifc_lookup

def get_date_cache() -> TaskDateCache:
    """Gets the global date cache"""
    return _date_cache

def invalidate_all_lookups():
    """Invalidates all caches and lookups"""
    _ifc_lookup.invalidate()
    _date_cache.invalidate()