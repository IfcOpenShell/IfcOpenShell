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

#include "GeometryStreamer.h"
#include "AppSettings.h"
#include "../ifcgeom/hybrid_kernel.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/filter.h"
#include "../ifcparse/express.h"

#include <Eigen/Dense>

#include <thread>
#include <unordered_map>
#include <cmath>
#include <cstring>
#include <algorithm>
#include <limits>
#include <set>

#include <cstdio>
#include <QElapsedTimer>

struct MaterialInfo {
    float r = 0.75f, g = 0.75f, b = 0.78f, a = 1.0f;
};

static MaterialInfo materialFromStyle(const ifcopenshell::geom::taxonomy::style::ptr& style) {
    MaterialInfo material;
    if (!style) return material;
    const auto& color = style->get_color();
    if (color) {
        material.r = static_cast<float>(color.r());
        material.g = static_cast<float>(color.g());
        material.b = static_cast<float>(color.b());
    }
    if (!std::isnan(style->transparency)) {
        material.a = 1.0f - static_cast<float>(style->transparency);
    }
    return material;
}

static inline uint32_t packRGBA8(const MaterialInfo& material) {
    auto to_byte = [](float channel_value) -> uint32_t {
        float clamped_value = std::clamp(channel_value, 0.0f, 1.0f);
        return static_cast<uint32_t>(clamped_value * 255.0f + 0.5f);
    };
    uint32_t r = to_byte(material.r);
    uint32_t g = to_byte(material.g);
    uint32_t b = to_byte(material.b);
    uint32_t a = to_byte(material.a);
    // Little-endian byte layout [r,g,b,a] for GL_UNSIGNED_BYTE * 4 normalized.
    return r | (g << 8) | (b << 16) | (a << 24);
}

GeometryStreamer::GeometryStreamer(QObject* parent)
    : QObject(parent)
{
}

GeometryStreamer::~GeometryStreamer() {
    cancel();
    if (worker_thread_ && worker_thread_->isRunning()) {
        worker_thread_->quit();
        worker_thread_->wait();
    }
}

void GeometryStreamer::setIfcFile(std::unique_ptr<ifcopenshell::file> file) {
    ifc_file_ = std::move(file);
}

void GeometryStreamer::loadFile(const std::string& path, uint32_t session_model_id, int num_threads) {
    if (running_.load()) {
        cancel();
        if (worker_thread_ && worker_thread_->isRunning()) {
            worker_thread_->quit();
            worker_thread_->wait();
        }
    }

    cancel_requested_ = false;
    succeeded_ = false;
    running_ = true;
    progress_ = 0;
    next_object_id_ = 1;  // model-local; globalized at applyCachedModel install time
    session_model_id_ = session_model_id;

    {
        std::lock_guard<std::mutex> lock(elements_mutex_);
        pending_elements_.clear();
    }

    if (num_threads <= 0) {
        num_threads = std::max(1u, std::thread::hardware_concurrency());
    }

    worker_thread_ = std::make_unique<QThread>();
    QObject* context = new QObject();
    context->moveToThread(worker_thread_.get());

    connect(worker_thread_.get(), &QThread::started, context, [this, path, num_threads, context]() {
        run(path, num_threads);
        context->deleteLater();
        worker_thread_->quit();
    });

    connect(worker_thread_.get(), &QThread::finished, this, [this]() {
        running_ = false;
        if (succeeded_.load()) {
            emit finished();
        } else if (cancel_requested_.load()) {
            emit cancelled();
        }
    });

    worker_thread_->start();
}

void GeometryStreamer::cancel() {
    cancel_requested_ = true;
}

std::vector<ElementInfo> GeometryStreamer::drainElements() {
    std::lock_guard<std::mutex> lock(elements_mutex_);
    std::vector<ElementInfo> result;
    result.swap(pending_elements_);
    return result;
}

