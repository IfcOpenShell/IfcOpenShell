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

QString SceneLoader::filePath(uint32_t session_model_id) const {
    auto it = models_.find(session_model_id);
    return it == models_.end() ? QString() : it->second.file_path;
}

QString SceneLoader::displayName(uint32_t session_model_id) const {
    auto it = models_.find(session_model_id);
    return it == models_.end() ? QString() : it->second.display_name;
}

ifcopenshell::file* SceneLoader::ifcFile(uint32_t session_model_id) const {
    auto it = models_.find(session_model_id);
    return it == models_.end() ? nullptr : it->second.streamer->ifcFile();
}

const ModelGeoref* SceneLoader::modelGeoref(uint32_t session_model_id) {
    auto it = models_.find(session_model_id);
    if (it == models_.end()) return nullptr;
    auto& model = it->second;
    if (model.has_georef) return &model.georef;
    auto* file = model.streamer ? model.streamer->ifcFile() : nullptr;
    if (!file) return nullptr;
    model.georef = computeModelGeoref(file);
    model.has_georef = true;
    return &model.georef;
}

std::vector<uint32_t> SceneLoader::queueModels(const QStringList& paths) {
    std::vector<uint32_t> assigned;
    assigned.reserve(paths.size());
    for (const auto& path : paths) {
        uint32_t id = next_session_model_id_++;
        Model model;
        model.id = id;
        model.file_path = path;
        model.display_name = QFileInfo(path).fileName();
        model.streamer = new GeometryStreamer(this);
        models_[id] = std::move(model);
        load_queue_.push_back(id);
        assigned.push_back(id);
    }

    if (loading_session_model_id_ == 0) {
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

void SceneLoader::removeModel(uint32_t session_model_id) {
    // Refuse while the model is the active load: the streamer thread is still
    // running and would race with the deleteLater().  UI gates Remove on
    // isLoading(), but guard here too.
    if (loading_session_model_id_ == session_model_id) return;

    for (auto it = load_queue_.begin(); it != load_queue_.end();) {
        if (*it == session_model_id) it = load_queue_.erase(it);
        else            ++it;
    }

    auto it = models_.find(session_model_id);
    if (it == models_.end()) return;
    if (it->second.streamer) {
        it->second.streamer->deleteLater();
    }
    models_.erase(it);
}

void SceneLoader::cancelCurrentLoad() {
    if (loading_session_model_id_ == 0) return;
    auto it = models_.find(loading_session_model_id_);
    if (it == models_.end() || it->second.streamer == nullptr) return;
    it->second.streamer->cancel();
}

void SceneLoader::startNextLoad() {
    if (load_queue_.empty()) {
        loading_session_model_id_ = 0;
        emit allLoadsFinished();
        return;
    }

    loading_session_model_id_ = load_queue_.front();
    load_queue_.pop_front();

    auto& model = models_[loading_session_model_id_];
    model.load_timer.restart();

    emit loadStarted(model.id, model.display_name);

    std::string ifc_path = model.file_path.toStdString();
    uint32_t session_model_id = loading_session_model_id_;
    const bool is_sidecar_source =
        QFileInfo(model.file_path).suffix().compare("ifcview", Qt::CaseInsensitive) == 0;

    // No sidecar read probe when caching is off (and the user didn't pick a
    // .ifcview file directly). Skip the background thread and go straight
    // to a stream load.
    if (!is_sidecar_source && !should_read_sidecar_) {
        loadFromGeometryStreamer(session_model_id);
        return;
    }

    // Sidecar read on a background thread so the UI stays responsive.
    joinSidecarThread();
    sidecar_read_thread_ = std::thread([this, ifc_path, session_model_id, is_sidecar_source]() {
        QElapsedTimer read_timer; read_timer.start();
        auto cached = readSidecarMetadata(ifc_path);
        std::fprintf(stderr, "[info]   Sidecar metadata read: %lld ms (%s)\n",
                     (long long)read_timer.elapsed(), ifc_path.c_str());
        auto result = std::make_shared<std::optional<StreamingSidecar>>(std::move(cached));
        QMetaObject::invokeMethod(this, [this, session_model_id, result, is_sidecar_source]() {
            auto it = models_.find(session_model_id);
            if (*result && !(*result)->meta.instances.empty()) {
                applySidecarData(session_model_id, std::move(**result));
                if (!is_sidecar_source) {
                    startDataSourceLoad(session_model_id);
                }
                return;
            }

            if (it == models_.end()) return;

            if (is_sidecar_source) {
                loading_session_model_id_ = 0;
                emit loadError(session_model_id, QString("Failed to read IFC Viewer cache:\n%1").arg(it->second.file_path));
                QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
                return;
            }

            loadFromGeometryStreamer(session_model_id);
        }, Qt::QueuedConnection);
    });
}

void SceneLoader::loadFromGeometryStreamer(uint32_t session_model_id) {
    auto it = models_.find(session_model_id);
    if (it == models_.end()) return;
    auto& model = it->second;
    // Accumulate sidecar data alongside the GPU upload so the first load
    // naturally produces a cache for the next one — no GPU readback at
    // finish time. Skipped when caching writes are off.
    if (should_write_sidecar_) {
        model.sidecar_builder = std::make_unique<SidecarBuilder>();
    }
    // Elements are buffered here and emitted to the registry once at finalize,
    // after applyCachedModel assigns this model's global object_id base.
    model.streamed_elements.clear();
    connectStreamer(model.streamer);
    element_poll_timer_.start();
    model.streamer->loadFile(model.file_path.toStdString(), loading_session_model_id_);
}

void SceneLoader::applySidecarData(uint32_t session_model_id, StreamingSidecar metadata) {
    auto it = models_.find(session_model_id);
    if (it == models_.end()) return;
    auto& model = it->second;
    SidecarData& sidecar = metadata.meta;

    std::fprintf(stderr,
        "[info] Sidecar hit: %s (%zu chunks, %zu meshes, %zu instances, %zu elements)\n",
        model.file_path.toStdString().c_str(),
        sidecar.chunks.size(),
        sidecar.meshes.size(),
        sidecar.instances.size(),
        sidecar.elements.size());

    // Restore the cached CoordinateOperation into the model so
    // modelGeoref(session_model_id) returns it without needing the IFC source.  Prevents
    // sidecar-loaded models from silently losing their georef when the
    // .ifc/.rdb sibling is absent.
    {
        ModelGeoref& georef = model.georef;
        georef.has_coordinate_operation = sidecar.has_coordinate_operation != 0;
        Eigen::Map<const Eigen::Matrix<double, 4, 4, Eigen::ColMajor>> coord_op(
            sidecar.coordinate_operation_meters);
        georef.coordinate_operation_meters     = coord_op;
        georef.units.project_length_to_meters  = sidecar.project_length_to_meters;
        georef.units.map_unit_to_meters        = sidecar.map_unit_to_meters;
        model.has_georef                       = true;
    }

    // Pull the element table out before applyCachedModel consumes the metadata.
    // The geometry upload doesn't touch elements; it only reads/moves meshes and
    // instances.
    std::vector<ElementTableRecord> elements = std::move(sidecar.elements);
    std::string string_table                 = std::move(sidecar.string_table);

    // applyCachedModel is the sole authority for the global object_id space: the
    // sidecar stores model-LOCAL ids, and it assigns each instance's global id as
    // base + local, storing the base on the model. The element table gets the
    // same base below — one authority, two halves, no separate id assignment.
    viewport_->applyCachedModel(session_model_id, std::move(metadata));

    // Stamp the element records with the same base applyCachedModel gave the
    // instances, so registry ids match the ids pick/selection return. Mirrors
    // ViewportCore::loadElementMetadataWeb and the live-stream path
    // (onStreamerFinished).
    const uint32_t base = viewport_->modelObjectIdBase(session_model_id);
    for (auto& element : elements) {
        element.object_id += base;
        element.session_model_id = session_model_id;
    }

    emit sidecarElementsReady(session_model_id, std::move(elements), std::move(string_table));

    qint64 elapsed_ms = model.load_timer.elapsed();
    emit loadedFromSidecar(session_model_id, elapsed_ms);

    loading_session_model_id_ = 0;
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}

void SceneLoader::startDataSourceLoad(uint32_t session_model_id) {
    auto it = models_.find(session_model_id);
    if (it == models_.end()) return;

    std::string data_path_std = it->second.file_path.toStdString();
    data_source_threads_.emplace_back([this, session_model_id, data_path_std]() {
        QElapsedTimer timer; timer.start();
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
                     (long long)timer.elapsed(), data_path_std.c_str());

        auto shared = std::make_shared<std::unique_ptr<ifcopenshell::file>>(std::move(file));
        QMetaObject::invokeMethod(this, [this, session_model_id, shared]() {
            auto it = models_.find(session_model_id);
            if (it == models_.end()) return;
            auto* streamer = it->second.streamer;
            if (streamer == nullptr) return;
            // If the streamer already has a file (e.g. a later stream-fallback
            // path somehow populated it), don't clobber it.
            if (streamer->ifcFile() != nullptr) return;
            streamer->setIfcFile(std::move(*shared));
            emit dataSourceReady(session_model_id);
        }, Qt::QueuedConnection);
    });
}

void SceneLoader::onStreamerProgressChanged(int percent) {
    emit progressChanged(percent);
}

void SceneLoader::onStreamerMeshReady(StreamedMesh mesh) {
    viewport_->uploadStreamedMesh(mesh);
    if (loading_session_model_id_ != 0) {
        auto it = models_.find(loading_session_model_id_);
        if (it != models_.end() && it->second.sidecar_builder) {
            it->second.sidecar_builder->onMeshReady(mesh);
        }
    }
}

void SceneLoader::onStreamerInstanceReady(StreamedInstance instance_record) {
    if (loading_session_model_id_ != 0) {
        auto it = models_.find(loading_session_model_id_);
        if (it != models_.end() && it->second.sidecar_builder) {
            it->second.sidecar_builder->onInstanceReady(instance_record);
        }
    }
    viewport_->uploadStreamedInstance(instance_record);
}

void SceneLoader::onElementPollTick() {
    if (loading_session_model_id_ == 0) return;
    auto it = models_.find(loading_session_model_id_);
    if (it == models_.end()) return;

    auto batch = it->second.streamer->drainElements();
    if (batch.empty()) return;

    // Buffer the whole set. The streamer stamps model-LOCAL object_ids, so we
    // can't hand these to the registry yet — they're globalized and emitted
    // once at finalize (onStreamerFinished), after applyCachedModel assigns
    // this model's object_id base. The sidecar builder also reads this buffer.
    auto& buf = it->second.streamed_elements;
    buf.insert(buf.end(), batch.begin(), batch.end());
}

void SceneLoader::onStreamerFinished() {
    element_poll_timer_.stop();
    onElementPollTick();  // drain any remaining elements

    uint32_t session_model_id = loading_session_model_id_;
    if (session_model_id != 0) {
        auto it = models_.find(session_model_id);
        if (it != models_.end()) {
            auto& model = it->second;
            viewport_->finalizeModel(session_model_id);

            // Sidecar finalize + disk write. Wgpu has no live LOD1 apply —
            // LOD1 indices land in the on-disk sidecar and are picked up
            // on the *next* open of this file; first-session view is
            // LOD0-only. Acceptable trade-off vs reallocating chunk index
            // slices live to splice LOD1 in.
            //
            // The sidecar is written from the LOCAL element/instance ids (the
            // globalization below happens after), so a re-opened .ifcview
            // stores model-local ids exactly like a freshly-streamed one.
            if (model.sidecar_builder) {
                ModelGeoref georef;
                if (auto* file = model.streamer->ifcFile()) {
                    georef = computeModelGeoref(file);
                }
                QElapsedTimer write_timer; write_timer.start();
                SidecarData data = model.sidecar_builder->finalize(georef, model.streamed_elements);
                // Lay geometry out in streaming-chunk order + bake the chunk TOC
                // (v14) so it streams as one contiguous range per chunk.
                reorderSidecarByMorton(data);
                const bool ok = writeSidecar(model.file_path.toStdString(), data);
                std::fprintf(stderr,
                    "[info]   Sidecar finalize + write: %lld ms (%s)\n",
                    (long long)write_timer.elapsed(), ok ? "ok" : "FAILED");
                model.sidecar_builder.reset();
            }

            // Globalize the buffered element ids by the base applyCachedModel
            // assigned to this model's instances, then hand them to the
            // registry — one emit, ids matching the GPU/pick space. Mirrors the
            // sidecar-hit path (applySidecarData).
            const uint32_t base = viewport_->modelObjectIdBase(session_model_id);
            for (auto& element : model.streamed_elements) element.object_id += base;
            emit streamedElementsReady(session_model_id, std::move(model.streamed_elements));
            model.streamed_elements.clear();
            model.streamed_elements.shrink_to_fit();

            qint64 elapsed_ms = model.load_timer.elapsed();
            emit loadedFromStream(session_model_id, elapsed_ms);
        }
    }

    loading_session_model_id_ = 0;
    startNextLoad();
}

void SceneLoader::onStreamerCancelled() {
    element_poll_timer_.stop();

    const uint32_t session_model_id = loading_session_model_id_;
    loading_session_model_id_ = 0;

    if (session_model_id != 0) {
        viewport_->removeModel(session_model_id);
        emit loadCancelled(session_model_id);
    }
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}

void SceneLoader::onStreamerError(const QString& msg) {
    element_poll_timer_.stop();

    const uint32_t session_model_id = loading_session_model_id_;
    loading_session_model_id_ = 0;

    if (session_model_id != 0) {
        viewport_->removeModel(session_model_id);
    }
    emit loadError(session_model_id, msg);
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}
