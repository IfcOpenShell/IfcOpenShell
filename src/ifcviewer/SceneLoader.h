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
#include <memory>
#include <string>
#include <thread>
#include <vector>

#include "Federation.h"
#include "../ifcviewer/ViewportWindow.h"
#include "../ifcviewer/StreamingLoader.h"
#include "GeometryStreamer.h"
#include "SidecarBuilder.h"
#include "SidecarCache.h"

// Drives IFC file loading into a ViewportWindow.  Owns the per-model
// GeometryStreamer, the load queue, the sidecar read thread, and the
// next-free object_id counter used to rebase cached models onto the
// current session's ID space.
//
// Consumers (MainWindow, MinimalWindow) observe progress through signals
// and never touch the streamer, sidecar thread, or queue directly.
// Sidecar *writes* happen automatically as a side effect of stream loads —
// the SidecarBuilder accumulates from the streamer chunks alongside the
// viewport upload, and SceneLoader finalizes + writes the result when the
// stream finishes. No GPU readback involved.
class SceneLoader : public QObject {
    Q_OBJECT
public:
    explicit SceneLoader(ViewportWindow* viewport, QObject* parent = nullptr);
    ~SceneLoader();

    // Sidecar cache use is opt-in per direction. Embedders that don't care
    // about .ifcview can leave both off (default) and SceneLoader will never
    // probe for or produce one. Toggles only affect *subsequent* loads;
    // a load already in flight finishes with whatever was set when it
    // started. Opening a `.ifcview` file directly always reads it,
    // regardless of these flags.
    void setShouldReadSidecar(bool enabled);
    void setShouldWriteSidecar(bool enabled);
    bool shouldReadSidecar() const { return should_read_sidecar_; }
    bool shouldWriteSidecar() const { return should_write_sidecar_; }

    // Returns the session_model_ids assigned to the enqueued paths, in order.
    // Callers can use these to set up per-model UI state (tree roots, etc.)
    // before any load signal fires.
    std::vector<uint32_t> queueModels(const QStringList& paths);
    void cancelCurrentLoad();
    bool isLoading() const { return loading_session_model_id_ != 0 || !load_queue_.empty(); }
    bool isLoadingModel(uint32_t session_model_id) const { return loading_session_model_id_ == session_model_id; }
    size_t modelCount() const { return models_.size(); }

    // Drop the loader's tracking for `session_model_id` — its streamer, file path, georef
    // cache, and queue slot if still pending.  Caller is responsible for the
    // viewport / UI cleanup; this only releases the loader's own state.
    // Refuses while the model is the active load (use cancelCurrentLoad first).
    void removeModel(uint32_t session_model_id);

    QString filePath(uint32_t session_model_id) const;
    QString displayName(uint32_t session_model_id) const;
    ifcopenshell::file* ifcFile(uint32_t session_model_id) const;

    // Lazily computes the model's georef matrix + unit scales the first
    // time it's asked for, caches the result, and returns a pointer into the
    // cache.  Returns nullptr when the IFC file isn't available yet (e.g.
    // sidecar-hit path before the data-source thread populates the streamer).
    const ModelGeoref* modelGeoref(uint32_t session_model_id);

signals:
    void progressChanged(int percent);
    void loadStarted(uint32_t session_model_id, QString display_name);

    // Fired once per sidecar hit, before loadedFromSidecar, with the full
    // packed element set.  Consumer is responsible for decoding + tree/
    // property-map population.  Moved arguments — avoid unnecessary copies.
    void sidecarElementsReady(uint32_t session_model_id,
                              std::vector<ElementTableRecord> elements,
                              std::string string_table);
    void loadedFromSidecar(uint32_t session_model_id, qint64 elapsed_ms);

    // Fired after a sidecar-hit model has its .rdb/.ifc opened as a
    // property data source in the background.  Consumers can refresh
    // any UI that queries ifcFile(session_model_id) for attributes/properties.
    void dataSourceReady(uint32_t session_model_id);

    // Fired repeatedly while streaming, as the worker thread produces
    // elements.  Each batch contains whatever accumulated since the last
    // poll tick.
    void streamedElementsReady(uint32_t session_model_id, std::vector<ElementInfo> elements);

    // Fired once after the streamer finishes and the viewport has been
    // finalized.  Consumer may synchronously perform work that needs all
    // elements to be known (e.g. sidecar write) — SceneLoader will only
    // start the next queued load after all slots return.
    void loadedFromStream(uint32_t session_model_id, qint64 elapsed_ms);
    void loadCancelled(uint32_t session_model_id);

    void loadError(uint32_t session_model_id, QString message);
    void allLoadsFinished();

private slots:
    void onStreamerProgressChanged(int percent);
    void onStreamerMeshReady(StreamedMesh mesh);
    void onStreamerInstanceReady(StreamedInstance instance_record);
    void onStreamerFinished();
    void onStreamerCancelled();
    void onStreamerError(const QString& msg);
    void onElementPollTick();

private:
    struct Model {
        uint32_t id = 0;
        QString file_path;
        QString display_name;
        GeometryStreamer* streamer = nullptr;
        QElapsedTimer load_timer;

        // Cached on first SceneLoader::modelGeoref(session_model_id) call once the
        // streamer has its IFC file loaded.
        ModelGeoref georef;
        bool        has_georef = false;

        // Live-load sidecar accumulator. Constructed at the start of a
        // stream load when shouldWriteSidecar is on; null otherwise.
        std::unique_ptr<SidecarBuilder> sidecar_builder;
        // Element batches accumulated as the streamer yields, mirrored from
        // what's emitted via streamedElementsReady so finalize() has the
        // full set without re-draining.
        std::vector<ElementInfo> streamed_elements;
    };

    void startNextLoad();
    void loadFromGeometryStreamer(uint32_t session_model_id);
    void connectStreamer(GeometryStreamer* streamer);
    void joinSidecarThread();
    void joinDataSourceThreads();
    void applySidecarData(uint32_t session_model_id, StreamingSidecar metadata);
    void startDataSourceLoad(uint32_t session_model_id);

    ViewportWindow* viewport_ = nullptr;
    bool should_read_sidecar_ = false;
    bool should_write_sidecar_ = false;
    std::map<uint32_t, Model> models_;
    std::deque<uint32_t> load_queue_;
    uint32_t next_session_model_id_ = 1;
    uint32_t loading_session_model_id_ = 0;
    std::thread sidecar_read_thread_;
    // Background .ifcview compress + write, so the seconds of zstd on a big
    // model don't freeze the UI at 100%. Joined before the next write and in
    // the destructor so a pending write always completes.
    std::thread sidecar_write_thread_;
    // One thread per sidecar-hit model while its .rdb/.ifc opens in the
    // background.  Joined only at destruction so a slow SPF parse on model
    // A never blocks the sidecar-hit path of model B.
    std::vector<std::thread> data_source_threads_;
    QTimer element_poll_timer_;
};

#endif // SCENELOADER_H
