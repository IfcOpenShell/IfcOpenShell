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

#ifndef SCENELOADER_H
#define SCENELOADER_H

#include <QObject>
#include <QString>
#include <QStringList>
#include <QTimer>
#include <QElapsedTimer>

#include <cstdint>
#include <deque>
#include <map>
#include <string>
#include <thread>
#include <vector>

#include "ViewportWindow.h"
#include "GeometryStreamer.h"
#include "SidecarCache.h"

// Drives IFC file loading into a ViewportWindow.  Owns the per-model
// GeometryStreamer, the load queue, the sidecar read thread, and the
// next-free object_id counter used to rebase cached models onto the
// current session's ID space.
//
// Consumers (MainWindow, MinimalWindow) observe progress through signals
// and never touch the streamer, sidecar thread, or queue directly.
// Sidecar *writes* are intentionally left to the consumer: they need the
// consumer's element metadata (guid/name/type strings) which SceneLoader
// does not retain.
class SceneLoader : public QObject {
    Q_OBJECT
public:
    explicit SceneLoader(ViewportWindow* viewport, QObject* parent = nullptr);
    ~SceneLoader();

    // Returns the model_ids assigned to the enqueued paths, in order.
    // Callers can use these to set up per-model UI state (tree roots, etc.)
    // before any load signal fires.
    std::vector<uint32_t> addFiles(const QStringList& paths);
    void cancelCurrentLoad();
    bool isLoading() const { return loading_model_id_ != 0 || !load_queue_.empty(); }
    size_t modelCount() const { return models_.size(); }

    QString filePath(uint32_t mid) const;
    QString displayName(uint32_t mid) const;
    uint64_t fileSize(uint32_t mid) const;
    ifcopenshell::file* ifcFile(uint32_t mid) const;

signals:
    void progressChanged(int percent);
    void loadStarted(uint32_t mid, QString display_name);

    // Fired once per sidecar hit, before loadedFromSidecar, with the full
    // packed element set.  Consumer is responsible for decoding + tree/
    // property-map population.  Moved arguments — avoid unnecessary copies.
    void sidecarElementsReady(uint32_t mid,
                              std::vector<PackedElementInfo> elements,
                              std::string string_table);
    void loadedFromSidecar(uint32_t mid, qint64 elapsed_ms);

    // Fired repeatedly while streaming, as the worker thread produces
    // elements.  Each batch contains whatever accumulated since the last
    // poll tick.
    void streamedElementsReady(uint32_t mid, std::vector<ElementInfo> elements);

    // Fired once after the streamer finishes and the viewport has been
    // finalized.  Consumer may synchronously perform work that needs all
    // elements to be known (e.g. sidecar write) — SceneLoader will only
    // start the next queued load after all slots return.
    void loadedFromStream(uint32_t mid, qint64 elapsed_ms);
    void loadCancelled(uint32_t mid);

    void loadError(uint32_t mid, QString message);
    void allLoadsFinished();

private slots:
    void onStreamerProgressChanged(int percent);
    void onStreamerMeshReady(MeshChunk chunk);
    void onStreamerInstanceReady(InstanceChunk chunk);
    void onStreamerFinished();
    void onStreamerCancelled();
    void onStreamerError(const QString& msg);
    void onElementPollTick();

private:
    struct Entry {
        uint32_t id = 0;
        QString file_path;
        QString display_name;
        GeometryStreamer* streamer = nullptr;
        QElapsedTimer load_timer;
    };

    void startNextLoad();
    void connectStreamer(GeometryStreamer* streamer);
    void joinSidecarThread();
    void applySidecarData(uint32_t mid, SidecarData data);

    ViewportWindow* viewport_ = nullptr;
    std::map<uint32_t, Entry> models_;
    std::deque<uint32_t> load_queue_;
    uint32_t next_model_id_ = 1;
    uint32_t next_object_id_ = 1;
    uint32_t loading_model_id_ = 0;
    std::thread sidecar_read_thread_;
    QTimer element_poll_timer_;
};

#endif // SCENELOADER_H
