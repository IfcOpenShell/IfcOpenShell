// This file was generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later
#include "ifcopenshell_api_internal.hpp"

#include <cmath>
#include <emscripten/bind.h>
#include <limits>

namespace {
using emscripten::val;
using settings = ifcopenshell::geom::settings;

template <typename T>
T from_js(const val& value) {
    const auto type = value.typeOf().as<std::string>();
    if constexpr (std::is_same_v<T, bool>) {
        if (type != "boolean") {
            throw std::runtime_error("Expected boolean");
        }
        return value.as<bool>();
    } else if constexpr (std::is_enum_v<T>) {
        return static_cast<T>(from_js<int>(value));
    } else if constexpr (std::is_same_v<T, int> || std::is_same_v<T, double>) {
        if (type != "number") {
            throw std::runtime_error("Expected number");
        }
        const double number = value.as<double>();
        if constexpr (std::is_same_v<T, int>) {
            if (!std::isfinite(number) || std::trunc(number) != number ||
                number < std::numeric_limits<int>::min() || number > std::numeric_limits<int>::max()) {
                throw std::runtime_error("Expected int32");
            }
        }
        return static_cast<T>(number);
    } else if constexpr (std::is_same_v<T, std::string>) {
        if (type != "string") {
            throw std::runtime_error("Expected string");
        }
        return value.as<std::string>();
    } else {
        if (!val::global("Array").call<bool>("isArray", value)) {
            throw std::runtime_error("Expected array");
        }
        T result;
        const auto size = value["length"].as<unsigned>();
        for (unsigned i = 0; i < size; ++i) {
            result.insert(result.end(), from_js<typename T::value_type>(value[i]));
        }
        return result;
    }
}

template <typename T>
val to_js(const T& value) {
    if constexpr (std::is_enum_v<T>) {
        return val(static_cast<int>(value));
    } else if constexpr (std::is_arithmetic_v<T> || std::is_same_v<T, std::string>) {
        return val(value);
    } else {
        auto result = val::array();
        for (const auto& item : value) {
            result.call<void>("push", to_js(item));
        }
        return result;
    }
}

template <std::size_t I = 0>
void set_value(settings& target, const std::string& name, const val& value) {
    using option = std::tuple_element_t<I, settings::settings_tuple>;
    if (name == option::name) {
        target.set(name, from_js<typename option::base_type>(value));
    } else if constexpr (I + 1 < std::tuple_size_v<settings::settings_tuple>) {
        set_value<I + 1>(target, name, value);
    } else {
        throw std::runtime_error("Setting not available: " + name);
    }
}

void write_setting(uintptr_t ptr, const std::string& name, const val& value) {
    try {
        set_value(*reinterpret_cast<ifcopenshell_geom_settings_t*>(ptr)->ptr, name, value);
    } catch (const std::exception& error) {
        val::global("TypeError").new_(std::string(error.what())).throw_();
    }
}

val read_setting(uintptr_t ptr, const std::string& name) {
    try {
        return std::visit([](const auto& value) { return to_js(value); },
                          reinterpret_cast<ifcopenshell_geom_settings_t*>(ptr)->ptr->get(name));
    } catch (const std::exception& error) {
        val::global("Error").new_(std::string(error.what())).throw_();
        return val::undefined();
    }
}
} // namespace

EMSCRIPTEN_BINDINGS(ifcopenshell_settings_values) {
    emscripten::function("setSettingFromJs", &write_setting);
    emscripten::function("settingToJs", &read_setting);
}
