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

#include <BRep_Tool.hxx>
#include <BRepTools.hxx>
#include <BRep_Builder.hxx>

#include <TopoDS.hxx>
#include <TopoDS_Compound.hxx>
#include <Geom_Plane.hxx>
#include <GProp_GProps.hxx>
#include <BRepGProp.hxx>

#include "IfcGeomRepresentation.h"
#include "../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

ifcopenshell::geometry::Representation::Serialization::Serialization(const BRep& brep)
	: Representation(brep.settings())
	, id_(brep.id())
{
	ifcopenshell::geometry::ConversionResultShape* shape = brep.as_compound();
	TopoDS_Compound compound = TopoDS::Compound(((OpenCascadeShape*) shape)->shape());
	delete shape;

	for (ifcopenshell::geometry::ConversionResults::const_iterator it = brep.begin(); it != brep.end(); ++ it) {
		if (it->hasStyle() && it->Style().diffuse) {
			auto clr = it->Style().diffuse.get().components;
			surface_styles_.push_back(clr[0]);
			surface_styles_.push_back(clr[1]);
			surface_styles_.push_back(clr[2]);
		} else {
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
			surface_styles_.push_back(-1.);
		}
		if (it->hasStyle() && it->Style().transparency) {
			surface_styles_.push_back(1. - *it->Style().transparency);
		} else {
			surface_styles_.push_back(1.);
		}
	}
	std::stringstream sstream;
	BRepTools::Write(compound,sstream);
	brep_data_ = sstream.str();
}

// @todo copied from kernel
#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBuilderAPI_GTransform.hxx>

TopoDS_Shape apply_transformation(const TopoDS_Shape& s, const gp_Trsf& t) {
	if (t.Form() == gp_Identity) {
		return s;
	} else {
		/// @todo set to 1. and exactly 1. or use epsilon?
		if (t.ScaleFactor() != 1.) {
			return BRepBuilderAPI_Transform(s, t, true);
		} else {
			return s.Moved(t);
		}
	}
}

TopoDS_Shape apply_transformation(const TopoDS_Shape& s, const gp_GTrsf& t) {
	if (t.Form() == gp_Other) {
		return BRepBuilderAPI_GTransform(s, t, true);
	} else {
		return apply_transformation(s, t.Trsf());
	}
}

ifcopenshell::geometry::ConversionResultShape* ifcopenshell::geometry::Representation::BRep::as_compound(bool force_meters) const {
	TopoDS_Compound compound;
	BRep_Builder builder;
	builder.MakeCompound(compound);

	for (ifcopenshell::geometry::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
		const TopoDS_Shape& s = *(OpenCascadeShape*) it->Shape();
		
		// @todo, check
		gp_GTrsf trsf;
		for (int i = 0; i < 3; ++i) {
			for (int j = 0; j < 4; ++i) {
				trsf.SetValue(i + 1, j + 1, it->Placement().components(i, j));
			}
		}

		if (!force_meters && settings().get(ifcopenshell::geometry::settings::CONVERT_BACK_UNITS)) {
			gp_Trsf scale;
			scale.SetScaleFactor(1.0 / settings().unit_magnitude());
			trsf.PreMultiply(scale);
		}

		const TopoDS_Shape moved_shape = apply_transformation(s, trsf);
		builder.Add(compound, moved_shape);
	}

	return new OpenCascadeShape(compound);
}

namespace {
	void accumulate(const gp_Ax3& ax, const gp_Dir& normal, double area, double& along_x, double& along_y, double& along_z) {
		along_x += area * fabs(ax.XDirection().Dot(normal));
		along_y += area * fabs(ax.YDirection().Dot(normal));
		along_z += area * fabs(ax.Direction().Dot(normal));
	}

