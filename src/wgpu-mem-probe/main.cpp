// Standalone wgpu memory-allocation probe. Headless — no surface, no Qt.
// Discovers what the adapter reports vs what the runtime actually grants:
//
// 1. Print all relevant adapter + device limits.
// 2. Single-allocation probe: try createBuffer at descending sizes,
//    report which sizes succeed/refuse.
// 3. Cumulative allocation probe: keep allocating (without releasing)
//    until the driver refuses, halving the requested size on each
//    refusal. Reports total bytes / count we got to.
//
// Build: ninja -C build-viewer-wgpu WgpuMemProbe
// Run:   ./build-viewer-wgpu/wgpu-mem-probe/WgpuMemProbe

#include <webgpu/webgpu.h>

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {

// Drain async wgpu events. Both adapter/device requests AND error scope
// pops fire on the instance's event loop.
void processEventsUntil(WGPUInstance instance, const bool* done) {
    while (!*done) {
        wgpuInstanceProcessEvents(instance);
    }
}

// Capture an error scope pop. Treats both Validation and OOM as "the
// allocation failed" — wgpu-native lumps "Not enough memory" into
// Validation, while spec-compliant impls (Dawn / browsers) classify
// as OutOfMemory.
struct ScopeResult {
    bool done  = false;
    bool error = false;
    WGPUErrorType type = WGPUErrorType_NoError;
};

void popScope(WGPUDevice device, WGPUInstance instance, ScopeResult* out) {
    WGPUPopErrorScopeCallbackInfo cb = {};
    cb.mode     = WGPUCallbackMode_AllowProcessEvents;
    cb.callback = [](WGPUPopErrorScopeStatus, WGPUErrorType type,
                     WGPUStringView, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<ScopeResult*>(ud1);
        r->done  = true;
        r->error = (type != WGPUErrorType_NoError);
        r->type  = type;
    };
    cb.userdata1 = out;
    wgpuDevicePopErrorScope(device, cb);
    processEventsUntil(instance, &out->done);
}

// Try createBuffer(size). Returns the buffer if successful (caller
// owns and must release), or nullptr otherwise. Captures both OOM
// and Validation error scopes — wgpu-native classifies OOM as
// Validation, so checking only OOM misses the signal.
WGPUBuffer tryAllocate(WGPUInstance instance, WGPUDevice device,
                       uint64_t size, const char* label) {
    wgpuDevicePushErrorScope(device, WGPUErrorFilter_Validation);
    wgpuDevicePushErrorScope(device, WGPUErrorFilter_OutOfMemory);

    WGPUBufferDescriptor desc = {};
    desc.usage        = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
    desc.size         = size;
    desc.label.data   = label;
    desc.label.length = std::strlen(label);
    WGPUBuffer buf = wgpuDeviceCreateBuffer(device, &desc);

    ScopeResult oom, validation;
    popScope(device, instance, &oom);
    popScope(device, instance, &validation);

    if (!buf || oom.error || validation.error) {
        if (buf) wgpuBufferRelease(buf);
        return nullptr;
    }
    return buf;
}

// Returns a std::string so multiple humanSize calls in one printf can
// coexist (static-buffer version had every "%s" point at the same
// last-written buffer).
std::string humanSize(uint64_t b) {
    char buf[32];
    if (b >= (1ull << 30)) std::snprintf(buf, sizeof(buf), "%.2f GB", double(b) / double(1ull << 30));
    else if (b >= (1ull << 20)) std::snprintf(buf, sizeof(buf), "%.1f MB", double(b) / double(1ull << 20));
    else if (b >= (1ull << 10)) std::snprintf(buf, sizeof(buf), "%.1f KB", double(b) / double(1ull << 10));
    else std::snprintf(buf, sizeof(buf), "%llu B", (unsigned long long)b);
    return buf;
}

// Suppress wgpu-native's own logging during probe so the output isn't
// drowned in "[wgpu device error 2]" noise from the OOM attempts that
// the error scopes have already captured.
void onUncapturedError(WGPUDevice const*, WGPUErrorType, WGPUStringView,
                       void*, void*) {
    // intentionally silent
}

}  // namespace

