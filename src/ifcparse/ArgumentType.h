#ifndef ARGUMENTTYPE_H
#define ARGUMENTTYPE_H

namespace IfcUtil {
    enum ArgumentType {
        Argument_INT, Argument_BOOL, Argument_DOUBLE, Argument_STRING, Argument_VECTOR_INT, Argument_VECTOR_DOUBLE, Argument_VECTOR_STRING, Argument_ENTITY, Argument_ENTITY_LIST, Argument_ENUMERATION, Argument_UNKNOWN
    };
}

#endif