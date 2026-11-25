# This file was generated with the assistance of an AI coding tool.

from ...abi_ir import CFunctionIR
from .._shared import _public_name


def public_name(function: CFunctionIR, c_prefix: str) -> str:
    name = _public_name(function, c_prefix)
    if function.receiver == "file":
        return {
            "create": "createByDeclaration",
            "getInverse": "getInverseList",
            "schema": "schemaDefinition",
            "schemaName": "schemaIdentifier",
        }.get(name, name)
    return name
