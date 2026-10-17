// This file was generated with the assistance of an AI coding tool.

// Cross-kernel tests for profiles whose boundary is an IfcCompositeCurve, see
// https://github.com/IfcOpenShell/IfcOpenShell/issues/9768.
//
// The fixture extrudes four profiles by one metre so that the volume of each
// converted solid equals its profile area, which is known analytically:
//
//   * a full circle profile, which must convert with the default
//     circle-segments = 0 and must not degenerate to a single chord,
//   * a square with a concave quarter circle whose arc segment is used forward,
//   * the identical outline with the same arc encoded in reverse
//     (IfcCompositeCurveSegment.SameSense = .F.), and
//   * a rounded rectangle whose fillets are arcs.
//
// Everything is converted through ifcopenshell::geom::iterator so that the
// comparisons run on the triangulation elements (verts, edges and faces) that
// downstream consumers see. Conforming kernels must agree on the volume and on
// the vertices the profile is sampled at, and the two encodings of the same
// outline must triangulate identically.

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <limits>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include <catch2/catch_approx.hpp>
#include <catch2/catch_test_macros.hpp>

#include "ifcgeom/element.h"
#include "ifcgeom/iterator.h"
#include "ifcgeom/kernel_registry.h"
#include "ifcparse/macros.h"
#include IFCGEOM_TEST_SCHEMA_HEADER

namespace {

using ifcopenshell::geom::settings;
using ifcopenshell::geom::triangulation_element;

constexpr double kPi = 3.14159265358979323846;

// Largest profile dimension in the fixture, used for relative tolerances.
constexpr double kProfileExtent = 1.;

// Kernels sample conics at different densities, so vertex sets of different
// kernels are only expected to agree to within 5% of the profile size. The
// single chord per arc of #9768 deviates by 15% and is rejected.
constexpr double kVertexAgreement = 0.05 * kProfileExtent;

// The OpenCascade tessellation of these profiles stays within 0.15% of the
// exact area, so 0.5% accepts tessellation error while it rejects the chords
// (1.2% - 1.8%) and wrong outlines (14.2%) that #9768 is about.
constexpr double kVolumeTolerance = 0.005;

// Kernel volumes are compared against the OpenCascade reference within 1%.
constexpr double kKernelAgreement = 0.01;

// Vertices and edges are compared on a 0.1 mm grid, far below the sampling
// differences that the tests probe for.
constexpr double kWeld = 1.e4;

struct profile_case {
    int product_id;
    const char* name;
    double exact_volume;
};

const std::array<profile_case, 4> kProfiles = {{
    {20, "circle", kPi * 0.25},
    {54, "cc_forward", 1. - kPi * 0.2 * 0.2 / 4.},
    {88, "cc_reverse", 1. - kPi * 0.2 * 0.2 / 4.},
    {102, "rounded", 0.4 * 0.4 - (4. - kPi) * 0.05 * 0.05},
}};

// The two encodings of the same outline, see kProfiles.
constexpr int kForwardProduct = 54;
constexpr int kReversedProduct = 88;

using welded_point = std::array<long long, 3>;

welded_point weld(const double* coordinates) {
    return {
        std::llround(coordinates[0] * kWeld),
        std::llround(coordinates[1] * kWeld),
        std::llround(coordinates[2] * kWeld),
    };
}

struct kernel_geometry {
    std::vector<double> verts;
    std::vector<int> edges;
    std::vector<int> faces;

    std::size_t vertex_count() const { return verts.size() / 3; }

    std::vector<welded_point> distinctive_vertices() const {
        std::vector<welded_point> points;
        for (std::size_t i = 0; i + 2 < verts.size(); i += 3) {
            points.push_back(weld(&verts[i]));
        }
        std::sort(points.begin(), points.end());
        points.erase(std::unique(points.begin(), points.end()), points.end());
        return points;
    }

    std::vector<std::pair<welded_point, welded_point>> geometric_edges() const {
        std::vector<std::pair<welded_point, welded_point>> result;
        for (std::size_t i = 0; i + 1 < edges.size(); i += 2) {
            const auto a = weld(&verts[3 * edges[i]]);
            const auto b = weld(&verts[3 * edges[i + 1]]);
            result.emplace_back(std::min(a, b), std::max(a, b));
        }
        std::sort(result.begin(), result.end());
        return result;
    }

