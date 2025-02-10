from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Union
from services.youtube.loader import get_transcripts_async
from services.utils.summarizer import summarize_long_text
from services.utils.text_splitter import count_tokens, get_model_config
from services.prompts.text.model_manager import get_current_model


class YoutubeTranscriptLoaderArgs(BaseModel):
    """Arguments for loading YouTube video transcripts."""
    youtube_video_links: Union[List[str], str] = Field(
        ...,
        description="The youtube video links for the transcript loading. Make sure "
                   "that their format is correct. Links should contain `watch?v=` "
                   "or `youtu.be/`, as these are the parts that the built-in "
                   "parser uses to extract the id of each video to get the "
                   "transcription later."
    )


class AsyncYoutubeTranscriptLoader(BaseTool):
    """Asynchronous tool for loading and processing YouTube video transcripts.
    
    This tool loads transcripts from YouTube videos and automatically handles long transcripts
    by summarizing them if they exceed the model's context window.
    """
    name: str = "youtube_transcript_loader_tool"
    description: str = "Use this tool to load transcript from youtube videos"
    args_schema: type[BaseModel] = YoutubeTranscriptLoaderArgs

    async def _arun(self, youtube_video_links: Union[List[str], str]) -> List[str]:
        """Asynchronously load and process YouTube video transcripts.
        
        Args:
            youtube_video_links: List of YouTube video URLs or a single URL to process
            
        Returns:
            List of processed transcripts. Each transcript may be summarized
            if it exceeds the model's context window.
            
        Note:
            If a transcript is summarized, it will be prefixed with a note
            indicating this fact.
        """
        try:
            # Convert single string to list if necessary
            if isinstance(youtube_video_links, str):
                youtube_video_links = [youtube_video_links]
                
            # Get current model and its configuration
            model_name = get_current_model()
            model_config = get_model_config(model_name)
            
            # Get transcripts from YouTube without timestamps for conciseness
            transcripts = await get_transcripts_async(youtube_video_links, include_timestamps=False)
            
            # Process each transcript
            processed_transcripts = []
            for transcript in transcripts:
                if not transcript.startswith("Error:"):
                    # Check if transcript exceeds model's context window
                    if count_tokens(transcript, model_name) > model_config["context_window"]:
                        # Summarize long transcript using o3-mini
                        summarized = await summarize_long_text(
                            text=transcript,
                            target_model=model_name,
                            summarizer_model="o3-mini"
                        )
                        processed_transcripts.append(
                            f"[Note: This transcript was summarized due to length]\n\n{summarized}"
                        )
                    else:
                        processed_transcripts.append(transcript)
                else:
                    # Preserve error messages
                    processed_transcripts.append(transcript)
            
            return processed_transcripts
            
        except Exception as e:
            return [f"Error: {str(e)}"]

    def _run(self, query: str) -> str:
        """Synchronous execution is not supported."""
        raise NotImplementedError("This tool only supports async execution")


# Create a default instance of the tool
youtube_transcript_loader_tool = AsyncYoutubeTranscriptLoader()
