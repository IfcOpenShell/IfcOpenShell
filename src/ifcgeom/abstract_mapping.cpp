#include "abstract_mapping.h"

#include "../ifcparse/IfcFile.h"

ifcopenshell::geometry::impl::MappingFactoryImplementation& ifcopenshell::geometry::impl::mapping_implementations() {
	static MappingFactoryImplementation impl;
	return impl;
}

extern void init_MappingImplementation_Ifc2x3(ifcopenshell::geometry::impl::MappingFactoryImplementation*);
extern void init_MappingImplementation_Ifc4(ifcopenshell::geometry::impl::MappingFactoryImplementation*);
// extern void init_MappingImplementation_Ifc4x1(ifcopenshell::geometry::impl::MappingFactoryImplementation*);
// extern void init_MappingImplementation_Ifc4x2(ifcopenshell::geometry::impl::MappingFactoryImplementation*);

ifcopenshell::geometry::impl::MappingFactoryImplementation::MappingFactoryImplementation() {
	init_MappingImplementation_Ifc2x3(this);
	init_MappingImplementation_Ifc4(this);
	// init_MappingImplementation_Ifc4x1(this);
	// init_MappingImplementation_Ifc4x2(this);
}

void ifcopenshell::geometry::impl::MappingFactoryImplementation::bind(const std::string& schema_name, ifcopenshell::geometry::impl::mapping_fn fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

ifcopenshell::geometry::abstract_mapping* ifcopenshell::geometry::impl::MappingFactoryImplementation::construct(IfcParse::IfcFile* file, settings& s) {
	const std::string schema_name_lower = boost::to_lower_copy(file->schema()->name());
	std::map<std::string, ifcopenshell::geometry::impl::mapping_fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == end()) {
		throw IfcParse::IfcException("No geometry mapping registered for " + schema_name_lower);
	}
	return it->second(file, s);
}

void ifcopenshell::geometry::remove_duplicate_points_from_loop(std::vector<taxonomy::point3>& polygon, bool closed, double tol) {
	for (;;) {
		bool removed = false;
		int n = polygon.size() - (closed ? 0 : 1);
		for (int i = 1; i <= n; ++i) {
			// wrap around to the first point in case of a closed loop
			int j = (i % polygon.size()) + 1;
			double dist = (polygon.at(i - 1).components() - polygon.at(j - 1).components()).squaredNorm();
			if (dist < tol) {
				// do not remove the first or last point to
				// maintain connectivity with other wires
				if ((closed && j == 1) || (!closed && j == n)) polygon.erase(polygon.begin() + i - 1);
				else polygon.erase(polygon.begin() + j - 1);
				removed = true;
				break;
			}
		}
		if (!removed) break;
	}
}