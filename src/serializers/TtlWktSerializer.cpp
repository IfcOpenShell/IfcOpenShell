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

#include "TtlWktSerializer.h"

#ifdef IFOPSH_WITH_OPENCASCADE
#include "../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"

#include <TopTools_HSequenceOfShape.hxx>
#include <BRepBuilderAPI_Transform.hxx>
#include <BRepBndLib.hxx>
#include <BRepAlgoAPI_Section.hxx>
#include <ShapeAnalysis_FreeBounds.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <TopoDS.hxx>
#include <Bnd_Box.hxx>
#include <gp_Pln.hxx>

#endif

#include <iomanip>
#include <iostream>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <queue>

namespace {
    const char* const LINESTRING = "LINESTRING";
    const char* const POLYGON = "POLYGON";

    void emit_polyhedral_surface(
        std::ostream& os,
        const std::vector<double>& vertices,
        const std::vector<std::vector<std::vector<int>>>& faces)
    {
        os << "POLYHEDRALSURFACE Z(";

        for (size_t i = 0; i < faces.size(); ++i) {
            const auto& face = faces[i];
            os << "(";
            for (size_t j = 0; j < face.size(); ++j) {
                const auto& loop = face[j];
                os << "(";
                for (size_t k = 0; k < loop.size(); ++k) {
                    int index = loop[k];
                    for (size_t l = 0; l < 3; ++l) {
                        os << vertices[index * 3 + l];
                        if (l != 2) {
                            os << " ";
                        }
                    }
                    if (k < loop.size() - 1) {
                        os << ", ";
                    }
                }
                os << ")";
                if (j < face.size() - 1) {
                    os << ", ";
                }
            }
            os << ")";
            if (i < faces.size() - 1) {
                os << ",";
            }
        }
        os << ")";
    }

    void emit_line_component(
        std::ostream& os, 
        const std::vector<double>& vertices,
        const std::vector<int>& component,
        bool force_2d = false,
        const char* const wkt_geometry_type=LINESTRING)
    {
        os << wkt_geometry_type << " ";
        if (!force_2d) {
            os << "Z";
        }
        os << "(";
        if (wkt_geometry_type == POLYGON) {
            os << "(";
        }
        for (size_t i = 0; i < component.size() + (wkt_geometry_type == POLYGON ? 1 : 0); ++i) {
            if (i != 0) {
                os << ", ";
            }
            for (size_t l = 0; l < (force_2d ? 2 : 3); ++l) {
                os << vertices[component[i % component.size()] * 3 + l];
                if (l != (force_2d ? 1 : 2)) {
                    os << " ";
                }
            }
        }
        os << ")";
        if (wkt_geometry_type == POLYGON) {
            os << ")";
        }
    }

    void emit_line_strings(
        std::ostream& os,
        const std::vector<double>& vertices,
        const std::vector<int>& lines,
        bool force_2d = false)
    {
        std::unordered_map<int, std::vector<int>> adjacencyList;
        std::unordered_set<int> visited;

        for (size_t i = 0; i < lines.size(); i += 2) {
            for (size_t j = 0; j < 2; ++j) {
                const auto& p0 = lines[i + (j ? 1 : 0)];
                const auto& p1 = lines[i + (j ? 0 : 1)];
                adjacencyList[p0].push_back(p1);
            }
        }

        auto traverseComponent = [&](int start) {
            std::vector<int> component;  // To store the current component
            std::queue<int> toVisit;
            toVisit.push(start);
            visited.insert(start);

            while (!toVisit.empty()) {
                int current = toVisit.front();
                toVisit.pop();
                component.push_back(current);

                for (int neighbor : adjacencyList[current]) {
                    if (visited.find(neighbor) == visited.end()) {
                        toVisit.push(neighbor);
                        visited.insert(neighbor);
                    }
                }
            }

            return component;
        };

        std::vector<std::vector<int>> components;

        for (auto it = lines.begin(); it != lines.end(); it += 2) {
            if (visited.find(*it) == visited.end()) {
                components.emplace_back(std::move(traverseComponent(*it)));
            }
        }

        if (components.size() == 1) {
            emit_line_component(os, vertices, components.front(), force_2d);
        } else {
            os << "GEOMETRYCOLLECTION(";
            for (auto it = components.begin(); it != components.end(); ++it) {
                if (it != components.begin()) {
                    os << ",";
                }
                emit_line_component(os, vertices, *it, force_2d);
            }
            os << ")";
        }
    }

