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

#include "IfcViewBuilder.h"

#include "Federation.h"
#include "GeometryStreamer.h"
#include "IfcViewAssembler.h"
#include "IfcViewWriter.h"

#include <QEventLoop>
#include <QObject>

bool IfcViewBuilder::build(const QString& ifc_path,
                           const QString& anchor_path,
                           int num_threads) {
    last_error_.clear();

    GeometryStreamer streamer;
    IfcViewAssembler assembler;
    QEventLoop loop;
    bool failed = false;

    QObject::connect(&streamer, &GeometryStreamer::meshReady, &loop,
                     [&](const StreamedMesh& mesh) { assembler.onMeshReady(mesh); });
    QObject::connect(&streamer, &GeometryStreamer::instanceReady, &loop,
                     [&](const StreamedInstance& instance) { assembler.onInstanceReady(instance); });
    QObject::connect(&streamer, &GeometryStreamer::finished, &loop, &QEventLoop::quit);
    QObject::connect(&streamer, &GeometryStreamer::cancelled, &loop, &QEventLoop::quit);
    QObject::connect(&streamer, &GeometryStreamer::errorOccurred, &loop,
                     [&](const QString& msg) {
        last_error_ = msg;
        failed = true;
        loop.quit();
    });

    streamer.loadFile(ifc_path.toStdString(),
                      /*session_model_id*/ 1,
                      num_threads);

    loop.exec();

    if (failed) return false;

    ModelGeoref georef;
    if (auto* file = streamer.ifcFile()) {
        georef = computeModelGeoref(file);
    }

    IfcViewData data = assembler.finalize(georef, streamer.drainElements());

    if (!writeIfcView(anchor_path.toStdString(), data)) {
        last_error_ = "writeIfcView failed";
        return false;
    }

    return true;
}
