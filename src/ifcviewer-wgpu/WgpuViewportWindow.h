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

#ifndef WGPUVIEWPORTWINDOW_H
#define WGPUVIEWPORTWINDOW_H

#include <QWindow>
#include <QColor>

#include <webgpu/webgpu.h>

// Stage-1 wgpu viewport: opens a native QWindow, brings up a wgpu instance/
// adapter/device, configures a surface against the platform-native window
// handle, and clears to background_color_ on every UpdateRequest.
//
// Mirrors the lifecycle shape of the GL ViewportWindow so subsequent stages
// can grow this into a full IFC renderer without restructuring the host.
class WgpuViewportWindow : public QWindow {
    Q_OBJECT
public:
    explicit WgpuViewportWindow(QWindow* parent = nullptr);
    ~WgpuViewportWindow();

    void setBackgroundColor(const QColor& color);

protected:
    void exposeEvent(QExposeEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;
    bool event(QEvent* event) override;

private:
    bool initWgpu();
    bool createSurface();
    void configureSurface(int width_px, int height_px);
    void render();
    void shutdown();

    bool wgpu_initialized_ = false;
    bool surface_configured_ = false;
    int  configured_w_ = 0;
    int  configured_h_ = 0;

    WGPUInstance      instance_       = nullptr;
    WGPUAdapter       adapter_        = nullptr;
    WGPUDevice        device_         = nullptr;
    WGPUQueue         queue_          = nullptr;
    WGPUSurface       surface_        = nullptr;
    WGPUTextureFormat surface_format_ = WGPUTextureFormat_Undefined;

    QColor background_color_ = QColor("#202329");
};

#endif // WGPUVIEWPORTWINDOW_H
