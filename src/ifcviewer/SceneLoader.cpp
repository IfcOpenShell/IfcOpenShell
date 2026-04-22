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

#include <QFileInfo>
#include <QTimer>
#include <QDebug>

#include <memory>
#include <optional>
#include <utility>

SceneLoader::SceneLoader(ViewportWindow* viewport, QObject* parent)
    : QObject(parent), viewport_(viewport)
{
    connect(&element_poll_timer_, &QTimer::timeout,
            this, &SceneLoader::onElementPollTick);
    element_poll_timer_.setInterval(100);
}

SceneLoader::~SceneLoader() {
    joinSidecarThread();
}

void SceneLoader::joinSidecarThread() {
    if (sidecar_read_thread_.joinable())
        sidecar_read_thread_.join();
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

std::vector<uint32_t> SceneLoader::addFiles(const QStringList& paths) {
    std::vector<uint32_t> assigned;
    assigned.reserve(paths.size());
    for (const auto& path : paths) {
        uint32_t id = next_model_id_++;
        Entry entry;
        entry.id = id;
        entry.file_path = path;
        entry.display_name = QFileInfo(path).fileName();
        entry.streamer = new GeometryStreamer(this);
        models_[id] = std::move(entry);
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

    // Sidecar read on a background thread so the UI stays responsive.
    joinSidecarThread();
    sidecar_read_thread_ = std::thread([this, ifc_path, mid]() {
        QElapsedTimer rt; rt.start();
        auto cached = readSidecar(ifc_path);
        qDebug("  Sidecar read: %lld ms (%s)", rt.elapsed(), ifc_path.c_str());
        auto result = std::make_shared<std::optional<SidecarData>>(std::move(cached));
        QMetaObject::invokeMethod(this, [this, mid, result]() {
            if (*result && !(*result)->instances.empty()) {
                applySidecarData(mid, std::move(**result));
            } else {
                auto it = models_.find(mid);
                if (it == models_.end()) return;
                auto& m = it->second;
                connectStreamer(m.streamer);
                element_poll_timer_.start();
                m.streamer->loadFile(
                    m.file_path.toStdString(), next_object_id_, loading_model_id_);
            }
        }, Qt::QueuedConnection);
    });
}

void SceneLoader::applySidecarData(uint32_t mid, SidecarData data) {
    auto it = models_.find(mid);
    if (it == models_.end()) return;
    auto& model = it->second;

    qDebug("Sidecar hit: %s (%zu verts, %zu indices, %zu meshes, %zu instances, %zu elements)",
           model.file_path.toStdString().c_str(),
           data.vertices.size() / INSTANCED_VERTEX_STRIDE_BYTES,
           data.indices.size(),
           data.meshes.size(),
           data.instances.size(),
           data.elements.size());

    // Rebase object/model IDs onto the current session's ID space.  Two
    // cached models both starting at object_id=1 would collide otherwise.
    uint32_t min_oid = UINT32_MAX;
    for (const auto& pe : data.elements) {
        if (pe.object_id < min_oid) min_oid = pe.object_id;
    }
    uint32_t oid_offset = 0;
    if (!data.elements.empty() && min_oid < UINT32_MAX) {
        oid_offset = next_object_id_ - min_oid;
    }
    for (auto& pe : data.elements) {
        pe.object_id += oid_offset;
        pe.model_id   = mid;
        if (pe.object_id >= next_object_id_)
            next_object_id_ = pe.object_id + 1;
    }
    for (auto& inst : data.instances) {
        inst.object_id += oid_offset;
        inst.model_id   = mid;
    }

    std::vector<PackedElementInfo> elements = std::move(data.elements);
    std::string stbl                        = std::move(data.string_table);

    viewport_->applyCachedModel(mid, std::move(data));

    emit sidecarElementsReady(mid, std::move(elements), std::move(stbl));

    qint64 ms = model.load_timer.elapsed();
    emit loadedFromSidecar(mid, ms);

    loading_model_id_ = 0;
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}

void SceneLoader::onStreamerProgressChanged(int percent) {
    emit progressChanged(percent);
}

void SceneLoader::onStreamerMeshReady(MeshChunk chunk) {
    viewport_->uploadMeshChunk(chunk);
}

void SceneLoader::onStreamerInstanceReady(InstanceChunk chunk) {
    viewport_->uploadInstanceChunk(chunk);
}

void SceneLoader::onElementPollTick() {
    if (loading_model_id_ == 0) return;
    auto it = models_.find(loading_model_id_);
    if (it == models_.end()) return;

    auto batch = it->second.streamer->drainElements();
    if (!batch.empty()) {
        emit streamedElementsReady(loading_model_id_, std::move(batch));
    }
}

void SceneLoader::onStreamerFinished() {
    element_poll_timer_.stop();
    onElementPollTick();  // drain any remaining elements

    uint32_t mid = loading_model_id_;
    if (mid != 0) {
        auto it = models_.find(mid);
        if (it != models_.end()) {
            next_object_id_ = it->second.streamer->lastObjectId();
            viewport_->finalizeModel(mid);

            qint64 ms = it->second.load_timer.elapsed();
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
