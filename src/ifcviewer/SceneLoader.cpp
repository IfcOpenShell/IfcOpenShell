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

#include "SceneLoader.h"
#include "AppSettings.h"
#include "SidecarLayout.h"

#include <QFileInfo>
#include <QTimer>
#include <cstdio>
#include <QElapsedTimer>

#include <memory>
#include <optional>
#include <utility>

void SceneLoader::setShouldReadSidecar(bool enabled) {
    should_read_sidecar_ = enabled;
}

void SceneLoader::setShouldWriteSidecar(bool enabled) {
    should_write_sidecar_ = enabled;
}

SceneLoader::SceneLoader(ViewportWindow* viewport, QObject* parent)
    : QObject(parent), viewport_(viewport)
{
    connect(&element_poll_timer_, &QTimer::timeout,
            this, &SceneLoader::onElementPollTick);
    element_poll_timer_.setInterval(100);
}

SceneLoader::~SceneLoader() {
    joinSidecarThread();
    joinDataSourceThreads();
}

void SceneLoader::joinSidecarThread() {
    if (sidecar_read_thread_.joinable())
        sidecar_read_thread_.join();
}

void SceneLoader::joinDataSourceThreads() {
    for (auto& t : data_source_threads_) {
        if (t.joinable()) t.join();
    }
    data_source_threads_.clear();
}

QString SceneLoader::filePath(uint32_t mid) const {
    auto it = models_.find(mid);
    return it == models_.end() ? QString() : it->second.file_path;
}

QString SceneLoader::displayName(uint32_t mid) const {
    auto it = models_.find(mid);
    return it == models_.end() ? QString() : it->second.display_name;
}

ifcopenshell::file* SceneLoader::ifcFile(uint32_t mid) const {
    auto it = models_.find(mid);
    return it == models_.end() ? nullptr : it->second.streamer->ifcFile();
}

const ModelGeoref* SceneLoader::modelGeoref(uint32_t mid) {
    auto it = models_.find(mid);
    if (it == models_.end()) return nullptr;
    auto& m = it->second;
    if (m.has_georef) return &m.georef;
    auto* file = m.streamer ? m.streamer->ifcFile() : nullptr;
    if (!file) return nullptr;
    m.georef = computeModelGeoref(file);
    m.has_georef = true;
    return &m.georef;
}

std::vector<uint32_t> SceneLoader::addFiles(const QStringList& paths) {
    std::vector<uint32_t> assigned;
    assigned.reserve(paths.size());
    for (const auto& path : paths) {
        uint32_t id = next_model_id_++;
        Model model;
        model.id = id;
        model.file_path = path;
        model.display_name = QFileInfo(path).fileName();
        model.streamer = new GeometryStreamer(this);
        models_[id] = std::move(model);
        load_queue_.push_back(id);
        assigned.push_back(id);
    }

    if (loading_model_id_ == 0) {
        QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
    }
    return assigned;
}

void SceneLoader::connectStreamer(GeometryStreamer* streamer) {
    connect(streamer, &GeometryStreamer::progressChanged,
            this, &SceneLoader::onStreamerProgressChanged, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::meshReady,
            this, &SceneLoader::onStreamerMeshReady, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::instanceReady,
            this, &SceneLoader::onStreamerInstanceReady, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::finished,
            this, &SceneLoader::onStreamerFinished, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::cancelled,
            this, &SceneLoader::onStreamerCancelled, Qt::QueuedConnection);
    connect(streamer, &GeometryStreamer::errorOccurred,
            this, &SceneLoader::onStreamerError, Qt::QueuedConnection);
}

void SceneLoader::removeModel(uint32_t mid) {
    // Refuse while the model is the active load: the streamer thread is still
    // running and would race with the deleteLater().  UI gates Remove on
    // isLoading(), but guard here too.
    if (loading_model_id_ == mid) return;

    for (auto it = load_queue_.begin(); it != load_queue_.end();) {
        if (*it == mid) it = load_queue_.erase(it);
        else            ++it;
    }

    auto it = models_.find(mid);
    if (it == models_.end()) return;
    if (it->second.streamer) {
        it->second.streamer->deleteLater();
    }
    models_.erase(it);
}

void SceneLoader::cancelCurrentLoad() {
    if (loading_model_id_ == 0) return;
    auto it = models_.find(loading_model_id_);
    if (it == models_.end() || it->second.streamer == nullptr) return;
    it->second.streamer->cancel();
}

