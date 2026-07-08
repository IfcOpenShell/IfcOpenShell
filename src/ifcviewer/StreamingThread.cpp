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

#include "StreamingThread.h"

#include "StreamingLoader.h"

StreamingThread::~StreamingThread() {
    stop();
}

void StreamingThread::start() {
    std::unique_lock lock(mu_);
    if (running_) return;
    shutdown_ = false;
    running_  = true;
    lock.unlock();
    worker_ = std::thread(&StreamingThread::workerLoop, this);
}

void StreamingThread::stop() {
    {
        std::unique_lock lock(mu_);
        if (!running_) return;
        shutdown_ = true;
    }
    cv_.notify_all();
    if (worker_.joinable()) worker_.join();
    std::unique_lock lock(mu_);
    running_ = false;
    requests_.clear();
    results_.clear();
}

bool StreamingThread::enqueue(Request req) {
    {
        std::unique_lock lock(mu_);
        if (!running_ || shutdown_) return false;
        requests_.push_back(std::move(req));
    }
    cv_.notify_one();
    return true;
}

std::vector<StreamingThread::Result> StreamingThread::drainResults() {
    std::vector<Result> results;
    {
        std::unique_lock lock(mu_);
        results.reserve(results_.size());
        while (!results_.empty()) {
            results.push_back(std::move(results_.front()));
            results_.pop_front();
        }
    }
    return results;
}

std::size_t StreamingThread::inFlightApprox() const {
    std::unique_lock lock(mu_);
    return requests_.size() + (in_progress_ ? 1u : 0u);
}

void StreamingThread::workerLoop() {
    for (;;) {
        Request req;
        {
            std::unique_lock lock(mu_);
            cv_.wait(lock, [this]() { return shutdown_ || !requests_.empty(); });
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
        Result result;
        result.session_model_id  = req.session_model_id;
        result.chunk_idx = req.chunk_idx;
        result.success   = readChunkGeometryCompressed(
            req.file_path, req.geometry_section_offset,
            req.v_comp_off, req.v_comp_size, req.v_raw_size,
            req.i_comp_off, req.i_comp_size, req.i_raw_size,
            result.vbytes, result.idx);

        {
            std::unique_lock lock(mu_);
            results_.push_back(std::move(result));
            in_progress_ = false;
        }
    }
}
