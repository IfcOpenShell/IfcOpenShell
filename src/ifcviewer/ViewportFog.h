/********************************************************************************
 *                                                                              *
 * Three.js-style viewport fog settings (Fog / FogExp2).                        *
 * Uniform packing and WGSL live in ViewportFogWgsl.h.                          *
 *                                                                              *
 ********************************************************************************/

#ifndef VIEWPORTFOG_H
#define VIEWPORTFOG_H

#include <Eigen/Core>

enum class ViewportFogMode : int {
    Off    = 0,
    Linear = 1,
    Exp2   = 2,
};

// Distance fog state owned by ViewportCore, consumed by main + grid passes.
class ViewportFog {
public:
    void set(int mode, float near, float far, float density,
             float r, float g, float b);

    ViewportFogMode mode() const { return mode_; }
    bool enabled() const { return mode_ != ViewportFogMode::Off; }
    float near() const { return near_; }
    float far() const { return far_; }
    float density() const { return density_; }
    const Eigen::Vector4f& color() const { return color_; }

    // Write fog + camera tail of FrameUniforms / grid uniform slots (128 bytes).
    void writeUniformTail(float camera_pos[4],
                          float view_forward[4],
                          float fog_color[4],
                          float fog_params[4],
                          const Eigen::Vector3f& eye,
                          const Eigen::Vector3f& forward) const;

private:
    ViewportFogMode mode_    = ViewportFogMode::Off;
    Eigen::Vector4f color_   = {0.125f, 0.137f, 0.161f, 1.0f};
    float near_              = 1.0f;
    float far_               = 1000.0f;
    float density_           = 0.002f;
};

#endif  // VIEWPORTFOG_H
