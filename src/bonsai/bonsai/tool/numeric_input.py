# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from dataclasses import dataclass, field
from typing import Literal, Protocol

ModalResult = Literal["RUNNING_MODAL", "FINISHED", "CANCELLED"]


class IntegerInputOperator(Protocol):
    """Protocol for operators using IntegerInputState."""

    _input: "IntegerInputState"

    def _apply_value(self, context) -> None: ...
    def _restore_value(self, context) -> None: ...
    def _format_header(self) -> str: ...


@dataclass
class IntegerInputState:
    """State for keyboard integer input during modal operations."""

    characters: list[str] = field(default_factory=list)
    is_valid: bool = True
    min_value: int = 1
    _user_started_typing: bool = False

    @classmethod
    def from_value(cls, value: int, min_value: int = 1) -> "IntegerInputState":
        """Create state initialized with an existing value."""
        return cls(
            characters=list(str(value)),
            is_valid=True,
            min_value=min_value,
            _user_started_typing=False,
        )

    def get_input_string(self) -> str:
        return "".join(self.characters)

    def get_value(self) -> int | None:
        """Return parsed integer value, or None if invalid."""
        if not self.characters:
            return None
        try:
            value = int(self.get_input_string())
            return value if value >= self.min_value else None
        except ValueError:
            return None

    def handle_digit(self, digit: str) -> None:
        """Handle a digit key press."""
        if not self._user_started_typing:
            self.characters.clear()
            self._user_started_typing = True
        self.characters.append(digit)
        self._update_validity()

    def handle_backspace(self) -> None:
        """Handle backspace key press."""
        self._user_started_typing = True
        if self.characters:
            self.characters.pop()
        self._update_validity()

    def _update_validity(self) -> None:
        """Update is_valid based on current input."""
        self.is_valid = self.get_value() is not None


def handle_numeric_event(state: IntegerInputState, event) -> tuple[bool, ModalResult | None]:
    """
    Process a Blender event for numeric input.

    Returns:
        (handled, result):
        - handled: True if the event was consumed
        - result: "FINISHED", "CANCELLED", or None if still running
    """
    if event.value != "PRESS":
        return False, None

    # Digit input
    if event.ascii and event.ascii in "0123456789":
        state.handle_digit(event.ascii)
        return True, None

    # Backspace
    if event.type == "BACK_SPACE":
        state.handle_backspace()
        return True, None

    # Confirm
    if event.type in {"RET", "NUMPAD_ENTER"}:
        if state.is_valid:
            return True, "FINISHED"
        return True, None  # Invalid - don't confirm yet

    # Click confirm
    if event.type == "LEFTMOUSE":
        if state.characters and state.is_valid:
            return True, "FINISHED"
        return True, "FINISHED"  # Empty or invalid - still finish

    # Cancel
    if event.type in {"ESC", "RIGHTMOUSE"}:
        return True, "CANCELLED"

    return False, None


def run_integer_input_modal(op: IntegerInputOperator, context, event) -> set[str]:
    """
    Run the modal loop for an integer input operator.

    The operator must implement:
    - _input: IntegerInputState
    - _apply_value(context): Apply the current input value
    - _restore_value(context): Restore original value on cancel
    - _format_header(): Return the header string to display

    Returns the Blender modal return set (e.g., {"RUNNING_MODAL"}).
    """
    handled, result = handle_numeric_event(op._input, event)

    if handled:
        if result == "FINISHED":
            op._apply_value(context)
            cleanup_header(context)
            return {"FINISHED"}
        elif result == "CANCELLED":
            op._restore_value(context)
            cleanup_header(context)
            return {"CANCELLED"}
        else:
            op._apply_value(context)
            update_header(context, op._format_header())
            return {"RUNNING_MODAL"}

    return {"RUNNING_MODAL"}


def update_header(context, text: str) -> None:
    """Update the area header text."""
    if context.area:
        context.area.header_text_set(text)


def cleanup_header(context) -> None:
    """Clear the area header text."""
    if context.area:
        context.area.header_text_set(None)
