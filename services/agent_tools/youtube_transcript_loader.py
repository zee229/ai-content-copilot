from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List
from services.youtube.loader import get_transcripts


class YoutubeTranscriptLoaderArgs(BaseModel):
    youtube_video_links: List[str] = Field(...,
                                           description="The youtube video links for the transcript loading. Make sure "
                                                       "that their format is correct. Links should contain `watch?v=` "
                                                       "or `youtu.be/`, as these are the parts that the built-in "
                                                       "parser uses to extract the id of each video to get the "
                                                       "transcription later.")


class AsyncYoutubeTranscriptLoader(BaseTool):
    name: str = Field(default="youtube_transcript_loader_tool", description="The name of the tool")
    description: str = Field(
        default="Use this tool to load transcript from youtube videos"
    )
    args_schema: type[BaseModel] = Field(default=YoutubeTranscriptLoaderArgs)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _arun(self, youtube_video_links: List[str]) -> List[str] | str:
        try:
            transcripts = get_transcripts(youtube_video_links)
        except Exception as e:
            return str(e)
        return transcripts

    def _run(self, query: str) -> str:
        """Run the tool synchronously."""
        raise NotImplementedError("This tool only supports async execution")


youtube_transcript_loader_tool = AsyncYoutubeTranscriptLoader()
