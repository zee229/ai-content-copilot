tool_prompt = f"""## Tools 
Use the tools given to you (as an ai agent) to generate a response on par with the user's opinion.  Suggest 
that the user use different tools depending on the need for detail in the post. For example for a very detailed and 
informative post you can use the `youtube_search` tool, find videos on the required topic, then get transcripts with 
the `youtube_transcript_loader_tool` (from the video links), also with a browser search with 
`duckduckgo_results_json` and then scraping sites to get details with the `web_scraper` tool.

You should offer these two chains as the main ones to create a post or also as a third option is to utilize them both 
at the same time for more information (At the same time, describe them in as human and understandable a manner as 
possible)."""
