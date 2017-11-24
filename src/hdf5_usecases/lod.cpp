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
#include "../../../src/ifcgeom/IfcGeom.h"

#include <Bnd_Box.hxx>
#include <BRepBndLib.hxx>

int main(int, char** argv) {
	IfcParse::IfcFile f;
	f.Init(argv[1]);

	std::vector<IfcSchema::IfcProductDefinitionShape*> new_defs;
	IfcSchema::IfcProductDefinitionShape::list::ptr defs = f.entitiesByType<IfcSchema::IfcProductDefinitionShape>();

	IfcGeom::Kernel kernel;
	kernel.initializeUnits(*f.entitiesByType<IfcSchema::IfcUnitAssignment>()->begin());

	std::transform(defs->begin(), defs->end(), std::back_inserter(new_defs), [&kernel](IfcSchema::IfcProductDefinitionShape* def) {
		Bnd_Box box;
		auto reps = def->Representations();
		IfcSchema::IfcRepresentationContext* context;

		std::for_each(reps->begin(), reps->end(), [&kernel, &box, &context](auto rep) {
			IfcGeom::IfcRepresentationShapeItems items;

			if (rep->RepresentationIdentifier() == "Body") {
				kernel.convert(rep, items);
				context = rep->ContextOfItems();
			}

			for (auto& i : items) {
				BRepBndLib::AddClose(i.Shape(), box);
			}
		});

		double x1, y1, z1, x2, y2, z2;
		box.Get(x1, y1, z1, x2, y2, z2);

		IfcSchema::IfcCartesianPoint* corner = new IfcSchema::IfcCartesianPoint(std::vector<double>{x1, y1, z1});;
		IfcSchema::IfcBoundingBox* bbox = new IfcSchema::IfcBoundingBox(corner, x2-x1, y2-y1, z2-z1);
		IfcSchema::IfcRepresentationItem::list::ptr items(new IfcSchema::IfcRepresentationItem::list);
		items->push(bbox);
		
		IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(context, std::string("Body"), std::string("BoundingBox"), items);
		IfcSchema::IfcRepresentation::list::ptr new_reps(new IfcSchema::IfcRepresentation::list);
		new_reps->push(rep);
		
		IfcSchema::IfcProductDefinitionShape* new_def = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, new_reps);
		return new_def;
	});
}