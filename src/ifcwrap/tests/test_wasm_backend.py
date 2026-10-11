# SPDX-License-Identifier: LGPL-3.0-or-later

from __future__ import annotations

import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from src.ifcwrap.binding_generator.abi_ir import (
    BindingABI,
    CFieldIR,
    CFunctionIR,
    CParamIR,
    CTypeIR,
)
from src.ifcwrap.binding_generator.binding_model import TypeSpec
from src.ifcwrap.binding_generator.targets.wasm.backend import render_wasm_bindings
from src.ifcwrap.binding_generator.targets.wasm.js_glue import _render_handle_classes


def make_metadata() -> BindingABI:
    file_handle = CTypeIR(
        c_type="ifcopenshell_file_t",
        kind="handle",
        fields=(CFieldIR("ptr", "void*"), CFieldIR("owned", "bool")),
        destroy_function="ifcopenshell_file_destroy",
        layout="ptr_owned",
    )
    open_function = CFunctionIR(
        c_name="ifcopenshell_parse_open",
        restype="bool",
        params=(
            CParamIR("path", "const char*", "param", "string"),
            CParamIR("streaming", "bool", "param", "bool"),
            CParamIR(
                "out_result",
                "ifcopenshell_file_t**",
                "out_result",
                "handle",
            ),
        ),
        error_policy="bool_return_last_error",
        returns=TypeSpec(kind="handle", handle="file"),
        receiver=None,
    )
    return BindingABI(
        module="ifcopenshell",
        c_prefix="ifcopenshell",
        handles={"file": file_handle},
        value_types={},
        functions={
            open_function.c_name: open_function,
        },
        error_functions={
            "clear_error": "ifcopenshell_clear_error",
            "last_error_message": "ifcopenshell_last_error_message",
            "last_error_kind": "ifcopenshell_last_error_kind",
            "last_error_code": "ifcopenshell_last_error_code",
        },
    )


def test_wasm_glue_wraps_handles() -> None:
    javascript, _ = render_wasm_bindings(make_metadata())

    assert "ifcopenshell_parse_open" in javascript
    assert "ifcopenshell_file_destroy" in javascript
    assert "class IfcOpenshellFile" in javascript
    assert "UTF8ToString" in javascript
    assert (
        "await module.loadDynamicLibrary(path, { loadAsync: true, global: true, allowUndefined: true });" in javascript
    )
    assert "IfcOpenShellErrorKind.CANCELLED" in javascript
    assert "IfcOpenShellErrorCode.OPERATION_CANCELLED" in javascript
    assert "Cyclic WASM plugin dependency" in javascript


def test_typescript_declares_low_level_contract() -> None:
    _, declarations = render_wasm_bindings(make_metadata())

    assert "export class IfcOpenshellFile" in declarations
    assert "open(path: string, streaming: boolean)" in declarations
    assert "CANCELLED: 4" in declarations


