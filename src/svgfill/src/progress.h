/***************************************************************************
/*                                                                         *
/* Copyright 2021 AECgeeks                                                 *
/*                                                                         *
/* Permission is hereby granted, free of charge, to any person obtaining a *
/* copy of this software and associated documentation files (the           *
/* "Software"), to deal in the Software without restriction, including     *
/* without limitation the rights to use, copy, modify, merge, publish,     *
/* distribute, sublicense, and/or sell copies of the Software, and to      *
/* permit persons to whom the Software is furnished to do so, subject to   *
/* the following conditions:                                               *
/*                                                                         *
/* The above copyright notice and this permission notice shall be included *
/* in all copies or substantial portions of the Software.                  *
/*                                                                         *
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS *
/* OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF              *
/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  *
/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY    *
/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,    *
/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE       *
/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                  *
/*                                                                         *
/***************************************************************************/

// A trivial C++ progress bar

#ifndef PROGRESS_H
#define PROGRESS_H

#include <string>
#include <ostream>
#include <iostream>
#include <vector>
#include <functional>
#include <numeric>

class progress_bar {
	std::ostream& s_;
	float max_;
	size_t width_;
	size_t* last_emitted_p_ = nullptr;

public:
	enum style {
		BAR, DOTS
	};

private:
	style style_;

public:
	progress_bar(std::ostream& s = std::cerr, style st = BAR, float max = 1., size_t width = 50)
		: s_(s)
		, max_(max)
		, width_(st == BAR ? width : 100U)
		, style_(st)
	{}

	void operator()(size_t p) {
		if (last_emitted_p_ && p <= *last_emitted_p_) {
			return;
		}

		p = p > width_ ? width_ : p;
		if (style_ == BAR) {
			s_ << "\r[" + std::string(p, '#') + std::string(width_ - p, ' ') + "]" << std::flush;
		} else {
			s_ << std::string(p - (last_emitted_p_ ? *last_emitted_p_ : 0U), '.') << std::flush;
		}

		if (last_emitted_p_) {
			*last_emitted_p_ = p;
		}
		else {
			last_emitted_p_ = new size_t(p);
		}
	}

	void operator()(float p) {
		(*this)((size_t) (p / max_ * width_));
	}

	~progress_bar() {
		delete last_emitted_p_;
	}
};

class application_progress {
	std::vector<float> estimates_;
	size_t phase_ = 0;
	std::function<void(float)> callback_;
	float total_;

public:
	void operator()(float p) {
		auto progress = std::accumulate(estimates_.begin(), estimates_.begin() + phase_, 0.f);
		progress += p * estimates_[phase_];
		callback_(progress / total_);
	}

	application_progress(const std::vector<float>& estimates, const std::function<void(float)>& callback)
		: estimates_(estimates)
		, callback_(callback)
	{
		total_ = std::accumulate(estimates_.begin(), estimates_.end(), 0.f);
		(*this)(0.);
	}	

	void finished() {
		++phase_;
		(*this)(0.);
	}

	~application_progress() {
		phase_ = estimates_.size() - 2;
		finished();
	}

};

#endif