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

"""Data validation module"""

from __future__ import print_function

import sys
import json
import functools

from collections import namedtuple

import ifcopenshell
import ifcopenshell.express.rule_executor

named_type = ifcopenshell.ifcopenshell_wrapper.named_type
aggregation_type = ifcopenshell.ifcopenshell_wrapper.aggregation_type
simple_type = ifcopenshell.ifcopenshell_wrapper.simple_type
type_declaration = ifcopenshell.ifcopenshell_wrapper.type_declaration
enumeration_type = ifcopenshell.ifcopenshell_wrapper.enumeration_type
entity_type = ifcopenshell.ifcopenshell_wrapper.entity
select_type = ifcopenshell.ifcopenshell_wrapper.select_type
attribute = ifcopenshell.ifcopenshell_wrapper.attribute


class ValidationError(Exception):
    def __init__(self, message, attribute=None):
        super(ValidationError, self).__init__(message)
        self.attribute = attribute


log_entry_type = namedtuple("log_entry_type", ("level", "message", "instance", "attribute"))


class json_logger:
    def __init__(self):
        self.statements = []
        self.state = {}

    def set_state(self, key, value):
        self.state[key] = value

    def log(self, level, message, *args):
        self.statements.append({"level": level, "message": message % args, **self.state})

    def __getattr__(self, level):
        return functools.partial(self.log, level)


simple_type_python_mapping = {
    # @todo should include unicode for Python2
    "string": str,
    "integer": int,
    "real": float,
    "number": float,
    "boolean": bool,
    "logical": {True, False, "UNKNOWN"},
    "binary": str,  # maps to a str of "0" and "1"
}


def annotate_inst_attr_pos(inst, pos):
    def get_pos():
        depth = 0
        idx = -1
        for c in str(inst):
            if c == "(":
                depth += 1
                if depth == 1:
                    idx = 0
                    yield -1
                else:
                    yield idx
            elif c == ")":
                depth -= 1
                if depth == 0:
                    idx = -1
                    yield -1
                else:
                    yield idx
            elif depth == 1 and c == ",":
                idx += 1
                yield -1
            else:
                yield idx

    return "".join(" ^"[i == pos] for i in get_pos())


def format(val):
    if isinstance(val, tuple) and val and isinstance(val[0], ifcopenshell.entity_instance):
        return "[\n%s\n    ]" % "\n".join("      {}. {}".format(*x) for x in enumerate(val, start=1))
    else:
        return repr(val)


def assert_valid_inverse(attr, val, schema):
    b1, b2 = attr.bound1(), attr.bound2()
    
    if (b1, b2) == (-1, -1):
        invalid = len(val) != 1
    else:
        invalid = len(val) < b1 or (b2 != -1 and len(val) > b2)
    
    if invalid:

        ent_ref = attr.entity_reference().name()
        attr_ref = attr.attribute_reference().name()
        aggr = attr.type_of_aggregation_string().upper()

        if aggr:
            aggr_str = f'{aggr} [{b1}:{b2}] OF '
        else:
            aggr_str = ''

        attr_formatted = f"{attr.name()} : {aggr_str}{ent_ref} FOR {attr_ref}"

        raise ValidationError(f"With inverse:\n    {attr_formatted}\nValue:\n    {format(val)}\nNot valid\n", attr.name())
    return True


select_members_cache = {}


def get_select_members(schema, ty):
    cache_key = schema.name(), ty.name()
    from_cache = select_members_cache.get(cache_key)
    if from_cache:
        return from_cache

    def inner(ty):
        if isinstance(ty, select_type):
            for st in ty.select_list():
                yield from inner(st)
        elif isinstance(ty, entity_type):
            yield ty.name()
            for st in ty.subtypes():
                yield from inner(st)
        elif isinstance(ty, type_declaration):
            yield ty.name()

    v = select_members_cache[cache_key] = set(inner(ty))
    return v


