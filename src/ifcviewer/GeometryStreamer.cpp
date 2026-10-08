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
#include "StreamedRecords.h"
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

    // Shared across passes: the same geom.id() across net/gross passes still
    // maps to one mesh upload, and MeshDedup folds congruent meshes.
    MeshRegistry mesh_registry;

    uint32_t total_shapes = 0;
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

                // Vertex rebasing: pick a rebase offset when the mesh's
                // first source vertex is far from origin (>1 km in metres,
                // matching bonsai's distance_limit default).  Iterator
                // outputs metres, so the threshold is in metres directly.
                Eigen::Vector3d rebase_offset = Eigen::Vector3d::Zero();
                constexpr double kFarAwayThresholdMeters = 1000.0;
                const auto& src_verts = geom.verts();
                if (src_verts.size() >= 3) {
                    const double x = src_verts[0];
                    const double y = src_verts[1];
                    const double z = src_verts[2];
                    if (std::abs(x) > kFarAwayThresholdMeters ||
                        std::abs(y) > kFarAwayThresholdMeters ||
                        std::abs(z) > kFarAwayThresholdMeters) {
                        rebase_offset = Eigen::Vector3d(x, y, z);
                    }
                }

                std::optional<StreamedMesh> new_mesh;
                const UniqueMesh unique_mesh = mesh_registry.resolve(
                    session_model_id_, *tri_elem, rebase_offset, new_mesh);
                if (new_mesh) emit meshReady(std::move(*new_mesh));

                // The rebase and the dedup transform are folded into the
                // placement by the shared builder; the raw placement stays in
                // double so later CoordinateOperation / false-origin
                // composition can cancel large translations before the final
                // GPU float upload.
                StreamedInstance inst = makeStreamedInstance(
                    session_model_id_, object_id, *tri_elem, unique_mesh,
                    mesh_registry.aabb(unique_mesh.mesh_id));

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

    const uint32_t total_meshes = mesh_registry.meshCount();
    double dedup_ratio = total_meshes > 0
        ? static_cast<double>(total_shapes) / static_cast<double>(total_meshes) : 1.0;
    std::fprintf(stderr,
        "[info] Streamer done: %s  %.2fs  shapes=%u  unique_meshes=%u  dedup=%.2fx  "
        "congruent_meshes=%u\n",
        path.c_str(), stream_timer.elapsed() / 1000.0,
        total_shapes, total_meshes, dedup_ratio, mesh_registry.congruentMeshCount());
    succeeded_ = !cancel_requested_.load();
}
