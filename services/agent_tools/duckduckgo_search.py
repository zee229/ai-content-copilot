from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Optional
from duckduckgo_search import DDGS
import logging


class DuckDuckGoSearchArgs(BaseModel):
    """Arguments for DuckDuckGo search."""
    query: str = Field(..., description="The search query")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class DuckDuckGoSearchTool(BaseTool):
    """Tool for searching web content using DuckDuckGo."""
    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo"
    args_schema: type[BaseModel] = DuckDuckGoSearchArgs
    
    def _run(self, query: str, max_results: int = 5) -> List[dict]:
        """
        Run DuckDuckGo search.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        try:
            with DDGS() as ddgs:
                # Get search results
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    # Extract fields with fallbacks
                    title = r.get('title', '')
                    url = r.get('href', '') 
                    snippet = r.get('body', '')
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
                
            return results if results else [{"error": "No results found"}]
            
        except Exception as e:
            logging.error(f"DuckDuckGo search error: {str(e)}")
            return [{"error": f"Error searching DuckDuckGo: {str(e)}"}]
    
    async def _arun(self, query: str, max_results: int = 5) -> List[dict]:
        """Async implementation of the tool."""
        return self._run(query, max_results)


# Create tool instance
duckduckgo_search_tool = DuckDuckGoSearchTool()