    double volume() const {
        double total = 0.;
        for (std::size_t i = 0; i + 2 < faces.size(); i += 3) {
            const double* a = &verts[3 * faces[i]];
            const double* b = &verts[3 * faces[i + 1]];
            const double* c = &verts[3 * faces[i + 2]];
            total += a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0]);
        }
        return std::abs(total) / 6.;
    }
};

double max_nearest_distance(const std::vector<welded_point>& from, const std::vector<welded_point>& to) {
    double worst = 0.;
    for (const auto& a : from) {
        double best = std::numeric_limits<double>::infinity();
        for (const auto& b : to) {
            best = std::min(best, std::hypot(
                double(a[0] - b[0]),
                double(a[1] - b[1]),
                double(a[2] - b[2])) / kWeld);
        }
        worst = std::max(worst, best);
    }
    return worst;
}

std::string fixture_spf() {
    std::string schema = STRINGIFY(IfcSchema);
    std::transform(schema.begin(), schema.end(), schema.begin(), [](unsigned char c) { return std::toupper(c); });
    std::string spf = R"IFC(ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC4X3_ADD2'));
ENDSEC;
DATA;
#1=IFCCARTESIANPOINT((0.,0.,0.));
#2=IFCAXIS2PLACEMENT3D(#1,$,$);
#3=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#2,$);
#4=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#5=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
#6=IFCUNITASSIGNMENT((#4,#5));
#7=IFCPROJECT('0000000000000000000001',$,'synthetic',$,$,$,$,(#3),#6);
#8=IFCCARTESIANPOINT((0.,0.));
#9=IFCAXIS2PLACEMENT2D(#8,$);
#10=IFCCIRCLEPROFILEDEF(.AREA.,$,#9,0.5);
#11=IFCCARTESIANPOINT((0.,0.,0.));
#12=IFCAXIS2PLACEMENT3D(#11,$,$);
#13=IFCLOCALPLACEMENT($,#12);
#14=IFCCARTESIANPOINT((0.,0.,0.));
#15=IFCAXIS2PLACEMENT3D(#14,$,$);
#16=IFCDIRECTION((0.,0.,1.));
#17=IFCEXTRUDEDAREASOLID(#10,#15,#16,1.);
#18=IFCSHAPEREPRESENTATION(#3,'Body','SweptSolid',(#17));
#19=IFCPRODUCTDEFINITIONSHAPE($,$,(#18));
#20=IFCBUILDINGELEMENTPROXY('0000000000000000000002',$,'circle',$,$,#13,#19,$,$);
#21=IFCRELCONTAINEDINSPATIALSTRUCTURE('0000000000000000000003',$,$,$,(#20),#7);
#22=IFCCARTESIANPOINT((1.,1.));
#23=IFCAXIS2PLACEMENT2D(#22,$);
#24=IFCCIRCLE(#23,0.2);
#25=IFCTRIMMEDCURVE(#24,(IFCPARAMETERVALUE(4.71238898038469)),(IFCPARAMETERVALUE(3.141592653589793)),.F.,.PARAMETER.);
#26=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#25);
#27=IFCCARTESIANPOINT((0.,0.));
#28=IFCCARTESIANPOINT((1.,0.));
#29=IFCPOLYLINE((#27,#28));
#30=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#29);
#31=IFCCARTESIANPOINT((1.,0.));
#32=IFCCARTESIANPOINT((1.,0.8));
#33=IFCPOLYLINE((#31,#32));
#34=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#33);
#35=IFCCARTESIANPOINT((0.8,1.));
#36=IFCCARTESIANPOINT((0.,1.));
#37=IFCPOLYLINE((#35,#36));
#38=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#37);
#39=IFCCARTESIANPOINT((0.,1.));
#40=IFCCARTESIANPOINT((0.,0.));
#41=IFCPOLYLINE((#39,#40));
#42=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#41);
#43=IFCCOMPOSITECURVE((#30,#34,#26,#38,#42),.F.);
#44=IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#43);
#45=IFCCARTESIANPOINT((2.,0.,0.));
#46=IFCAXIS2PLACEMENT3D(#45,$,$);
#47=IFCLOCALPLACEMENT($,#46);
#48=IFCCARTESIANPOINT((0.,0.,0.));
#49=IFCAXIS2PLACEMENT3D(#48,$,$);
#50=IFCDIRECTION((0.,0.,1.));
#51=IFCEXTRUDEDAREASOLID(#44,#49,#50,1.);
#52=IFCSHAPEREPRESENTATION(#3,'Body','SweptSolid',(#51));
#53=IFCPRODUCTDEFINITIONSHAPE($,$,(#52));
#54=IFCBUILDINGELEMENTPROXY('0000000000000000000004',$,'cc_forward',$,$,#47,#53,$,$);
#55=IFCRELCONTAINEDINSPATIALSTRUCTURE('0000000000000000000005',$,$,$,(#54),#7);
#56=IFCCARTESIANPOINT((1.,1.));
#57=IFCAXIS2PLACEMENT2D(#56,$);
#58=IFCCIRCLE(#57,0.2);
#59=IFCTRIMMEDCURVE(#58,(IFCPARAMETERVALUE(3.141592653589793)),(IFCPARAMETERVALUE(4.71238898038469)),.T.,.PARAMETER.);
#60=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.F.,#59);
#61=IFCCARTESIANPOINT((0.,0.));
#62=IFCCARTESIANPOINT((1.,0.));
#63=IFCPOLYLINE((#61,#62));
#64=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#63);
#65=IFCCARTESIANPOINT((1.,0.));
#66=IFCCARTESIANPOINT((1.,0.8));
#67=IFCPOLYLINE((#65,#66));
#68=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#67);
#69=IFCCARTESIANPOINT((0.8,1.));
#70=IFCCARTESIANPOINT((0.,1.));
#71=IFCPOLYLINE((#69,#70));
#72=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#71);
#73=IFCCARTESIANPOINT((0.,1.));
#74=IFCCARTESIANPOINT((0.,0.));
#75=IFCPOLYLINE((#73,#74));
#76=IFCCOMPOSITECURVESEGMENT(.CONTINUOUS.,.T.,#75);
#77=IFCCOMPOSITECURVE((#64,#68,#60,#72,#76),.F.);
#78=IFCARBITRARYCLOSEDPROFILEDEF(.AREA.,$,#77);
#79=IFCCARTESIANPOINT((4.,0.,0.));
#80=IFCAXIS2PLACEMENT3D(#79,$,$);
#81=IFCLOCALPLACEMENT($,#80);
#82=IFCCARTESIANPOINT((0.,0.,0.));
#83=IFCAXIS2PLACEMENT3D(#82,$,$);
#84=IFCDIRECTION((0.,0.,1.));
#85=IFCEXTRUDEDAREASOLID(#78,#83,#84,1.);
#86=IFCSHAPEREPRESENTATION(#3,'Body','SweptSolid',(#85));
#87=IFCPRODUCTDEFINITIONSHAPE($,$,(#86));
#88=IFCBUILDINGELEMENTPROXY('0000000000000000000006',$,'cc_reverse',$,$,#81,#87,$,$);
#89=IFCRELCONTAINEDINSPATIALSTRUCTURE('0000000000000000000007',$,$,(#88),#7);
#90=IFCCARTESIANPOINT((0.,0.));
#91=IFCAXIS2PLACEMENT2D(#90,$);
#92=IFCROUNDEDRECTANGLEPROFILEDEF(.AREA.,$,#91,0.4,0.4,0.05);
#93=IFCCARTESIANPOINT((6.,0.,0.));
#94=IFCAXIS2PLACEMENT3D(#93,$,$);
#95=IFCLOCALPLACEMENT($,#94);
#96=IFCCARTESIANPOINT((0.,0.,0.));
#97=IFCAXIS2PLACEMENT3D(#96,$,$);
#98=IFCDIRECTION((0.,0.,1.));
#99=IFCEXTRUDEDAREASOLID(#92,#97,#98,1.);
#100=IFCSHAPEREPRESENTATION(#3,'Body','SweptSolid',(#99));
#101=IFCPRODUCTDEFINITIONSHAPE($,$,(#100));
#102=IFCBUILDINGELEMENTPROXY('0000000000000000000008',$,'rounded',$,$,#95,#101,$,$);
#103=IFCRELCONTAINEDINSPATIALSTRUCTURE('0000000000000000000009',$,$,(#102),#7);
ENDSEC;
END-ISO-10303-21;
)IFC";
    const auto position = spf.find("IFC4X3_ADD2");
    spf.replace(position, std::string("IFC4X3_ADD2").size(), schema);
    return spf;
}