	void surface_area_along_direction(double tol, const TopoDS_Shape& s, const gp_Ax3& ax, double& along_x, double& along_y, double& along_z) {
		along_x = along_y = along_z = 0.;

		bool meshed = false;

		TopExp_Explorer exp(s, TopAbs_FACE);
		for (; exp.More(); exp.Next()) {
			const TopoDS_Face& face = TopoDS::Face(exp.Current());
			Handle(Geom_Surface) surf = BRep_Tool::Surface(face);
			Handle(Geom_Plane) plane = Handle(Geom_Plane)::DownCast(surf);

			if (surf->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
				GProp_GProps prop_area;
				BRepGProp::SurfaceProperties(face, prop_area);
				const double area = prop_area.Mass();

				accumulate(ax, plane->Position().Direction(), area, along_x, along_y, along_z);
			} else {

				if (!meshed) {
					try {
						BRepMesh_IncrementalMesh(s, tol);
					} catch (...) {
						Logger::Message(Logger::LOG_ERROR, "Failed to triangulate shape");
						return;
					}
					meshed = true;
				}

				TopLoc_Location loc;
				Handle(Poly_Triangulation) tri = BRep_Tool::Triangulation(face, loc);
				if (!tri.IsNull()) {
					const TColgp_Array1OfPnt& nodes = tri->Nodes();
					std::vector<gp_XYZ> coords;
					coords.reserve(nodes.Length());

					for (int i = 1; i <= nodes.Length(); ++i) {
						coords.push_back(nodes(i).Transformed(loc).XYZ());
					}

					const Poly_Array1OfTriangle& triangles = tri->Triangles();
					for (int i = 1; i <= triangles.Length(); ++i) {
						int n1, n2, n3;

						if (face.Orientation() == TopAbs_REVERSED) {
							triangles(i).Get(n3, n2, n1);
						} else {
							triangles(i).Get(n1, n2, n3);
						}

						const gp_XYZ& pt1 = coords[n1 - 1];
						const gp_XYZ& pt2 = coords[n2 - 1];
						const gp_XYZ& pt3 = coords[n3 - 1];
						const gp_Vec v1 = pt2 - pt1;
						const gp_Vec v2 = pt3 - pt2;
						const gp_Vec v3 = pt1 - pt3;
						const gp_Vec normal_vector = v1 ^ v2;
						if (normal_vector.Magnitude() > 1.e-9) {
							gp_Dir normal = gp_Dir();

							double edge_lengths[3] = { v1.Magnitude(), v2.Magnitude(), v3.Magnitude() };
							std::sort(&edge_lengths[0], &edge_lengths[2]);

							const double& a = edge_lengths[0];
							const double& b = edge_lengths[1];
							const double& c = edge_lengths[2];

							const double area = 0.25 * sqrt((a + (b + c))*(c - (a - b))*(c + (a - b))*(a + (b - c)));
							accumulate(ax, normal, area, along_x, along_y, along_z);
						}
					}
				}
			}
		}
	}
}

bool ifcopenshell::geometry::Representation::BRep::calculate_surface_area(double& area) const {
	try {
		area = 0.;

		for (ifcopenshell::geometry::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
			GProp_GProps prop;
			BRepGProp::SurfaceProperties(*(OpenCascadeShape*)it->Shape(), prop);
			area += prop.Mass();
		}

		return true;
	} catch (...) {
		Logger::Error("Error during calculation of surface area");
		return false;
	}
}

bool ifcopenshell::geometry::Representation::BRep::calculate_volume(double& volume) const {
	try {
		volume = 0.;

		for (ifcopenshell::geometry::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
			if (it->Shape()->is_manifold()) {
				GProp_GProps prop;
				BRepGProp::VolumeProperties(*(OpenCascadeShape*)it->Shape(), prop);
				volume += prop.Mass();
			} else {
				return false;
			}
		}

		return true;
	} catch (...) {
		Logger::Error("Error during calculation of volume");
		return false;
	}
}

bool ifcopenshell::geometry::Representation::BRep::calculate_projected_surface_area(const ifcopenshell::geometry::taxonomy::matrix4& place, double & along_x, double & along_y, double & along_z) const {
	try {
		// @todo check
		gp_GTrsf trsf;
		for (int i = 0; i < 3; ++i) {
			for (int j = 0; j < 4; ++i) {
				trsf.SetValue(i + 1, j + 1, place.components(i, j));
			}
		}

		gp_Mat mat = trsf.Trsf().HVectorialPart();
		gp_Ax3 ax(trsf.TranslationPart(), mat.Column(3), mat.Column(1));

		along_x = along_y = along_z = 0.;

		for (ifcopenshell::geometry::ConversionResults::const_iterator it = begin(); it != end(); ++it) {
			double x, y, z;
			surface_area_along_direction(settings().deflection_tolerance(), *(OpenCascadeShape*)it->Shape(), ax, x, y, z);

			if (it->Shape()->is_manifold()) {
				x /= 2.;
				y /= 2.;
				z /= 2.;
			}

			along_x += x;
			along_y += y;
			along_z += z;
		}

		return true;
	} catch (...) {
		Logger::Error("Error during calculation of projected surface area");
		return false;
	}
}
