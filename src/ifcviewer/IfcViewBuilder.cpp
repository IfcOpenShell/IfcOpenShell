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
#include "IfcViewWriter.h"

#include <QEventLoop>

#include <utility>

IfcViewBuilder::IfcViewBuilder(QObject* parent)
    : QObject(parent)
{
}

void IfcViewBuilder::onMeshReady(const StreamedMesh& mesh) {
    serializer_.onMeshReady(mesh);
}

void IfcViewBuilder::onInstanceReady(const StreamedInstance& instance_record) {
    serializer_.onInstanceReady(instance_record);
}

IfcViewData IfcViewBuilder::finalize(const ModelGeoref& georef,
                                     const std::vector<ElementInfo>& elements) {
    return serializer_.finalize(georef, elements);
}

bool IfcViewBuilder::build(const QString& ifc_path,
                           const QString& anchor_path,
                           int num_threads) {
    serializer_ = IfcViewAssembler{};
    last_error_.clear();

    GeometryStreamer streamer;
    QEventLoop loop;
    bool failed = false;

    connect(&streamer, &GeometryStreamer::meshReady,
            this, &IfcViewBuilder::onMeshReady);
    connect(&streamer, &GeometryStreamer::instanceReady,
            this, &IfcViewBuilder::onInstanceReady);
    connect(&streamer, &GeometryStreamer::finished,
            &loop, &QEventLoop::quit);
    connect(&streamer, &GeometryStreamer::cancelled,
            &loop, &QEventLoop::quit);
    connect(&streamer, &GeometryStreamer::errorOccurred, this,
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

    IfcViewData data = finalize(georef, streamer.drainElements());

    if (!writeIfcView(anchor_path.toStdString(), data)) {
        last_error_ = "writeIfcView failed";
        return false;
    }

    return true;
}