std::unique_ptr<ifcopenshell::file> load_fixture(ifcopenshell::logger& logger) {
    const auto spf = fixture_spf();
    std::istringstream stream(spf);
    return std::make_unique<ifcopenshell::file>(stream, static_cast<int>(spf.size()), logger);
}

settings kernel_settings(int circle_segments) {
    settings result;
    result.get<settings::OutputDimensionality>().value = settings::CURVES_SURFACES_AND_SOLIDS;
    result.set("circle-segments", circle_segments);
    return result;
}

std::map<int, kernel_geometry> triangulate_products(
    ifcopenshell::file& file,
    const std::string& backend,
    const settings& settings,
    ifcopenshell::logger& logger)
{
    auto kernel = ifcopenshell::geom::kernels::construct(&file, backend, settings, logger);
    ifcopenshell::geom::iterator iterator(std::move(kernel), settings, &file, {}, 1, logger);
    REQUIRE(iterator.initialize());
    std::map<int, kernel_geometry> geometry;
    while (true) {
        auto element = iterator.get();
        REQUIRE(element != nullptr);
        const auto* triangulated = dynamic_cast<const triangulation_element*>(element.get());
        REQUIRE(triangulated != nullptr);
        kernel_geometry converted;
        converted.verts = triangulated->geometry().verts();
        converted.edges = triangulated->geometry().edges();
        converted.faces = triangulated->geometry().faces();
        geometry.emplace(element->id(), std::move(converted));
        if (!iterator.next()) {
            break;
        }
    }
    return geometry;
}

