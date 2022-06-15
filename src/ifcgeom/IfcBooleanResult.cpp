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

#include <TopoDS_Wire.hxx>
#include <Standard_Version.hxx>
#include "../ifcgeom/IfcGeom.h"

#define Kernel MAKE_TYPE_NAME(Kernel)

bool IfcGeom::Kernel::convert(const IfcSchema::IfcBooleanResult* l, TopoDS_Shape& shape) {

	TopoDS_Shape s1;
	IfcRepresentationShapeItems items1;
	TopoDS_Wire boundary_wire;
	IfcSchema::IfcBooleanOperand* operand1 = l->FirstOperand();
	IfcSchema::IfcBooleanOperand* operand2 = l->SecondOperand();
	bool has_halfspace_operand = false;
	
	BOPAlgo_Operation occ_op;

	const IfcSchema::IfcBooleanOperator::Value op = l->Operator();
	if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
		occ_op = BOPAlgo_CUT;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION) {
		occ_op = BOPAlgo_COMMON;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION) {
		occ_op = BOPAlgo_FUSE;
	} else {
		return false;
	}

	std::vector<IfcSchema::IfcBooleanOperand*> second_operands;
	second_operands.push_back(operand2);

	if (occ_op == BOPAlgo_CUT) {
		int n_half_space_operands = 0;
		bool process_as_list = true;
		while (true) {
			auto res1 = operand1->as<IfcSchema::IfcBooleanResult>();
			if (res1 && res1->SecondOperand()->as<IfcSchema::IfcHalfSpaceSolid>() && ++n_half_space_operands > 8) {
				// There is something peculiar about many half space subtraction operands that OCCT does not like.
				// Often these are used to create a semi-curved arch, as is the case in 693. Supplying all these
				// operands at once apparently leads to too many edge-edge interference checks.
				process_as_list = false;
				break;
			}
			if (res1) {
				if (res1->Operator() == op) {
					operand1 = res1->FirstOperand();
					second_operands.push_back(res1->SecondOperand());
				} else {
					process_as_list = false;
					break;
				}
			} else {
				break;
			}
		}

		if (!process_as_list) {
			operand1 = l->FirstOperand();
			second_operands = { operand2 };
		}
	}

	if ( shape_type(operand1) == ST_SHAPELIST ) {
		if (!(convert_shapes(operand1, items1) && flatten_shape_list(items1, s1, true))) {
			return false;
		}
	} else if ( shape_type(operand1) == ST_SHAPE ) {
		if ( ! convert_shape(operand1, s1) ) {
			return false;
		}
		{ TopoDS_Solid temp_solid;
		s1 = ensure_fit_for_subtraction(s1, temp_solid); }
	} else {
		Logger::Message(Logger::LOG_ERROR, "Invalid representation item for boolean operation", operand1);
		return false;
	}

	if (getValue(GV_DISABLE_BOOLEAN_RESULT) > 0.0) {
		shape = s1;
		return true;
	}

	const double first_operand_volume = shape_volume(s1);
	if (first_operand_volume <= ALMOST_ZERO) {
		Logger::Message(Logger::LOG_WARNING, "Empty solid for:", l->FirstOperand());
	}

	TopTools_ListOfShape second_operand_shapes;

	for (auto& op2 : second_operands) {
		TopoDS_Shape s2;

		bool shape2_processed = false;

		bool is_halfspace = op2->declaration().is(IfcSchema::IfcHalfSpaceSolid::Class());
		bool is_unbounded_halfspace = is_halfspace && !op2->declaration().is(IfcSchema::IfcPolygonalBoundedHalfSpace::Class());
		has_halfspace_operand |= is_halfspace;

		{
			if (shape_type(op2) == ST_SHAPELIST) {
				IfcRepresentationShapeItems items2;
				shape2_processed = convert_shapes(op2, items2) && flatten_shape_list(items2, s2, true);
			} else if (shape_type(op2) == ST_SHAPE) {
				shape2_processed = convert_shape(op2, s2);
				if (shape2_processed) {
					TopoDS_Solid temp_solid;
					s2 = ensure_fit_for_subtraction(s2, temp_solid);
				}
			} else {
				Logger::Message(Logger::LOG_ERROR, "Invalid representation item for boolean operation", op2);
			}
		}

		if (is_unbounded_halfspace) {
			TopoDS_Shape temp;
			double d;
			if (fit_halfspace(s1, s2, temp, d)) {
				if (d < getValue(GV_PRECISION)) {
					Logger::Message(Logger::LOG_WARNING, "Halfspace subtraction yields unchanged volume:", l);
					continue;
				} else {
					s2 = temp;
				}
			}
		}

		if (!shape2_processed) {
			Logger::Message(Logger::LOG_ERROR, "Failed to convert SecondOperand:", op2);
			continue;
		}

		if (op2->declaration().is(IfcSchema::IfcHalfSpaceSolid::Class())) {
			const double second_operand_volume = shape_volume(s2);
			if (second_operand_volume <= ALMOST_ZERO) {
				Logger::Message(Logger::LOG_WARNING, "Empty solid for:", op2);
			}
		}

		second_operand_shapes.Append(s2);
	}

	/*
	// TK: A little debugging trick to output both operands for visual inspection
	
	BRep_Builder builder;
	TopoDS_Compound compound;
	builder.MakeCompound(compound);
	builder.Add(compound, s1);
	for (const auto& s2 : second_operand_shapes) {
		builder.Add(compound, s2);
	}
	shape = compound;
	return true;
	*/	

#if OCC_VERSION_HEX < 0x60900
	// @todo: this currently does not compile anymore, do we still need this?
	bool valid_result = boolean_operation(s1, s2, occ_op, shape);
#else
	
	bool valid_result;

	if (s1.ShapeType() == TopAbs_COMPOUND && TopoDS_Iterator(s1).More() && util::is_nested_compound_of_solid(s1)) {
		TopoDS_Compound C;
		BRep_Builder B;
		B.MakeCompound(C);
		TopoDS_Iterator it(s1);
		valid_result = true;
		for (; it.More(); it.Next()) {
			TopoDS_Shape part;
			if (boolean_operation(it.Value(), second_operand_shapes, occ_op, part)) {
				B.Add(C, part);
			} else {
				valid_result = false;
			}
		}
		shape = C;
	} else {
		valid_result = boolean_operation(s1, second_operand_shapes, occ_op, shape);
	}

#endif

	if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE) {
		// In case of a subtraction, a check on volume is performed.
		if (valid_result) {
			const double volume_after_subtraction = shape_volume(shape);
			if ( ALMOST_THE_SAME(first_operand_volume,volume_after_subtraction) )
				Logger::Message(Logger::LOG_WARNING,"Subtraction yields unchanged volume:",l);
		} else {
			Logger::Message(Logger::LOG_ERROR,"Failed to process subtraction:",l);
			shape = s1;
		}
		// NB: After issuing error the first operand is returned!
		return true;
	} else if (op == IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION && !valid_result) {
		BRep_Builder B;
		TopoDS_Compound C;
		B.MakeCompound(C);
		B.Add(C, s1);
		TopTools_ListIteratorOfListOfShape it(second_operand_shapes);
		for (; it.More(); it.Next()) {
			B.Add(C, it.Value());
		}
		Logger::Message(Logger::LOG_ERROR, "Failed to process union, creating compound:", l);
		shape = C;
		return true;
	} else {
		return valid_result;
	}
	return false;
}
