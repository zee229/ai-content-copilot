from .webscraper import webscraper_tool
from .youtube_search import youtube_search_tool
from .youtube_transcript_loader import youtube_transcript_loader_tool
from .duckduckgo_search import duckduckgo_search_tool, duckduckgo_search_results_tool
from .wikipedia import wikipedia_tool


toolkit = [webscraper_tool, youtube_search_tool, youtube_transcript_loader_tool, duckduckgo_search_tool,
           duckduckgo_search_results_tool, wikipedia_tool]

__all__ = [
    "webscraper_tool",
    "youtube_search_tool",
    "youtube_transcript_loader_tool",
    "duckduckgo_search_tool",
    "duckduckgo_search_results_tool",
    "wikipedia_tool",
    "toolkit",
]
