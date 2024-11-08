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

#include "IfcException.h"

namespace impl {
    // Trait to detect unique_ptr
    template <typename...> struct is_unique_ptr : std::false_type {};
    template<class T, typename... Args>
    struct is_unique_ptr<std::unique_ptr<T, Args...>> : std::true_type {};

    /*
    // Trait to find index of type in parameter pack
    template <typename T, typename... Ts>
    struct TypeIndex;
    template <typename T, typename... Ts>
    struct TypeIndex<T, T, Ts...> : std::integral_constant<std::size_t, 0> {};
    template <typename T, typename U, typename... Ts>
    struct TypeIndex<T, U, Ts...> : std::integral_constant<std::size_t, 1 + TypeIndex<T, Ts...>::value> {};
    template <typename T, typename... Ts>
    constexpr std::size_t TypeIndex_v = TypeIndex<T, Ts...>::value;
    */

    // Trait to find index of type in parameter pack considering inheritance
    template <typename T, typename... Ts>
    struct TypeIndex;

    // Base case: When the first type in the pack is the type we're looking for, or is a base class of it
    template <typename T, typename U, typename... Ts>
    struct TypeIndex<T, U, Ts...>
        : std::integral_constant<std::size_t, (std::is_pointer_v<T> ? std::is_base_of_v<std::remove_pointer_t<U>, std::remove_pointer_t<T>> : std::is_same_v<T, U>) ? 0 :
        (TypeIndex<T, Ts...>::value == std::numeric_limits<std::size_t>::max()
            ? std::numeric_limits<std::size_t>::max()
            : 1 + TypeIndex<T, Ts...>::value)> {};

    // Recursion termination: When the parameter pack is empty
    template <typename T>
    struct TypeIndex<T> : std::integral_constant<std::size_t, std::numeric_limits<std::size_t>::max()> {};

    // Helper variable template
    template <typename T, typename... Ts>
    constexpr std::size_t TypeIndex_v = TypeIndex<T, Ts...>::value;

    // Trait to determine if a type is small enough to be stored directly
    template <typename T>
    struct is_small_object {
        static constexpr bool value = sizeof(T) <= sizeof(void*) * 2;
    };

    // Metafunction to transform T to unique_ptr<T> based on size
    template <typename T>
    struct TransformType {
        using type = typename std::conditional<
            is_small_object<T>::value,
            T,
            std::unique_ptr<T>
        >::type;
    };

    // Helper to prepend a type to a tuple
    template <typename T, typename Tuple>
    struct TuplePrepend;
    template <typename T, typename... Types>
    struct TuplePrepend<T, std::tuple<Types...>> {
        using type = std::tuple<T, Types...>;
    };

    // Map types based on above size transform
    template <typename... Types>
    struct MapTypes;
    template <typename FirstType, typename... RestTypes>
    struct MapTypes<FirstType, RestTypes...> {
        using type = typename TuplePrepend<
            typename TransformType<FirstType>::type,
            typename MapTypes<RestTypes...>::type
        >::type;
    };
    template <>
    struct MapTypes<> {
        using type = std::tuple<>;
    };
    template <typename... Types>
    using MapTypes_t = typename MapTypes<Types...>::type;

    // Create aligned_union from paramater pack stored in tuple for storage in variant
    template <typename T>
    struct make_union_from_tuple {};
    template <typename... Args>
    struct make_union_from_tuple<std::tuple<Args...>> {
        using type = typename std::aligned_union<0, Args...>::type;
    };

}

template<typename... Types>
class VariantArray {
public:
    using TypesTuple = ::impl::MapTypes_t<Types...>;

    VariantArray(size_t size)
        : size_and_indices_(new uint8_t[size + 1])
        , storage_(size ? new StorageType[size] : nullptr)
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

    VariantArray(VariantArray&& other) noexcept
        : size_and_indices_(other.size_and_indices_)
        , storage_(other.storage_)
    {
        other.size_and_indices_ = nullptr;
        other.storage_ = nullptr;
    }

    VariantArray& operator=(VariantArray&& other) noexcept {
        if (this != &other) {
            free_();

            size_and_indices_ = other.size_and_indices_;
            storage_ = other.storage_;

            other.size_and_indices_ = nullptr;
            other.storage_ = nullptr;
        }
        return *this;
    }

    VariantArray(const VariantArray&) = delete;
    VariantArray(const VariantArray&&) = delete;
    VariantArray& operator= (const VariantArray&) = delete;

    template<typename T, typename = std::enable_if_t<!std::is_same_v<std::decay_t<T>, VariantArray>>>
    void set(std::size_t index, T&& value) {
        using U = std::decay_t<T>;
        static_assert(::impl::TypeIndex_v<U, Types...> < sizeof...(Types), "Type not supported by variant");
        if (index >= size_and_indices_[0]) {
            throw std::out_of_range("Index out of range");
        }

        destroy_at_index(index);

        size_and_indices_[index + 1] = ::impl::TypeIndex_v<U, Types...>;
        using V = typename std::tuple_element<::impl::TypeIndex_v<U, Types...>, ::impl::MapTypes_t<Types... >>::type;
        // std::wcout << "setting " << index << " to " << typeid(V).name() << " (" << ::impl::TypeIndex_v<U, Types...> << ")" << std::endl;
        if constexpr (::impl::is_unique_ptr<V>::value) {
            new(&storage_[index]) V(new U(value));
        } else {
            new(&storage_[index]) U(std::forward<T>(value));
        }
    }

