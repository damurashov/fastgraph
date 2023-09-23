import tired
import tired.datetime


_LOG_SECTION_DELIMETER = "-"


def debug(context, message):
    print("D", _LOG_SECTION_DELIMETER, f"[{tired.datetime.get_today_time_seconds_string()}]", context, _LOG_SECTION_DELIMETER,
       message)


def error(context, message):
    print("E", _LOG_SECTION_DELIMETER, f"[{tired.datetime.get_today_time_seconds_string()}]", context, _LOG_SECTION_DELIMETER,
       message)
