/********************************************************************************
 *                                                                              *
 * Shared WGSL snippets for Three.js-style distance fog (Fog / FogExp2).        *
 * Included by the main mesh shader and the grid overlay shader.                *
 *                                                                              *
 * Depth matches Three.js vFogDepth = -mvPosition.z (view-space, metres).       *
 * Colours are sRGB [0..1] (same as setBackgroundColor). Mix in that space —   *
 * same as Three.js fog_fragment — then callers run srgbToLinear() on output.   *
 *                                                                              *
 ********************************************************************************/

#ifndef VIEWPORTFOGWGSL_H
#define VIEWPORTFOGWGSL_H

// Extra FrameUniforms / GridUniforms fields appended after the core layout.
#define VIEWPORT_FOG_WGSL_UNIFORM_FIELDS \
    "    camera_pos:   vec4<f32>,\n" \
    "    view_forward: vec4<f32>, // xyz = unit camera forward (world space)\n" \
    "    fog_color:    vec4<f32>,\n" \
    "    fog_params:   vec4<f32>, // x=near, y=far, z=density, w=mode (0 off, 1 linear, 2 exp2)\n"

#define VIEWPORT_FOG_WGSL_SRGB_TO_LINEAR \
    "fn srgbToLinear(s: vec3<f32>) -> vec3<f32> {\n" \
    "    let lo = s / 12.92;\n" \
    "    let hi = pow((s + 0.055) / 1.055, vec3<f32>(2.4));\n" \
    "    return select(hi, lo, s <= vec3<f32>(0.04045));\n" \
    "}\n"

#define VIEWPORT_FOG_WGSL_LINEAR_TO_SRGB \
    "fn linearToSrgb(l: vec3<f32>) -> vec3<f32> {\n" \
    "    let lo = l * 12.92;\n" \
    "    let hi = 1.055 * pow(l, vec3<f32>(1.0 / 2.4)) - 0.055;\n" \
    "    return select(lo, hi, l <= vec3<f32>(0.0031308));\n" \
    "}\n"

#define VIEWPORT_FOG_WGSL_APPLY_FN \
    "fn viewport_fog_factor(\n" \
    "    world_pos: vec3<f32>,\n" \
    "    camera_pos: vec3<f32>,\n" \
    "    view_forward: vec3<f32>,\n" \
    "    fog_params: vec4<f32>,\n" \
    ") -> f32 {\n" \
    "    let fog_mode = fog_params.w;\n" \
    "    if (fog_mode <= 0.5) { return 0.0; }\n" \
    "    let fog_depth = max(dot(world_pos - camera_pos, view_forward), 0.0);\n" \
    "    if (fog_mode < 1.5) {\n" \
    "        return smoothstep(fog_params.x, fog_params.y, fog_depth);\n" \
    "    }\n" \
    "    let d = fog_params.z * fog_depth;\n" \
    "    return 1.0 - exp(-d * d);\n" \
    "}\n" \
    "fn viewport_apply_distance_fog(\n" \
    "    color: vec3<f32>,\n" \
    "    world_pos: vec3<f32>,\n" \
    "    camera_pos: vec3<f32>,\n" \
    "    view_forward: vec3<f32>,\n" \
    "    fog_color: vec3<f32>,\n" \
    "    fog_params: vec4<f32>,\n" \
    ") -> vec3<f32> {\n" \
    "    let fog_factor = viewport_fog_factor(\n" \
    "        world_pos, camera_pos, view_forward, fog_params);\n" \
    "    if (fog_factor <= 0.0) { return color; }\n" \
    "    return mix(color, fog_color, fog_factor);\n" \
    "}\n"

#endif  // VIEWPORTFOGWGSL_H
