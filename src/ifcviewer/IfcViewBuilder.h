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

#ifndef IFCVIEWBUILDER_H
#define IFCVIEWBUILDER_H

#include "IfcViewAssembler.h"

#include <QObject>
#include <QString>

// Thin QObject wrapper around IfcViewAssembler: the Qt bits a desktop app
// needs (QObject, QString, QEventLoop) live here, the assembly itself does not.
// Two use modes:
//
//   1. Live load — host (SceneLoader) drives its own GeometryStreamer and
//      forwards meshReady/instanceReady chunks via onMeshReady/onInstanceReady
//      while the viewport also consumes them. When the stream finishes the
//      host calls finalize(georef, elements) and writeIfcView() with the
//      returned data. No GPU readback involved.
//
//   2. Offline — build() owns a streamer, runs it on a non-GUI worker thread,
//      and writes the .ifcview to disk. Used by the .rdbview export path.
class IfcViewBuilder : public QObject {
    Q_OBJECT
public:
    explicit IfcViewBuilder(QObject* parent = nullptr);

    // Convenience for the offline path: construct an internal streamer,
    // accumulate, finalize, and write to disk. anchor_path is normalised to
    // <stem>.ifcview by writeIfcView. Call from a non-GUI worker thread with
    // a Qt event dispatcher; build() spins a local QEventLoop until the
    // streamer's worker thread completes.
    bool build(const QString& ifc_path,
               const QString& anchor_path,
               int num_threads = 0);

    // Accumulator interface. Safe to call repeatedly from the same thread the
    // streamer signals are delivered to.
    void onMeshReady(const StreamedMesh& mesh);
    void onInstanceReady(const StreamedInstance& instance_record);

    // Finishes assembly using the georef + element batch the host collected
    // during streaming. Returns the assembled IfcViewData by move; the
    // builder's internal state is left empty so the same instance can be
    // reused for another load.
    IfcViewData finalize(const ModelGeoref& georef,
                         const std::vector<ElementInfo>& elements);

    const QString& lastError() const { return last_error_; }

private:
    IfcViewAssembler serializer_;
    QString            last_error_;
};

#endif // IFCVIEWBUILDER_H
