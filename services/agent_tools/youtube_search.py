from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Optional
from youtube_search import YoutubeSearch
import json


class YouTubeSearchArgs(BaseModel):
    """Arguments for YouTube search."""
    query: str = Field(..., description="The search query for YouTube videos")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class YouTubeSearchTool(BaseTool):
    """Tool for searching YouTube videos."""
    name: str = "youtube_search"
    description: str = "Search for YouTube videos by query"
    args_schema: type[BaseModel] = YouTubeSearchArgs
    
    def _run(self, query: str, max_results: int = 5) -> List[dict]:
        """
        Run YouTube search.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of video information dictionaries
        """
        try:
            # Perform search
            results = YoutubeSearch(query, max_results=max_results).to_dict()
            
            # Format results
            formatted_results = []
            for video in results:
                formatted_results.append({
                    'title': video['title'],
                    'url': f"https://youtube.com{video['url_suffix']}",
                    'duration': video['duration'],
                    'views': video['views'],
                    'channel': video['channel']
                })
                
            return formatted_results
            
        except Exception as e:
            return [{"error": f"Error searching YouTube: {str(e)}"}]
    
    async def _arun(self, query: str, max_results: int = 5) -> List[dict]:
        """Async implementation of the tool."""
        return self._run(query, max_results)


# Create tool instance
youtube_search_tool = YouTubeSearchTool()
