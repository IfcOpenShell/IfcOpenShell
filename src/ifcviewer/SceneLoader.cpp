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

#include <QFileInfo>
#include <QTimer>
#include <QDebug>
#include <QElapsedTimer>

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

const Eigen::Matrix4d* SceneLoader::firstPlacement(uint32_t mid) const {
    auto it = models_.find(mid);
    if (it == models_.end() || !it->second.has_first_placement) return nullptr;
    return &it->second.first_placement;
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

    // Restore the cached CoordinateOperation into the model so
    // modelGeoref(mid) returns it without needing the IFC source.  Prevents
    // sidecar-loaded models from silently losing their georef when the
    // .ifc/.rdb sibling is absent or AppSettings.loadDataSource is off.
    {
        ModelGeoref& gr = model.georef;
        gr.has_coordinate_operation = data.has_coordinate_operation != 0;
        Eigen::Map<const Eigen::Matrix<double, 4, 4, Eigen::ColMajor>> M(
            data.coordinate_operation_meters);
        gr.coordinate_operation_meters     = M;
        gr.units.project_length_to_meters  = data.project_length_to_meters;
        gr.units.map_unit_to_meters        = data.map_unit_to_meters;
        model.has_georef                   = true;
    }

    if (!data.instances.empty() && !model.has_first_placement) {
        using Mat4fCol = Eigen::Matrix<float, 4, 4, Eigen::ColMajor>;
        model.first_placement =
            Eigen::Map<const Mat4fCol>(data.instances[0].placement_transformation)
                .cast<double>();
        model.has_first_placement = true;
    }

    std::vector<PackedElementInfo> elements = std::move(data.elements);
    std::string stbl                        = std::move(data.string_table);

    viewport_->applyCachedModel(mid, std::move(data));

    emit sidecarElementsReady(mid, std::move(elements), std::move(stbl));

    qint64 ms = model.load_timer.elapsed();
    emit loadedFromSidecar(mid, ms);

    startDataSourceLoad(mid);

    loading_model_id_ = 0;
    QTimer::singleShot(0, this, &SceneLoader::startNextLoad);
}

// Match SidecarCache.cpp's sidecarPath() stem logic so we resolve the
// data-source siblings against the same stem the sidecar was keyed on.
static std::string pathStem(const std::string& path) {
    std::string p = path;
    while (!p.empty() && (p.back() == '/' || p.back() == '\\')) p.pop_back();
    auto slash = p.find_last_of("/\\");
    auto dot   = p.find_last_of('.');
    return (dot != std::string::npos &&
            (slash == std::string::npos || dot > slash))
               ? p.substr(0, dot)
               : p;
}

void SceneLoader::startDataSourceLoad(uint32_t mid) {
    if (!AppSettings::instance().loadDataSource()) return;

    auto it = models_.find(mid);
    if (it == models_.end()) return;

    std::string original_path = it->second.file_path.toStdString();
    std::string stem = pathStem(original_path);

    // Prefer RocksDB (foo.rdb) over SPF (foo.ifc) for fast random lookups.
    QString data_path;
    const QString rdb_candidate = QString::fromStdString(stem + ".rdb");
    const QString ifc_candidate = QString::fromStdString(stem + ".ifc");
    if (QFileInfo::exists(rdb_candidate)) {
        data_path = rdb_candidate;
    } else if (QFileInfo::exists(ifc_candidate)) {
        data_path = ifc_candidate;
    } else {
        return;
    }

    std::string data_path_std = data_path.toStdString();
    data_source_threads_.emplace_back([this, mid, data_path_std]() {
        QElapsedTimer t; t.start();
        std::unique_ptr<ifcopenshell::file> file;
        try {
            file = std::make_unique<ifcopenshell::file>(
                data_path_std, ifcopenshell::FT_AUTODETECT, /*read_only=*/true);
        } catch (const std::exception& e) {
            qWarning("  Data source load failed: %s (%s)",
                     data_path_std.c_str(), e.what());
            return;
        }
        qDebug("  Data source load: %lld ms (%s)", t.elapsed(), data_path_std.c_str());

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
}

void SceneLoader::onStreamerInstanceReady(InstanceChunk chunk) {
    if (loading_model_id_ != 0) {
        auto it = models_.find(loading_model_id_);
        if (it != models_.end() && !it->second.has_first_placement) {
            using Mat4fCol = Eigen::Matrix<float, 4, 4, Eigen::ColMajor>;
            it->second.first_placement =
                Eigen::Map<const Mat4fCol>(chunk.transform).cast<double>();
            it->second.has_first_placement = true;
        }
    }
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

            // Slot(s) above run synchronously (sidecar write uses element_map_,
            // not ifcFile()); drop the parsed file now to save memory if the
            // user has opted out of keeping a property data source.
            if (!AppSettings::instance().loadDataSource()) {
                it->second.streamer->setIfcFile(nullptr);
            }
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