// Build a streamed mesh record (local coords, 28-byte interleaved vertices) from a
// TriangulationElement. Per-vertex color is baked from material_ids so that
// triangulations with per-face materials still render correctly.
// Vertex rebasing: when `offset` is non-zero, every vertex position is
// subtracted by it so the emitted mesh-local coordinates stay near the
// origin (and float32 precision survives upload to the GPU).  Caller
// compensates by post-multiplying each instance's PlacementTransformation
// by T(+offset), which is mathematically the identity overall but moves
// the magnitude off the float-precision-sensitive vertex column.
static StreamedMesh buildStreamedMesh(uint32_t session_model_id,
                                uint32_t local_mesh_id,
                                const ifcopenshell::geom::triangulation_element* elem,
                                const Eigen::Vector3d& offset) {
    StreamedMesh mesh;
    mesh.session_model_id = session_model_id;
    mesh.local_mesh_id = local_mesh_id;

    const auto& geom = elem->geometry();
    const auto& verts = geom.verts();
    const auto& faces = geom.faces();
    const auto& normals = geom.normals();
    const auto& materials = geom.materials();
    const auto& material_ids = geom.material_ids();

    if (verts.empty() || faces.empty()) return mesh;

    const size_t num_verts_src = verts.size() / 3;
    const size_t num_tris = faces.size() / 3;
    const bool have_per_tri_material = (material_ids.size() == num_tris);

    // Dedupe (original vertex index, material id) so vertices shared across
    // triangles of the same material stay shared; vertices spanning multiple
    // materials are split (per-face color demands it).
    auto make_key = [](uint32_t orig_idx, int mat_id) -> uint64_t {
        return (static_cast<uint64_t>(orig_idx) << 32) | static_cast<uint32_t>(mat_id);
    };

    std::unordered_map<uint64_t, uint32_t> remap;
    remap.reserve(num_verts_src);

    mesh.vertices.reserve(num_verts_src * INSTANCED_VERTEX_STRIDE_FLOATS);
    mesh.indices.reserve(faces.size());

    // Track local AABB as we emit vertices.
    float local_aabb_min[3] = { std::numeric_limits<float>::max(),
                                std::numeric_limits<float>::max(),
                                std::numeric_limits<float>::max() };
    float local_aabb_max[3] = { -std::numeric_limits<float>::max(),
                                -std::numeric_limits<float>::max(),
                                -std::numeric_limits<float>::max() };

    auto emit_vertex = [&](uint32_t orig_idx, int mat_id) -> uint32_t {
        const uint64_t key = make_key(orig_idx, mat_id);
        auto it = remap.find(key);
        if (it != remap.end()) return it->second;

        const uint32_t new_idx = static_cast<uint32_t>(
            mesh.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS);

        // Subtract in double, narrow to float — preserves precision when
        // verts are far from origin and offset cancels the magnitude.
        float px = static_cast<float>(verts[orig_idx * 3 + 0] - offset.x());
        float py = static_cast<float>(verts[orig_idx * 3 + 1] - offset.y());
        float pz = static_cast<float>(verts[orig_idx * 3 + 2] - offset.z());
        mesh.vertices.push_back(px);
        mesh.vertices.push_back(py);
        mesh.vertices.push_back(pz);
        if (px < local_aabb_min[0]) local_aabb_min[0] = px;
        if (px > local_aabb_max[0]) local_aabb_max[0] = px;
        if (py < local_aabb_min[1]) local_aabb_min[1] = py;
        if (py > local_aabb_max[1]) local_aabb_max[1] = py;
        if (pz < local_aabb_min[2]) local_aabb_min[2] = pz;
        if (pz > local_aabb_max[2]) local_aabb_max[2] = pz;

        if (orig_idx * 3 + 2 < normals.size()) {
            mesh.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 0]));
            mesh.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 1]));
            mesh.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 2]));
        } else {
            mesh.vertices.push_back(0.0f);
            mesh.vertices.push_back(1.0f);
            mesh.vertices.push_back(0.0f);
        }

        MaterialInfo m;
        if (mat_id >= 0 && mat_id < static_cast<int>(materials.size())) {
            m = materialFromStyle(materials[mat_id]);
        }
        uint32_t packed = packRGBA8(m);
        float packed_as_float;
        std::memcpy(&packed_as_float, &packed, sizeof(float));
        mesh.vertices.push_back(packed_as_float);

        remap.emplace(key, new_idx);
        return new_idx;
    };

    for (size_t t = 0; t < num_tris; ++t) {
        const int mat_id = have_per_tri_material ? material_ids[t] : -1;
        mesh.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 0]), mat_id));
        mesh.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 1]), mat_id));
        mesh.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 2]), mat_id));
    }

    if (mesh.vertices.empty()) {
        for (int a = 0; a < 3; ++a) local_aabb_min[a] = local_aabb_max[a] = 0.0f;
    }
    for (int a = 0; a < 3; ++a) {
        mesh.local_aabb_min[a] = local_aabb_min[a];
        mesh.local_aabb_max[a] = local_aabb_max[a];
    }
    return mesh;
}

