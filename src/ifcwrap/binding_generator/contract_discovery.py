from __future__ import annotations

import re


_COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", re.MULTILINE | re.DOTALL)
_ANNOTATIONS = frozenset(
    {
        "IFCAPI_OWNED",
        "IFCAPI_COPY",
        "IFCAPI_STATIC",
    }
)
_ANNOTATION_CALLS: tuple[str, ...] = ()


def _strip_comments(text: str) -> str:
    return _COMMENT_RE.sub("", text)


def _split_params(params: str) -> tuple[str, ...]:
    params = params.strip()
    if not params or params == "void":
        return ()
    result: list[str] = []
    start = 0
    angle_depth = paren_depth = bracket_depth = 0
    for index, char in enumerate(params):
        if char == "<":
            angle_depth += 1
        elif char == ">" and angle_depth:
            angle_depth -= 1
        elif char == "(":
            paren_depth += 1
        elif char == ")" and paren_depth:
            paren_depth -= 1
        elif char == "[":
            bracket_depth += 1
        elif char == "]" and bracket_depth:
            bracket_depth -= 1
        elif char == "," and not angle_depth and not paren_depth and not bracket_depth:
            result.append(params[start:index].strip())
            start = index + 1
    result.append(params[start:].strip())
    return tuple(param for param in result if param)


def _leading_annotations(text: str) -> tuple[frozenset[str], str]:
    annotations: list[str] = []
    rest = text.strip()
    while True:
        match = re.match(r"(?P<token>IFCAPI_[A-Z_]+(?:\s*\([^)]*\))?)(?=\s|$)", rest)
        if match is None:
            break
        token = " ".join(match.group("token").split())
        if token not in _ANNOTATIONS and not any(
            token.startswith(f"{name}(") for name in _ANNOTATION_CALLS
        ):
            break
        annotations.append(token)
        rest = rest[match.end() :].strip()
    return frozenset(annotations), rest


def _param_name(param: str) -> str:
    param = param.split("=", 1)[0].strip()
    matches = re.findall(r"\b([A-Za-z_]\w*)\b(?=\s*(?:\[[^\]]*\])?\s*$)", param)
    if not matches:
        msg = f"Unable to determine parameter name from contract declaration parameter: {param!r}"
        raise ValueError(msg)
    return matches[-1]


def _has_default(param: str) -> bool:
    angle_depth = paren_depth = bracket_depth = 0
    for char in param:
        if char == "<":
            angle_depth += 1
        elif char == ">" and angle_depth:
            angle_depth -= 1
        elif char == "(":
            paren_depth += 1
        elif char == ")" and paren_depth:
            paren_depth -= 1
        elif char == "[":
            bracket_depth += 1
        elif char == "]" and bracket_depth:
            bracket_depth -= 1
        elif char == "=" and not angle_depth and not paren_depth and not bracket_depth:
            return True
    return False


def _clean_doc_comment(raw: str | None) -> str | None:
    if raw is None:
        return None
    lines: list[str] = []
    for raw_line in raw.strip().splitlines():
        line = raw_line.strip()
        if line.startswith("/**") or line.startswith("/*!"):
            line = line[3:].strip()
        elif line.startswith("/*"):
            line = line[2:].strip()
        if line.endswith("*/"):
            line = line[:-2].strip()
        if line.startswith("///") or line.startswith("//!"):
            line = line[3:].strip()
        if line.startswith("*"):
            line = line[1:].strip()
        lines.append(line)
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    doc = "\n".join(lines).strip()
    return doc or None
