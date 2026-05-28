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

#include "WgpuStreamingThread.h"

#include "WgpuStreamingLoader.h"

WgpuStreamingThread::~WgpuStreamingThread() {
    stop();
}

void WgpuStreamingThread::start() {
    std::unique_lock lk(mu_);
    if (running_) return;
    shutdown_ = false;
    running_  = true;
    lk.unlock();
    worker_ = std::thread(&WgpuStreamingThread::workerLoop, this);
}

void WgpuStreamingThread::stop() {
    {
        std::unique_lock lk(mu_);
        if (!running_) return;
        shutdown_ = true;
    }
    cv_.notify_all();
    if (worker_.joinable()) worker_.join();
    std::unique_lock lk(mu_);
    running_ = false;
    requests_.clear();
    results_.clear();
}

bool WgpuStreamingThread::enqueue(Request req) {
    {
        std::unique_lock lk(mu_);
        if (!running_ || shutdown_) return false;
        requests_.push_back(std::move(req));
    }
    cv_.notify_one();
    return true;
}

std::vector<WgpuStreamingThread::Result> WgpuStreamingThread::drainResults() {
    std::vector<Result> out;
    {
        std::unique_lock lk(mu_);
        out.reserve(results_.size());
        while (!results_.empty()) {
            out.push_back(std::move(results_.front()));
            results_.pop_front();
        }
    }
    return out;
}

std::size_t WgpuStreamingThread::inFlightApprox() const {
    std::unique_lock lk(mu_);
    return requests_.size() + (in_progress_ ? 1u : 0u);
}

void WgpuStreamingThread::workerLoop() {
    for (;;) {
        Request req;
        {
            std::unique_lock lk(mu_);
            cv_.wait(lk, [this]() { return shutdown_ || !requests_.empty(); });
            if (shutdown_ && requests_.empty()) return;
            req = std::move(requests_.front());
            requests_.pop_front();
            in_progress_ = true;
        }

        // Disk reads happen off-thread. Each Request carries everything
        // the reader needs; the viewport keeps the corresponding chunk
        // marked is_loading so eviction won't yank the slot underneath
        // us. The vbytes / idx buffers are allocated here on the worker
        // thread — they cross back to the main thread when the result
        // is drained and applied (pool.alloc + queueWriteBuffer).
        Result res;
        res.model_id  = req.model_id;
        res.chunk_idx = req.chunk_idx;
        res.success   = true;
        if (!req.v_ranges.empty()) {
            if (!readSidecarVertexRanges(req.file_path,
                                         req.vertex_section_offset,
                                         req.v_ranges, res.vbytes)) {
                res.success = false;
            }
        }
        if (res.success && !req.i_ranges.empty()) {
            if (!readSidecarIndexRanges(req.file_path,
                                        req.index_section_offset,
                                        req.i_ranges, res.idx)) {
                res.success = false;
            }
        }

        {
            std::unique_lock lk(mu_);
            results_.push_back(std::move(res));
            in_progress_ = false;
        }
    }
}
