import lark


arithmetic_operator_symbols = {"ADD": "+", "DIVIDE": "/", "MULTIPLY": "*", "SUBTRACT": "-"}
symbol_arithmetic_operators = {"+": "ADD", "/": "DIVIDE", "*": "MULTIPLY", "-": "SUBTRACT"}


def serialise_cost_value(cost_value):
    result = _serialise_cost_value(cost_value)
    if result and result[0] == "(" and result[-1] == ")":
        return result[1:-1]
    return result


def _serialise_cost_value(cost_value):
    value = ""
    if cost_value.ArithmeticOperator and cost_value.Components:
        operator = arithmetic_operator_symbols[cost_value.ArithmeticOperator]
        serialised_components = []
        for component in cost_value.Components:
            serialised_components.append(_serialise_cost_value(component))
        value = operator.join(serialised_components)
    elif cost_value.AppliedValue is not None:
        value = serialise_applied_value(cost_value.AppliedValue)

    category = ""
    if cost_value.Category == "*":
        category = "SUM"
    elif cost_value.Category:
        category = cost_value.Category

    if not category and not value:
        value = "0"

    if category:
        return f"{category}({value})"
    elif cost_value.Components:
        return f"({value})"
    return value


def serialise_applied_value(applied_value):
    if applied_value.is_a("IfcMonetaryMeasure"):
        return str(applied_value.wrappedValue)
    return "?"


def unserialise_cost_value(formula, cost_value):
    unserialiser = CostValueUnserialiser()
    result = unserialiser.parse(formula)
    def map_element_to_result(element, result):
        result["ifc"] = element
        for i, component in enumerate(result.get("Components", [])):
            if element.Components and i < len(element.Components):
                map_element_to_result(element.Components[i], result["Components"][i])
    map_element_to_result(cost_value, result)
    return result


class CostValueUnserialiser:
    def parse(self, formula):
        l = lark.Lark(
            """start: formula
                    formula: operand (operator operand)*
                    operand: value | category "(" formula ")"
                    value: NUMBER?
                    category: WORD?
                    operator: add | divide | multiply | subtract
                    add: "+"
                    divide: "/"
                    multiply: "*"
                    subtract: "-"

                    // Embed common.lark for packaging
                    DIGIT: "0".."9"
                    HEXDIGIT: "a".."f"|"A".."F"|DIGIT
                    INT: DIGIT+
                    SIGNED_INT: ["+"|"-"] INT
                    DECIMAL: INT "." INT? | "." INT
                    _EXP: ("e"|"E") SIGNED_INT
                    FLOAT: INT _EXP | DECIMAL _EXP?
                    SIGNED_FLOAT: ["+"|"-"] FLOAT
                    NUMBER: FLOAT | INT
                    SIGNED_NUMBER: ["+"|"-"] NUMBER
                    _STRING_INNER: /.*?/
                    _STRING_ESC_INNER: _STRING_INNER /(?<!\\\\)(\\\\\\\\)*?/
                    ESCAPED_STRING : "\\"" _STRING_ESC_INNER "\\""
                    LCASE_LETTER: "a".."z"
                    UCASE_LETTER: "A".."Z"
                    LETTER: UCASE_LETTER | LCASE_LETTER
                    WORD: LETTER+
                    CNAME: ("_"|LETTER) ("_"|LETTER|DIGIT)*
                    WS_INLINE: (" "|/\\t/)+
                    WS: /[ \\t\\f\\r\\n]/+
                    CR : /\\r/
                    LF : /\\n/
                    NEWLINE: (CR? LF)+

                    %ignore WS // Disregard spaces in text
                 """
        )
        start = l.parse(formula)
        return self.get_formula(start.children[0])

    def get_formula(self, formula):
        if len(formula.children) == 1:
            return self.get_operand(formula.children[0])
        results = {"Components": []}
        for child in formula.children:
            if child.data == "operand":
                results["Components"].append(self.get_operand(child))
            elif child.data == "operator":
                results["ArithmeticOperator"] = self.get_operator(child)
        return results

    def get_operand(self, operand):
        child = operand.children[0]
        if child.data == "value":
            value = self.get_value(child)
            return {"AppliedValue": float(value) if value else None}
        elif child.data == "category":
            data = {}
            category = self.get_category(child)
            if category:
                if category.lower() == "sum":
                    category = "*"
                data["Category"] = category
            formula = self.get_formula(operand.children[1])
            if formula.get("Components"):
                data["Components"] = formula["Components"]
                data["ArithmeticOperator"] = formula["ArithmeticOperator"]
            else:
                data["AppliedValue"] = formula["AppliedValue"]
            return data

    def get_value(self, value):
        if value.children:
            return value.children[0].value

    def get_category(self, category):
        if category.children:
            return category.children[0].value

    def get_operator(self, operator):
        return operator.children[0].data.upper()
