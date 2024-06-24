import os
import re
import ast
import collections
import ifcopenshell
from logging import Logger
from dataclasses import dataclass
from codegen import indent


def reverse_compile(s):
    return re.sub(
        r"\s*\-\s*EXPRESS_ONE_BASED_INDEXING",
        "",
        re.sub(
            ", )?+.(, INDETERMINATE)\\"[::-1],
            "]\\1[",
            re.sub(
                r", '(\w+)', INDETERMINATE\)",
                ".\\1",
                s.strip()
                .replace("len(", "SIZEOF(")
                .replace("assert ", "")
                .replace(" is not False", "")
                .replace("getattr(", "")
                .replace("express_getitem(", ""),
            )[::-1],
        )[::-1],
    )


@dataclass
class error(Exception):
    rule_name: str
    rule_definition: str
    violation: str
    instance: ifcopenshell.entity_instance = None

    def __str__(self):
        inst = ""
        if self.instance:
            inst = f"On instance:\n{indent(4, str(self.instance))}\n"
        if self.rule_name:
            return f"{inst}Rule {self.rule_name}:\n{indent(4, self.rule_definition)}\nViolated by:\n{indent(4, self.violation)}"
        else:
            if inst:
                inst = f"\n\n{inst}"
            return f"{self.rule_definition}\n\nViolated by:\n{indent(4, self.violation)}{inst}"


def fix_type(v):
    if isinstance(v, (list, tuple)):
        # 1-based indexing:
        #
        # @todo this is not the best way, because it still allows to index the 0-th element,
        # but given the existing body of rules this should be sufficient.
        # return type(v)([None]) + type(v)(map(fix_type, v))

        # We don't do this anymore, because it doesn't fix instance attribute lookups
        # We now instead perform a -1 on the index qualifier in the code generation
        pass
    # @todo enrich entity instances with code to evaluate derived attributes
    return v


