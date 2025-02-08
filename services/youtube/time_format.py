def format_seconds_to_timestamp(seconds):
    """
    Convert seconds to HH:MM:SS.mmm format
    Args:
        seconds (float): Time in seconds

    Returns:
        str: Formatted time string in HH:MM:SS.mmm format
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_remainder = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds_remainder:06.3f}"
