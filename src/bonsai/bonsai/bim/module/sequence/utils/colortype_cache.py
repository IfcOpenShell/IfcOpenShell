"""
ColorType Cache Module - Ultra-fast Task-to-ColorProfile Mapping
==============================================================

PROBLEM SOLVED:
ColorType logic is computationally expensive when executed for 8,000 objects.
For each object, it must search the active group, check custom assignments,
fall back to PredefinedType, etc. This becomes the main bottleneck.

SOLUTION:
Pre-calculate the complex ColorType logic once per TASK (not per object).
Create an instant map: task_id -> color_profile_final.

BENEFIT:
- Pre-calculation: ~1 second
- Subsequent queries: instantaneous
- Accelerates: Animation Creation + Variance Calculation

USAGE:
    cache = ColorTypeCache()
    cache.build_cache(context)
    color_profile = cache.get_task_color_profile(task_id)
"""

import bpy
import time
from typing import Dict, Optional, Tuple, Any

class ColorTypeCache:
    """Ultra-fast cache for task-to-color-profile mappings"""

    def __init__(self):
        self._cache: Dict[int, Dict[str, Any]] = {}
        self._cache_built = False
        self._build_time = 0.0
        self._stats = {
            'tasks_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    def build_cache(self, context) -> float:
        """
        Pre-calculate color profiles for all tasks.
        Returns build time in seconds.
        """
        start_time = time.time()
        self._cache.clear()
        self._cache_built = False
        self._stats = {'tasks_processed': 0, 'cache_hits': 0, 'cache_misses': 0}

        try:
            # Import required modules
            import bonsai.tool as tool
            try:
                from .prop import UnifiedColorTypeManager
            except ImportError:
                # Fallback for direct execution
                try:
                    import sys, os
                    sys.path.insert(0, os.path.dirname(__file__))
                    from prop import UnifiedColorTypeManager
                except ImportError:
                    # Ultimate fallback - we'll work without it
                    UnifiedColorTypeManager = None

            # Get task tree properties
            tprops = tool.Sequence.get_task_tree_props()
            if not tprops or not hasattr(tprops, 'tasks'):
                print("[WARNING] ColorTypeCache: No tasks found")
                return 0.0

            # Get animation properties for active group
            anim_props = tool.Sequence.get_animation_props()
            active_group = getattr(anim_props, 'ColorType_groups', '') or 'DEFAULT'

            print(f"[INFO] ColorTypeCache: Building cache for {len(tprops.tasks)} tasks with group '{active_group}'...")

            # Process each task once
            for task in tprops.tasks:
                task_id = task.ifc_definition_id
                if task_id == 0:
                    continue

                # Calculate final color profile for this task
                color_profile = self._calculate_task_color_profile(task, active_group, context)

                # Store in cache
                self._cache[task_id] = color_profile
                self._stats['tasks_processed'] += 1

            self._cache_built = True
            self._build_time = time.time() - start_time

            print(f"[INFO] ColorTypeCache: Built cache in {self._build_time:.3f}s for {self._stats['tasks_processed']} tasks")
            return self._build_time

        except Exception as e:
            print(f"[ERROR] ColorTypeCache: Build failed: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

    def _calculate_task_color_profile(self, task, active_group: str, context) -> Dict[str, Any]:
        """
        Calculate the final color profile for a single task.
        This is the expensive operation we're caching.
        """
        try:
            # Default profile
            profile = {
                'color': (0.5, 0.5, 0.5, 1.0),  # Gray fallback
                'colortype': 'UNDEFINED',
                'source': 'fallback'
            }

            # Method 1: Check custom task assignment in active group
            if active_group != 'DEFAULT':
                try:
                    custom_colortype = getattr(task, 'selected_colortype_in_active_group', '')
                    if custom_colortype:
                        color = self._get_colortype_color(custom_colortype, active_group, context)
                        if color:
                            profile.update({
                                'color': color,
                                'colortype': custom_colortype,
                                'source': 'custom_assignment'
                            })
                            return profile
                except:
                    pass

            # Method 2: Use PredefinedType from task
            predefined_type = getattr(task, 'PredefinedType', '')
            if predefined_type and predefined_type != 'NOTDEFINED':
                color = self._get_colortype_color(predefined_type, active_group, context)
                if color:
                    profile.update({
                        'color': color,
                        'colortype': predefined_type,
                        'source': 'predefined_type'
                    })
                    return profile

            # Method 3: Use animation_color_schemes if available
            try:
                animation_colortype = getattr(task, 'animation_color_schemes', '')
                if animation_colortype:
                    color = self._get_colortype_color(animation_colortype, active_group, context)
                    if color:
                        profile.update({
                            'color': color,
                            'colortype': animation_colortype,
                            'source': 'animation_color_schemes'
                        })
                        return profile
            except:
                pass

            # Method 4: Fallback to UNDEFINED colortype
            color = self._get_colortype_color('UNDEFINED', active_group, context)
            if color:
                profile.update({
                    'color': color,
                    'colortype': 'UNDEFINED',
                    'source': 'undefined_fallback'
                })

            return profile

        except Exception as e:
            print(f"[WARNING] ColorTypeCache: Error calculating profile for task {task.ifc_definition_id}: {e}")
            return profile

    def _get_colortype_color(self, colortype_name: str, group_name: str, context) -> Optional[Tuple[float, float, float, float]]:
        """Get color for a specific colortype in a group"""
        try:
            import bonsai.tool as tool

            # Get animation props and search for the colortype
            anim_props = tool.Sequence.get_animation_props()
            if not hasattr(anim_props, 'ColorTypes'):
                return None

            # Find matching colortype in the active group
            for colortype in anim_props.ColorTypes:
                if hasattr(colortype, 'name') and colortype.name == colortype_name:
                    if hasattr(colortype, 'group') and colortype.group == group_name:
                        # Get color from colortype
                        if hasattr(colortype, 'color') and len(colortype.color) >= 3:
                            color = colortype.color
                            # Ensure RGBA format
                            if len(color) == 3:
                                return (color[0], color[1], color[2], 1.0)
                            else:
                                return (color[0], color[1], color[2], color[3])

            # If not found in specific group, try DEFAULT group
            if group_name != 'DEFAULT':
                return self._get_colortype_color(colortype_name, 'DEFAULT', context)

            return None

        except Exception as e:
            print(f"[WARNING] ColorTypeCache: Error getting color for {colortype_name}: {e}")
            return None

    def get_task_color_profile(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached color profile for a task.
        Ultra-fast O(1) lookup.
        """
        if not self._cache_built:
            print("[WARNING] ColorTypeCache: Cache not built. Call build_cache() first.")
            self._stats['cache_misses'] += 1
            return None

        if task_id in self._cache:
            self._stats['cache_hits'] += 1
            return self._cache[task_id]
        else:
            self._stats['cache_misses'] += 1
            return None

    def get_task_color(self, task_id: int) -> Optional[Tuple[float, float, float, float]]:
        """Get just the color tuple for a task"""
        profile = self.get_task_color_profile(task_id)
        return profile['color'] if profile else None

    def get_task_colortype(self, task_id: int) -> Optional[str]:
        """Get just the colortype name for a task"""
        profile = self.get_task_color_profile(task_id)
        return profile['colortype'] if profile else None

    def is_cache_valid(self) -> bool:
        """Check if cache is built and valid"""
        return self._cache_built and len(self._cache) > 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self._stats['cache_hits'] + self._stats['cache_misses']
        hit_rate = (self._stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self._stats,
            'cache_size': len(self._cache),
            'build_time': self._build_time,
            'hit_rate_percent': hit_rate,
            'is_built': self._cache_built
        }

    def clear_cache(self):
        """Clear the cache"""
        self._cache.clear()
        self._cache_built = False
        self._build_time = 0.0
        self._stats = {'tasks_processed': 0, 'cache_hits': 0, 'cache_misses': 0}
        print("[INFO] ColorTypeCache: Cache cleared")


# Global cache instance
_global_colortype_cache = None

def get_colortype_cache() -> ColorTypeCache:
    """Get the global ColorType cache instance"""
    global _global_colortype_cache
    if _global_colortype_cache is None:
        _global_colortype_cache = ColorTypeCache()
    return _global_colortype_cache

def clear_global_cache():
    """Clear the global cache"""
    global _global_colortype_cache
    if _global_colortype_cache:
        _global_colortype_cache.clear_cache()
    _global_colortype_cache = None

# Convenience functions for easy integration
def build_task_color_cache(context) -> float:
    """Build the global color cache. Returns build time."""
    cache = get_colortype_cache()
    return cache.build_cache(context)

def get_task_color_fast(task_id: int) -> Optional[Tuple[float, float, float, float]]:
    """Ultra-fast task color lookup"""
    cache = get_colortype_cache()
    return cache.get_task_color(task_id)

def get_task_colortype_fast(task_id: int) -> Optional[str]:
    """Ultra-fast task colortype lookup"""
    cache = get_colortype_cache()
    return cache.get_task_colortype(task_id)