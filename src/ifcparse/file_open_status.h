#ifndef FILE_OPEN_STATUS_H
#define FILE_OPEN_STATUS_H

#include "ifc_parse_api.h"

namespace IfcParse {

    class IFC_PARSE_API file_open_status {
    public:
        enum file_open_enum {
            SUCCESS,
            READ_ERROR,
            NO_HEADER,
            UNSUPPORTED_SCHEMA,
            INVALID_SYNTAX,
            UNKNOWN
        };

    private:
        file_open_enum error_;

    public:
        file_open_status(file_open_enum error = UNKNOWN)
            : error_(error) {
        }

        operator file_open_enum() const {
            return error_;
        }

        file_open_enum value() const {
            return error_;
        }

        operator bool() const {
            return error_ == SUCCESS;
        }
    };

}

#endif // !FILE_OPEN_STATUS_H