    std::string escape_for_turtle(const std::u32string& input) {
        std::wostringstream escaped;
        escaped << "\"";

        for (auto& c : input) {
            switch (c) {
            case '\\':
                escaped << "\\\\";
                break;
            case '\"':
                escaped << "\\\"";
                break;
            case '\n':
                escaped << "\\n";
                break;
            case '\r':
                escaped << "\\r";
                break;
            case '\t':
                escaped << "\\t";
                break;
            default:
                if (c < 0x20 || c > 0x7E) {
                    escaped << "\\u"
                        << std::hex << std::setw(4) << std::setfill(L'0')
                        << (c & 0xFFFF);
                } else {
                    escaped.put(c);
                }
                break;
            }
        }
        escaped << "\"";
        return IfcUtil::convert_utf8(escaped.str());
    }

    template <typename Fn, typename... Ts>
    std::string capture_output(Fn fn, Ts... ts) {
        std::ostringstream oss;
        fn(oss, ts...);
        return oss.str();
    }
}

TtlWktSerializer::TtlWktSerializer(const stream_or_filename& filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings)
    : WriteOnlyGeometrySerializer(geometry_settings, settings)
    , filename_(filename)
{
    const auto& tri_setting = geometry_settings.get<ifcopenshell::geometry::settings::TriangulationType>().get();
    if (settings_.get<ifcopenshell::geometry::settings::WktUseSection>().get()) {
        const auto& it_output = geometry_settings.get<ifcopenshell::geometry::settings::IteratorOutput>().get();
        if (it_output != ifcopenshell::geometry::settings::NATIVE) {
            throw std::runtime_error("The RDF Turtle WKT serializer needs native geometry when section mode is enabled");
        }
    } else {
        if (tri_setting != ifcopenshell::geometry::settings::POLYHEDRON_WITH_HOLES) {
            throw std::runtime_error("The RDF Turtle WKT serializer needs POLYHEDRON_WITH_HOLES triangulation output");
        }
    }
    filename_.stream << std::setprecision(settings.get<ifcopenshell::geometry::settings::FloatingPointDigits>().get());
}

bool TtlWktSerializer::ready()
{
    return filename_.is_ready();
}

void TtlWktSerializer::writeHeader()
{
    using namespace ifcopenshell::geometry::settings;
    filename_.stream << "# File generated by IfcOpenShell " << IFCOPENSHELL_VERSION << "\n";
    filename_.stream << "@prefix geo: <http://www.opengis.net/ont/geosparql#> .\n";
    if (settings_.get<BaseUri>().has()) {
        filename_.stream << "@prefix base: <" << settings_.get<BaseUri>().get() << "> .\n";
    } else {
        filename_.stream << "@prefix base: <http://example.org/> .\n";
    }
    filename_.stream << "@prefix dcterms: <http://purl.org/dc/terms/> .\n";
    filename_.stream << "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n\n";
}

