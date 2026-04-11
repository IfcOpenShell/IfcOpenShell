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

#include <thread>
#include <unordered_map>
#include <cmath>
#include <cstring>
#include <algorithm>

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

void GeometryStreamer::loadFile(const std::string& path, uint32_t start_object_id, uint32_t model_id, int num_threads) {
    if (running_.load()) {
        cancel();
        if (worker_thread_ && worker_thread_->isRunning()) {
            worker_thread_->quit();
            worker_thread_->wait();
        }
    }

    cancel_requested_ = false;
    running_ = true;
    progress_ = 0;
    next_object_id_ = start_object_id;
    model_id_ = model_id;

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
        emit finished();
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

void GeometryStreamer::run(const std::string& path, int num_threads) {
    try {
        ifc_file_ = std::make_unique<ifcopenshell::file>(path);
    } catch (const std::exception& e) {
        emit errorOccurred(QString("Failed to parse IFC file: %1").arg(e.what()));
        return;
    }

    ifcopenshell::geometry::Settings settings;
    settings.set("use-world-coords", true);
    settings.set("weld-vertices", false);
    settings.set("apply-default-materials", true);

    std::unique_ptr<IfcGeom::Iterator> iterator;
    try {
        const std::string geometry_library =
            AppSettings::instance().geometryLibrary().toStdString();
        auto kernel = ifcopenshell::geometry::kernels::construct(
            ifc_file_.get(), geometry_library, settings);
        iterator = std::make_unique<IfcGeom::Iterator>(
            std::move(kernel), settings, ifc_file_.get(), std::vector<ifcopenshell::geometry::filter_t>(), num_threads);
    } catch (const std::exception& e) {
        emit errorOccurred(QString("Failed to create geometry iterator: %1").arg(e.what()));
        return;
    }

    if (!iterator->initialize()) {
        emit errorOccurred("No geometry found in IFC file");
        return;
    }

    int last_progress = 0;

    do {
        if (cancel_requested_.load()) break;

        const IfcGeom::Element* elem = iterator->get();
        if (!elem) continue;

        const auto* tri_elem = dynamic_cast<const IfcGeom::TriangulationElement*>(elem);
        if (!tri_elem) continue;

        uint32_t object_id = next_object_id_++;

        // Record element metadata
        ElementInfo info;
        info.object_id = object_id;
        info.model_id = model_id_;
        info.ifc_id = tri_elem->id();
        info.guid = tri_elem->guid();
        info.name = tri_elem->name();
        info.type = tri_elem->type();
        info.parent_id = tri_elem->parent_id();

        {
            std::lock_guard<std::mutex> lock(elements_mutex_);
            pending_elements_.push_back(std::move(info));
        }

        // Convert geometry to upload chunk
        UploadChunk chunk = convertElement(tri_elem, object_id);
        if (!chunk.indices.empty()) {
            emit elementReady(std::move(chunk));
        }

        int p = iterator->progress();
        if (p != last_progress) {
            last_progress = p;
            progress_ = p;
            emit progressChanged(p);
        }
    } while (iterator->next());

    progress_ = 100;
    emit progressChanged(100);
}

static MaterialInfo materialFromStyle(const ifcopenshell::geometry::taxonomy::style::ptr& style) {
    MaterialInfo m;
    if (!style) return m;

    const auto& color = style->get_color();
    if (color) {
        m.r = static_cast<float>(color.r());
        m.g = static_cast<float>(color.g());
        m.b = static_cast<float>(color.b());
    }
    if (!std::isnan(style->transparency)) {
        m.a = 1.0f - static_cast<float>(style->transparency);
    }
    return m;
}

static inline uint32_t packRGBA8(const MaterialInfo& m) {
    auto to_byte = [](float v) -> uint32_t {
        float c = std::clamp(v, 0.0f, 1.0f);
        return static_cast<uint32_t>(c * 255.0f + 0.5f);
    };
    uint32_t r = to_byte(m.r);
    uint32_t g = to_byte(m.g);
    uint32_t b = to_byte(m.b);
    uint32_t a = to_byte(m.a);
    // Layout in memory (little-endian) reads as bytes [r, g, b, a] which is
    // what the GL_UNSIGNED_BYTE * 4 normalized vertex attribute expects.
    return r | (g << 8) | (b << 16) | (a << 24);
}

UploadChunk GeometryStreamer::convertElement(const IfcGeom::TriangulationElement* elem, uint32_t object_id) {
    UploadChunk chunk;
    chunk.object_id = object_id;
    chunk.model_id = model_id_;

    const auto& geom = elem->geometry();
    const auto& verts = geom.verts();
    const auto& faces = geom.faces();
    const auto& normals = geom.normals();
    const auto& materials = geom.materials();
    const auto& material_ids = geom.material_ids();

    if (verts.empty() || faces.empty()) return chunk;

    // Encode object_id as float bits for the vertex attribute
    float id_as_float;
    static_assert(sizeof(float) == sizeof(uint32_t));
    std::memcpy(&id_as_float, &object_id, sizeof(float));

    const size_t num_verts = verts.size() / 3;
    const size_t num_tris = faces.size() / 3;
    const bool have_per_tri_material = (material_ids.size() == num_tris);

    // Per-vertex color requires that any vertex shared between triangles with
    // *different* materials be split. We dedupe (orig_vert_idx, mat_id) pairs
    // so vertices that are only ever used by one material stay shared.
    auto make_key = [](uint32_t orig_idx, int mat_id) -> uint64_t {
        return (static_cast<uint64_t>(orig_idx) << 32) |
               static_cast<uint32_t>(mat_id);
    };

    std::unordered_map<uint64_t, uint32_t> remap;
    remap.reserve(num_verts);

    chunk.vertices.reserve(num_verts * 8);
    chunk.indices.reserve(faces.size());

    auto emit_vertex = [&](uint32_t orig_idx, int mat_id) -> uint32_t {
        const uint64_t key = make_key(orig_idx, mat_id);
        auto it = remap.find(key);
        if (it != remap.end()) return it->second;

        const uint32_t new_idx = static_cast<uint32_t>(chunk.vertices.size() / 8);

        // pos
        chunk.vertices.push_back(static_cast<float>(verts[orig_idx * 3 + 0]));
        chunk.vertices.push_back(static_cast<float>(verts[orig_idx * 3 + 1]));
        chunk.vertices.push_back(static_cast<float>(verts[orig_idx * 3 + 2]));

        // normal
        if (orig_idx * 3 + 2 < normals.size()) {
            chunk.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 0]));
            chunk.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 1]));
            chunk.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 2]));
        } else {
            chunk.vertices.push_back(0.0f);
            chunk.vertices.push_back(1.0f);
            chunk.vertices.push_back(0.0f);
        }

        // object_id (float bits)
        chunk.vertices.push_back(id_as_float);

        // color (packed RGBA8 reinterpreted as float)
        MaterialInfo m;
        if (mat_id >= 0 && mat_id < static_cast<int>(materials.size())) {
            m = materialFromStyle(materials[mat_id]);
        }
        uint32_t packed = packRGBA8(m);
        float packed_as_float;
        std::memcpy(&packed_as_float, &packed, sizeof(float));
        chunk.vertices.push_back(packed_as_float);

        remap.emplace(key, new_idx);
        return new_idx;
    };

    for (size_t t = 0; t < num_tris; ++t) {
        const int mat_id = have_per_tri_material ? material_ids[t] : -1;
        chunk.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 0]), mat_id));
        chunk.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 1]), mat_id));
        chunk.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 2]), mat_id));
    }

    return chunk;
}
