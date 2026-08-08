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

/*
A dynamic sequence of variant types arranged in a way to reduce size impact due
to alignment by grouping the 1 byte type indices. Using heap allocation - hence
storing a pointer instead - for larger types so that the overall size of the
variant - which is the maximum size of its constituents - is reduced.
*/

#ifndef VARIANTARRAY_H
#define VARIANTARRAY_H

#include <iostream>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <memory>
#include <tuple>
#include <cstdint>
#include <cstring>
#include <cstddef>
#include <limits>
#include <exception>

namespace impl {
    class storage_type_mismatch : public std::exception {
      private:
        std::string requested_, actual__, message_;

      public:
        storage_type_mismatch(const std::string& requested, const std::string& actual)
            : requested_(requested), actual__(actual), message_("Requested type " + requested_ + " does not match actual type " + actual__) {}

        const char* what() const noexcept override {
            return message_.c_str();
        }

        const std::string& requested() const { return requested_; }
        const std::string& actual() const { return actual__; }
    };

    template <typename T>
    struct variant_type_name;

    // Trait to detect unique_ptr
    template <typename...> struct is_unique_ptr : std::false_type {};
    template<class T, typename... Args>
    struct is_unique_ptr<std::unique_ptr<T, Args...>> : std::true_type {};

    // Trait to find index of type in parameter pack considering inheritance
    template <typename T, typename... Ts>
    struct type_index;

    // Base case: When the first type in the pack is the type we're looking for, or is a base class of it
    template <typename T, typename U, typename... Ts>
    struct type_index<T, U, Ts...>
        : std::integral_constant<std::size_t, (std::is_pointer_v<T> ? std::is_base_of_v<std::remove_pointer_t<U>, std::remove_pointer_t<T>> : std::is_same_v<T, U>) ? 0 :
        (type_index<T, Ts...>::value == std::numeric_limits<std::size_t>::max()
            ? std::numeric_limits<std::size_t>::max()
            : 1 + type_index<T, Ts...>::value)> {};

    // Recursion termination: When the parameter pack is empty
    template <typename T>
    struct type_index<T> : std::integral_constant<std::size_t, std::numeric_limits<std::size_t>::max()> {};

    // Helper variable template
    template <typename T, typename... Ts>
    constexpr std::size_t TypeIndex_v = type_index<T, Ts...>::value;

    // Trait to determine if a type is small enough to be stored directly
    template <typename T>
    struct is_small_object {
        static constexpr bool value = sizeof(T) <= sizeof(void*) * 2;
    };

    // Metafunction to transform T to unique_ptr<T> based on size
    template <typename T>
    struct transform_type {
        using type = typename std::conditional<
            is_small_object<T>::value,
            T,
            std::unique_ptr<T>
        >::type;
    };

    // Helper to prepend a type to a tuple
    template <typename T, typename Tuple>
    struct tuple_prepend;
    template <typename T, typename... Types>
    struct tuple_prepend<T, std::tuple<Types...>> {
        using type = std::tuple<T, Types...>;
    };

    // Map types based on above size transform
    template <typename... Types>
    struct map_types;
    template <typename FirstType, typename... RestTypes>
    struct map_types<FirstType, RestTypes...> {
        using type = typename tuple_prepend<
            typename transform_type<FirstType>::type,
            typename map_types<RestTypes...>::type
        >::type;
    };
    template <>
    struct map_types<> {
        using type = std::tuple<>;
    };
    template <typename... Types>
    using map_types_t = typename map_types<Types...>::type;

    // Create aligned_union from paramater pack stored in tuple for storage in variant
    template <typename T>
    struct make_union_from_tuple {};
    template <typename... Args>
    struct make_union_from_tuple<std::tuple<Args...>> {
        using type = typename std::aligned_union<0, Args...>::type;
    };

}

template<typename... Types>
class variant_array {
public:
    using types_tuple = ::impl::map_types_t<Types...>;