void TtlWktSerializer::write(const IfcGeom::TriangulationElement* o)
{
    filename_.stream << ttl_object_id(o) << " a geo:Feature ;\n";
    filename_.stream << "    dcterms:identifier " << escape_for_turtle(
        IfcUtil::convert_utf8_to_utf32(o->guid())) << " ;\n";
    filename_.stream << "    rdfs:label " << escape_for_turtle(
        IfcUtil::convert_utf8_to_utf32(o->name())
    ) << " ;\n";
    filename_.stream << "    geo:hasGeometry " << ttl_object_id(o, "_geometry") << " .\n\n";

    if (!o->geometry().polyhedral_faces_with_holes().empty()) {
        filename_.stream << ttl_object_id(o, "_geometry") << " a geo:Geometry ;\n";
        filename_.stream << "    geo:asWKT " << escape_for_turtle(
            IfcUtil::convert_utf8_to_utf32(
                capture_output(
                    emit_polyhedral_surface,
                    o->geometry().verts(),
                    o->geometry().polyhedral_faces_with_holes()))
        ) << "^^geo:wktLiteral .\n\n";

        Eigen::Map<const Eigen::Matrix<double, 3, Eigen::Dynamic>> vertex_map(o->geometry().verts().data(), 3, o->geometry().verts().size() / 3);

        boost::optional<std::vector<std::vector<int>>::const_iterator> lowest_face;
        double lowest_z = std::numeric_limits<double>::infinity();

        for (const auto& f : o->geometry().polyhedral_faces_with_holes()) {
            Eigen::Vector3d v0, v1, v2, v1_v0, v2_v0;
            for (size_t i = 0; i < f[0].size(); ++i) {
                v0 = vertex_map.transpose().row(f[0][0 + i]);
                v1 = vertex_map.transpose().row(f[0][1 + i]);
                v2 = vertex_map.transpose().row(f[0][2 + i]);
                v1_v0 = v1 - v0;
                v2_v0 = v2 - v0;
                v1_v0.normalize();
                v2_v0.normalize();
                if ((std::abs(v1_v0.dot(v2_v0)) + 1.e-9) >= 1.0) {
                    // Don't derive normal from collinear edges
                    continue;
                }
                break;
            }

            Eigen::Vector3d cross_product = v1_v0.cross(v2_v0);
            cross_product.normalize();

            // @nb we take abs because so that we can ignore face orientation and potential convatities rquire
            if ((std::abs(cross_product.z()) + 1.e-9) >= 1.0 && v0.z() < lowest_z) {
                lowest_face = f.begin();
                lowest_z = v0.z();
            }
        }

        if (lowest_face) {
            filename_.stream << ttl_object_id(o) << " geo:hasGeometry " << ttl_object_id(o, "_footprint_geometry") << " .\n\n";
            filename_.stream << ttl_object_id(o, "_footprint_geometry") << " a geo:Geometry ;\n";
            filename_.stream << "    geo:asWKT " << escape_for_turtle(
                IfcUtil::convert_utf8_to_utf32(
                    capture_output(
                        // @nb this is line_component, because this is the linestring
                        // from a faceboundary, not the edges as pairs of indices.
                        emit_line_component,
                        o->geometry().verts(),
                        **lowest_face,
                        true,
                        POLYGON))
            ) << "^^geo:wktLiteral .\n\n";
        }
    } else {
        filename_.stream << ttl_object_id(o, "_geometry") << " a geo:Geometry ;\n";
        bool force_2d = true;
        double z_value;
        for (size_t i = 2; i < o->geometry().verts().size(); i += 3) {
            const auto& cur = o->geometry().verts()[i];
            if (i == 2) {
                z_value = cur;
            } else {
                if (z_value != cur) {
                    force_2d = false;
                    break;
                }
            }
        }
        filename_.stream << "    geo:asWKT " << escape_for_turtle(
            IfcUtil::convert_utf8_to_utf32(
                capture_output(
                    emit_line_strings,
                    o->geometry().verts(),
                    o->geometry().edges(),
                    force_2d))
        ) << "^^geo:wktLiteral .\n\n";
    }
}

