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

#include <QString>

// Offline bake of an .ifcview with the viewer's own pipeline: build() runs a
// GeometryStreamer over the IFC, assembles its output with IfcViewAssembler
// and writes the file.  Used by the models-panel export and the out-of-tree
// bake tool.  The live viewer does not come through here: SceneLoader feeds
// an IfcViewAssembler straight from the streamer it already drives.
class IfcViewBuilder {
public:
    // anchor_path is normalised to <stem>.ifcview by writeIfcView.  Call from
    // a non-GUI worker thread with a Qt event dispatcher; build() spins a
    // local QEventLoop until the streamer's worker thread completes.
    bool build(const QString& ifc_path,
               const QString& anchor_path,
               int num_threads = 0);

    const QString& lastError() const { return last_error_; }

private:
    QString last_error_;
};

#endif // IFCVIEWBUILDER_H
