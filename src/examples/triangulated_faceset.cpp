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

/********************************************************************************
 *                                                                              *
 * Example that generates an IfcTriangulatedFaceSet                             *
 *                                                                              *
 ********************************************************************************/

#include <iostream>
#include <fstream>
#include <optional>

#include "ifcparse/macros.h"

#ifndef IfcSchema
#define IfcSchema Ifc4
#endif

#include INCLUDE_SCHEMA(ifcparse, IfcSchema)
#include INCLUDE_SCHEMA_DEFINITIONS(ifcparse, IfcSchema)

#include "ifcparse/IfcHierarchyHelper.h"

#include "suzanne_geometry.h"

typedef std::string S;
typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = boost::none;

template <typename T>
std::vector< std::vector<T> > create_vector_from_array(const T* arr, unsigned size) {
	std::vector< std::vector<T> > result;
	result.reserve(size);	
	
	for (unsigned i = 0; i < size; ) {
		std::vector<T> ts; ts.reserve(3);
		for (unsigned j = 0; j < 3; ++i, ++j) {
			ts.push_back(arr[i]);
		}
		result.push_back(ts);
	}

	return result;
}

int main(int argc, char** argv) {
	IfcHierarchyHelper<IfcSchema> file;

	IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
		guid(), 0, S("Blender's Suzanne"), null, null, 0, 0, null, null);
	file.addBuildingProduct(product);
	product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	product->setObjectPlacement(file.addLocalPlacement());

	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list);

	std::vector< std::vector< double > > vertices_vector = create_vector_from_array(vertices, sizeof(vertices) / sizeof(vertices[0]));
	std::vector< std::vector< int > > indices_vector = create_vector_from_array(indices, sizeof(indices) / sizeof(indices[0]));

	IfcSchema::IfcCartesianPointList3D* coordinates = new IfcSchema::IfcCartesianPointList3D(vertices_vector
#ifdef SCHEMA_IfcCartesianPointList3D_HAS_TagList
		, boost::none
#endif
	);
	IfcSchema::IfcTriangulatedFaceSet* faceset = new IfcSchema::IfcTriangulatedFaceSet(coordinates, null, null, indices_vector, null);
		
	items->push(faceset);
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		file.getRepresentationContext("Model"), S("Body"), S("SurfaceModel"), items);
	reps->push(rep);

	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	file.addEntity(shape);
		
	product->setRepresentation(shape);

	const std::string filename = "triangulated_faceset.ifc";
	file.header().file_name()->setname(filename);
	std::ofstream f(filename);
	f << file;
}