// Port of ifcopenshell.util.representation.get_prioritised_contexts: rank every
// IfcGeometricRepresentationContext (and SubContext) by (ContextType,
// ContextIdentifier, TargetView, TargetScale) — tuple comparison, descending —
// and return the resulting context ids high-priority first.  Used to drive a
// pass-per-context iteration in the streamer (mirrors bonsai's
// create_generic_element loop), so each element is rendered from its
// preferred representation if available, falling back to lower-priority
// contexts only when the preferred one is missing.
static std::vector<int> prioritisedContextIds(ifcopenshell::file* ifc_file) {
    static const std::vector<std::string> type_order = {
        // "Annotation" accommodates broken Revit files that put 3D bodies
        // under a context typed Annotation. See revit-ifc#187.
        "Model", "Plan", "Annotation",
    };
    static const std::vector<std::string> identifier_order = {
        "Body", "Body-FallBack", "Facetation", "FootPrint", "Profile",
        "Surface", "Reference", "Axis", "Clearance", "Box", "Lighting",
        "Annotation", "CoG",
    };
    static const std::vector<std::string> target_view_order = {
        "MODEL_VIEW", "PLAN_VIEW", "REFLECTED_PLAN_VIEW", "ELEVATION_VIEW",
        "SECTION_VIEW", "GRAPH_VIEW", "SKETCH_VIEW", "USERDEFINED",
        "NOTDEFINED",
    };

    auto rank = [](const std::vector<std::string>& order,
                   const std::string& value) -> int {
        if (value.empty()) return 0;
        auto it = std::find(order.begin(), order.end(), value);
        if (it == order.end()) return 0;
        return static_cast<int>(order.size() - (it - order.begin()));
    };

    struct ContextInfo {
        int id;
        int type_priority;
        int identifier_priority;
        int target_view_priority;
        double target_scale;
    };

    std::vector<ContextInfo> infos;
    auto contexts =
        ifc_file->instances_by_type("IfcGeometricRepresentationContext");
    infos.reserve(contexts.size());

    for (const auto& ctx : contexts) {
        ContextInfo info{};
        info.id = ctx.id();

        const auto entity = ctx.as<express::entity>();
        const std::string ctype =
            entity.get_value<std::string>("ContextType", "");
        const std::string cident =
            entity.get_value<std::string>("ContextIdentifier", "");
        info.type_priority = rank(type_order, ctype);
        info.identifier_priority = rank(identifier_order, cident);

        // TargetView and TargetScale only exist on
        // IfcGeometricRepresentationSubContext; get() throws on the parent
        // type, so gate by declaration before reading.
        if (ctx.declaration().is("IfcGeometricRepresentationSubContext")) {
            try {
                auto tv = entity.get("TargetView");
                if (!tv.isNull()) {
                    ifcopenshell::enumeration_reference er = tv;
                    info.target_view_priority =
                        rank(target_view_order, er.value());
                }
            } catch (...) {}
            try {
                auto ts = entity.get("TargetScale");
                if (!ts.isNull()) {
                    info.target_scale = static_cast<double>(ts);
                }
            } catch (...) {}
        }

        infos.push_back(info);
    }

    std::sort(infos.begin(), infos.end(),
              [](const ContextInfo& a, const ContextInfo& b) {
                  if (a.type_priority != b.type_priority)
                      return a.type_priority > b.type_priority;
                  if (a.identifier_priority != b.identifier_priority)
                      return a.identifier_priority > b.identifier_priority;
                  if (a.target_view_priority != b.target_view_priority)
                      return a.target_view_priority > b.target_view_priority;
                  return a.target_scale > b.target_scale;
              });

    std::vector<int> result;
    result.reserve(infos.size());
    for (const auto& i : infos) result.push_back(i.id);
    return result;
}