int main() {
    WGPUInstance instance = wgpuCreateInstance(nullptr);
    if (!instance) { std::printf("wgpuCreateInstance failed\n"); return 1; }

    // Request adapter (headless — no surface). HighPerformance for the
    // discrete GPU on hybrid systems.
    struct AdapterReq { WGPUAdapter adapter = nullptr; bool done = false; bool ok = false; };
    AdapterReq areq;
    WGPURequestAdapterOptions opts = {};
    opts.powerPreference = WGPUPowerPreference_HighPerformance;

    WGPURequestAdapterCallbackInfo acb = {};
    acb.mode     = WGPUCallbackMode_AllowProcessEvents;
    acb.callback = [](WGPURequestAdapterStatus status, WGPUAdapter adapter,
                      WGPUStringView, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<AdapterReq*>(ud1);
        r->done = true;
        if (status == WGPURequestAdapterStatus_Success) {
            r->adapter = adapter;
            r->ok = true;
        }
    };
    acb.userdata1 = &areq;
    wgpuInstanceRequestAdapter(instance, &opts, acb);
    while (!areq.done) wgpuInstanceProcessEvents(instance);
    if (!areq.ok) { std::printf("RequestAdapter failed\n"); return 1; }

    // Adapter info.
    WGPUAdapterInfo info = {};
    wgpuAdapterGetInfo(areq.adapter, &info);
    std::printf("Adapter:\n");
    std::printf("  vendor  : %.*s\n", int(info.vendor.length),      info.vendor.data);
    std::printf("  device  : %.*s\n", int(info.device.length),      info.device.data);
    std::printf("  desc    : %.*s\n", int(info.description.length), info.description.data);
    std::printf("  backend : %d\n",   int(info.backendType));
    wgpuAdapterInfoFreeMembers(info);

    WGPULimits alimits = {};
    wgpuAdapterGetLimits(areq.adapter, &alimits);
    std::printf("\nAdapter limits:\n");
    std::printf("  maxBufferSize                = %s\n", humanSize(alimits.maxBufferSize).c_str());
    std::printf("  maxStorageBufferBindingSize  = %s\n", humanSize(alimits.maxStorageBufferBindingSize).c_str());
    std::printf("  maxStorageBuffersPerStage    = %u\n", alimits.maxStorageBuffersPerShaderStage);

    // Request device with adapter's max limits (so we don't artificially
    // restrict ourselves to the WebGPU floor).
    WGPUDeviceDescriptor ddesc = {};
    ddesc.requiredLimits = &alimits;
    ddesc.uncapturedErrorCallbackInfo.callback = onUncapturedError;

    struct DeviceReq { WGPUDevice device = nullptr; bool done = false; bool ok = false; };
    DeviceReq dreq;
    WGPURequestDeviceCallbackInfo dcb = {};
    dcb.mode     = WGPUCallbackMode_AllowProcessEvents;
    dcb.callback = [](WGPURequestDeviceStatus status, WGPUDevice device,
                      WGPUStringView, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<DeviceReq*>(ud1);
        r->done = true;
        if (status == WGPURequestDeviceStatus_Success) {
            r->device = device;
            r->ok = true;
        }
    };
    dcb.userdata1 = &dreq;
    wgpuAdapterRequestDevice(areq.adapter, &ddesc, dcb);
    while (!dreq.done) wgpuInstanceProcessEvents(instance);
    if (!dreq.ok) { std::printf("RequestDevice failed\n"); return 1; }

    WGPULimits dlimits = {};
    wgpuDeviceGetLimits(dreq.device, &dlimits);
    std::printf("\nDevice limits (granted):\n");
    std::printf("  maxBufferSize                = %s\n", humanSize(dlimits.maxBufferSize).c_str());
    std::printf("  maxStorageBufferBindingSize  = %s\n", humanSize(dlimits.maxStorageBufferBindingSize).c_str());

    // ---- Test 1: Single-allocation probe. ------------------------------
    // Try createBuffer at descending sizes, release after each. Tells us
    // the biggest single buffer the driver will grant at all (independent
    // of fragmentation from prior allocations).
    std::printf("\nSingle-allocation probe (each released before next):\n");
    static const uint64_t test_sizes[] = {
        16ull << 30, 8ull << 30, 4ull << 30,
        2ull << 30,  1ull << 30,
        512ull << 20, 256ull << 20, 128ull << 20, 64ull << 20,
    };
    for (uint64_t s : test_sizes) {
        WGPUBuffer b = tryAllocate(instance, dreq.device, s, "probe.single");
        std::printf("  %-10s : %s\n", humanSize(s).c_str(), b ? "OK" : "REFUSED");
        if (b) wgpuBufferRelease(b);
    }

    // ---- Test 2: Cumulative allocation. --------------------------------
    // Keep allocating without releasing, halving the requested size on
    // each refusal. Discovers actual total VRAM the runtime will let us
    // park behind one device. THIS is what determines the upper bound
    // of a multi-sub-buffer streaming pool.
    std::printf("\nCumulative allocation probe (halve on refusal,"
                " stop at 64 MB floor):\n");
    constexpr uint64_t MIN_BYTES = 64ull << 20;
    uint64_t try_size = dlimits.maxBufferSize;
    if (try_size > (4ull << 30)) try_size = 4ull << 30;  // 4 GB sane cap
    std::vector<WGPUBuffer> retained;
    uint64_t total = 0;
    while (try_size >= MIN_BYTES) {
        char label[64];
        std::snprintf(label, sizeof(label), "probe.cum.%zu", retained.size());
        WGPUBuffer b = tryAllocate(instance, dreq.device, try_size, label);
        if (b) {
            retained.push_back(b);
            total += try_size;
            std::printf("  + sub-buffer %2zu : %-9s (cumulative %s, %zu buffers)\n",
                        retained.size() - 1, humanSize(try_size).c_str(),
                        humanSize(total).c_str(), retained.size());
        } else {
            std::printf("  - refused at      %-9s (halving)\n", humanSize(try_size).c_str());
            try_size /= 2;
        }
    }
    std::printf("\nFinal: %zu sub-buffers totalling %s\n",
                retained.size(), humanSize(total).c_str());

    // Release retained buffers.
    for (WGPUBuffer b : retained) wgpuBufferRelease(b);
    retained.clear();
    total = 0;

    // ---- Test 3: Uniform-size cumulative probe. ------------------------
    // Start with a smaller per-buffer size and keep stacking. Tells us
    // whether the "max single size first" strategy leaves total VRAM on
    // the table — e.g. on hardware where 2×2GB is refused but 4×1GB
    // works (heap fragmentation favours smaller allocs).
    static const uint64_t fixed_sizes[] = {
        1ull << 30,       // 1 GB each
        512ull << 20,     // 512 MB each
        256ull << 20,     // 256 MB each
    };
    for (uint64_t fixed : fixed_sizes) {
        std::printf("\nFixed-size %s cumulative probe:\n",
                    humanSize(fixed).c_str());
        std::vector<WGPUBuffer> bufs;
        uint64_t cum = 0;
        for (;;) {
            char label[64];
            std::snprintf(label, sizeof(label), "probe.fixed.%zu", bufs.size());
            WGPUBuffer b = tryAllocate(instance, dreq.device, fixed, label);
            if (!b) break;
            bufs.push_back(b);
            cum += fixed;
        }
        std::printf("  %zu buffers × %s = %s\n",
                    bufs.size(), humanSize(fixed).c_str(),
                    humanSize(cum).c_str());
        for (WGPUBuffer b : bufs) wgpuBufferRelease(b);
    }

    wgpuDeviceRelease(dreq.device);
    wgpuAdapterRelease(areq.adapter);
    wgpuInstanceRelease(instance);
    return 0;
}
