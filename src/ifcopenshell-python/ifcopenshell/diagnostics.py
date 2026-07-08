# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""Crash diagnostics for invalid IFC files.

Many crashes deep inside geometry or utility code are not really bugs in the
code. They are the symptom of an invalid file: a required attribute that is not
set, a reference that points at nothing, a value of the wrong type. Guarding
every call site against every possible schema violation is not maintainable, so
instead of being defensive everywhere this module turns a raised exception into
a report that points at the entity most likely responsible.

Given an exception (or the one currently being handled), :func:`diagnose` walks
the traceback, collects the :class:`ifcopenshell.entity_instance` objects that
were live in the frames, validates them with :func:`ifcopenshell.validate` and
ranks them by how likely each is to be the cause. A schema invalid entity that
sat in the crashing frame is the strongest suspect. An invalid entity that the
crashing frame's entity referenced is the next strongest. The result stringifies
to a human readable report.

Example:

.. code:: python

    import ifcopenshell.diagnostics

    try:
        ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    except Exception as e:
        report = ifcopenshell.diagnostics.diagnose(e)
        print(report)
        culprit = report.likely_cause  # the top ranked entity, or None
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from types import TracebackType
from typing import Optional, Union

import ifcopenshell
import ifcopenshell.validate

__all__ = ["Candidate", "DiagnosisReport", "diagnose", "on_error"]

# How the score is built. A schema invalid entity always outranks a valid one.
# Among entities of the same validity, one that appeared directly in a frame
# outranks one only reachable by reference, and a frame closer to the raise
# (lower depth) outranks a frame further away.
_INVALID_BONUS = 10000
_IN_FRAME_BASE = 1000
_REFERENCED_BASE = 500


@dataclass
class Candidate:
    """A single entity considered as a possible cause of the crash."""

    instance: ifcopenshell.entity_instance
    #: Depth of the frame it relates to, 0 being the frame where the exception was raised.
    depth: int
    #: True when the entity itself was a local variable (or one level inside a
    #: container) in a traceback frame. False when it was only reachable by
    #: following a reference from such an entity.
    in_frame: bool
    #: Human description of where the entity was found.
    location: str
    #: Validation errors reported by :func:`ifcopenshell.validate.validate_instance`.
    errors: list[str] = field(default_factory=list)

    @property
    def score(self) -> int:
        score = _IN_FRAME_BASE - self.depth if self.in_frame else _REFERENCED_BASE - self.depth
        if self.errors:
            score += _INVALID_BONUS
        return score

    @property
    def confidence(self) -> str:
        if not self.errors:
            return "low"
        return "high" if self.in_frame else "medium"

    def __str__(self) -> str:
        header = f"{_format_instance(self.instance)}  [{self.confidence} confidence]"
        lines = [header, f"    {self.location}"]
        if self.errors:
            lines.append("    validation:")
            lines.extend(f"      - {e}" for e in self.errors)
        else:
            lines.append("    validation: no schema violations found on this entity")
        return "\n".join(lines)


@dataclass
class DiagnosisReport:
    """The result of :func:`diagnose`, a ranked list of suspect entities."""

    exception: Optional[BaseException]
    candidates: list[Candidate] = field(default_factory=list)

    @property
    def likely_cause(self) -> Optional[ifcopenshell.entity_instance]:
        """The entity most likely responsible, or None if nothing invalid was found."""
        for candidate in self.candidates:
            if candidate.errors:
                return candidate.instance
        return None

    def __str__(self) -> str:
        lines = ["ifcopenshell crash diagnostics"]
        if self.exception is not None:
            lines.append(f"{type(self.exception).__name__}: {self.exception}")

        invalid = [c for c in self.candidates if c.errors]
        if not invalid:
            lines.append("")
            if not self.candidates:
                lines.append("No IFC entities were found in the traceback frames.")
            else:
                lines.append(
                    "No schema violations were found on the entities in the traceback. "
                    "The cause is probably not an invalid file."
                )
                lines.append("")
                lines.append("Entities seen in the traceback:")
                for candidate in self.candidates:
                    lines.append(_indent(str(candidate)))
            return "\n".join(lines)

        top = self.candidates[0]
        lines.append("")
        lines.append(f"Most likely cause ({top.confidence} confidence):")
        lines.append(_indent(str(top)))

        rest = self.candidates[1:]
        if rest:
            lines.append("")
            lines.append("Other candidates considered:")
            for candidate in rest:
                lines.append(_indent(str(candidate)))
        return "\n".join(lines)


def diagnose(
    exception: Optional[BaseException] = None,
    *,
    traceback: Optional[TracebackType] = None,
) -> DiagnosisReport:
    """Produce a report naming the entity most likely responsible for an exception.

    :param exception: The exception to diagnose. When omitted, the exception
        currently being handled is used (``sys.exc_info()``), so this can be
        called from inside an ``except`` block with no arguments.
    :param traceback: The traceback to walk. Defaults to the one attached to
        ``exception``.
    :return: A :class:`DiagnosisReport`. Its ``str()`` is a human readable
        report and ``.likely_cause`` is the top ranked entity or None.
    """
    if exception is None:
        exception = sys.exc_info()[1]
    if traceback is None and exception is not None:
        traceback = exception.__traceback__

    candidates = _collect_candidates(traceback)
    _validate_candidates(candidates)
    candidates.sort(key=lambda c: c.score, reverse=True)
    return DiagnosisReport(exception=exception, candidates=candidates)