void check_edges_reference_vertices(const kernel_geometry& geometry) {
    for (const int index : geometry.edges) {
        REQUIRE(index >= 0);
        REQUIRE(index < static_cast<int>(geometry.vertex_count()));
    }
}

// The forward and the reversed encoding are the same outline, so they must be
// sampled at the same vertices and connected by the same edges, also when the
// arc becomes a chord because circle-segments is 0.
void check_identical_encodings(
    ifcopenshell::file& file,
    const std::vector<std::string>& backends,
    ifcopenshell::logger& logger)
{
    for (const int circle_segments : {0, 64}) {
        for (const auto& backend : backends) {
            CAPTURE(backend, circle_segments);
            const auto geometry = triangulate_products(file, backend, kernel_settings(circle_segments), logger);
            const auto forward = geometry.find(kForwardProduct);
            const auto reversed = geometry.find(kReversedProduct);
            CHECK(forward != geometry.end());
            CHECK(reversed != geometry.end());
            if (forward == geometry.end() || reversed == geometry.end()) {
                continue;
            }
            check_edges_reference_vertices(forward->second);
            check_edges_reference_vertices(reversed->second);
            CHECK(forward->second.distinctive_vertices() == reversed->second.distinctive_vertices());
            CHECK(forward->second.geometric_edges() == reversed->second.geometric_edges());
            CHECK(forward->second.edges.size() == reversed->second.edges.size());
            CHECK(forward->second.volume() == Catch::Approx(reversed->second.volume()).epsilon(1.e-6));
        }
    }
}

void check_kernel_agreement(
    ifcopenshell::file& file,
    const std::vector<std::string>& backends,
    const std::string& reference_backend,
    ifcopenshell::logger& logger)
{
    for (const int circle_segments : {0, 64}) {
        CAPTURE(circle_segments);
        const auto reference = triangulate_products(file, reference_backend, kernel_settings(circle_segments), logger);
        for (const auto& profile : kProfiles) {
            CAPTURE(profile.name);
            const auto reference_shape = reference.find(profile.product_id);
            REQUIRE(reference_shape != reference.end());
            CHECK(reference_shape->second.volume() == Catch::Approx(profile.exact_volume).epsilon(kVolumeTolerance));
            const auto reference_vertices = reference_shape->second.distinctive_vertices();
            for (const auto& backend : backends) {
                CAPTURE(backend);
                const auto geometry = triangulate_products(file, backend, kernel_settings(circle_segments), logger);
                const auto found = geometry.find(profile.product_id);
                CHECK(found != geometry.end());
                if (found == geometry.end()) {
                    continue;
                }
                const auto& shape = found->second;
                // The conversion settings include curves, so the profile
                // boundary must be present as edge geometry.
                CHECK(shape.edges.size() >= 2);
                check_edges_reference_vertices(shape);
                CHECK(shape.volume() == Catch::Approx(profile.exact_volume).epsilon(kVolumeTolerance));
                CHECK(shape.volume() == Catch::Approx(reference_shape->second.volume()).epsilon(kKernelAgreement));
                const auto vertices = shape.distinctive_vertices();
                CHECK(max_nearest_distance(vertices, reference_vertices) < kVertexAgreement);
                CHECK(max_nearest_distance(reference_vertices, vertices) < kVertexAgreement);
            }
        }
    }
}