// Compute the world-space AABB by transforming the 8 corners of the local
// AABB through the column-major 4x4 transform.
static void worldAabbFromLocal(const float local_min[3],
                               const float local_max[3],
                               const float M[16],
                               float out_min[3], float out_max[3]) {
    out_min[0] = out_min[1] = out_min[2] =  std::numeric_limits<float>::max();
    out_max[0] = out_max[1] = out_max[2] = -std::numeric_limits<float>::max();
    for (int c = 0; c < 8; ++c) {
        float x = (c & 1) ? local_max[0] : local_min[0];
        float y = (c & 2) ? local_max[1] : local_min[1];
        float z = (c & 4) ? local_max[2] : local_min[2];
        // Column-major: world = M * [x,y,z,1].
        float wx = M[0]*x + M[4]*y + M[8]*z  + M[12];
        float wy = M[1]*x + M[5]*y + M[9]*z  + M[13];
        float wz = M[2]*x + M[6]*y + M[10]*z + M[14];
        if (wx < out_min[0]) out_min[0] = wx; if (wx > out_max[0]) out_max[0] = wx;
        if (wy < out_min[1]) out_min[1] = wy; if (wy > out_max[1]) out_max[1] = wy;
        if (wz < out_min[2]) out_min[2] = wz; if (wz > out_max[2]) out_max[2] = wz;
    }
}

