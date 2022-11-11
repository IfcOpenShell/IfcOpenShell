#include "mapping.h"
#define mapping POSTFIX_SCHEMA(mapping)
using namespace ifcopenshell::geometry;

namespace {
	taxonomy::boolean_result::operation_t boolean_op_type(IfcSchema::IfcBooleanOperator::Value op) {
		if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
			return taxonomy::boolean_result::SUBTRACTION;
		} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION) {
			return taxonomy::boolean_result::INTERSECTION;
		} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION) {
			return taxonomy::boolean_result::UNION;
		} else {
			throw taxonomy::topology_error("Unknown boolean operation");
		}
	}

}

taxonomy::item* mapping::map_impl(const IfcSchema::IfcBooleanResult* inst) {
	IfcSchema::IfcBooleanOperand* operand1 = inst->FirstOperand();
	IfcSchema::IfcBooleanOperand* operand2 = inst->SecondOperand();

	std::vector<IfcUtil::IfcBaseClass*> operands = { operand2 };

	auto op = boolean_op_type(inst->Operator());

	bool process_as_list = true;
	while (true) {
		auto res1 = operand1->as<IfcSchema::IfcBooleanResult>();
		if (res1) {
			if (boolean_op_type(res1->Operator()) == op) {
				operand1 = res1->FirstOperand();
				operands.push_back(res1->SecondOperand());
			} else {
				process_as_list = false;
				break;
			}
		} else {
			operands.push_back(operand1);
			break;
		}
	}

	if (process_as_list) {
		std::reverse(operands.begin(), operands.end());
	} else {
		operand1 = inst->FirstOperand();
		operands.clear();
		operands.push_back(operand1);
		operands.push_back(operand2);
	}

	auto br = map_to_collection<taxonomy::boolean_result>(this, &operands);
	if (br) {
		br->operation = op;
	}
	return br;
}
