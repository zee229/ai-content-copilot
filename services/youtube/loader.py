from youtube_transcript_api import YouTubeTranscriptApi

from services.youtube.time_format import format_seconds_to_timestamp
from services.youtube.url_parser import get_video_id

from typing import List


def _get_transcript_with_time(video_id: str) -> str:
    """
    Retrieve transcript for a given video and return it as a formatted string with start and end times.
    """
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    lines = []
    for block in transcript:
        start = block['start']
        duration = block['duration']
        end = start + duration
        text = block['text']
        lines.append(f"{format_seconds_to_timestamp(start)} - {format_seconds_to_timestamp(end)}: {text}")
    return "\n".join(lines)


def get_transcripts(video_urls: List[str]) -> List[str]:
    """
    Retrieve transcript for a given video and return it as a formatted string with start and end times.
    """
    transcripts = []
    for url in video_urls:
        video_id = get_video_id(url)
        transcripts.append(_get_transcript_with_time(video_id))
    return transcripts
