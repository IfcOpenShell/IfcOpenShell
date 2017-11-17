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

#include "../../../src/ifcparse/IfcHdf5File.h"

#include <set>

#pragma warning(disable:4100) 

class ifc_inst_cmp {
public:

	// For these we simply assume that only a single instance exists
	bool operator()(IfcSchema::IfcSite* a, IfcSchema::IfcSite* b) { return false; }
	bool operator()(IfcSchema::IfcProject* a, IfcSchema::IfcProject* b) { return false; }
	bool operator()(IfcSchema::IfcBuilding* a, IfcSchema::IfcBuilding* b) { return false; }
	bool operator()(IfcSchema::IfcPostalAddress* a, IfcSchema::IfcPostalAddress* b) { return false; }
	bool operator()(IfcSchema::IfcUnitAssignment* a, IfcSchema::IfcUnitAssignment* b) { return false; }

	bool operator()(IfcSchema::IfcConversionBasedUnit* a, IfcSchema::IfcConversionBasedUnit* b) {
		return a->Name() < b->Name();
	}

	bool operator()(IfcSchema::IfcDimensionalExponents* a, IfcSchema::IfcDimensionalExponents* b) {
		// For every attribute (which are all integers) check equality

		unsigned num_attrs = a->data().getArgumentCount();
		for (unsigned i = 0; i < num_attrs; ++i) {
			const int v1 = *a->data().getArgument(i);
			const int v2 = *b->data().getArgument(i);
			if (v1 != v2) {
				return v1 < v2;
			}
		}

		return false;
	}

	bool operator()(IfcSchema::IfcMeasureWithUnit* a, IfcSchema::IfcMeasureWithUnit* b) {
		// Assume the value component is enough to differentiate

		double v1 = *a->ValueComponent()->data().getArgument(0);
		double v2 = *b->ValueComponent()->data().getArgument(0);
		return v1 < v2;
	}

	bool operator()(IfcSchema::IfcGeometricRepresentationSubContext* a, IfcSchema::IfcGeometricRepresentationSubContext* b) {
		return a->ContextType() < b->ContextType();
	}

	bool operator()(IfcSchema::IfcGeometricRepresentationContext* a, IfcSchema::IfcGeometricRepresentationContext* b) {
		return a->ContextType() < b->ContextType();
	}

	bool operator()(IfcSchema::IfcSIUnit* a, IfcSchema::IfcSIUnit* b) {
		// Assume same units accross files

		return a->UnitType() < b->UnitType();
	}

	bool operator()(IfcSchema::IfcBuildingStorey* a, IfcSchema::IfcBuildingStorey* b) {
		return a->Name() < b->Name();
	}

