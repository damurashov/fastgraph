import tired
import tired.datetime


_LOG_SECTION_DELIMETER = "-"
NONE = 0
ERROR = 1
WARNING = 2
INFO = 3
DEBUG = 4
LOG_LEVEL_TO_STRING_MAPPING = {
    ERROR: "E",
    WARNING: "W",
    INFO: "I",
    DEBUG: "D"
}

def _log_impl(context, message, level):
    print(LOG_LEVEL_TO_STRING_MAPPING[level], _LOG_SECTION_DELIMETER,
        f"{tired.datetime.get_today_time_milliseconds_string()}", f"[{context}]", _LOG_SECTION_DELIMETER, message)


def debug(context, message):
    _log_impl(context, message, DEBUG)


def error(context, message):
    _log_impl(context, message, ERROR)


def info(context, message):
    _log_impl(context, message, INFO)


def warning(context, message):
    _log_impl(context, message, DEBUG)
