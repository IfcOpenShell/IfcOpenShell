# SPDX-License-Identifier: LGPL-3.0-or-later

from __future__ import annotations

import re
import shutil
import subprocess
import threading
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ParsedTranslationUnit:
    records: tuple[dict, ...]
    enums: tuple[dict, ...]
    functions: dict[str, tuple[dict, ...]]


_CONFIG_LOCK = threading.Lock()
_CONFIGURED_LIBRARY: Path | None = None


def _compiler_output(compiler: str, *args: str) -> str:
    proc = subprocess.run(
        [compiler, *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            proc.stderr.strip() or f"Unable to query compiler '{compiler}'"
        )
    return proc.stdout.strip()


def _matching_libclang(compiler: str) -> Path | None:
    resource_dir_text = _compiler_output(compiler, "-print-resource-dir")
    resource_dir = Path(resource_dir_text)
    library_dir = (
        resource_dir.parents[1]
        if len(resource_dir.parents) > 1
        else resource_dir.parent
    )
    names = ("libclang.dylib", "libclang.so", "libclang.dll")
    for directory in (library_dir, library_dir.parent / "bin"):
        for name in names:
            candidate = directory / name
            if candidate.exists():
                return candidate.resolve()
        versioned = sorted(
            directory.glob("libclang.so.*"),
            key=lambda path: tuple(
                int(part)
                for part in re.findall(r"\d+", path.name.removeprefix("libclang.so."))
            ),
            reverse=True,
        )
        if versioned:
            return versioned[0].resolve()
    return None


def _configure_libclang(compiler: str):
    global _CONFIGURED_LIBRARY
    from clang import cindex

    compiler = shutil.which(compiler) or compiler
    library = _matching_libclang(compiler)
    if library is None:
        raise RuntimeError(
            f"Unable to find a libclang library matching compiler '{compiler}'"
        )
    with _CONFIG_LOCK:
        if _CONFIGURED_LIBRARY is not None:
            if _CONFIGURED_LIBRARY != library:
                raise RuntimeError(
                    "One binding discovery process cannot use multiple Clang compilers"
                )
            return cindex
        cindex.Config.set_compatibility_check(False)
        cindex.Config.set_library_file(str(library))
        _CONFIGURED_LIBRARY = library
        return cindex


def _system_include_args(compiler: str) -> tuple[str, ...]:
    proc = subprocess.run(
        [compiler, "-E", "-x", "c++", "-", "-v"],
        input="",
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            proc.stderr.strip() or f"Unable to query compiler '{compiler}'"
        )
    in_search = False
    args: list[str] = []
    for raw_line in proc.stderr.splitlines():
        line = raw_line.strip()
        if line == "#include <...> search starts here:":
            in_search = True
            continue
        if line == "End of search list.":
            break
        if not in_search or not line:
            continue
        framework_suffix = " (framework directory)"
        if line.endswith(framework_suffix):
            args.extend(("-iframework", line.removesuffix(framework_suffix)))
        else:
            args.extend(("-isystem", line))
    return tuple(args)


def _project_root(source: Path) -> Path:
    for directory in (source.parent, *source.parents):
        if (directory / ".git").exists():
            return directory
    return source.parent


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False


def _kind_id(cursor) -> int:
    return cursor._kind_id  # noqa: SLF001


def _qualified_name(cursor, kinds) -> str:
    names: list[str] = []
    current = cursor
    included_kinds = {
        kinds.NAMESPACE.value,
        kinds.CLASS_DECL.value,
        kinds.STRUCT_DECL.value,
        kinds.CLASS_TEMPLATE.value,
    }
    while current is not None and _kind_id(current) != kinds.TRANSLATION_UNIT.value:
        if _kind_id(current) in included_kinds and current.spelling:
            names.append(current.spelling)
        current = current.semantic_parent
    return "::".join(reversed(names))


def _template_argument_count(spelling: str) -> int | None:
    start = spelling.find("<")
    if start == -1 or not spelling.rstrip().endswith(">"):
        return None
    depth = 0
    count = 1
    for char in spelling[start + 1 : spelling.rfind(">")]:
        if char == "<":
            depth += 1
        elif char == ">":
            depth -= 1
        elif char == "," and depth == 0:
            count += 1
    return count


def _references_incomplete_declaration(cpp_type) -> bool:
    current = cpp_type
    while str(current.kind).rsplit(".", 1)[-1] in {
        "POINTER",
        "LVALUEREFERENCE",
        "RVALUEREFERENCE",
    }:
        current = current.get_pointee()
    declaration = current.get_declaration()
    return bool(declaration.spelling) and not declaration.is_definition()


def _type_info(cpp_type, current_scope: str = "") -> dict[str, str]:
    raw_spelling = cpp_type.spelling
    result = {"qualType": raw_spelling}
    canonical = cpp_type.get_canonical().spelling
    raw_arg_count = _template_argument_count(raw_spelling)
    canonical_arg_count = _template_argument_count(canonical)
    compiler_added_default_args = (
        raw_arg_count is not None
        and canonical_arg_count is not None
        and canonical_arg_count > raw_arg_count
        and raw_spelling.split("<", 1)[0].rsplit("::", 1)[-1]
        == canonical.split("<", 1)[0].rsplit("::", 1)[-1]
    )
    if (
        canonical
        and canonical != raw_spelling
        and not compiler_added_default_args
        and not _references_incomplete_declaration(cpp_type)
    ):
        result["desugaredQualType"] = canonical
    return result


def _enum_constant_literal(cursor, kinds) -> str | None:
    prefix = "ifcapi.literal:"
    for child in cursor.get_children():
        if _kind_id(child) != kinds.ANNOTATE_ATTR.value:
            continue
        annotation = child.spelling or child.displayname
        if annotation.startswith(prefix):
            return annotation.removeprefix(prefix)
    return None


def _clean_comment(comment: str | None) -> str | None:
    if not comment:
        return None
    text = comment.strip()
    if text.startswith(("/**", "/*!")) and text.endswith("*/"):
        text = text[3:-2]
    lines = []
    for line in text.splitlines():
        line = re.sub(r"^\s*(?://[/!]|\*)\s?", "", line).rstrip()
        lines.append(line)
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) or None


