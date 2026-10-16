# This file was generated with the assistance of an AI coding tool.
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Small AST pattern matcher; target-language knowledge lives in the selected YAML rules."""

import argparse
import ast
import json
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, StrictUndefined


def match(pattern, value, captures):
    if isinstance(pattern, str) and pattern.startswith("$"):
        key = pattern[1:]
        if key in captures:
            describe = lambda v: ast.dump(v) if isinstance(v, ast.AST) else repr(v)
            return describe(value) == describe(captures[key])
        captures[key] = value
        return True
    if isinstance(pattern, dict):
        return isinstance(value, ast.AST) and all(
            type(value).__name__ == expected
            if key == "node"
            else hasattr(value, key) and match(expected, getattr(value, key), captures)
            for key, expected in pattern.items()
        )
    if isinstance(pattern, list):
        return (
            isinstance(value, list)
            and len(pattern) == len(value)
            and all(match(p, v, captures) for p, v in zip(pattern, value))
        )
    return pattern == value


class Transpiler:
    def __init__(self, rules):
        self.rules = yaml.safe_load(Path(rules).read_text(encoding="utf-8"))
        self.scope = {}
        self.depth = 0
        self.unsupported = []
        self.functions = {}
        self.symbols = {}
        self.aliases = {}
        self.return_annotation = None
        self.declared = []
        self.env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
        self.env.filters.update(
            emit=self.emit,
            type=lambda n: self.emit(n, "types"),
            kind=lambda n: self.emit(n, "inference"),
            condition=lambda n: self.emit(n, context="condition"),
            iterable=lambda n: self.emit(n, context="iterable"),
            literal=json.dumps,
        )

    def render(self, template, captures):
        return self.env.from_string(template).render(self.context(captures))

    def context(self, captures):
        return dict(
            self.rules,
            functions=self.functions,
            symbols=self.symbols,
            aliases=self.aliases,
            return_annotation=self.return_annotation,
            declared=self.declared,
            **captures,
        )

    def emit(self, node, mode="rules", context="expression"):
        if isinstance(node, list):
            return "\n".join(filter(None, (self.emit(n, mode) for n in node)))
        for rule in self.rules[mode]:
            if rule.get("context", "expression") != context:
                continue
            captures = {}
            if match(rule["input"], node, captures) and all(
                isinstance(captures[name], ast.Name) and self.scope.get(captures[name].id) == expected
                for name, expected in rule.get("where", {}).items()
            ):
                if "when" in rule and not self.env.compile_expression(rule["when"])(**self.context(captures)):
                    continue
                captures["top_level"] = self.depth == 0
                if isinstance(node, ast.FunctionDef):
                    # Binding discovery is shared by targets; declaration syntax remains in YAML.
                    bindings = {
                        n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
                    }
                    parameters = {a.arg for a in node.args.args}
                    captures["locals"] = sorted(bindings - parameters)
                self.depth += 1
                try:
                    return self.render(rule["output"], captures)
                finally:
                    self.depth -= 1
        code = ast.unparse(node) if isinstance(node, ast.AST) else repr(node)
        raise ValueError(f"No {mode} rule at line {getattr(node, 'lineno', '?')}: {code[:180]}")

    def translate(self, source):
        module = ast.parse(source)
        self.functions = {n.name: n for n in module.body if isinstance(n, ast.FunctionDef)}
        self.aliases = {
            n.targets[0].id: [e.value for e in n.value.slice.elts]
            for n in module.body
            if isinstance(n, ast.Assign)
            and isinstance(n.value, ast.Subscript)
            and isinstance(n.value.value, ast.Name)
            and n.value.value.id == "Literal"
        }
        self.unsupported = []
        self.symbols = {}
        output = []
        for node in module.body:
            self.scope = (
                {a.arg: ast.unparse(a.annotation) for a in node.args.args if a.annotation}
                if isinstance(node, ast.FunctionDef)
                else {}
            )
            globals_ = self.symbols.copy()
            self.declared = list(self.scope)
            self.return_annotation = node.returns if isinstance(node, ast.FunctionDef) else None
            if isinstance(node, ast.FunctionDef):
                self.symbols.update({a.arg: self.emit(a.annotation, "annotation_kinds") for a in node.args.args})
            # Resolve local data shapes without embedding target-language decisions here.
            bindings = [n for n in ast.walk(node) if isinstance(n, (ast.Assign, ast.AnnAssign, ast.NamedExpr))]
            for _ in range(len(bindings) + 1):
                previous = self.symbols.copy()
                for binding in bindings:
                    value = binding.value
                    kind = self.emit(value, "inference")
                    targets = binding.targets if isinstance(binding, ast.Assign) else [binding.target]
                    for target in targets:
                        if isinstance(target, ast.Name) and kind != "unknown":
                            self.symbols[target.id] = kind
                if previous == self.symbols:
                    break
            try:
                result = self.emit(node).rstrip()
            except ValueError as error:
                name = getattr(node, "name", f"line {node.lineno}")
                self.unsupported.append(f"{name}: {error}")
                if not isinstance(node, ast.FunctionDef):
                    raise  # Never silently discard module data.
                result = self.render(self.rules["unsupported"], {"name": name, "reason": str(error)})
            if result:
                output.append(result)
            if isinstance(node, ast.FunctionDef):
                self.symbols = globals_
        return "\n\n".join(output) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--rules", type=Path, default=Path(__file__).with_name("ts.yaml"))
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    compiler = Transpiler(args.rules)
    result = compiler.translate(args.source.read_text(encoding="utf-8"))
    for diagnostic in compiler.unsupported:
        print(diagnostic, file=sys.stderr)
    print(
        f"Translated {len(compiler.functions) - len(compiler.unsupported)}/{len(compiler.functions)} functions",
        file=sys.stderr,
    )
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
