// This file was generated with the assistance of an AI coding tool.
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

#ifndef IFCINTERFACE_PANELS_VIEWPORT_CONTROLLER_H
#define IFCINTERFACE_PANELS_VIEWPORT_CONTROLLER_H

#include <QHash>
#include <QObject>

class Federation;
class SceneLoader;
class ViewportWindow;

namespace ifcinterface::panels::viewport {

class ViewportController : public QObject {
    Q_OBJECT

public:
    explicit ViewportController(Federation* federation,
                                SceneLoader* loader,
                                ViewportWindow* viewport,
                                const QHash<QString, uint32_t>* fed_id_to_model_id,
                                const QHash<uint32_t, QString>* model_id_to_fed_id,
                                QObject* parent = nullptr);

    void applyFederatedFalseOrigin();

private:
    void applyCoordinateOperation(uint32_t mid);
    void applyModelTransformation(uint32_t mid);
    void maybeGuessFederatedFalseOrigin(uint32_t mid);

    Federation* federation_ = nullptr;
    SceneLoader* loader_ = nullptr;
    ViewportWindow* viewport_ = nullptr;
    const QHash<QString, uint32_t>* fed_id_to_model_id_ = nullptr;
    const QHash<uint32_t, QString>* model_id_to_fed_id_ = nullptr;
};

} // namespace ifcinterface::panels::viewport

#endif