void TtlWktSerializer::write(const IfcGeom::BRepElement* brep_obj) {
#ifdef IFOPSH_WITH_OPENCASCADE
	filename_.stream << ttl_object_id(brep_obj) << " a geo:Feature ;\n";
	filename_.stream << "    dcterms:identifier " << escape_for_turtle(
		IfcUtil::convert_utf8_to_utf32(brep_obj->guid())) << " ;\n";
	filename_.stream << "    rdfs:label " << escape_for_turtle(
		IfcUtil::convert_utf8_to_utf32(brep_obj->name())
	) << " .\n";

    // @todo unify logic with SVG serializer

	auto itm = brep_obj->geometry().as_compound();
	TopoDS_Shape compound_local = ((ifcopenshell::geometry::OpenCascadeShape*)itm)->shape();
	delete itm;

	gp_Trsf trsf;
	const auto& m = brep_obj->transformation().data()->ccomponents();
	trsf.SetValues(
		m(0, 0), m(0, 1), m(0, 2), m(0, 3),
		m(1, 0), m(1, 1), m(1, 2), m(1, 3),
		m(2, 0), m(2, 1), m(2, 2), m(2, 3)
	);

	BRepBuilderAPI_Transform make_transform_global(compound_local, trsf, true);
	make_transform_global.Build();
	auto compound = make_transform_global.Shape();

	Bnd_Box bb;
	try {
		BRepBndLib::Add(compound, bb);
	} catch (const Standard_Failure&) {}

	// Empty geometry
	if (bb.IsVoid()) {
		return;
	}

	double x1, y1, zmin, x2, y2, zmax;
	bb.Get(x1, y1, zmin, x2, y2, zmax);

	gp_Pln pln(gp_Pnt(0, 0, zmin + 1.), gp::DZ());

	Handle(TopTools_HSequenceOfShape) wires = new TopTools_HSequenceOfShape();

	size_t N = 0;
	TopoDS_Iterator it(compound);
	// Iterate over components of compound to have better chance of matching section edges to closed wires
	for (; it.More(); it.Next()) {
		Handle(TopTools_HSequenceOfShape) edges = new TopTools_HSequenceOfShape();
		TopoDS_Shape result = BRepAlgoAPI_Section(it.Value(), pln);

		{
			TopExp_Explorer exp(result, TopAbs_EDGE);
			for (; exp.More(); exp.Next()) {
				edges->Append(exp.Current());
			}
		}

		ShapeAnalysis_FreeBounds::ConnectEdgesToWires(edges, 1e-4, false, wires);
		for (int i = 1; i <= wires->Length(); ++i) {
			const TopoDS_Wire& wire = TopoDS::Wire(wires->Value(i));
			BRepTools_WireExplorer it(wire);
			std::vector<double> loop_coords;
			for (; it.More(); it.Next()) {
				const auto& v = it.CurrentVertex();
				auto pnt = BRep_Tool::Pnt(v);
				loop_coords.push_back(pnt.X());
				loop_coords.push_back(pnt.Y());
				loop_coords.push_back(pnt.Z());
			}
			std::vector<int> loop_idxs(loop_coords.size() / 3);
			for (int i = 0; i < loop_idxs.size(); ++i) {
				loop_idxs[i] = i;
			}

			std::string postfix = "_section_geometry_" + std::to_string(N++);

			filename_.stream << ttl_object_id(brep_obj) << " geo:hasGeometry " << ttl_object_id(brep_obj, postfix.c_str()) << " .\n\n";
			filename_.stream << ttl_object_id(brep_obj, postfix.c_str()) << " a geo:Geometry ;\n";
			filename_.stream << "    geo:asWKT " << escape_for_turtle(
				IfcUtil::convert_utf8_to_utf32(
					capture_output(
						emit_line_component,
						loop_coords,
						loop_idxs,
						true,
						POLYGON))
			) << "^^geo:wktLiteral .\n\n";
		}
	}
#endif
}

std::string TtlWktSerializer::ttl_object_id(const IfcGeom::Element* o, const char* const postfix)
{
	using namespace ifcopenshell::geometry::settings;
	auto oid = boost::replace_all_copy(object_id(o), "-", "_");
	if (oid.find('$') == std::string::npos) {
		return "base:" + oid + (postfix ? postfix : (const char* const)"");
	} else {
		std::string base;
		if (settings_.get<BaseUri>().has()) {
			base = settings_.get<BaseUri>().get();
		} else {
			base = "http://example.org/";
		}
		return "<" + base + oid + (postfix ? postfix : (const char* const)"") + ">";
	}
}

bool TtlWktSerializer::isTesselated() const {
    using namespace ifcopenshell::geometry::settings;
    return !settings_.get<WktUseSection>().get();
}