@contextmanager
def on_error(reraise: bool = True) -> Iterator[None]:
    """Context manager that prints a diagnosis if the wrapped block raises.

    .. code:: python

        with ifcopenshell.diagnostics.on_error():
            ifcopenshell.util.placement.get_local_placement(placement)

    :param reraise: Re-raise the original exception after reporting. Defaults to True.
    """
    try:
        yield
    except Exception as e:
        report = diagnose(e)
        print(report, file=sys.stderr)
        if reraise:
            raise


def _collect_candidates(traceback: Optional[TracebackType]) -> list[Candidate]:
    # Walk the traceback into a list of frames, innermost last, then reverse so
    # the frame where the exception was raised is at depth 0.
    frames = []
    tb = traceback
    while tb is not None:
        frames.append(tb.tb_frame)
        tb = tb.tb_next
    frames.reverse()

    candidates: list[Candidate] = []
    seen: set[tuple[int, int]] = set()

    # First pass: entities that were live in the frames.
    for depth, frame in enumerate(frames):
        location = f"in frame {frame.f_code.co_name} ({_short_path(frame.f_code.co_filename)}:{frame.f_lineno})"
        for value in frame.f_locals.values():
            for inst in _iter_instances(value):
                key = _key(inst)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(
                    Candidate(instance=inst, depth=depth, in_frame=True, location=f"{location}, as a local variable")
                )

    # Second pass: entities that the frame entities reference directly. Only
    # invalid references are worth reporting, an in-frame entity referencing a
    # perfectly valid one tells us nothing.
    for parent in list(candidates):
        for attr_name, inst in _iter_direct_references(parent.instance):
            key = _key(inst)
            if key in seen:
                continue
            seen.add(key)
            errors = _validate(inst)
            if not errors:
                continue
            location = (
                f"referenced by {_format_instance(parent.instance)} via .{attr_name}, "
                f"{parent.location.split(', ')[0]}"
            )
            candidates.append(
                Candidate(instance=inst, depth=parent.depth, in_frame=False, location=location, errors=errors)
            )

    return candidates


def _validate_candidates(candidates: list[Candidate]) -> None:
    for candidate in candidates:
        if candidate.in_frame:
            candidate.errors = _validate(candidate.instance)


def _validate(inst: ifcopenshell.entity_instance) -> list[str]:
    logger = ifcopenshell.validate.json_logger()
    try:
        ifcopenshell.validate.validate_instance(inst, logger)
    except Exception:
        # A non-entity (a simple or select value) or an unexpected schema issue.
        # It cannot be validated per-instance, so it contributes no findings.
        return []
    messages = []
    for statement in logger.statements:
        attribute = statement.get("attribute")
        message = statement.get("message", "")
        messages.append(f"{attribute}: {message}" if attribute else message)
    return messages


def _iter_instances(value: object, _depth: int = 0) -> Iterator[ifcopenshell.entity_instance]:
    """Yield entity instances in ``value``, descending one level into containers."""
    if isinstance(value, ifcopenshell.entity_instance):
        # Only numbered instances are real entities we can validate. Simple and
        # select values carry id 0 and are not per-instance validatable.
        if value.id() != 0:
            yield value
    elif _depth == 0 and isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            yield from _iter_instances(item, _depth + 1)
    elif _depth == 0 and isinstance(value, dict):
        for item in value.values():
            yield from _iter_instances(item, _depth + 1)


def _iter_direct_references(inst: ifcopenshell.entity_instance) -> Iterator[tuple[str, ifcopenshell.entity_instance]]:
    """Yield (attribute name, entity) for entities directly referenced by ``inst``."""
    try:
        count = len(inst)
    except Exception:
        return
    for i in range(count):
        try:
            value = inst[i]
            name = inst.attribute_name(i)
        except Exception:
            continue
        for ref in _iter_instances(value):
            yield name, ref


def _key(inst: ifcopenshell.entity_instance) -> tuple[int, int]:
    return (id(inst.file), inst.id())


def _format_instance(inst: ifcopenshell.entity_instance) -> str:
    text = str(inst)
    if len(text) > 120:
        text = text[:117] + "..."
    return text


def _short_path(path: str) -> str:
    marker = "ifcopenshell"
    idx = path.replace("\\", "/").rfind(marker + "/")
    if idx != -1:
        return path.replace("\\", "/")[idx:]
    return path.rsplit("/", 1)[-1]


def _indent(text: str, prefix: str = "  ") -> str:
    return "\n".join(prefix + line for line in text.splitlines())