void SceneLoader::startNextLoad() {
    if (load_queue_.empty()) {
        loading_model_id_ = 0;
        emit allLoadsFinished();
        return;
    }

    loading_model_id_ = load_queue_.front();
    load_queue_.pop_front();

    auto& model = models_[loading_model_id_];
    model.load_timer.restart();

    emit loadStarted(model.id, model.display_name);

    std::string ifc_path = model.file_path.toStdString();
    uint32_t mid = loading_model_id_;
    const bool is_sidecar_source =
        QFileInfo(model.file_path).suffix().compare("ifcview", Qt::CaseInsensitive) == 0;

    // No sidecar read probe when caching is off (and the user didn't pick a
    // .ifcview file directly). Skip the background thread and go straight
    // to a stream load.
    if (!is_sidecar_source && !should_read_sidecar_) {
        startStreamLoadFor(mid);
        return;
    }

    // Sidecar read on a background thread so the UI stays responsive.
    joinSidecarThread();
    sidecar_read_thread_ = std::thread([this, ifc_path, mid, is_sidecar_source]() {
        QElapsedTimer rt; rt.start();
        auto cached = readSidecarMetadataOnly(ifc_path);
        std::fprintf(stderr, "[info]   Sidecar metadata read: %lld ms (%s)\n",
                     (long long)rt.elapsed(), ifc_path.c_str());
        auto result = std::make_shared<std::optional<StreamingSidecar>>(std::move(cached));
        QMetaObject::invokeMethod(this, [this, mid, result, is_sidecar_source]() {
            if (*result && !(*result)->meta.instances.empty()) {
                applySidecarData(mid, std::move(**result));
                if (!is_sidecar_source) {
                    startDataSourceLoad(mid);
                }
                return;
            }

            auto it = models_.find(mid);
            if (it == models_.end()) return;

            if (is_sidecar_source) {
                loading_model_id_ = 0;
                emit loadError(mid, QString("Failed to read IFC Viewer cache:\n%1").arg(it->second.file_path));
                QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
                return;
            }

            startStreamLoadFor(mid);
        }, Qt::QueuedConnection);
    });
}

void SceneLoader::startStreamLoadFor(uint32_t mid) {
    auto it = models_.find(mid);
    if (it == models_.end()) return;
    auto& m = it->second;
    // Accumulate sidecar data alongside the GPU upload so the first load
    // naturally produces a cache for the next one — no GPU readback at
    // finish time. Skipped when caching writes are off.
    if (should_write_sidecar_) {
        m.sidecar_builder = std::make_unique<SidecarBuilder>();
        m.streamed_elements.clear();
    }
    connectStreamer(m.streamer);
    element_poll_timer_.start();
    m.streamer->loadFile(
        m.file_path.toStdString(), next_object_id_, loading_model_id_);
}

void SceneLoader::applySidecarData(uint32_t mid, StreamingSidecar metadata) {
    auto it = models_.find(mid);
    if (it == models_.end()) return;
    auto& model = it->second;
    SidecarData& d = metadata.meta;

    std::fprintf(stderr,
        "[info] Sidecar hit: %s (%zu metadata bytes, %zu indices, %zu meshes, %zu instances, %zu elements)\n",
        model.file_path.toStdString().c_str(),
        size_t(metadata.vertex_total_bytes),
        size_t(metadata.index_total_count),
        d.meshes.size(),
        d.instances.size(),
        d.elements.size());

    // Rebase object/model IDs onto the current session's ID space.  Two
    // cached models both starting at object_id=1 would collide otherwise.
    uint32_t min_oid = UINT32_MAX;
    for (const auto& pe : d.elements) {
        if (pe.object_id < min_oid) min_oid = pe.object_id;
    }
    uint32_t oid_offset = 0;
    if (!d.elements.empty() && min_oid < UINT32_MAX) {
        oid_offset = next_object_id_ - min_oid;
    }
    for (auto& pe : d.elements) {
        pe.object_id += oid_offset;
        pe.model_id   = mid;
        if (pe.object_id >= next_object_id_)
            next_object_id_ = pe.object_id + 1;
    }
    for (auto& inst : d.instances) {
        inst.object_id += oid_offset;
        inst.model_id   = mid;
    }

    // Restore the cached CoordinateOperation into the model so
    // modelGeoref(mid) returns it without needing the IFC source.  Prevents
    // sidecar-loaded models from silently losing their georef when the
    // .ifc/.rdb sibling is absent.
    {
        ModelGeoref& gr = model.georef;
        gr.has_coordinate_operation = d.has_coordinate_operation != 0;
        Eigen::Map<const Eigen::Matrix<double, 4, 4, Eigen::ColMajor>> M(
            d.coordinate_operation_meters);
        gr.coordinate_operation_meters     = M;
        gr.units.project_length_to_meters  = d.project_length_to_meters;
        gr.units.map_unit_to_meters        = d.map_unit_to_meters;
        model.has_georef                   = true;
    }

    std::vector<PackedElementInfo> elements = std::move(d.elements);
    std::string stbl                        = std::move(d.string_table);

    viewport_->applyCachedModel(mid, std::move(metadata));

    emit sidecarElementsReady(mid, std::move(elements), std::move(stbl));

    qint64 ms = model.load_timer.elapsed();
    emit loadedFromSidecar(mid, ms);

    loading_model_id_ = 0;
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}

