import re
from typing import Optional


def get_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats.
    
    Supports:
    - Standard watch URLs: youtube.com/watch?v=VIDEO_ID
    - Short URLs: youtu.be/VIDEO_ID
    - Embedded URLs: youtube.com/embed/VIDEO_ID
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID if found, None otherwise
    """
    if not isinstance(url, str):
        return None
        
    # Clean the URL
    url = url.strip()
    
    # Try different URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Validate video ID format
            if re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
                return video_id
                
    return None
