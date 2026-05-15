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

#ifndef HEADLESSSIDECARBUILDER_H
#define HEADLESSSIDECARBUILDER_H

#include "InstancedGeometry.h"
#include "SidecarCache.h"

#include <QObject>
#include <QString>

// Produces a .ifcview sidecar from an IFC file without touching the
// ViewportWindow or any GL state.  Mirrors the data path that
// SceneLoader + ViewportWindow + ModelsPanelController.writeSidecarForModel
// take for live loads, but does the vertex quantization and SidecarData
// assembly entirely on the CPU.
//
// Threading: call ::build() from a non-GUI worker thread that has a Qt
// event dispatcher (e.g. the thread spawned by QThread::create).  build()
// spins a local QEventLoop until the streamer's worker thread completes.
class HeadlessSidecarBuilder : public QObject {
    Q_OBJECT
public:
    explicit HeadlessSidecarBuilder(QObject* parent = nullptr);

    // `anchor_path` is fed to writeSidecar(), which normalises it to
    // `<stem(anchor_path)>.ifcview`.  Pass either the IFC path itself
    // (sidecar lands beside it) or a temp path whose stem you control.
    bool build(const QString& ifc_path,
               const QString& anchor_path,
               int num_threads = 0);

    const QString& lastError() const { return last_error_; }

private:
    void onMeshReady(const MeshChunk& chunk);
    void onInstanceReady(const InstanceChunk& chunk);

    SidecarData sidecar_data_;
    QString     last_error_;
};

#endif // HEADLESSSIDECARBUILDER_H