	bool operator()(IfcUtil::IfcBaseClass* a, IfcUtil::IfcBaseClass* b) {
		if (a->declaration().type() != b->declaration().type()) {
			throw std::runtime_error("Types not matching");
		}

		std::cerr << IfcSchema::Type::ToString(a->declaration().type()) << std::endl;

		if (a->declaration().type() == IfcSchema::Type::IfcSite) { return (*this)((IfcSchema::IfcSite*) a, (IfcSchema::IfcSite*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcConversionBasedUnit) { return (*this)((IfcSchema::IfcConversionBasedUnit*) a, (IfcSchema::IfcConversionBasedUnit*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcDimensionalExponents) { return (*this)((IfcSchema::IfcDimensionalExponents*) a, (IfcSchema::IfcDimensionalExponents*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcMeasureWithUnit) { return (*this)((IfcSchema::IfcMeasureWithUnit*) a, (IfcSchema::IfcMeasureWithUnit*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcProject) { return (*this)((IfcSchema::IfcProject*) a, (IfcSchema::IfcProject*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcBuilding) { return (*this)((IfcSchema::IfcBuilding*) a, (IfcSchema::IfcBuilding*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcPostalAddress) { return (*this)((IfcSchema::IfcPostalAddress*) a, (IfcSchema::IfcPostalAddress*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcUnitAssignment) { return (*this)((IfcSchema::IfcUnitAssignment*) a, (IfcSchema::IfcUnitAssignment*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcGeometricRepresentationSubContext) { return (*this)((IfcSchema::IfcGeometricRepresentationSubContext*) a, (IfcSchema::IfcGeometricRepresentationSubContext*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcGeometricRepresentationContext) { return (*this)((IfcSchema::IfcGeometricRepresentationContext*) a, (IfcSchema::IfcGeometricRepresentationContext*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcSIUnit) { return (*this)((IfcSchema::IfcSIUnit*) a, (IfcSchema::IfcSIUnit*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcBuildingStorey) { return (*this)((IfcSchema::IfcBuildingStorey*) a, (IfcSchema::IfcBuildingStorey*) b); }

		throw std::runtime_error("Unexpected type");
	}
};

int main(int argc, char** argv) {
	
	std::set<IfcSchema::Type::Enum> shared {
		IfcSchema::Type::IfcSite,
		IfcSchema::Type::IfcConversionBasedUnit,
		IfcSchema::Type::IfcDimensionalExponents,
		IfcSchema::Type::IfcMeasureWithUnit,
		IfcSchema::Type::IfcProject,
		IfcSchema::Type::IfcBuilding,
		IfcSchema::Type::IfcPostalAddress,
		IfcSchema::Type::IfcUnitAssignment,
		IfcSchema::Type::IfcGeometricRepresentationSubContext,
		IfcSchema::Type::IfcGeometricRepresentationContext,
		IfcSchema::Type::IfcSIUnit,
		IfcSchema::Type::IfcBuildingStorey
	};

	std::vector<IfcParse::IfcFile*> files;

	for (int i = 1; i < argc; ++i) {
		files.push_back(new IfcParse::IfcFile());
		files.back()->Init(argv[i]);
	}

	std::set<IfcUtil::IfcBaseClass*> shared_instances;

	for (auto& ty : shared) {	
		std::cout << IfcSchema::Type::ToString(ty) << std::endl;

		for (auto& file : files) {
			IfcEntityList::ptr insts = file->entitiesByType(ty);
			std::vector<IfcUtil::IfcBaseClass*> no_subtypes;
			std::copy_if(insts->begin(), insts->end(), std::back_inserter(no_subtypes), [ty](IfcUtil::IfcBaseClass* inst) {
				return inst->declaration().type() == ty;
			});
			
			std::set<IfcUtil::IfcBaseClass*, ifc_inst_cmp> insts_unique(no_subtypes.begin(), no_subtypes.end());

			if (insts_unique.size() != no_subtypes.size()) {
				throw std::runtime_error("Non-unique instances encountered within file");
			}

			shared_instances.insert(insts_unique.begin(), insts_unique.end());
		}
	}

	std::set<IfcUtil::IfcBaseClass*> shared_instances_and_refs;

	for (auto& inst : shared_instances) {
		IfcEntityList::ptr insts = inst->data().file->traverse(inst);

		// Filter out simple types
		std::vector<IfcUtil::IfcBaseClass*> insts_without_types;
		std::copy_if(insts->begin(), insts->end(), std::back_inserter(insts_without_types), [](IfcUtil::IfcBaseClass* inst) {
			return inst->declaration().as_entity() != nullptr;
		});

		shared_instances_and_refs.insert(insts_without_types.begin(), insts_without_types.end());
	}

	for (auto& i : shared_instances_and_refs) {
		if (shared_instances.find(i) == shared_instances.end()) {
			std::cerr << i->data().toString() << std::endl;
		}
	}		
	
	IfcParse::Hdf5Settings settings;
	settings.profile() = IfcParse::Hdf5Settings::standard_referenced;

	H5::H5File file("merged.hdf", H5F_ACC_TRUNC);
	H5::Group group1 = file.createGroup("shared");

	IfcParse::IfcHdf5File ifc_hdf5(file, get_schema(), settings);
	IfcParse::IfcSpfHeader header;
	header.set_default();

	IfcParse::instance_enumerator shared_insts_enum(&header, shared_instances_and_refs.begin(), shared_instances_and_refs.end());

	ifc_hdf5.write_schema();
	ifc_hdf5.write_population(group1, shared_insts_enum);
}