void SceneLoader::startDataSourceLoad(uint32_t mid) {
    auto it = models_.find(mid);
    if (it == models_.end()) return;

    std::string data_path_std = it->second.file_path.toStdString();
    data_source_threads_.emplace_back([this, mid, data_path_std]() {
        QElapsedTimer t; t.start();
        std::unique_ptr<ifcopenshell::file> file;
        try {
            file = std::make_unique<ifcopenshell::file>(
                data_path_std, ifcopenshell::FT_AUTODETECT, /*read_only=*/true);
        } catch (const std::exception& e) {
            std::fprintf(stderr, "[warn]   Data source load failed: %s (%s)\n",
                         data_path_std.c_str(), e.what());
            return;
        }
        std::fprintf(stderr, "[info]   Data source load: %lld ms (%s)\n",
                     (long long)t.elapsed(), data_path_std.c_str());

        auto shared = std::make_shared<std::unique_ptr<ifcopenshell::file>>(std::move(file));
        QMetaObject::invokeMethod(this, [this, mid, shared]() {
            auto it = models_.find(mid);
            if (it == models_.end()) return;
            auto* streamer = it->second.streamer;
            if (streamer == nullptr) return;
            // If the streamer already has a file (e.g. a later stream-fallback
            // path somehow populated it), don't clobber it.
            if (streamer->ifcFile() != nullptr) return;
            streamer->setIfcFile(std::move(*shared));
            emit dataSourceReady(mid);
        }, Qt::QueuedConnection);
    });
}

void SceneLoader::onStreamerProgressChanged(int percent) {
    emit progressChanged(percent);
}

void SceneLoader::onStreamerMeshReady(MeshChunk chunk) {
    viewport_->uploadMeshChunk(chunk);
    if (loading_model_id_ != 0) {
        auto it = models_.find(loading_model_id_);
        if (it != models_.end() && it->second.sidecar_builder) {
            it->second.sidecar_builder->onMeshReady(chunk);
        }
    }
}

void SceneLoader::onStreamerInstanceReady(InstanceChunk chunk) {
    if (loading_model_id_ != 0) {
        auto it = models_.find(loading_model_id_);
        if (it != models_.end() && it->second.sidecar_builder) {
            it->second.sidecar_builder->onInstanceReady(chunk);
        }
    }
    viewport_->uploadInstanceChunk(chunk);
}

void SceneLoader::onElementPollTick() {
    if (loading_model_id_ == 0) return;
    auto it = models_.find(loading_model_id_);
    if (it == models_.end()) return;

    auto batch = it->second.streamer->drainElements();
    if (batch.empty()) return;

    // Mirror into the per-model accumulator so finalize() has the full set
    // without re-draining (the streamer's queue is consumed by this drain).
    if (it->second.sidecar_builder) {
        auto& buf = it->second.streamed_elements;
        buf.insert(buf.end(), batch.begin(), batch.end());
    }
    emit streamedElementsReady(loading_model_id_, std::move(batch));
}

void SceneLoader::onStreamerFinished() {
    element_poll_timer_.stop();
    onElementPollTick();  // drain any remaining elements

    uint32_t mid = loading_model_id_;
    if (mid != 0) {
        auto it = models_.find(mid);
        if (it != models_.end()) {
            auto& m = it->second;
            next_object_id_ = m.streamer->lastObjectId();
            viewport_->finalizeModel(mid);

            // Sidecar finalize + disk write. Wgpu has no live LOD1 apply —
            // LOD1 indices land in the on-disk sidecar and are picked up
            // on the *next* open of this file; first-session view is
            // LOD0-only. Acceptable trade-off vs reallocating chunk index
            // slices live to splice LOD1 in.
            if (m.sidecar_builder) {
                ModelGeoref georef;
                if (auto* file = m.streamer->ifcFile()) {
                    georef = computeModelGeoref(file);
                }
                QElapsedTimer wt; wt.start();
                SidecarData data = m.sidecar_builder->finalize(georef, m.streamed_elements);
                // Lay geometry out in streaming-chunk order + bake the chunk TOC
                // (v14) so it streams as one contiguous range per chunk.
                reorderSidecarByMorton(data);
                const bool ok = writeSidecar(m.file_path.toStdString(), data);
                std::fprintf(stderr,
                    "[info]   Sidecar finalize + write: %lld ms (%s)\n",
                    (long long)wt.elapsed(), ok ? "ok" : "FAILED");
                m.sidecar_builder.reset();
                m.streamed_elements.clear();
                m.streamed_elements.shrink_to_fit();
            }

            qint64 ms = m.load_timer.elapsed();
            emit loadedFromStream(mid, ms);
        }
    }

    loading_model_id_ = 0;
    startNextLoad();
}

void SceneLoader::onStreamerCancelled() {
    element_poll_timer_.stop();

    const uint32_t mid = loading_model_id_;
    loading_model_id_ = 0;

    if (mid != 0) {
        viewport_->removeModel(mid);
        emit loadCancelled(mid);
    }
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}

void SceneLoader::onStreamerError(const QString& msg) {
    element_poll_timer_.stop();

    const uint32_t mid = loading_model_id_;
    loading_model_id_ = 0;

    if (mid != 0) {
        viewport_->removeModel(mid);
    }
    emit loadError(mid, msg);
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}
