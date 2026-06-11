#include "express.h"
#include "instance_data.h"

const ifcopenshell::declaration& express::Base::declaration() const {
    return *data()->declaration();
}
uint32_t express::Base::identity() const { return data()->identity(); }

uint32_t express::Base::id() const { return data()->id(); }

const instance_data* express::Base::data() const {
#ifdef IFOPSH_SAFE_INSTANCE
    auto sp = data_.lock();
    if (sp) {
        return sp.get();
    } else {
        throw std::runtime_error("Trying to access deleted instance reference");
    }
#else
    return data_;
#endif
}

instance_data* express::Base::data() { 
#ifdef IFOPSH_SAFE_INSTANCE
    auto sp = data_.lock();
    if (sp) {
        return sp.get();
    } else {
        throw std::runtime_error("Trying to access deleted instance reference");
    }
#else
    return data_;
#endif
}
