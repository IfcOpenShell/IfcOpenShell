#include "profile_helper.h"

#include "wire_utils.h"
#include "Kernel.h"
#include "../ifcparse/IfcLogger.h"

#include <TopoDS_Face.hxx>
#include <TopoDS_Vertex.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepBuilderAPI_MakeWire.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepFilletAPI_MakeFillet2d.hxx>
#include <TopoDS.hxx>

#include <algorithm>

bool IfcGeom::util::profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face_shape) {
	TopoDS_Vertex* vertices = new TopoDS_Vertex[numVerts];

	for (int i = 0; i < numVerts; i++) {
		gp_XY xy(verts[2 * i], verts[2 * i + 1]);
		trsf.Transforms(xy);
		vertices[i] = BRepBuilderAPI_MakeVertex(gp_Pnt(xy.X(), xy.Y(), 0.0f));
	}

	BRepBuilderAPI_MakeWire w;
	for (int i = 0; i < numVerts; i++)
		w.Add(BRepBuilderAPI_MakeEdge(vertices[i], vertices[(i + 1) % numVerts]));

	TopoDS_Face face;
	// For profiles we're not checking wire intersections regardless of settings
	util::convert_wire_to_face(w.Wire(), face, {false, false, 0., 0.});

	if (numFillets && *std::max_element(filletRadii, filletRadii + numFillets) > ALMOST_ZERO) {
		BRepFilletAPI_MakeFillet2d fillet(face);
		for (int i = 0; i < numFillets; i++) {
			const double radius = filletRadii[i];
			if (radius <= ALMOST_ZERO) continue;
			fillet.AddFillet(vertices[filletIndices[i]], radius);
		}
		fillet.Build();
		if (fillet.IsDone()) {
			face = TopoDS::Face(fillet.Shape());
		} else {
			Logger::Error("Failed to process profile fillets");
		}
	}

	face_shape = face;

	delete[] vertices;
	return true;
}