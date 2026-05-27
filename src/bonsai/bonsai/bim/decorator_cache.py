# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

"""Shared structural-change cache token for POST_VIEW decorators.

Decorators include the token in their cache key and rebuild on bump."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar

import bpy

T = TypeVar("T")

_DECORATOR_CACHE_TOKEN = 0


def get_decorator_cache_token() -> int:
    return _DECORATOR_CACHE_TOKEN


def reset_for_test() -> None:
    """Test-only: reset the cache token to 0 so bump-count assertions are stable."""
    global _DECORATOR_CACHE_TOKEN
    _DECORATOR_CACHE_TOKEN = 0


@bpy.app.handlers.persistent
def _bump_decorator_cache_token(*args: Any) -> None:
    """depsgraph_update_post fires every animation frame and every driver
    evaluation, even when no IFC-relevant ID block changed. Unconditional
    bumping defeats the cache: an animated scene rebuilds every decorator
    every viewport tick. Gate the depsgraph path on Object geometry or
    transform updates; undo / redo / load have no depsgraph and always
    invalidate.

    Coverage assumption: ``TokenCache`` consumers key on Object identity
    (depsgraph updates whose ``id`` is a ``bpy.types.Object``). Mesh /
    Material / NodeTree updates that don't surface as an Object change
    do NOT invalidate the token — a decorator that caches material- or
    mesh-data-derived state must gate on a separate signal."""
    global _DECORATOR_CACHE_TOKEN
    if len(args) >= 2:
        depsgraph = args[1]
        if depsgraph is not None and hasattr(depsgraph, "updates"):
            if not any(
                (getattr(u, "is_updated_geometry", False) or getattr(u, "is_updated_transform", False))
                and hasattr(u, "id")
                and isinstance(u.id, bpy.types.Object)
                for u in depsgraph.updates
            ):
                return
    _DECORATOR_CACHE_TOKEN += 1


def _hooks() -> tuple[Any, ...]:
    return (
        bpy.app.handlers.depsgraph_update_post,
        bpy.app.handlers.undo_post,
        bpy.app.handlers.redo_post,
        bpy.app.handlers.load_post,
    )


def install_decorator_cache_handlers() -> None:
    """Append the bump handler to each hook; idempotent."""
    for hook in _hooks():
        if _bump_decorator_cache_token not in hook:
            hook.append(_bump_decorator_cache_token)


def uninstall_decorator_cache_handlers() -> None:
    for hook in _hooks():
        try:
            hook.remove(_bump_decorator_cache_token)
        except ValueError:
            pass


class TokenCache(Generic[T]):
    """Memoise a single value keyed on ``(caller_key, get_decorator_cache_token())``.

    The token component invalidates the cache on depsgraph / undo / redo / load,
    so cached ``bpy.types.Object`` references can't outlive the underlying ID
    blocks. Holds exactly one entry — last key wins."""

    __slots__ = ("_key", "_value")

    def __init__(self) -> None:
        self._key: tuple[Any, int] | None = None
        self._value: T | None = None

    def get_or_compute(self, key: Any, compute: Callable[[], T]) -> T:
        token_key = (key, _DECORATOR_CACHE_TOKEN)
        if token_key == self._key:
            return self._value  # type: ignore[return-value]
        value = compute()
        self._key = token_key
        self._value = value
        return value
