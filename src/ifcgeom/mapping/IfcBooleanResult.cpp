/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

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

taxonomy::ptr mapping::map_impl(const IfcSchema::IfcBooleanResult* inst) {
	IfcSchema::IfcBooleanOperand* operand1 = inst->FirstOperand();
	IfcSchema::IfcBooleanOperand* operand2 = inst->SecondOperand();
	bool has_halfspace_operand = false;
	
	std::vector<IfcSchema::IfcBooleanOperand*> operands;
	operands.push_back(operand2);

	auto op = boolean_op_type(inst->Operator());

	if (op == taxonomy::boolean_result::SUBTRACTION) {
		int n_half_space_operands = 0;
		bool process_as_list = true;
		while (true) {
			auto res1 = operand1->as<IfcSchema::IfcBooleanResult>();
			if (res1 && res1->SecondOperand()->as<IfcSchema::IfcHalfSpaceSolid>() && ++n_half_space_operands > 8) {
				// There is something peculiar about many half space subtraction operands that OCCT does not like.
				// Often these are used to create a semi-curved arch, as is the case in 693. Supplying all these
				// operands at once apparently leads to too many edge-edge interference checks.

				// @todo this should probably be moved to the opencascade kernel and not the mapping.
				process_as_list = false;
				break;
			}
			if (res1) {
				if (boolean_op_type(res1->Operator()) == op) {
					operand1 = res1->FirstOperand();
					operands.push_back(res1->SecondOperand());
				} else {
					process_as_list = false;
					break;
				}
			} else {
				break;
			}
		}

		if (!process_as_list) {
			operand1 = inst->FirstOperand();
			operands = { operand2 };
		}
	}

	operands.insert(operands.begin(), operand1);

	auto br = map_to_collection<taxonomy::boolean_result>(this, &operands);
	if (br) {
		br->operation = op;
	}
	return br;
}