def assert_valid(attr_type, val, schema, no_throw=False, attr=None):
    type_wrappers = (named_type,)
    if not isinstance(val, ifcopenshell.entity_instance):
        # If val is not an entity instance we need to
        # flatten the type declaration to something that
        # maps to the python types
        type_wrappers += (type_declaration,)

    while isinstance(attr_type, type_wrappers):
        attr_type = attr_type.declared_type()

    invalid = False

    if isinstance(attr_type, simple_type):
        simple_type_python = simple_type_python_mapping[attr_type.declared_type()]
        if type(simple_type_python) == set:
            invalid = val not in simple_type_python
        else:
            invalid = type(val) != simple_type_python
    elif isinstance(attr_type, (entity_type, type_declaration)):
        invalid = not isinstance(val, ifcopenshell.entity_instance) or not val.is_a(attr_type.name())
    elif isinstance(attr_type, select_type):
        val_to_use = val
        if isinstance(schema.declaration_by_name(val.is_a()), enumeration_type):
            if isinstance(val, ifcopenshell.entity_instance):
                val_to_use = val.wrappedValue
            else:
                invalid = True
        if not invalid:
            # Previously we relied on `is_a(x) for x in attr_type.select_items()`
            # this was linear in the number of select leafs, which is very large
            # for e.g IfcValue, which is an often used select. Therefore, we now
            # calculate (and cache) the select leafs (including entity subtypes)
            # for the select definition and simply check for membership in this
            # set.
            invalid = val_to_use.is_a() not in get_select_members(schema, attr_type)
    elif isinstance(attr_type, enumeration_type):
        invalid = val not in attr_type.enumeration_items()
    elif isinstance(attr_type, aggregation_type):
        b1, b2 = attr_type.bound1(), attr_type.bound2()
        ty = attr_type.type_of_element()
        invalid = len(val) < b1 or (b2 != -1 and len(val) > b2) or not all(assert_valid(ty, v, schema) for v in val)
    else:
        raise NotImplementedError("Not impl %s %s" % (type(attr_type), attr_type))

    if no_throw:
        return not invalid
    elif invalid:
        raise ValidationError(f"With attribute:\n    {attr or attr_type}\nValue:\n    {val}\nNot valid\n", (attr or attr_type).name())
    else:
        return True


def log_internal_cpp_errors(filename, logger):
    import re
    import bisect

    chr_offset_re = re.compile(r"at offset (\d+)\s*")

    log = ifcopenshell.get_log()
    msgs = list(map(json.loads, filter(None, log.split("\n"))))
    chr_offsets = [chr_offset_re.findall(m["message"]) for m in msgs]
    if chr_offsets:

        # The file is opened in binary mode, in order
        # to correspond with the offsets reported by
        # IfcOpenShell C++
        lines = list(open(filename, "rb"))
        lengths = list(map(len, lines))
        cumsum = 0
        cs = [cumsum := cumsum + x for x in lengths]

        for offsets, msg in zip(chr_offsets, msgs):
            if offsets:
                line = lines[bisect.bisect_left(cs, int(offsets[0]))].decode("ascii", errors="ignore").rstrip()
                m = chr_offset_re.sub("", msg["message"])

                if hasattr(logger, "set_state"):
                    logger.set_state('instance', line)
                    logger.set_state('attribute', None)
                    logger.error("%s:\n\n%s" % (m, line))
                else:
                    logger.error("For instance:\n    %s\n%s", line, m)


entity_attribute_map = {}


def get_entity_attributes(schema, entity):
    cache_key = schema.name(), entity
    from_cache = entity_attribute_map.get(cache_key)
    if from_cache:
        return from_cache

    entity_attrs = (
        ent := schema.declaration_by_name(entity),
        ent.all_attributes(),
    )

    entity_attribute_map[cache_key] = entity_attrs
    return entity_attrs