def _access_name(cursor) -> str | None:
    access = str(cursor.access_specifier).rsplit(".", 1)[-1].lower()
    return access if access in {"public", "protected", "private"} else None


def _param_node(cursor, current_scope: str) -> dict:
    return {
        "kind": "ParmVarDecl",
        "name": cursor.spelling,
        "type": _type_info(cursor.type, current_scope),
    }


def _record_node(cursor, kinds) -> dict:
    current_scope = _qualified_name(cursor, kinds)
    inner: list[dict] = []
    bases: list[dict] = []
    active_access: str | None = None
    for child in cursor.get_children():
        kind = _kind_id(child)
        if kind == kinds.CXX_BASE_SPECIFIER.value:
            bases.append({"type": _type_info(child.type, current_scope)})
            continue
        if kind not in {
            kinds.CXX_METHOD.value,
            kinds.CONSTRUCTOR.value,
            kinds.FIELD_DECL.value,
        }:
            continue
        access = _access_name(child)
        if access is not None and access != active_access:
            inner.append({"kind": "AccessSpecDecl", "access": access})
            active_access = access
        params = [
            _param_node(item, current_scope)
            for item in child.get_children()
            if _kind_id(item) == kinds.PARM_DECL.value
        ]
        if kind == kinds.CXX_METHOD.value:
            suffix = " const" if child.is_const_method() else ""
            node = {
                "kind": "CXXMethodDecl",
                "name": child.spelling,
                "returnType": _type_info(child.result_type, current_scope),
                "type": {
                    "qualType": f"{child.result_type.spelling} ({', '.join(param['type']['qualType'] for param in params)}){suffix}"
                },
                "inner": params,
            }
        elif kind == kinds.CONSTRUCTOR.value:
            node = {
                "kind": "CXXConstructorDecl",
                "name": child.spelling,
                "inner": params,
                "isDeleted": child.is_deleted_method(),
            }
        else:
            tokens = [token.spelling for token in child.get_tokens()]
            try:
                name_index = tokens.index(child.spelling)
            except ValueError:
                name_index = len(tokens)
            node = {
                "kind": "FieldDecl",
                "name": child.spelling,
                "type": _type_info(child.type, current_scope),
                "doc": _clean_comment(child.raw_comment),
                "hasInitializer": any(
                    token in {"=", "{"} for token in tokens[name_index + 1 :]
                ),
            }
        inner.append(node)
    return {
        "kind": "CXXRecordDecl",
        "name": cursor.spelling,
        "qualifiedName": _qualified_name(cursor, kinds),
        "completeDefinition": True,
        "tagUsed": "struct" if _kind_id(cursor) == kinds.STRUCT_DECL.value else "class",
        "bases": bases,
        "inner": inner,
    }


