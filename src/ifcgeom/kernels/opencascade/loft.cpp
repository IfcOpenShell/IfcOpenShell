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

#include "base_utils.h"
#include "opencascade_kernel.h"

#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepOffsetAPI_ThruSections.hxx>
#include <BRepFill.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <TopExp.hxx>

using namespace ifcopenshell::geom;
using namespace ifcopenshell::geom::kernels;
using namespace ifcopenshell::geom::util;

bool open_cascade_kernel::convert(const taxonomy::loft::ptr loft, TopoDS_Shape& result) {
    if (loft->children.size() < 2) {
        logger_.error("OpenCascade kernel: loft requires at least two sections; got " + std::to_string(loft->children.size()), loft->instance);
        return false;
    }

    if (loft->is_polygonal()) {
        return convert(loft->to_polyhedron(), result);
    }

    if (!loft->axis && !settings_.get<settings::LoftUseRuledSurfaces>().get()) {
        return convert(loft->make_polygonal_sections(settings_)->to_polyhedron(), result);
    }

    if (!loft->is_polygonal()) {
        TopoDS_Shape f0, f1;
        std::vector<std::vector<TopoDS_Wire>> sections;

        // Convert all children to vectors of wires
        for (const auto& child : loft->children) {
            const auto section_index = sections.size() + 1;
            const auto section_context = "OpenCascade kernel: loft section " + std::to_string(section_index) + "/" + std::to_string(loft->children.size());
            if (child->kind() != taxonomy::FACE) {
                logger_.error(section_context + " is not a face (" + taxonomy::kind_to_string(child->kind()) + ")", loft->instance);
                return false;
            }
            TopoDS_Shape shape;
            if (!convert(std::static_pointer_cast<taxonomy::face>(child), shape)) {
                logger_.error(section_context + " failed to convert to a face", loft->instance);
                return false;
            }
            if (shape.IsNull() || shape.ShapeType() != TopAbs_FACE) {
                logger_.error(section_context + " did not produce a single face", loft->instance);
                return false;
            }
            // At least make sure to have outer wire consistent, but in reality
            // this is probably not a concern given how to build up these faces
            auto f = TopoDS::Face(shape);

            if (child == loft->children.front()) {
                f0 = f;
            } else if (child == loft->children.back()) {
                f1 = f;
            }

            auto outer = BRepTools::OuterWire(f);
            sections.emplace_back();
            sections.back().push_back(outer);
            for (TopoDS_Iterator it(f); it.More(); it.Next()) {
                if (outer != it.Value()) {
                    sections.back().push_back(TopoDS::Wire(it.Value()));
                }
            }
        }

        auto first_wire_count = sections.front().size();
        for (auto& section : sections) {
            if (section.size() != first_wire_count) {
                logger_.error("GEO", 178, "OpenCascade kernel: inconsistent number of wires in loft sections; expected " + std::to_string(first_wire_count) + ", got " + std::to_string(section.size()), loft->instance);
                return false;
            }
        }

        if (f0.ShapeType() != TopAbs_FACE || f1.ShapeType() != TopAbs_FACE) {
            logger_.error("OpenCascade kernel: loft end sections are not faces", loft->instance);
            return false;
        }

        if (sections.size() == 2 && loft->axis) {
            TopoDS_Shell comp;
            BRep_Builder BB;
            BB.MakeShell(comp);
            TopExp_Explorer exp1(f0, TopAbs_WIRE);
            TopExp_Explorer exp2(f1, TopAbs_WIRE);
            for (; exp1.More() && exp2.More(); exp1.Next(), exp2.Next()) {
                const auto& w1 = TopoDS::Wire(exp1.Current());
                const auto& w2 = TopoDS::Wire(exp2.Current());
                BRepOffsetAPI_ThruSections builder;
                builder.AddWire(w1);
                builder.AddWire(w2);
                builder.Build();
                if (!builder.IsDone()) {
#if OCC_VERSION_HEX >= 0x70800
                    logger_.error("OpenCascade kernel: loft wire construction failed; BRepOffsetAPI_ThruSections status=" + std::to_string(static_cast<int>(builder.GetStatus())), loft->instance);
#else
                    logger_.error("OpenCascade kernel: loft wire construction failed", loft->instance);
#endif
                    return false;
                }
                for (TopExp_Explorer exp(builder.Shape(), TopAbs_FACE); exp.More(); exp.Next()) {
                    BB.Add(comp, exp.Current());
                }
            }

            BB.Add(comp, f0.Reversed());
            BB.Add(comp, f1);

            result = BRepBuilderAPI_MakeSolid(comp).Solid();

            return true;
        } else if (!loft->axis) {
            NCollection_List<TopoDS_Shape> faces;
            faces.Append(f0.Reversed());
            faces.Append(f1);
            for (size_t i = 1; i < sections.size(); ++i) {
                for (size_t j = 0; j < first_wire_count; ++j) {
                    BRepTools_WireExplorer a(sections[i - 1][j]), b(sections[i][j]);
                    for (; a.More() && b.More(); a.Next(), b.Next()) {
                        try {
                            faces.Append(BRepFill::Face(a.Current(), b.Current()));
                        } catch (const Standard_Failure& e) {
                            logger_.error("OpenCascade kernel: ruled loft surface failed between sections " +
                                std::to_string(i) + " and " + std::to_string(i + 1) + ", boundary " + std::to_string(j + 1) +
                                ": " + (e.GetMessageString() ? e.GetMessageString() : "unknown OpenCascade exception"), loft->instance);
                            return false;
                        }
                    }
                    if (a.More() || b.More()) {
                        logger_.error("OpenCascade kernel: ruled loft sections have inconsistent edge counts at sections " +
                            std::to_string(i) + " and " + std::to_string(i + 1), loft->instance);
                        return false;
                    }
                }
            }
            if (!create_solid_from_faces(faces, result, settings_.get<settings::Precision>().get(), true)) {
                logger_.error("OpenCascade kernel: failed to sew ruled loft surfaces into a solid", loft->instance);
                return false;
            }
            return true;
        } else {
            logger_.error("OpenCascade kernel: lofting more than two non-polygonal sections is not supported; got " + std::to_string(sections.size()) + " sections", loft->instance);
            return false;
        }
    }

    return false;
}

bool open_cascade_kernel::convert_impl(const taxonomy::loft::ptr loft, std::vector<ifcopenshell::geom::conversion_result>& results) {
    TopoDS_Shape shape;
    if (!handle_occt_exception([&]() { return convert(loft, shape); })) {
        return false;
    }
    results.emplace_back(conversion_result(
        loft->instance.id(),
        loft->matrix,
        new open_cascade_shape(shape),
        loft->surface_style));
    return true;
}
