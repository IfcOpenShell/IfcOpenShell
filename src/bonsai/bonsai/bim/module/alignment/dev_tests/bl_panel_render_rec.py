# This file was generated with the assistance of an AI coding tool.
# Development test script for the alignment authoring work -- remove before the final PR (see README.md).

class Rec:
    """Records what a panel's draw() puts on screen: labels, operators, props."""

    def __init__(self, out, depth=0):
        self.out, self.depth = out, depth

    def _child(self, *a, **k):
        return Rec(self.out, self.depth + 1)

    row = column = box = split = column_flow = grid_flow = _child

    def label(self, text="", icon="NONE", **k):
        self.out.append("  " * self.depth + f"label: {text}")

    def operator(self, idname, text=None, **k):
        self.out.append("  " * self.depth + f"op: {idname} {text!r}")
        return type("OpProps", (), {"__setattr__": lambda s, n, v: None})()

    def prop(self, data, name, text=None, **k):
        self.out.append("  " * self.depth + f"prop: {name}")

    def template_list(self, *a, **k):
        self.out.append("  " * self.depth + f"list: {a[0]}")

    def separator(self, *a, **k):
        pass

    def __setattr__(self, name, value):
        if name in ("out", "depth"):
            object.__setattr__(self, name, value)