def test_gc_handles_and_instance_arrays(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute generated JavaScript")
    metadata = make_metadata()
    handles = dict(metadata.handles)
    for name, c_type in [
        ("instance", "ifcopenshell_instance_t"),
        ("instance_list", "ifcopenshell_parse_instance_list_t"),
        ("geom_iterator", "ifcopenshell_geom_iterator_t"),
    ]:
        handles[name] = CTypeIR(
            c_type=c_type, kind="handle", fields=(), destroy_function=c_type.removesuffix("_t") + "_destroy"
        )
    functions = {}
    for name, returns in [("size", TypeSpec(kind="size")), ("get", TypeSpec(kind="handle", handle="instance"))]:
        function = replace(
            metadata.functions["ifcopenshell_parse_open"],
            c_name=f"ifcopenshell_parse_instance_list_{name}",
            receiver="instance_list",
            params=(CParamIR("self", "ifcopenshell_parse_instance_list_t*", "receiver", "handle"),),
            returns=returns,
        )
        functions[function.c_name] = function
    metadata = replace(metadata, handles=handles, functions=functions)
    _, declarations = render_wasm_bindings(metadata)
    assert "get(): IfcOpenshellInstance;" in declarations
    instance_decl = declarations.split("export class IfcOpenshellInstance {")[1].split("\n  }")[0]
    assert "dispose" not in instance_decl
    assert "export class IfcOpenshellGeomIterator" in declarations
    (tmp_path / "api.mjs").write_text(
        _render_handle_classes(metadata)
        + """
function invoke_ifcopenshell_parse_instance_list_size(module, self) { return 2; }
function invoke_ifcopenshell_parse_instance_list_get(module, self) {
    return new IfcOpenshellInstance(++module.next, true, module);
}
export const wrapList = _wrapIfcOpenshellParseInstanceList;
"""
    )
    (tmp_path / "test.mjs").write_text("""
import assert from 'node:assert/strict';
let registry;
globalThis.FinalizationRegistry = class {
    entries = new Map();
    constructor(callback) { this.callback = callback; registry = this; }
    register(target, held, token) { this.entries.set(token, held); }
    unregister(token) { return this.entries.delete(token); }
};
const api = await import('./api.mjs');
const destroyed = [];
const module = { next: 100,
    _ifcopenshell_instance_destroy: ptr => destroyed.push(['instance', ptr]),
    _ifcopenshell_parse_instance_list_destroy: ptr => destroyed.push(['list', ptr]),
    _ifcopenshell_geom_iterator_destroy: ptr => destroyed.push(['iterator', ptr]),
};
const items = api.wrapList(42, true, module);
assert(Array.isArray(items));
assert.equal(items.length, 2);
assert.deepEqual(destroyed, [['list', 42]]);
for (const item of items) {
    assert.equal(item.dispose, undefined);
    assert.equal(item[Symbol.dispose], undefined);
    assert(registry.entries.has(item));
}
const transferred = new api.IfcOpenshellInstance(items[0]);
assert.equal(items[0].ptr, 0);
assert(!registry.entries.has(items[0]));
assert(registry.entries.has(transferred));
registry.callback(registry.entries.get(transferred));
assert.deepEqual(destroyed.at(-1), ['instance', 101]);
const iterator = new api.IfcOpenshellGeomIterator(43, true, module);
iterator[Symbol.dispose]();
iterator.dispose();
assert(!registry.entries.has(iterator));
assert.equal(iterator.ptr, 0);
assert.deepEqual(destroyed.filter(([kind]) => kind === 'iterator'), [['iterator', 43]]);
""")
    subprocess.run([node, str(tmp_path / "test.mjs")], check=True, capture_output=True, text=True)


@pytest.mark.parametrize(
    ("native_name", "public_name"),
    [
        ("create", "createByDeclaration"),
        ("get_inverse", "getInverseList"),
        ("schema", "schemaDefinition"),
        ("schema_name", "schemaIdentifier"),
    ],
)
def test_file_native_names_leave_room_for_python_compatible_methods(native_name: str, public_name: str) -> None:
    metadata = make_metadata()
    function = replace(
        metadata.functions["ifcopenshell_parse_open"],
        c_name=f"ifcopenshell_file_{native_name}",
        receiver="file",
        params=(CParamIR("self", "ifcopenshell_file_t*", "receiver", "handle"),),
        returns=TypeSpec(kind="void"),
    )
    javascript, declarations = render_wasm_bindings(replace(metadata, functions={function.c_name: function}))
    assert f"    {public_name}() {{" in javascript
    assert f"    {public_name}(): void;" in declarations
    assert f"module._ifcopenshell_file_{native_name}(" in javascript
    assert "OPERATION_CANCELLED: 4" in declarations


def test_handle_subclass_ownership(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute generated JavaScript")
    javascript, declarations = render_wasm_bindings(make_metadata())
    assert "protected constructor(source: IfcOpenshellFile);" in declarations
    assert "[Symbol.dispose](): void;" in declarations
    (tmp_path / "api.mjs").write_text(javascript)
    (tmp_path / "test.mjs").write_text("""
import assert from 'node:assert/strict';
// Exercise finalizer registration deterministically, without depending on GC timing.
let registry;
globalThis.FinalizationRegistry = class {
    entries = new Map();
    constructor(callback) { this.callback = callback; registry = this; }
    register(target, held, token) { this.entries.set(token, held); }
    unregister(token) { return this.entries.delete(token); }
};
const { IfcOpenshellFile } = await import('./api.mjs');
class File extends IfcOpenshellFile { constructor(source) { super(source); } }
const destroyed = [];
const module = { _ifcopenshell_file_destroy: ptr => destroyed.push(ptr) };
const source = new IfcOpenshellFile(42, true, module);
assert.throws(() => source[Symbol.for('ifcopenshell.wasm.handle.transfer.v1')]('wrong_type'), /incompatible/);
assert.equal(source.ptr, 42);
const first = new File(source);
assert(first instanceof IfcOpenshellFile);
assert.equal(source.ptr, 0);
assert.equal(first.ptr, 42);
source.destroy();
assert.deepEqual(destroyed, []);
assert.throws(() => new File(source), /disposed/);
assert.throws(() => new File({ ptr: 42 }), /incompatible/);
assert.throws(() => new File(null), /incompatible/);
const second = new File(first);
assert.equal(first.ptr, 0);
assert.equal(registry.entries.has(first), false);
assert.equal(registry.entries.size, 1);
second.dispose();
second.destroy();
second[Symbol.dispose]();
await second[Symbol.asyncDispose]();
assert.equal(second.ptr, 0);
assert.equal(registry.entries.size, 0);
assert.deepEqual(destroyed, [42]);
const borrowed = new File(new IfcOpenshellFile(43, false, module));
assert.equal(registry.entries.size, 0);
borrowed.destroy();
assert.equal(borrowed.ptr, 0);
assert.deepEqual(destroyed, [42]);
const abandoned = new File(new IfcOpenshellFile(44, true, module));
registry.callback(registry.entries.get(abandoned));
assert.deepEqual(destroyed, [42, 44]);
assert.doesNotThrow(() => registry.callback({ module: {
    _ifcopenshell_file_destroy() { throw new Error('runtime gone'); }
}, ptr: 45, destroy: '_ifcopenshell_file_destroy' }));
const failing = new File(new IfcOpenshellFile(46, true, {
    _ifcopenshell_file_destroy() { throw new Error('explicit failure'); }
}));
assert.throws(() => failing.destroy(), /explicit failure/);
assert.equal(failing.ptr, 0);
assert.equal(registry.entries.has(failing), false);
// A separately loaded API module has different class identities/private brands.
const ownRegistry = registry;
const { IfcOpenshellFile: OtherFile } = await import('./api.mjs?another-copy');
class OtherSubclass extends OtherFile { constructor(source) { super(source); } }
const other = new OtherSubclass(new OtherFile(47, true, module));
const otherRegistry = registry;
assert.equal(otherRegistry.entries.size, 1);
const adopted = new File(other);
assert.equal(other.ptr, 0);
assert.equal(otherRegistry.entries.size, 0);
assert.equal(ownRegistry.entries.has(adopted), true);
assert(adopted instanceof IfcOpenshellFile);
adopted.destroy();
assert.deepEqual(destroyed, [42, 44, 47]);
""")
    subprocess.run([node, str(tmp_path / "test.mjs")], check=True, capture_output=True, text=True)


def test_attribute_values_are_converted_in_the_native_binding(tmp_path: Path) -> None:
    metadata = make_metadata()
    handles = dict(metadata.handles)
    for name, c_type in [
        ("instance", "ifcopenshell_instance_t"),
        ("attribute_value", "ifcopenshell_parse_attribute_value_t"),
    ]:
        handles[name] = CTypeIR(
            c_type=c_type,
            kind="handle",
            fields=(CFieldIR("ptr", "void*"), CFieldIR("owned", "bool")),
            destroy_function=c_type.removesuffix("_t") + "_destroy",
            layout="ptr_owned",
        )
    javascript, declarations = render_wasm_bindings(replace(metadata, handles=handles))
    assert "module.attributeValueToJs(ptr," in javascript
    assert "setAttributeValueFromJs(this.#ptr, index, value," in javascript
    assert "class IfcOpenshellParseAttributeValue" not in javascript
    assert "class IfcOpenshellParseAttributeValue" not in declarations
    assert "export type AttributeValueType" in declarations
    node = shutil.which("node")
    if node:
        path = tmp_path / "api.mjs"
        path.write_text(javascript)
        subprocess.run([node, "--check", str(path)], check=True, capture_output=True, text=True)


def test_math_llround_returns_bigint(tmp_path: Path) -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required")
    script = tmp_path / "math.cjs"
    script.write_text(
        "const assert = require('node:assert/strict');\n"
        "let math; global.addToLibrary = value => { math = value; };\n"
        + (Path(__file__).parents[1] / "wasm_math_imports.js").read_text()
        + "\nfor (const [input, expected] of [[86000, 86000n], [0, 0n], [1.5, 2n], [-1.5, -2n], "
        "[1.4, 1n], [-1.4, -1n], [2 ** 40, 1099511627776n]]) {\n"
        "  assert.equal(math.llround(input), expected);\n"
        "}\n"
        "assert.equal(math.lround(1.5), 2);\n"
        "assert.equal(math.round(-1.5), -2);\n"
    )
    subprocess.run([node, str(script)], check=True, capture_output=True, text=True)