    variant_array(size_t size)
        : size_and_indices_(size ? new uint8_t[size + 1] : nullptr)
        , storage_(size ? new storage_type[size] : nullptr)
    {
        if (size) {
            size_and_indices_[0] = (uint8_t)size;
            memset(size_and_indices_ + 1, 0, sizeof(uint8_t) * size);
            for (size_t i = 0; i < size; ++i) {
                // type 0 needs to be default constructable
                set(i, typename std::tuple_element<0, std::tuple<Types...>>::type{});
            }
        }
    }

    variant_array(variant_array&& other) noexcept
        : size_and_indices_(other.size_and_indices_)
        , storage_(other.storage_)
    {
        other.size_and_indices_ = nullptr;
        other.storage_ = nullptr;
    }

    variant_array& operator=(variant_array&& other) noexcept {
        if (this != &other) {
            free_();

            size_and_indices_ = other.size_and_indices_;
            storage_ = other.storage_;

            other.size_and_indices_ = nullptr;
            other.storage_ = nullptr;
        }
        return *this;
    }

    variant_array(const variant_array& other) = delete;
    variant_array(const variant_array&& other) = delete;
    variant_array& operator= (const variant_array& other) = delete;

    template<typename T, typename = std::enable_if_t<!std::is_same_v<std::decay_t<T>, variant_array>>>
    void set(std::size_t index, T&& value) {
        using u = std::decay_t<T>;
        static_assert(::impl::TypeIndex_v<u, Types...> < sizeof...(Types), "Type not supported by variant");
        if (index >= size()) {
            throw std::out_of_range("Index " + std::to_string(index) + " is out of range for storage of size " + std::to_string(size()));
        }

        destroy_at_index(index);

        size_and_indices_[index + 1] = ::impl::TypeIndex_v<u, Types...>;
        using v = typename std::tuple_element<::impl::TypeIndex_v<u, Types...>, ::impl::map_types_t<Types... >>::type;
        if constexpr (::impl::is_unique_ptr<v>::value) {
            new(&storage_[index]) v(new u(value));
        } else {
            new(&storage_[index]) u(std::forward<T>(value));
        }
    }

    ~variant_array() {
        free_();
    }

    std::size_t index(std::size_t index) const {
        if (index >= size()) {
            throw std::out_of_range(
                "Index " + std::to_string(index) + " is out of range for storage of size " + std::to_string(size())
            );
        }
        return size_and_indices_[index + 1];
    }

    template<typename T>
    T& get(std::size_t index) {
        if (index >= size()) {
            throw std::out_of_range(
                "Index " + std::to_string(index) + " is out of range for storage of size " + std::to_string(size())
            );
        }
        if (!has<T>(index)) {
            throw std::bad_cast();
        }
        using v = typename std::tuple_element<::impl::TypeIndex_v<T, Types...>, ::impl::map_types_t<Types... >>::type;
        if constexpr (::impl::is_unique_ptr<v>::value) {
            return **reinterpret_cast<v*>(&storage_[index]);
        } else {
            return *reinterpret_cast<v*>(&storage_[index]);
        }
    }

    template<typename T>
    bool has(std::size_t index) const {
        return index < size() && size_and_indices_[index + 1] == ::impl::type_index<T, Types...>::value;
    }

    template<typename T>
    const T& get(std::size_t index) const {
        if (index >= size()) {
            throw std::out_of_range(
				"Index " + std::to_string(index) + " is out of range for storage of size " + std::to_string(size())
            );
        }
        if (size_and_indices_[index + 1] != ::impl::type_index<T, Types...>::value) {
            // @todo this exception is silly. Figure out what
            // to do, but at the moment it is specifically caught
            // in various places.
            throw impl::storage_type_mismatch(
                ::impl::variant_type_name<T>::get(), get_type_name(size_and_indices_[index + 1])
            );
        }
        using v = typename std::tuple_element<::impl::TypeIndex_v<T, Types...>, ::impl::map_types_t<Types... >>::type;
        if constexpr (::impl::is_unique_ptr<v>::value) {
            return **reinterpret_cast<const v*>(&storage_[index]);
        } else {
            return *reinterpret_cast<const v*>(&storage_[index]);
        }
    }