def _function_node(cursor, kinds) -> dict:
    current_scope = _qualified_name(cursor.semantic_parent, kinds)
    params = [
        _param_node(item, current_scope)
        for item in cursor.get_children()
        if _kind_id(item) == kinds.PARM_DECL.value
    ]
    return {
        "kind": "FunctionDecl",
        "name": cursor.spelling,
        "namespace": current_scope,
        "returnType": _type_info(cursor.result_type, current_scope),
        "type": {
            "qualType": f"{cursor.result_type.spelling} ({', '.join(param['type']['qualType'] for param in params)})"
        },
        "inner": params,
    }


def parse_translation_unit(command) -> ParsedTranslationUnit:
    cindex = _configure_libclang(command.arguments[0])
    source = str(command.file)
    args: list[str] = []
    skip_next = False
    for token in command.arguments[1:]:
        if skip_next:
            skip_next = False
            continue
        if token == "-o":
            skip_next = True
            continue
        if token in {"-c", source}:
            continue
        args.append(token)
    args.extend(_system_include_args(command.arguments[0]))
    translation_unit = cindex.Index.create().parse(
        source,
        args=args,
        options=cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
    )
    errors = [
        str(item)
        for item in translation_unit.diagnostics
        if item.severity >= cindex.Diagnostic.Error
    ]
    if errors:
        raise RuntimeError("\n".join(errors))

    kinds = cindex.CursorKind
    project_root = command.project_root or _project_root(command.file)
    records: list[dict] = []
    enums: list[dict] = []
    functions: dict[str, list[dict]] = defaultdict(list)
    stack = list(translation_unit.cursor.get_children())
    while stack:
        cursor = stack.pop()
        location_file = cursor.location.file
        if location_file is None or not _is_under(
            Path(str(location_file)), project_root
        ):
            continue
        kind = _kind_id(cursor)
        if (
            kind
            in {
                kinds.CLASS_DECL.value,
                kinds.STRUCT_DECL.value,
                kinds.CLASS_TEMPLATE.value,
            }
            and cursor.is_definition()
        ):
            records.append(_record_node(cursor, kinds))
        elif kind == kinds.ENUM_DECL.value and cursor.spelling:
            parent_name = _qualified_name(cursor.semantic_parent, kinds)
            enums.append(
                {
                    "kind": "EnumDecl",
                    "name": cursor.spelling,
                    "qualifiedName": "::".join(
                        item for item in (parent_name, cursor.spelling) if item
                    ),
                    "inner": [
                        {
                            "kind": "EnumConstantDecl",
                            "name": child.spelling,
                            "value": child.enum_value,
                            "literal": _enum_constant_literal(child, kinds),
                        }
                        for child in cursor.get_children()
                        if _kind_id(child) == kinds.ENUM_CONSTANT_DECL.value
                    ],
                }
            )
        elif kind in {kinds.TYPEDEF_DECL.value, kinds.TYPE_ALIAS_DECL.value}:
            declaration = cursor.underlying_typedef_type.get_declaration()
            if _kind_id(declaration) == kinds.ENUM_DECL.value:
                parent_name = _qualified_name(cursor.semantic_parent, kinds)
                enums.append(
                    {
                        "kind": "EnumDecl",
                        "name": cursor.spelling,
                        "qualifiedName": "::".join(
                            item for item in (parent_name, cursor.spelling) if item
                        ),
                    }
                )
        elif kind == kinds.FUNCTION_DECL.value:
            node = _function_node(cursor, kinds)
            functions[node["namespace"]].append(node)
        stack.extend(cursor.get_children())
    return ParsedTranslationUnit(
        records=tuple(records),
        enums=tuple(enums),
        functions={name: tuple(items) for name, items in functions.items()},
    )