    ~VariantArray() {
        free_();
    }

    std::size_t index(std::size_t index) const noexcept {
        return size_and_indices_[index + 1];
    }

    template<typename T>
    T& get(std::size_t index) {
        if (!has<T>(index)) {
            throw std::bad_cast();
        }
        using V = typename std::tuple_element<::impl::TypeIndex_v<T, Types...>, ::impl::MapTypes_t<Types... >>::type;
        if constexpr (::impl::is_unique_ptr<V>::value) {
            return **reinterpret_cast<V*>(&storage_[index]);
        } else {
            return *reinterpret_cast<V*>(&storage_[index]);
        }
    }

    template<typename T>
    bool has(std::size_t index) const {
        return size_and_indices_[index + 1] == ::impl::TypeIndex<T, Types...>::value;
    }

    template<typename T>
    const T& get(std::size_t index) const {
        if (size_and_indices_[index + 1] != ::impl::TypeIndex<T, Types...>::value) {
            // @todo this IfcException is silly. Figure out what
            // to do, but at the moment it is specifically caught
            // in various places.
            throw IfcParse::IfcException(
                "Type held at index " + std::to_string(index) + " is " +
                get_type_name(size_and_indices_[index + 1]) + " and not " + typeid(T).name()
            );
        }
        using V = typename std::tuple_element<::impl::TypeIndex_v<T, Types...>, ::impl::MapTypes_t<Types... >>::type;
        if constexpr (::impl::is_unique_ptr<V>::value) {
            return **reinterpret_cast<const V*>(&storage_[index]);
        } else {
            return *reinterpret_cast<const V*>(&storage_[index]);
        }
    }

    template<typename Visitor>
    auto apply_visitor(Visitor&& visitor, std::size_t index) const {
        return apply_visitor_impl(std::forward<Visitor>(visitor), index, std::integral_constant<std::size_t, sizeof...(Types)>{});
    }

    auto size() const {
        return size_and_indices_ ? size_and_indices_[0] : 0;
    }

private:
    using StorageType = typename ::impl::make_union_from_tuple<::impl::MapTypes_t<Types...>>::type;

    uint8_t* size_and_indices_;
    StorageType* storage_;

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
            using T = typename std::tuple_element_t<Index - 1, ::impl::MapTypes_t<Types...>>;
            if constexpr (!std::is_trivially_destructible<T>::value) {
                reinterpret_cast<T*>(&storage_[index])->~T();
            }
            size_and_indices_[index + 1] = sizeof...(Types);
        } else {
            destroy_type_at_index(index, std::integral_constant<std::size_t, Index - 1>{});
        }
    }

    void destroy_type_at_index(std::size_t, std::integral_constant<std::size_t, 0>) {}

    template<typename Visitor, std::size_t Index>
    auto apply_visitor_impl(Visitor&& visitor, std::size_t idx, std::integral_constant<std::size_t, Index>) const {
        if (size_and_indices_[idx + 1] == Index - 1) {
            using T = typename std::tuple_element_t<Index - 1, ::impl::MapTypes_t<Types...>>;
            if constexpr (::impl::is_unique_ptr<T>::value) {
                return visitor(**reinterpret_cast<T*>(&storage_[idx]));
            } else {
                return visitor(*reinterpret_cast<T*>(&storage_[idx]));
            }
        }
        return apply_visitor_impl(std::forward<Visitor>(visitor), idx, std::integral_constant<std::size_t, Index - 1>{});
    }

    template<typename Visitor>
    auto apply_visitor_impl(Visitor&&, std::size_t, std::integral_constant<std::size_t, 0>) const {
        throw std::runtime_error("Invalid variant index");
        if constexpr (!std::is_void_v<decltype(std::declval<Visitor>()(std::declval<typename std::tuple_element_t<0, ::impl::MapTypes_t<Types...>> &>()))>) {
            return decltype(std::declval<Visitor>()(std::declval<typename std::tuple_element_t<0, ::impl::MapTypes_t<Types...>> &>())){};
        }
    }

    template <size_t I>
    const char* get_type_name_impl(size_t i) const {
        if constexpr (I == 0) {
            return "";
        } else {
            if (i == I - 1) {
                return typeid(std::tuple_element_t<I - 1, std::tuple<Types...>>).name();
            } else {
                return get_type_name_impl<I - 1>(i);
            }
        }
    }

    const char* get_type_name(size_t i) const {
        return get_type_name_impl<sizeof...(Types)>(i);
    }
};

#endif