from enum import Enum

URL_NAME_CONTRACTEN_UPLOAD = "contracten_upload"


#
# STATUS VALUES
#
class FileStatus(Enum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"
    OK = "OK"

# ROW STATISTICS

TOTAL_ROWS_RECEIVED = "TOTAL_ROWS_RECEIVED"
TOTAL_DATA_ROWS_RECEIVED = "TOTAL_DATA_ROWS_RECEIVED"

class RowStatus(Enum):
    EMPTY_ROW = "EMPTY_ROW"
    HEADER_ROW = "HEADER_OK"

    DATA_OK = "DATA_OK"
    DATA_ERROR = "DATA_ERROR"
    DATA_WARNING = "DATA_WARNING"
    DATA_IGNORED = "DATA_IGNORED"

    def is_data_row(self):
        return self.name.startswith("DATA")
#
# INTERFACE TYPES
#
INTERFACE_TYPE_FILE = "FILE"
INTERFACE_TYPE_API = "API"

#
# SYSTEM
#
NEGOMETRIX = "Negometrix"
CONTRACTEN = "Contracten"
UNKNOWN = "UNKNOWN"
#
# DATA_ERROR MESSAGES
#
ERROR_MSG_FILE_DEFINITION_ERROR = "File definition error, fields have been declared " \
                                  "mandatory, but the corresponding header not!"
ERROR_MSG_FILE_CAN_NOT_BE_RECOGNISED = "File can not be recognized as one of the interface files"
MISSING_ONE_OR_MORE_MANDATORY_FIELDS = "Missing one or more mandatory fields"
NO_PERMISSION_TO_UPLOAD_CONTRACT_FILE = "You have no permission to upload a file with contracts"
