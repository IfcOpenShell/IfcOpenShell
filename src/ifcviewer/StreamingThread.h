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

#ifndef WGPUSTREAMINGTHREAD_H
#define WGPUSTREAMINGTHREAD_H

#include <condition_variable>
#include <cstdint>
#include <deque>
#include <mutex>
#include <string>
#include <thread>
#include <utility>
#include <vector>

// Worker thread for scatter-gather chunk reads. Decouples disk I/O
// (~tens of ms per chunk on SSD, hundreds on slower media) from the
// render thread. The viewport's per-frame driveStreamingLoads enqueues
// requests for non-resident-frustum-visible chunks, drains any
// completed Results on subsequent frames, and only performs the
// GPU-side (pool.alloc + queueWriteBuffer + bind-group build) work
// on the main thread — wgpu queue ops aren't thread-safe.
//
// Lifetime: start() spawns the worker; stop() signals shutdown and
// joins. The Result destructor releases its byte vectors back to the
// heap, so dropping unclaimed Results (e.g. when their model was
// unloaded mid-flight) is a free operation.
class StreamingThread {
public:
    struct Request {
        uint32_t     session_model_id;
        std::size_t  chunk_idx;
        std::string  file_path;
        // v16: the chunk's two zstd frames in the geometry section. The reader
        // fetches [geometry_section_offset + *_comp_off, +*_comp_size) and
        // decompresses to *_raw_size.
        uint64_t     geometry_section_offset = 0;
        uint64_t     v_comp_off = 0, v_comp_size = 0, v_raw_size = 0;
        uint64_t     i_comp_off = 0, i_comp_size = 0, i_raw_size = 0;
    };

    struct Result {
        uint32_t              session_model_id;
        std::size_t           chunk_idx;
        bool                  success;
        std::vector<uint8_t>  vbytes;
        std::vector<uint32_t> idx;
    };

    ~StreamingThread();

    // Spawn the worker thread. Safe to call once; subsequent calls are
    // no-ops while the worker is alive.
    void start();
    // Signal shutdown, wake the worker, join. Idempotent. Must be
    // called before the BufferPool the results would upload into
    // is destroyed.
    void stop();

    // Enqueue a request. Returns false if the worker has stopped.
    bool enqueue(Request req);
    // Move all completed results out of the result queue. Always
    // non-blocking; if nothing is ready, returns an empty vector.
    std::vector<Result> drainResults();

    // Approximate count of requests still in flight (in queue or
    // currently being processed). Useful for the bench warm gate to
    // know when streaming has truly settled.
    std::size_t inFlightApprox() const;

private:
    void workerLoop();

    std::thread             worker_;
    mutable std::mutex      mu_;
    std::condition_variable cv_;
    std::deque<Request>     requests_;
    std::deque<Result>      results_;
    bool                    in_progress_ = false;
    bool                    shutdown_    = false;
    bool                    running_     = false;
};

#endif  // WGPUSTREAMINGTHREAD_H