void GeometryStreamer::run(const std::string& path, int num_threads) {
    try {
        // read_only is a no-op for SPF; for RocksDB it allows concurrent
        // readers and avoids acquiring the exclusive DB lock.
        ifc_file_ = std::make_unique<ifcopenshell::file>(
            path, ifcopenshell::FT_AUTODETECT, /*read_only=*/true);
    } catch (const std::exception& e) {
        emit errorOccurred(QString("Failed to parse IFC file: %1").arg(e.what()));
        return;
    }

    ifcopenshell::geom::settings settings;
    // Instancing path: geometry stays in local coords; the transform is
    // applied on the GPU per instance.
    settings.set("use-world-coords", false);
    settings.set("weld-vertices", false);
    settings.set("apply-default-materials", false);
    // Off by default in IfcOpenShell — makes face winding consistent within
    // each shell, which we need for GL_CULL_FACE and for per-vertex normals
    // to shade a solid without dark inside-out patches.  Costs some iterator
    // time, but results are cached in the sidecar so it's a one-shot hit.
    settings.set("reorient-shells", true);
    settings.set("layerset-first", true);
    settings.set("mesher-linear-deflection", AppSettings::instance().deflectionTolerance());
    settings.set("mesher-angular-deflection", AppSettings::instance().angularTolerance());
    // Wire intersection checks is prohibitively slow on advanced breps. See bug #5999.
    settings.set("no-wire-intersection-check", true);

    // Mirror bonsai's IfcImporter.process_element_filter: walk IfcElement
    // (plus IfcProxy on IFC2X3/IFC4), drop IfcFeatureElement except
    // IfcSurfaceFeature, pick up spatial elements, and split elements
    // with more openings than the configured void limit into a "gross"
    // set that is rendered without opening subtractions.  Both sets
    // become include filters so we don't waste time mapping openings.
    std::set<int> net_ids;
    std::set<int> gross_ids;
    {
        const std::string& schema_name = ifc_file_->schema()->name();
        std::vector<express::base> elements =
            ifc_file_->instances_by_type("IfcElement");
        if (schema_name == "IFC2X3" || schema_name == "IFC4") {
            auto proxies = ifc_file_->instances_by_type("IfcProxy");
            elements.insert(elements.end(), proxies.begin(), proxies.end());
        }
        const char* spatial_root = (schema_name == "IFC2X3")
            ? "IfcSpatialStructureElement"
            : "IfcSpatialElement";
        auto spatials = ifc_file_->instances_by_type(spatial_root);
        elements.insert(elements.end(), spatials.begin(), spatials.end());

        const int void_limit = AppSettings::instance().voidLimit();
        for (const auto& e : elements) {
            const auto& decl = e.declaration();
            if (decl.is("IfcFeatureElement") && !decl.is("IfcSurfaceFeature")) {
                continue;
            }
            int opening_count = 0;
            if (decl.is("IfcElement")) {
                try {
                    opening_count = static_cast<int>(
                        e.as<express::entity>().get_inverse("HasOpenings").size());
                } catch (...) {
                    // HasOpenings not declared on this entity — treat as 0.
                }
            }
            if (opening_count > void_limit) {
                gross_ids.insert(e.id());
            } else {
                net_ids.insert(e.id());
            }
        }
    }

    if (net_ids.empty() && gross_ids.empty()) {
        emit errorOccurred("No geometry-bearing elements found in IFC file");
        return;
    }
    if (!gross_ids.empty()) {
        std::fprintf(stderr,
            "[info] Excessive voids: %zu element(s) will be loaded without "
            "opening subtractions\n",
            gross_ids.size());
    }

    // Shared dedup + AABB state across passes — same geom.id() across
    // net/gross passes still maps to one mesh upload.
    std::unordered_map<std::string, uint32_t> geom_to_local_mesh_id;
    // Per-unique-mesh state shared across instances.  `offset` is the stage-1
    // rebase applied to verts (zero when the mesh's first vert is near origin
    // and rebasing wasn't worth it).
    struct MeshAabb {
        float lmin[3], lmax[3];
        double offset[3] = {0.0, 0.0, 0.0};
        bool   has_offset = false;
    };
    std::vector<MeshAabb> mesh_aabbs;

    uint32_t total_shapes = 0;
    uint32_t total_meshes = 0;
    QElapsedTimer stream_timer;
    stream_timer.start();

    // Drive the bar from yields across all passes/contexts.  Earlier the
    // [0,100] range was carved evenly across N prioritised contexts, but
    // in practice nearly every element yields from the first (Body)
    // context, so smooth progress only ever filled 1/n of the bar before
    // jumping to the next allocation — visually, a typical 5-context
    // file looked like it capped at ~20%.
    const size_t total_count = net_ids.size() + gross_ids.size();
    size_t yielded_count = 0;
    int last_emitted_progress = 0;

    // High-priority context first, so each element gets its preferred
    // representation; lower-priority contexts only pick up elements the
    // earlier passes didn't yield geometry for.  Mirrors bonsai's
    // create_generic_element loop over context_settings.
    const std::vector<int> prioritised_contexts =
        prioritisedContextIds(ifc_file_.get());

    auto run_pass = [&](const std::set<int>& include_ids,
                        bool is_gross) -> bool {
        if (include_ids.empty()) return true;

        ifcopenshell::geom::settings base_settings = settings;
        if (is_gross) {
            base_settings.set("disable-opening-subtractions", true);
        }

        // Elements that haven't yet produced geometry from any context.
        std::set<int> remaining = include_ids;

        auto run_iterator = [&](ifcopenshell::geom::settings& iter_settings) -> bool {
            if (remaining.empty()) return true;

            std::vector<ifcopenshell::geom::filter_function> filters;
            ifcopenshell::geom::instance_id_filter idf{
                /*include=*/true, /*traverse=*/false, remaining};
            filters.push_back(idf);

            std::unique_ptr<ifcopenshell::geom::iterator> iterator;
            try {
                const std::string geometry_library =
                    AppSettings::instance().geometryLibrary().toStdString();
                auto kernel = ifcopenshell::geom::kernels::construct(
                    ifc_file_.get(), geometry_library, iter_settings);
                iterator = std::make_unique<ifcopenshell::geom::iterator>(
                    std::move(kernel), iter_settings, ifc_file_.get(),
                    filters, num_threads);
            } catch (const std::exception& e) {
                emit errorOccurred(QString("Failed to create geometry iterator: %1").arg(e.what()));
                return false;
            }
            if (!iterator->initialize()) {
                // No geometry survived this context for the remaining ids.
                // Subsequent contexts will pick them up; nothing to emit.
                return true;
            }

            do {
                if (cancel_requested_.load()) break;

				auto element = iterator->get();
				const ifcopenshell::geom::element* elem = element.get();
                if (!elem) continue;

                const auto* tri_elem = dynamic_cast<const ifcopenshell::geom::triangulation_element*>(elem);
                if (!tri_elem) continue;

                const auto& geom = tri_elem->geometry();
                if (geom.verts().empty() || geom.faces().empty()) continue;

                // Once an element yields geometry from this context, drop it
                // from the remaining set so lower-priority contexts don't
                // re-render it.
                remaining.erase(tri_elem->id());

                uint32_t object_id = next_object_id_++;

                ElementInfo info;
                info.object_id = object_id;
                info.session_model_id = session_model_id_;
                info.ifc_id = tri_elem->id();
                info.guid = tri_elem->guid();
                info.name = tri_elem->name();
                info.type = tri_elem->type();
                {
                    std::lock_guard<std::mutex> lock(elements_mutex_);
                    pending_elements_.push_back(std::move(info));
                }

                const std::string& geom_id = geom.id();
                uint32_t local_mesh_id;
                bool first_sight = false;
                if (geom_id.empty()) {
                    local_mesh_id = total_meshes++;
                    first_sight = true;
                } else {
                    auto it = geom_to_local_mesh_id.find(geom_id);
                    if (it == geom_to_local_mesh_id.end()) {
                        local_mesh_id = total_meshes++;
                        geom_to_local_mesh_id.emplace(geom_id, local_mesh_id);
                        first_sight = true;
                    } else {
                        local_mesh_id = it->second;
                    }
                }

                if (first_sight) {
                    // Vertex rebasing: pick a rebase offset when the mesh's
                    // first source vertex is far from origin (>1 km in metres,
                    // matching bonsai's distance_limit default).  Iterator
                    // outputs metres, so the threshold is in metres directly.
                    Eigen::Vector3d offset = Eigen::Vector3d::Zero();
                    constexpr double kFarAwayThresholdMeters = 1000.0;
                    const auto& src_verts = tri_elem->geometry().verts();
                    if (src_verts.size() >= 3) {
                        const double x = src_verts[0];
                        const double y = src_verts[1];
                        const double z = src_verts[2];
                        if (std::abs(x) > kFarAwayThresholdMeters ||
                            std::abs(y) > kFarAwayThresholdMeters ||
                            std::abs(z) > kFarAwayThresholdMeters) {
                            offset = Eigen::Vector3d(x, y, z);
                        }
                    }

                    StreamedMesh streamed_mesh =
                        buildStreamedMesh(session_model_id_, local_mesh_id, tri_elem, offset);
                    MeshAabb mesh_aabb;
                    for (int a = 0; a < 3; ++a) {
                        mesh_aabb.lmin[a] = streamed_mesh.local_aabb_min[a];
                        mesh_aabb.lmax[a] = streamed_mesh.local_aabb_max[a];
                        mesh_aabb.offset[a] = offset[a];
                    }
                    mesh_aabb.has_offset = (offset.squaredNorm() > 0.0);
                    if (mesh_aabbs.size() <= local_mesh_id) mesh_aabbs.resize(local_mesh_id + 1);
                    mesh_aabbs[local_mesh_id] = mesh_aabb;
                    if (!streamed_mesh.indices.empty()) {
                        emit meshReady(std::move(streamed_mesh));
                    }
                }

                // Vertex rebasing cont.: post-multiply the per-instance
                // PlacementTransformation by T(+offset) so world position is
                // preserved.  Keep the emitted placement in double so later
                // CoordinateOperation / false-origin composition can cancel
                // large translations before the final GPU float upload.
                Eigen::Matrix4d mat_d =
                    tri_elem->transformation().data()->ccomponents();
                if (mesh_aabbs[local_mesh_id].has_offset) {
                    const Eigen::Vector3d mesh_rebase_offset(
                        mesh_aabbs[local_mesh_id].offset[0],
                        mesh_aabbs[local_mesh_id].offset[1],
                        mesh_aabbs[local_mesh_id].offset[2]);
                    mat_d.block<3, 1>(0, 3) += mat_d.block<3, 3>(0, 0) * mesh_rebase_offset;
                }

                StreamedInstance inst;
                inst.session_model_id = session_model_id_;
                inst.local_mesh_id = local_mesh_id;
                inst.object_id = object_id;
                inst.color_override_rgba8 = 0;
                for (int i = 0; i < 16; ++i) {
                    inst.transform[i] = mat_d.data()[i];
                }

                const MeshAabb& mesh_aabb = mesh_aabbs[local_mesh_id];
                float mat_f[16];
                for (int i = 0; i < 16; ++i) {
                    mat_f[i] = static_cast<float>(inst.transform[i]);
                }
                worldAabbFromLocal(mesh_aabb.lmin, mesh_aabb.lmax, mat_f,
                                   inst.world_aabb_min, inst.world_aabb_max);

                emit instanceReady(std::move(inst));
                total_shapes++;
                yielded_count++;

                const int progress_percent = total_count > 0
                    ? static_cast<int>((100 * yielded_count) / total_count)
                    : 100;
                if (progress_percent != last_emitted_progress) {
                    last_emitted_progress = progress_percent;
                    progress_ = progress_percent;
                    emit progressChanged(progress_percent);
                }
            } while (iterator->next());

            return true;
        };

        if (prioritised_contexts.empty()) {
            // No IfcGeometricRepresentationContext entities — fall back to
            // a single iterator pass without context-id filtering.
            return run_iterator(base_settings);
        }

        for (size_t i = 0; i < prioritised_contexts.size(); ++i) {
            if (cancel_requested_.load()) break;
            if (remaining.empty()) break;

            ifcopenshell::geom::settings iter_settings = base_settings;
            iter_settings.set("context-ids",
                std::set<int>{ prioritised_contexts[i] });

            if (!run_iterator(iter_settings)) return false;
        }

        return true;
    };

    if (!run_pass(net_ids, /*is_gross=*/false)) return;
    if (!cancel_requested_.load()) {
        run_pass(gross_ids, /*is_gross=*/true);
    }

    progress_ = 100;
    emit progressChanged(100);

    double dedup_ratio = total_meshes > 0
        ? static_cast<double>(total_shapes) / static_cast<double>(total_meshes) : 1.0;
    std::fprintf(stderr,
        "[info] Streamer done: %s  %.2fs  shapes=%u  unique_meshes=%u  dedup=%.2fx\n",
        path.c_str(), stream_timer.elapsed() / 1000.0,
        total_shapes, total_meshes, dedup_ratio);
    succeeded_ = !cancel_requested_.load();
}
