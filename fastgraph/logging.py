import tired
import tired.datetime


_LOG_SECTION_DELIMETER = "-"


def _log_impl(context, message, level):
    print(level, _LOG_SECTION_DELIMETER, f"[{tired.datetime.get_today_time_seconds_string()}]", context, _LOG_SECTION_DELIMETER,
       message)


def debug(context, message):
    _log_impl(context, message, "D")


def error(context, message):
    _log_impl(context, message, "E")


def info(context, message):
    _log_impl(context, message, "I")


def warning(context, message):
    _log_impl(context, message, "W")
