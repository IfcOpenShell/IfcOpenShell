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
 * Example that generates a Constructive Solid Geometry example                 *
 *                                                                              *
 ********************************************************************************/

#include <string>
#include <iostream>
#include <fstream>

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcHierarchyHelper.h"

typedef std::string S;
typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = boost::none;

class Node {
private:
	typedef enum {
		OP_ADD, OP_SUBTRACT, OP_INTERSECT, OP_TERMINAL
	} Op;
	typedef enum {
		PRIM_BOX, PRIM_CONE, PRIM_CYLINDER, PRIM_PYRAMID, PRIM_SPHERE
	} Prim;

	double x,y,z, zx,zy,zz, xx,xy,xz, a,b,c;
	const Node *left, *right;
	
	Op op;
	Prim prim;

	Node& operate(Op op, const Node& p) {
		left = new Node(*this);
		right = new Node(p);
		this->op = op;
		return *this;
	}

	Node(Prim p, double la, double lb=0., double lc=0.)
		: prim(p), op(OP_TERMINAL),
		  x(0.), y(0.), z(0.), 
		  zx(0.), zy(0.), zz(1.), 
		  xx(1.), xy(0.), xz(0.), 
		  a(la), b(lb), c(lc) {}
public:
	static Node Sphere(double r) {
		return Node(PRIM_SPHERE, r);
	}
	static Node Box(double dx, double dy, double dz) {
		return Node(PRIM_BOX, dx, dy, dz);
	}
	static Node Pyramid(double dx, double dy, double dz) {
		return Node(PRIM_PYRAMID, dx, dy, dz);
	}
	static Node Cylinder(double r, double h) {
		return Node(PRIM_CYLINDER, r, h);
	}
	static Node Cone(double r, double h) {
		return Node(PRIM_CONE, r, h);
	}

	Node& move(
		double px = 0., double py = 0., double pz = 0., 
		double zx = 0., double zy = 0., double zz = 1., 
		double xx = 1., double xy = 0., double xz = 0.) 
	{
		this->x = px; this->y = py;	this->z = pz;
		this->zx = zx; this->zy = zy; this->zz = zz;
		this->xx = xx; this->xy = xy; this->xz = xz;
		return *this;
	}

	Node& add(const Node& p) {
		return operate(OP_ADD, p);
	}
	Node& subtract(const Node& p) {
		return operate(OP_SUBTRACT, p);
	}
	Node& intersect(const Node& p) {
		return operate(OP_INTERSECT, p);
	}

	IfcSchema::IfcRepresentationItem* serialize(IfcHierarchyHelper& file) const {
		IfcSchema::IfcRepresentationItem* my;
		if (op == OP_TERMINAL) {
			IfcSchema::IfcAxis2Placement3D* place = file.addPlacement3d(x,y,z,zx,zy,zz,xx,xy,xz);
			if (prim == PRIM_SPHERE) {
				my = new IfcSchema::IfcSphere(place, a);
			} else if (prim == PRIM_BOX) {
				my = new IfcSchema::IfcBlock(place, a, b, c);
			} else if (prim == PRIM_PYRAMID) {
				my = new IfcSchema::IfcRectangularPyramid(place, a, b, c);
			} else if (prim == PRIM_CYLINDER) {
				my = new IfcSchema::IfcRightCircularCylinder(place, b, a);
			} else if (prim == PRIM_CONE) {
				my = new IfcSchema::IfcRightCircularCone(place, b, a);
			}
		} else {
			IfcSchema::IfcBooleanOperator::IfcBooleanOperator o;
			if (op == OP_ADD) {
				o = IfcSchema::IfcBooleanOperator::IfcBooleanOperator_UNION;
			} else if (op == OP_SUBTRACT) {
				o = IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE;
			} else if (op == OP_INTERSECT) {
				o = IfcSchema::IfcBooleanOperator::IfcBooleanOperator_INTERSECTION;
			}
			my = new IfcSchema::IfcBooleanResult(o, left->serialize(file), right->serialize(file));
		}
		file.addEntity(my);
		return my;
	}
};

int main(int argc, char** argv) {
	const char filename[] = "IfcCsgPrimitive.ifc";
	IfcHierarchyHelper file;
	file.header().file_name().name(filename);

	IfcSchema::IfcRepresentationItem* csg1 = Node::Box(8000.,6000.,3000.).subtract(
		Node::Box(7600.,5600.,2800.).move(200.,200.,200.)
	).add(
		Node::Pyramid(8000.,6000.,3000.).move(0,0,3000.).add(
			Node::Cylinder(1000.,4000.).move(4000.,1000.,4000., 0.,1.,0.)
		).subtract(
			Node::Pyramid(7600.,5600.,2800.).move(200.,200.,3000.)
		).subtract(
			Node::Cylinder(900.,4000.).move(4000.,1000.,4000., 0.,1.,0.).intersect(
				Node::Box(2000.,4000.,1000.).move(3000.,1000.,4000.)
			)
		)
	).serialize(file);

	const double x = 1000.; const double y = -4000.;

	IfcSchema::IfcRepresentationItem* csg2 = Node::Sphere(5000.).move(x,y,-4500.).intersect(
		Node::Box(6000., 6000., 6000.).move(x-3000., y-3000., 0.)
	).add(
		Node::Cone(500., 3000.).move(x,y).add(
			Node::Cone(1500., 1000.).move(x,y, 900.).add(
				Node::Cone(1100., 1000.).move(x,y, 1800.).add(
					Node::Cone(750., 600.).move(x,y, 2700.)
	)))).serialize(file);

	IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
			guid(), 0, S("IfcCsgPrimitive"), null, null, 0, 0, null, null);

	file.addBuildingProduct(product);

	product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	product->setObjectPlacement(file.addLocalPlacement());
		
	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list());
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list());
		
	items->push(csg1);
	items->push(csg2);
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		file.getSingle<IfcSchema::IfcRepresentationContext>(), S("Body"), S("CSG"), items);
	reps->push(rep);

	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(null, null, reps);
	file.addEntity(rep);
	file.addEntity(shape);
		
	product->setRepresentation(shape);

	file.getSingle<IfcSchema::IfcProject>()->setName("IfcCompositeProfileDef");

	std::ofstream f(filename);
	f << file;
}
