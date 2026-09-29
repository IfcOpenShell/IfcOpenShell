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


#include "GpuMemory.h"

#include <cstdio>
#include <cstring>
#include <string>

#if defined(__linux__) && !defined(__EMSCRIPTEN__)
#include <dirent.h>
#include <dlfcn.h>
#endif

namespace ifcviewer {
namespace {

#if defined(__linux__) && !defined(__EMSCRIPTEN__)

// NVML, loaded at run time rather than linked: the viewer must run on machines
// with no NVIDIA driver at all, so a link-time dependency is not an option.
// Only the four entry points needed here are resolved.
struct Nvml {
    void* handle = nullptr;
    int  (*init)()                                              = nullptr;
    int  (*shutdown)()                                          = nullptr;
    int  (*device_count)(unsigned*)                             = nullptr;
    int  (*handle_by_index)(unsigned, void**)                   = nullptr;
    int  (*pci_info)(void*, void*)                              = nullptr;
    int  (*memory_info)(void*, unsigned long long*)             = nullptr;

    bool load() {
        // .so.1 first: the unversioned name is part of the -dev package and is
        // frequently absent on user machines.
        for (const char* name : {"libnvidia-ml.so.1", "libnvidia-ml.so"}) {
            handle = dlopen(name, RTLD_LAZY | RTLD_LOCAL);
            if (handle) break;
        }
        if (!handle) return false;
        auto sym = [&](const char* n) { return dlsym(handle, n); };
        init            = (int (*)())sym("nvmlInit_v2");
        shutdown        = (int (*)())sym("nvmlShutdown");
        device_count    = (int (*)(unsigned*))sym("nvmlDeviceGetCount_v2");
        handle_by_index = (int (*)(unsigned, void**))sym("nvmlDeviceGetHandleByIndex_v2");
        pci_info        = (int (*)(void*, void*))sym("nvmlDeviceGetPciInfo_v3");
        memory_info     = (int (*)(void*, unsigned long long*))sym("nvmlDeviceGetMemoryInfo");
        return init && shutdown && device_count && handle_by_index && memory_info;
    }
    ~Nvml() { if (handle) dlclose(handle); }
};

// nvmlPciInfo_t. Only pciDeviceId is read; the leading char arrays are sized
// from the NVML headers so the offset is right.
struct NvmlPciInfo {
    char busIdLegacy[16];
    unsigned domain;
    unsigned bus;
    unsigned device;
    unsigned pciDeviceId;      // (device_id << 16) | vendor_id
    unsigned pciSubSystemId;
    char busId[32];
};

bool queryNvml(std::uint32_t vendor_id, std::uint32_t device_id, GpuMemoryInfo& out) {
    Nvml nvml;
    if (!nvml.load()) return false;
    if (nvml.init() != 0) return false;

    unsigned count = 0;
    bool found = false;
    if (nvml.device_count(&count) == 0) {
        for (unsigned i = 0; i < count && !found; ++i) {
            void* dev = nullptr;
            if (nvml.handle_by_index(i, &dev) != 0 || !dev) continue;

            // Match the card wgpu picked. With a single NVIDIA device and no
            // way to read its ids, fall through to it rather than reporting
            // nothing -- a slightly uncertain number beats none.
            if (nvml.pci_info && (vendor_id || device_id)) {
                NvmlPciInfo pci{};
                if (nvml.pci_info(dev, &pci) == 0) {
                    const unsigned dev_id = (pci.pciDeviceId >> 16) & 0xFFFF;
                    const unsigned ven_id = pci.pciDeviceId & 0xFFFF;
                    if (device_id && dev_id != device_id) continue;
                    if (vendor_id && ven_id != vendor_id) continue;
                }
            } else if (count != 1) {
                continue;
            }

            // nvmlMemory_t: { total, free, used }, all unsigned long long.
            //
            // This reports more `used` than nvidia-smi does -- measured here,
            // 1427 MiB against 1046 MiB, consistently -- because the v1 call
            // folds driver-reserved memory into `used` where nvidia-smi
            // accounts for it separately. The larger figure is the one worth
            // having: what actually allocated on this card topped out around
            // 2431 MB, against 2669 MB free by this measure and 3050 MB by
            // nvidia-smi's. Budgeting against the optimistic number would
            // promise memory that is not there.
            unsigned long long mem[3] = {0, 0, 0};
            if (nvml.memory_info(dev, mem) == 0 && mem[0] > 0) {
                out.total_bytes = mem[0];
                out.used_bytes  = mem[2];
                out.valid       = true;
                found           = true;
            }
        }
    }
    nvml.shutdown();
    return found;
}

// amdgpu and i915 expose VRAM through sysfs. Reads every card and keeps the
// one whose vendor/device ids match, because the first card is often the
// integrated GPU rather than the one in use.
bool readUint64(const std::string& path, std::uint64_t& out) {
    FILE* f = std::fopen(path.c_str(), "r");
    if (!f) return false;
    unsigned long long v = 0;
    const bool ok = std::fscanf(f, "%llu", &v) == 1;
    std::fclose(f);
    if (ok) out = v;
    return ok;
}

bool readHexId(const std::string& path, std::uint32_t& out) {
    FILE* f = std::fopen(path.c_str(), "r");
    if (!f) return false;
    unsigned v = 0;
    const bool ok = std::fscanf(f, "0x%x", &v) == 1;
    std::fclose(f);
    if (ok) out = v;
    return ok;
}

bool querySysfs(std::uint32_t vendor_id, std::uint32_t device_id, GpuMemoryInfo& out) {
    DIR* dir = opendir("/sys/class/drm");
    if (!dir) return false;
    bool found = false;
    while (dirent* entry = readdir(dir)) {
        const std::string name = entry->d_name;
        // "card0", not "card0-DP-1".
        if (name.rfind("card", 0) != 0 || name.find('-') != std::string::npos) continue;
        const std::string base = "/sys/class/drm/" + name + "/device/";

        std::uint32_t ven = 0, dev = 0;
        if (vendor_id && readHexId(base + "vendor", ven) && ven != vendor_id) continue;
        if (device_id && readHexId(base + "device", dev) && dev != device_id) continue;

        std::uint64_t total = 0, used = 0;
        if (readUint64(base + "mem_info_vram_total", total) && total > 0) {
            readUint64(base + "mem_info_vram_used", used);
            out.total_bytes = total;
            out.used_bytes  = used;
            out.valid       = true;
            found           = true;
            break;
        }
    }
    closedir(dir);
    return found;
}

#endif  // __linux__ && !__EMSCRIPTEN__

}  // namespace

GpuMemoryInfo queryGpuMemory(std::uint32_t vendor_id, std::uint32_t device_id) {
    GpuMemoryInfo info;
#if defined(__linux__) && !defined(__EMSCRIPTEN__)
    if (queryNvml(vendor_id, device_id, info)) return info;
    if (querySysfs(vendor_id, device_id, info)) return info;
#else
    // Windows (DXGI QueryVideoMemoryInfo) and macOS
    // (recommendedMaxWorkingSetSize) both expose this; not implemented here
    // because neither can be verified from this machine. `valid` stays false,
    // and callers fall back to behaving as they did before.
    (void)vendor_id; (void)device_id;
#endif
    return info;
}

}  // namespace ifcviewer
