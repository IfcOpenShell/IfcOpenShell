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

#ifndef SIDECARBUILDER_H
#define SIDECARBUILDER_H

#include "Federation.h"
#include "GeometryStreamer.h"
#include "InstancedGeometry.h"
#include "SidecarCache.h"

#include <QObject>
#include <QString>

#include <vector>

// Assembles a .ifcview SidecarData from streamer output, then finalizes it
// (LOD build, georef, packed elements) ready for writeSidecar() and/or
// ViewportWindow::applyLodExtension(). Two use modes:
//
//   1. Live load — host (SceneLoader) drives its own GeometryStreamer and
//      forwards meshReady/instanceReady chunks via onMeshReady/onInstanceReady
//      while the viewport also consumes them. When the stream finishes the
//      host calls finalize(georef, elements) and writeSidecar() with the
//      returned data. No GPU readback involved.
//
//   2. Offline — build() owns a streamer, runs it on a non-GUI worker thread,
//      and writes the sidecar to disk. Used by the .rdbview export path.
class SidecarBuilder : public QObject {
    Q_OBJECT
public:
    explicit SidecarBuilder(QObject* parent = nullptr);

    // Convenience for the offline path: construct an internal streamer,
    // accumulate, finalize, and write to disk. anchor_path is normalised to
    // <stem>.ifcview by writeSidecar. Call from a non-GUI worker thread with
    // a Qt event dispatcher; build() spins a local QEventLoop until the
    // streamer's worker thread completes.
    bool build(const QString& ifc_path,
               const QString& anchor_path,
               int num_threads = 0);

    // Accumulator interface. Safe to call repeatedly from the same thread the
    // streamer signals are delivered to.
    void onMeshReady(const MeshChunk& chunk);
    void onInstanceReady(const InstanceChunk& chunk);

    // Finishes assembly using the georef + element batch the host collected
    // during streaming. Returns the assembled SidecarData by move; the
    // builder's internal state is left empty so the same instance can be
    // reused for another load.
    SidecarData finalize(const ModelGeoref& georef,
                         const std::vector<ElementInfo>& elements);

    const QString& lastError() const { return last_error_; }

private:
    SidecarData sidecar_data_;
    QString     last_error_;
};

#endif // SIDECARBUILDER_H

