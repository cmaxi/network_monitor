import ping3

from modules.common import ms_time

def get_response_ping(address, timeout_value):
    """Get ping value in millisecons.
    Convert None values to -1.
    """

    result = ping3.ping(address, timeout=timeout_value)

    if isinstance(result, float):
        return ms_time(result)
    else:
        return -1
