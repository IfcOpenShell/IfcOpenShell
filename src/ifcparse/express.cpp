#include "express.h"
#include "InstanceData.h"

const IfcParse::declaration& express::Base::declaration() const {
    return *data()->declaration();
}
uint32_t express::Base::identity() const { return data()->identity(); }

uint32_t express::Base::id() const { return data()->id(); }

const InstanceData* express::Base::data() const {
    auto sp = data_.lock();
    if (sp) {
        return sp.get();
    } else {
        throw std::runtime_error("Trying to access deleted instance reference");
    }
}

InstanceData* express::Base::data() { 
    auto sp = data_.lock();
    if (sp) {
        return sp.get();
    } else {
        throw std::runtime_error("Trying to access deleted instance reference");
    }
}
