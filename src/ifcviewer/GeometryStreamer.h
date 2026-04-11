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

#ifndef GEOMETRYSTREAMER_H
#define GEOMETRYSTREAMER_H

#include <QObject>
#include <QThread>

#include <string>
#include <vector>
#include <atomic>
#include <functional>
#include <memory>
#include <mutex>
#include <deque>

#include "../ifcparse/file.h"
#include "../ifcgeom/Iterator.h"

#include "ViewportWindow.h"

struct ElementInfo {
    uint32_t object_id;
    int ifc_id;
    std::string guid;
    std::string name;
    std::string type;
    int parent_id;
};

class GeometryStreamer : public QObject {
    Q_OBJECT
public:
    explicit GeometryStreamer(QObject* parent = nullptr);
    ~GeometryStreamer();

    void loadFile(const std::string& path, int num_threads = 0);
    void cancel();

    bool isRunning() const { return running_.load(); }
    int progress() const { return progress_.load(); }

    ifcopenshell::file* ifcFile() const { return ifc_file_.get(); }

    // Thread-safe access to discovered elements
    std::vector<ElementInfo> drainElements();

signals:
    void progressChanged(int percent);
    void elementReady(UploadChunk chunk);
    void finished();
    void errorOccurred(const QString& message);

private:
    void run(const std::string& path, int num_threads);

    UploadChunk convertElement(const IfcGeom::TriangulationElement* elem, uint32_t object_id);

    std::unique_ptr<ifcopenshell::file> ifc_file_;
    std::unique_ptr<QThread> worker_thread_;
    std::atomic<bool> running_{false};
    std::atomic<bool> cancel_requested_{false};
    std::atomic<int> progress_{0};

    std::mutex elements_mutex_;
    std::vector<ElementInfo> pending_elements_;

    // Map from IFC product id to our compact object_id
    uint32_t next_object_id_ = 1; // 0 = no object
};

#endif // GEOMETRYSTREAMER_H