    template<typename Visitor>
    auto apply_visitor(Visitor&& visitor, std::size_t index) const {
        if (index >= size()) {
            throw std::out_of_range(
                "Index " + std::to_string(index) + " is out of range for storage of size " + std::to_string(size())
            );
        }
        return apply_visitor_impl(std::forward<Visitor>(visitor), index, std::integral_constant<std::size_t, sizeof...(Types)>{});
    }

    size_t size() const {
        return size_and_indices_ ? size_and_indices_[0] : 0;
    }

private:
    using storage_type = typename ::impl::make_union_from_tuple<::impl::map_types_t<Types...>>::type;

    uint8_t* size_and_indices_;
    storage_type* storage_;

    void destroy_at_index(std::size_t index) {
        destroy_type_at_index(index, std::integral_constant<std::size_t, sizeof...(Types)>{});
    }

    void free_() {
        if (size_and_indices_) {
            for (std::size_t i = 0; i < size_and_indices_[0]; ++i) {
                destroy_at_index(i);
            }
            delete[] size_and_indices_;
            delete[] storage_;
        }
    }

    template<std::size_t Index>
    void destroy_type_at_index(std::size_t index, std::integral_constant<std::size_t, Index>) {
        if (size_and_indices_[index + 1] == Index - 1) {
            using t = typename std::tuple_element_t<Index - 1, ::impl::map_types_t<Types...>>;
            if constexpr (!std::is_trivially_destructible<t>::value) {
                reinterpret_cast<t*>(&storage_[index])->~t();
            }
            size_and_indices_[index + 1] = sizeof...(Types);
        } else {
            destroy_type_at_index(index, std::integral_constant<std::size_t, Index - 1>{});
        }
    }

    void destroy_type_at_index(std::size_t index, std::integral_constant<std::size_t, 0>) {
        static_cast<void>(index);
    }

    template<typename Visitor, std::size_t Index>
    auto apply_visitor_impl(Visitor&& visitor, std::size_t index, std::integral_constant<std::size_t, Index>) const {
        if (size_and_indices_[index + 1] == Index - 1) {
            using t = typename std::tuple_element_t<Index - 1, ::impl::map_types_t<Types...>>;
            if constexpr (::impl::is_unique_ptr<t>::value) {
                return visitor(**reinterpret_cast<t*>(&storage_[index]));
            } else {
                return visitor(*reinterpret_cast<t*>(&storage_[index]));
            }
        }
        return apply_visitor_impl(std::forward<Visitor>(visitor), index, std::integral_constant<std::size_t, Index - 1>{});
    }

    template<typename Visitor>
    auto apply_visitor_impl(Visitor&& visitor, std::size_t index, std::integral_constant<std::size_t, 0>) const {
        static_cast<void>(visitor);
        static_cast<void>(index);
        throw std::runtime_error("Invalid variant index");
        if constexpr (!std::is_void_v<decltype(std::declval<Visitor>()(std::declval<typename std::tuple_element_t<0, ::impl::map_types_t<Types...>> &>()))>) {
            return decltype(std::declval<Visitor>()(std::declval<typename std::tuple_element_t<0, ::impl::map_types_t<Types...>> &>())){};
        }
    }

    template <size_t I>
    std::string get_type_name_impl(size_t type_index) const {
        if constexpr (I == 0) {
            return "";
        } else {
            if (type_index == I - 1) {
                return ::impl::variant_type_name<std::tuple_element_t<I - 1, std::tuple<Types...>>>::get();
            } else {
                return get_type_name_impl<I - 1>(type_index);
            }
        }
    }

    std::string get_type_name(size_t type_index) const {
        return get_type_name_impl<sizeof...(Types)>(type_index);
    }
};

#endif