std::vector<std::string> portable_backends() {
    std::vector<std::string> backends;
#ifdef TAXONOMY_TEST_OPENCASCADE
    backends.push_back("opencascade");
#endif
#ifdef TAXONOMY_TEST_CGAL
    backends.push_back("cgal");
#endif
#ifdef TAXONOMY_TEST_CGAL_SIMPLE
    backends.push_back("cgal-simple");
#endif
    return backends;
}

std::vector<std::string> manifold_backends() {
    std::vector<std::string> backends;
#ifdef TAXONOMY_TEST_MANIFOLD
    backends.push_back("manifold");
#if defined(TAXONOMY_TEST_OPENCASCADE)
    backends.push_back("hybrid-manifold-opencascade");
#endif
#endif
    return backends;
}

} // namespace

TEST_CASE("Reversed composite curve segments triangulate like forward segments", "[ifcgeom][kernels][curves]") {
    const auto backends = portable_backends();
    REQUIRE_FALSE(backends.empty());
    ifcopenshell::logger logger;
    logger.output_format(ifcopenshell::logger::FMT_INMEMORY);
    auto file = load_fixture(logger);
    REQUIRE(file->good());
    check_identical_encodings(*file, backends, logger);
}

TEST_CASE("Composite curve extrusions agree between the portable kernels", "[ifcgeom][kernels][curves]") {
    const auto backends = portable_backends();
    REQUIRE_FALSE(backends.empty());
    ifcopenshell::logger logger;
    logger.output_format(ifcopenshell::logger::FMT_INMEMORY);
    auto file = load_fixture(logger);
    REQUIRE(file->good());
    check_kernel_agreement(*file, backends, backends.front(), logger);
}

#ifdef TAXONOMY_TEST_CGAL
#ifdef TAXONOMY_TEST_CGAL_SIMPLE
TEST_CASE("Cgal and cgal-simple triangulate composite curve extrusions identically", "[ifcgeom][kernels][curves]") {
    ifcopenshell::logger logger;
    logger.output_format(ifcopenshell::logger::FMT_INMEMORY);
    auto file = load_fixture(logger);
    REQUIRE(file->good());
    for (const int circle_segments : {0, 64}) {
        CAPTURE(circle_segments);
        const auto cgal = triangulate_products(*file, "cgal", kernel_settings(circle_segments), logger);
        const auto cgal_simple = triangulate_products(*file, "cgal-simple", kernel_settings(circle_segments), logger);
        REQUIRE(cgal.size() == kProfiles.size());
        REQUIRE(cgal_simple.size() == kProfiles.size());
        for (const auto& profile : kProfiles) {
            CAPTURE(profile.name);
            REQUIRE(cgal.at(profile.product_id).distinctive_vertices() == cgal_simple.at(profile.product_id).distinctive_vertices());
            REQUIRE(cgal.at(profile.product_id).geometric_edges() == cgal_simple.at(profile.product_id).geometric_edges());
        }
    }
}
#endif
#endif

// The manifold kernel samples extrusion profiles without the taxonomy curve
// evaluation: it divides the raw circle-segments setting over the arc span, so
// with the default value of 0 every arc becomes one chord and full circles or
// ellipses cannot be converted at all, and it only reads the edge's curve_sense
// while IfcCompositeCurveSegment.SameSense = .F. ends up in the edge's
// orientation flag, so reversed arcs are traced the wrong way round. Until
// #9768 is fixed the checks below fail for manifold and for the hybrid kernel
// that starts with it, which is why they are tagged as may-fail.
TEST_CASE("Manifold composite curve extrusions match the portable kernels", "[ifcgeom][kernels][curves][!mayfail]") {
    const auto reference_backends = portable_backends();
    const auto backends = manifold_backends();
    REQUIRE_FALSE(reference_backends.empty());
    REQUIRE_FALSE(backends.empty());
    ifcopenshell::logger logger;
    logger.output_format(ifcopenshell::logger::FMT_INMEMORY);
    auto file = load_fixture(logger);
    REQUIRE(file->good());
    check_kernel_agreement(*file, backends, reference_backends.front(), logger);
    check_identical_encodings(*file, backends, logger);
}