def run(f: ifcopenshell.file, logger: Logger) -> None:
    from _pytest import assertion

    if hasattr(logger, "set_instance"):
        # when using the json logger, we notify it of the relevant instance
        pre_annotate_instance = lambda instance: logger.set_state('instance', instance) if hasattr(logger, 'set_state') else None
        post_annotate_instance = lambda instance: instance
        pre_annotate_attribute = lambda attribute: logger.set_state('attribute', attribute) if hasattr(logger, 'set_state') else None
        post_annotate_attribute = lambda attribute: None
    else:
        # when using the normal text logger the instance is appended to the method
        pre_annotate_instance = lambda instance: None
        post_annotate_instance = lambda instance: instance
        pre_annotate_attribute = lambda attribute: None
        post_annotate_attribute = lambda attribute: attribute

    orig = ifcopenshell.settings.unpack_non_aggregate_inverses
    ifcopenshell.settings.unpack_non_aggregate_inverses = True

    fn = os.path.join(os.path.dirname(__file__), "rules", f"{f.schema_identifier}.py")
    try:
        source = open(fn, "r").read()
    except FileNotFoundError as e:
        import sys
        import time
        import subprocess

        current_dir_files = {fn.lower(): fn for fn in os.listdir('.')}
        schema_name = str(f.schema_identifier).split(' ')[-1].lower()
        schema_path = current_dir_files.get(schema_name + '.exp')
        fn = schema_path[:-4] + '.py'
        if not os.path.exists(fn):
            subprocess.run([sys.executable, "-m", "ifcopenshell.express.rule_compiler", schema_path, fn], check=True)
            time.sleep(1.)
        source = open(fn, "r").read()

    a = ast.parse(source)
    assertion.rewrite.rewrite_asserts(mod=a, source=source)
    cd = compile(a, f"{f.schema_identifier}.py", "exec")
    scope = {}
    exec(cd, scope)
    S = ifcopenshell.ifcopenshell_wrapper.schema_by_name(f.schema_identifier)

    rules = list(filter(lambda x: hasattr(x, "SCOPE"), scope.values()))

    if hasattr(logger, 'set_state'):
        logger.set_state('type', 'global_rule')

    for R in [r for r in rules if r.SCOPE == "file"]:
        try:
            R()(f)
        except Exception as e:
            ln = e.__traceback__.tb_next.tb_lineno
            pre_annotate_attribute(R.__name__)
            logger.error(
                str(
                    error(
                        post_annotate_attribute(R.__name__),
                        reverse_compile(source.split("\n")[ln - 1]),
                        reverse_compile(e.args[0]),
                    )
                )
            )

    if hasattr(logger, 'set_state'):
        logger.set_state('type', 'simpletype_rule')

    types = {}
    subtypes = collections.defaultdict(list)
    for d in S.declarations():
        if isinstance(d, ifcopenshell.ifcopenshell_wrapper.type_declaration):
            types[d.name()] = d
            if isinstance(
                d.declared_type(), ifcopenshell.ifcopenshell_wrapper.named_type
            ):
                subtypes[d.declared_type().declared_type().name()].append(d.name())

    D = collections.defaultdict(list)
    for r in rules:
        if r.SCOPE == "type":

            def visit(nm):
                D[nm].append(r)
                for nm2 in subtypes[nm]:
                    visit(nm2)

            visit(r.TYPE_NAME)

    def type_name(ty):
        if isinstance(ty, ifcopenshell.ifcopenshell_wrapper.named_type):
            return type_name(ty.declared_type())
        elif isinstance(ty, ifcopenshell.ifcopenshell_wrapper.aggregation_type):
            # breakpoint()
            pass
        elif isinstance(ty, ifcopenshell.ifcopenshell_wrapper.simple_type):
            pass
        else:
            return ty.name()

    def check(value, type, instance):
        if value is None:
            return

        if type_name(type) in D:
            for R in D[type_name(type)]:
                try:
                    R()(fix_type(value))
                except Exception as e:
                    ln = e.__traceback__.tb_next.tb_lineno
                    pre_annotate_instance(instance)
                    pre_annotate_attribute(f"{R.TYPE_NAME}.{R.RULE_NAME}")
                    logger.error(
                        str(
                            error(
                                post_annotate_attribute(f"{R.TYPE_NAME}.{R.RULE_NAME}"),
                                reverse_compile(source.split("\n")[ln - 1]),
                                reverse_compile(e.args[0]),
                                post_annotate_instance(instance),
                            )
                        )
                    )

        # @nb something can be a named type with rules and still be an aggregation.
        # case in point IfcCompoundPlaneAngleMeasure. Therefore only unpack named
        # type references from this point onwards.
        while isinstance(
            type,
            (
                ifcopenshell.ifcopenshell_wrapper.named_type,
                ifcopenshell.ifcopenshell_wrapper.type_declaration,
            ),
        ):
            type = type.declared_type()

        if isinstance(value, (list, tuple)):
            if isinstance(type, ifcopenshell.ifcopenshell_wrapper.aggregation_type):
                ty = type.type_of_element()
                for v in value:
                    check(v, ty, instance=inst)
            else:
                # Let's hope a schema validation error was reported for this case
                pass

        elif isinstance(value, ifcopenshell.entity_instance):
            if isinstance(
                S.declaration_by_name(value.is_a()),
                ifcopenshell.ifcopenshell_wrapper.entity,
            ):
                # top level entity instances will be checked on their own
                pass
            else:
                # unpack the type instance
                check(value[0], S.declaration_by_name(value.is_a()), instance=inst)

    for inst in f:
        try:
            values = list(inst)
        except Exception as e:
            if hasattr(logger, "set_state"):
                logger.error(str(e))
            else:
                logger.error("For instance:\n    %s\n%s", inst, e)
            continue
        entity = S.declaration_by_name(inst.is_a())
        attrs = entity.all_attributes()
        for i, (attr, val, is_derived) in enumerate(
            zip(attrs, values, entity.derived())
        ):
            if is_derived:
                # @todo
                pass
            else:
                check(val, attr.type_of_attribute(), instance=inst)

    if hasattr(logger, 'set_state'):
        logger.set_state('type', 'entity_rule')

    for R in [r for r in rules if r.SCOPE == "entity"]:
        for inst in f.by_type(R.TYPE_NAME):
            try:
                R()(inst)
            except Exception as e:
                ln = e.__traceback__.tb_next.tb_lineno
                pre_annotate_instance(inst)
                pre_annotate_attribute(f"{R.TYPE_NAME}.{R.RULE_NAME}")
                logger.error(
                    str(
                        error(
                            post_annotate_attribute(f"{R.TYPE_NAME}.{R.RULE_NAME}"),
                            reverse_compile(source.split("\n")[ln - 1]),
                            reverse_compile(e.args[0]),
                            post_annotate_instance(inst),
                        )
                    )
                )

    ifcopenshell.settings.unpack_non_aggregate_inverses = orig


if __name__ == "__main__":
    import sys
    import json
    import logging
    import ifcopenshell
    from ifcopenshell.validate import json_logger

    filenames = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = set(x for x in sys.argv[1:] if x.startswith("--"))

    for fn in filenames:
        if "--json" in flags:
            logger = json_logger()
        else:
            logger = logging.getLogger("validate")
            logger.setLevel(logging.DEBUG)

        f = ifcopenshell.open(fn)

        run(f, logger)

        if "--json" in flags:
            print("\n".join(json.dumps(x, default=str) for x in logger.statements))