def validate(f, logger, express_rules=False):
    """
    For an IFC population model `f` (or filepath to such a file) validate whether the entity attribute values are correctly supplied. As this
    is a function that is applied after a file has been parsed, certain types of errors in syntax, duplicate
    numeric identifiers or invalidate entity names are not caught by this function. Some of these might have been
    logged and can be retrieved by calling `ifcopenshell.get_log()`. A verification of the type, entity and global
    WHERE rules is also not implemented.

    For every entity instance in the model, it is checked that the entity is not abstract that every attribute value
    is of the correct type and that the inverse attributes are of the correct cardinality.

    Express simple types are checked for their valuation type. For select types it is asserted that the value conforms
    to one of the leaves. For enumerations it is checked that the value is indeed on of the items. For aggregations it
    is checked that the elements and the cardinality conforms. Type declarations (IfcInteger which is an integer) are
    unpacked until one of the above cases is reached.

    It is recommended to supply the path to the file, so that internal C++ errors reported during the parse stage
    are also captured.
    """

    # Originally there was no way in Python to distinguish on an entity instance attribute value whether the
    # value supplied in the model was NIL ($) or 'missing because derived in subtype' (*). For validation this
    # however this may be important, and hence a feature switch has been implemented to return *-values as
    # instances of a dedicated type `ifcopenshell.ifcopenshell_wrapper.attribute_value_derived`.
    attribute_value_derived_org = ifcopenshell.ifcopenshell_wrapper.get_feature("use_attribute_value_derived")
    ifcopenshell.ifcopenshell_wrapper.set_feature("use_attribute_value_derived", True)

    filename = None

    logger.set_state('type', 'schema')

    if not isinstance(f, ifcopenshell.file):

        # get_log() clears log existing output
        ifcopenshell.get_log()
        # @todo restore log format
        ifcopenshell.ifcopenshell_wrapper.set_log_format_json()

        filename = f
        f = ifcopenshell.open(f)

        log_internal_cpp_errors(filename, logger)

    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(f.schema)
    for inst in f:
        if hasattr(logger, "set_state"):
            logger.set_state('instance', inst)

        entity, attrs = get_entity_attributes(schema, inst.is_a())

        if entity.is_abstract():
            e = "Entity %s is abstract" % entity.name()
            if hasattr(logger, "set_state"):
                logger.set_state('attribute', None)
                logger.error(e)
            else:
                logger.error("For instance:\n    %s\n%s", inst, e)

        has_invalid_value = False
        values = [None] * len(attrs)
        for i in range(len(attrs)):
            try:
                values[i] = inst[i]
                pass
            except:
                if hasattr(logger, "set_state"):
                    logger.set_state('attribute', f"{entity.name()}.{attrs[i].name()}")
                    logger.error("Invalid attribute value")
                else:
                    logger.error(
                        "For instance:\n    %s\n    %s\nInvalid attribute value for %s.%s",
                        inst,
                        annotate_inst_attr_pos(inst, i),
                        entity,
                        attrs[i],
                    )
                has_invalid_value = True

        if not has_invalid_value:
            for i, (attr, val, is_derived) in enumerate(zip(attrs, values, entity.derived())):

                if is_derived and not isinstance(val, ifcopenshell.ifcopenshell_wrapper.attribute_value_derived):
                    if hasattr(logger, "set_state"):
                        logger.set_state('attribute', f"{entity.name()}.{attr.name()}")
                        logger.error("Attribute is derived in subtype")
                    else:
                        logger.error(
                            "For instance:\n    %s\n    %s\nWith attribute:\n    %s\nDerived in subtype\n",
                            inst,
                            annotate_inst_attr_pos(inst, i),
                            attr,
                        )

                if val is None and not attr.optional() and not is_derived:
                    if hasattr(logger, "set_state"):
                        logger.set_state('attribute', f"{entity.name()}.{attr.name()}")
                        logger.error("Attribute not optional")
                    else:
                        logger.error(
                            "For instance:\n    %s\n    %s\nWith attribute:\n    %s\nNot optional\n",
                            inst,
                            annotate_inst_attr_pos(inst, i),
                            attr,
                        )

                if val is not None and not is_derived:
                    attr_type = attr.type_of_attribute()
                    try:
                        assert_valid(attr_type, val, schema, attr=attr)
                    except ValidationError as e:
                        if hasattr(logger, "set_state"):
                            logger.set_state('attribute', e.attribute)
                            logger.error(str(e))
                        else:
                            logger.error(
                                "For instance:\n    %s\n    %s\n%s",
                                inst,
                                annotate_inst_attr_pos(inst, i),
                                e,
                            )

        for attr in entity.all_inverse_attributes():
            val = getattr(inst, attr.name())
            try:
                assert_valid_inverse(attr, val, schema)
            except ValidationError as e:
                if hasattr(logger, "set_state"):
                    logger.set_state('attribute', f"{entity.name()}.{attr.name()}")
                    logger.error(str(e))
                else:
                    logger.error("For instance:\n    %s\n%s", inst, e)

    if filename:
        # IfcOpenShell uses lazy-loading, so entity instance
        # attributes aren't parsed yet, and counts aren't verified yet.
        # Re capturing the log when validate() is finished
        # iterating over every instance so that all attribute counts
        # are verified.
        log_internal_cpp_errors(filename, logger)

    # Restore the original value for 'use_attribute_value_derived'
    ifcopenshell.ifcopenshell_wrapper.set_feature("use_attribute_value_derived", attribute_value_derived_org)

    if express_rules:
        if hasattr(logger, 'set_state'):
            logger.set_state('instance', None)
            logger.set_state('attribute', None)
        ifcopenshell.express.rule_executor.run(f, logger)


if __name__ == "__main__":
    import sys
    import logging

    filenames = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = set(x for x in sys.argv[1:] if x.startswith("--"))

    for fn in filenames:
        if "--json" in flags:
            logger = json_logger()
        else:
            logger = logging.getLogger("validate")
            logger.setLevel(logging.DEBUG)

        print("Validating", fn, file=sys.stderr)
        validate(fn, logger, "--rules" in flags)

        if "--json" in flags:
            sys.stdout.reconfigure(encoding='utf-8')
            conv = str
            if "--spf" in flags:
                conv = lambda x: x.to_string() if isinstance(x, ifcopenshell.entity_instance) else str(x)
            if "--fields" in flags:
                def conv(x):
                    if isinstance(x, ifcopenshell.entity_instance):
                        return x.get_info(scalar_only=True)
                    else:
                        return str(x)
            print("\n".join(json.dumps(x, default=conv) for x in logger.statements))
