import json
from typing import Literal, Optional, Union

import ifcopenshell
import pytest

from ifcedit.coerce import coerce_value


class TestStringCoercion:
    def test_plain_string(self):
        assert coerce_value("hello", str) == "hello"

    def test_empty_string(self):
        assert coerce_value("", str) == ""


class TestIntCoercion:
    def test_plain_int(self):
        assert coerce_value("42", int) == 42

    def test_hash_prefix(self):
        assert coerce_value("#42", int) == 42

    def test_negative(self):
        assert coerce_value("-5", int) == -5


class TestFloatCoercion:
    def test_plain_float(self):
        assert coerce_value("3.14", float) == pytest.approx(3.14)

    def test_integer_as_float(self):
        assert coerce_value("5", float) == 5.0


class TestBoolCoercion:
    def test_true_values(self):
        for val in ("true", "True", "TRUE", "1", "yes"):
            assert coerce_value(val, bool) is True

    def test_false_values(self):
        for val in ("false", "False", "0", "no"):
            assert coerce_value(val, bool) is False


class TestOptionalCoercion:
    def test_optional_string(self):
        assert coerce_value("hello", Optional[str]) == "hello"

    def test_optional_none(self):
        assert coerce_value("none", Optional[str]) is None
        assert coerce_value("None", Optional[str]) is None

    def test_optional_int(self):
        assert coerce_value("42", Optional[int]) == 42


class TestUnionCoercion:
    def test_union_str_int(self):
        # Tries str first (or int first depending on order), both work
        result = coerce_value("hello", Union[str, int])
        assert result == "hello"

    def test_union_int_none(self):
        result = coerce_value("42", Union[int, None])
        assert result == 42


class TestLiteralCoercion:
    def test_valid_literal(self):
        assert coerce_value("IFC4", Literal["IFC2X3", "IFC4", "IFC4X3"]) == "IFC4"

    def test_invalid_literal(self):
        with pytest.raises(ValueError, match="not one of"):
            coerce_value("IFC5", Literal["IFC2X3", "IFC4", "IFC4X3"])


class TestDictCoercion:
    def test_json_dict(self):
        result = coerce_value('{"IsExternal": true, "FireRating": "2HR"}', dict[str, object])
        assert result == {"IsExternal": True, "FireRating": "2HR"}


class TestListCoercion:
    def test_comma_separated(self):
        result = coerce_value("a,b,c", list[str])
        assert result == ["a", "b", "c"]

    def test_json_array(self):
        result = coerce_value("[1, 2, 3]", list[int])
        assert result == [1, 2, 3]


class TestEntityCoercion:
    def test_entity_by_id(self, model):
        wall = model.by_type("IfcWall")[0]
        result = coerce_value(str(wall.id()), ifcopenshell.entity_instance, model)
        assert result == wall

    def test_entity_with_hash(self, model):
        wall = model.by_type("IfcWall")[0]
        result = coerce_value(f"#{wall.id()}", ifcopenshell.entity_instance, model)
        assert result == wall

    def test_entity_not_found(self, model):
        with pytest.raises(ValueError, match="not found"):
            coerce_value("999999", ifcopenshell.entity_instance, model)

    def test_entity_list(self, model):
        wall = model.by_type("IfcWall")[0]
        result = coerce_value(str(wall.id()), list[ifcopenshell.entity_instance], model)
        assert len(result) == 1
        assert result[0] == wall

    def test_entity_list_multiple(self, model):
        wall = model.by_type("IfcWall")[0]
        storey = model.by_type("IfcBuildingStorey")[0]
        result = coerce_value(f"{wall.id()},{storey.id()}", list[ifcopenshell.entity_instance], model)
        assert len(result) == 2

    def test_entity_no_model(self):
        with pytest.raises(ValueError, match="without an IFC model"):
            coerce_value("42", ifcopenshell.entity_instance, None)


class TestFallback:
    def test_no_type_hint(self):
        assert coerce_value("hello", None) == "hello"
