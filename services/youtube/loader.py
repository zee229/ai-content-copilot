from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import asyncio
from functools import lru_cache
from typing import List, Dict, Optional

from services.youtube.time_format import format_seconds_to_timestamp
from services.youtube.url_parser import get_video_id


@lru_cache(maxsize=100)
def _get_cached_transcript(video_id: str) -> Optional[List[Dict]]:
    """
    Retrieve and cache transcript for a given video ID.
    Returns None if transcript is not available.
    """
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception:
        return None


def _format_transcript(transcript: List[Dict], include_timestamps: bool = False) -> str:
    """
    Format transcript, optionally including timestamps.
    
    Args:
        transcript: List of transcript blocks
        include_timestamps: Whether to include timestamps in output
        
    Returns:
        Formatted transcript text
    """
    if include_timestamps:
        lines = []
        for block in transcript:
            start = block['start']
            duration = block['duration']
            end = start + duration
            text = block['text']
            lines.append(f"{format_seconds_to_timestamp(start)} - {format_seconds_to_timestamp(end)}: {text}")
        return "\n".join(lines)
    else:
        # Just concatenate the text for more concise output
        return " ".join(block['text'] for block in transcript)


async def _get_transcript_async(video_id: str, include_timestamps: bool = False) -> Optional[str]:
    """
    Asynchronously retrieve and format transcript for a video.
    """
    # Run the blocking API call in a thread pool
    transcript = await asyncio.get_event_loop().run_in_executor(
        None, _get_cached_transcript, video_id
    )
    
    if transcript:
        # Format the transcript in the thread pool as well
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: _format_transcript(transcript, include_timestamps)
        )
    return None


async def get_transcripts_async(video_urls: List[str], include_timestamps: bool = False) -> List[str]:
    """
    Asynchronously retrieve transcripts for multiple videos.
    
    Args:
        video_urls: List of YouTube video URLs
        include_timestamps: Whether to include timestamps in output
        
    Returns:
        List of formatted transcripts or error messages
    """
    async def process_url(url: str) -> str:
        try:
            # First validate URL and get video ID
            video_id = get_video_id(url)
            if not video_id:
                return f"Error: Invalid YouTube URL format: {url}"
                
            # Get transcript
            transcript = await _get_transcript_async(video_id, include_timestamps)
            if not transcript:
                return f"Error: Could not get transcript for video {url}. The video might not have captions available."
                
            return transcript
            
        except Exception as e:
            return f"Error: {str(e)} for video {url}"

    # Process all URLs concurrently
    tasks = [process_url(url) for url in video_urls]
    return await asyncio.gather(*tasks)


def get_transcripts(video_urls: List[str], include_timestamps: bool = False) -> List[str]:
    """
    Synchronous wrapper for backward compatibility.
    """
    return asyncio.run(get_transcripts_async(video_urls, include_timestamps))
