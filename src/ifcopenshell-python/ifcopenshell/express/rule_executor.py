import ast
import collections
from dataclasses import dataclass
import pathlib
import tempfile
from _pytest import assertion
import ifcopenshell
from ifcopenshell.validate import json_logger

from rule_compiler import reverse_compile

CODE_DIR = pathlib.Path(tempfile.gettempdir())

@dataclass
class error(Exception):
    rule_name : str
    rule_definition : str
    violation : str
    instance : ifcopenshell.entity_instance = None

    def __str__(self):
        inst = ""
        if self.instance:
            inst = "\nOn instance:\n{self.instance}"
        return f"Rule: {self.rule_name}\n{self.rule_definition}\nViolated by:\n{self.violation}{inst}"


def fix_type(v):
    if isinstance(v, (list, tuple)):
        # 1-based indexing:
        # 
        # @todo this is not the best way, because it still allows to index the 0-th element,
        # but given the existing body of rules this should be sufficient.
        return type(v)([None]) + type(v)(map(fix_type, v))
    # @todo enrich entity instances with code to evaluate derived attributes
    return v


def run(f, logger):
    fn = CODE_DIR / f"{f.schema}.py"
    source = open(fn, "r").read()
    a = ast.parse(source)
    assertion.rewrite.rewrite_asserts(mod=a, source=source)
    cd = compile(a, f"{f.schema}.py", 'exec')
    scope = {}
    exec(cd, scope)
    S = ifcopenshell.ifcopenshell_wrapper.schema_by_name(f.schema)
    
    rules = list(filter(lambda x: hasattr(x, 'SCOPE'), scope.values()))
    
    for R in [r for r in rules if r.SCOPE == 'file']:
        try:
            R()(f)
        except Exception as e:
            ln = e.__traceback__.tb_next.tb_lineno
            logger.error(str(error(
                R.__name__,
                reverse_compile(source.split("\n")[ln-1]),
                reverse_compile(e.args[0])
            )))

    types = {}
    subtypes = collections.defaultdict(list)
    for d in S.declarations():
        if isinstance(d, ifcopenshell.ifcopenshell_wrapper.type_declaration):
            types[d.name()] = d
            if isinstance(d.declared_type(), ifcopenshell.ifcopenshell_wrapper.named_type):
                subtypes[d.declared_type().declared_type().name()].append(d.name())

    D = collections.defaultdict(list)
    for r in rules:
        if r.SCOPE == 'type':
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
    
    def check(value, type):
        if value is None:
            return

        # if value == (-361, 0, 0):
        #     breakpoint()
        
        if type_name(type) in D:
            for R in D[type_name(type)]:
                try:
                    R()(fix_type(value))
                except Exception as e:
                    ln = e.__traceback__.tb_next.tb_lineno
                    logger.error(str(error(
                        R.__name__,
                        reverse_compile(source.split("\n")[ln-1]),
                        reverse_compile(e.args[0])
                    )))

        # @nb something can be a named type with rules and still be an aggregation.
        # case in point IfcCompoundPlaneAngleMeasure. Therefore only unpack named
        # type references from this point onwards.
        while isinstance(type, (ifcopenshell.ifcopenshell_wrapper.named_type, ifcopenshell.ifcopenshell_wrapper.type_declaration)):
            type = type.declared_type()

        if isinstance(value, (list, tuple)):
            assert isinstance(type, ifcopenshell.ifcopenshell_wrapper.aggregation_type)
            ty = type.type_of_element()
            for v in value:
                check(v, ty)
        elif isinstance(value, ifcopenshell.entity_instance):
            if isinstance(S.declaration_by_name(value.is_a()), ifcopenshell.ifcopenshell_wrapper.entity):
                # top level entity instances will be checked on their own
                pass
            else:
                # unpack the type instance
                check(value[0], S.declaration_by_name(value.is_a()))
        

    for inst in f:
        values = list(inst)
        entity = S.declaration_by_name(inst.is_a())
        attrs = entity.all_attributes()
        for i, (attr, val, is_derived) in enumerate(zip(attrs, values, entity.derived())):
            if is_derived:
                # @todo
                pass
            else:
                check(val, attr.type_of_attribute())

    for R in [r for r in rules if r.SCOPE == 'entity']:
        for inst in f.by_type(R.TYPE_NAME):
            try:
                R()(inst)
            except Exception as e:
                ln = e.__traceback__.tb_next.tb_lineno
                logger.error(str(error(
                    R.__name__,
                    reverse_compile(source.split("\n")[ln-1]),
                    reverse_compile(e.args[0])
                )))

    """
    for R in []:
        r = R()
        S = ifcopenshell.ifcopenshell_wrapper.schema_by_name(f.schema)
        entities = [x for x in S.declarations() if isinstance(x, ifcopenshell.ifcopenshell_wrapper.entity)]
        for e in entities:
            for attr in e.attributes():
                ty = attr.type_of_attribute()
                if isinstance(ty, ifcopenshell.ifcopenshell_wrapper.named_type):
                    pass
                ifcopenshell.ifcopenshell_wrapper.type_declaration
                # check for type inheritance
                ifcopenshell.ifcopenshell_wrapper.aggregation_type
                # check elements of lists
                ifcopenshell.ifcopenshell_wrapper.select_type
                # check based on value in model and then get wrapped data
                # also check aggregation of select
                # and select of aggregation
                # is it better to do it the other way around? probably
                if ty.name() == R.TYPE_NAME:
                    for inst in f.by_type(e.name()):
                        attr = getattr(inst, attr.name())
                        try:
                            r(attr)
                        except Exception as e:
                            ln = e.__traceback__.tb_next.tb_lineno
                            logger.error(str(error(
                                R.__name__,
                                reverse_compile(source.split("\n")[ln-1]),
                                reverse_compile(e.args[0]),
                                inst
                            )))
    """

if __name__ == "__main__":
    import sys
    import json
    import logging
    import ifcopenshell

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
