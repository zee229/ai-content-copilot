from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from services.utils.text_splitter import split_text_by_tokens, count_tokens, get_model_config

SUMMARIZE_PROMPT = """Create a highly detailed summary of the following text. Your summary should be comprehensive and preserve as much specific information as possible while still fitting within the required length.

Text to summarize:
{text}

Guidelines for summarization:
1. Maintain chronological order of events and topics
2. Preserve specific:
   - Names, dates, numbers, and statistics
   - Technical terms and their explanations
   - Key arguments and their supporting evidence
   - Cause-and-effect relationships
   - Methodologies and processes described
   - Examples and case studies
   - Quotes and important statements
3. Structure the summary with clear sections and transitions
4. Use bullet points or numbered lists for dense information when appropriate
5. Include any caveats, limitations, or important context
6. Preserve the original tone and technical level of the content

Your summary should be as detailed as possible while remaining coherent and well-organized. Focus on making every word count - avoid general statements in favor of specific, actionable information."""

async def summarize_long_text(text: str, target_model: str = "gpt-4o", summarizer_model: str = "o3-mini") -> str:
    """
    Summarize text that exceeds the target model's context window.
    Uses o3-mini for summarization, handling text in chunks if necessary.
    
    Args:
        text: Text to summarize
        target_model: Model that will ultimately use the text
        summarizer_model: Model to use for summarization (default: o3-mini)
    
    Returns:
        Summarized text that fits within target_model's context window
    """
    target_config = get_model_config(target_model)
    target_max_tokens = target_config["context_window"]
    
    # If text already fits in target model's context, return as is
    if count_tokens(text, target_model) <= target_max_tokens:
        return text
        
    # Initialize summarizer
    summarizer = ChatOpenAI(
        model_name=summarizer_model,
        max_tokens=get_model_config(summarizer_model)["max_output_tokens"],
        temperature=0.3  # Lower temperature for more precise summaries
    )
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(SUMMARIZE_PROMPT)
    
    # If text is too long for summarizer, split and summarize chunks
    if count_tokens(text, summarizer_model) > get_model_config(summarizer_model)["context_window"]:
        chunks = split_text_by_tokens(text, summarizer_model)
        summaries = []
        
        for i, chunk in enumerate(chunks, 1):
            # Add context about which part this is
            chunk_context = f"Part {i} of {len(chunks)}:\n\n{chunk}"
            messages = prompt.format_messages(text=chunk_context)
            response = await summarizer.ainvoke(messages)
            summaries.append(response.content)
        
        # Combine chunk summaries with clear section markers
        combined_summary = "\n\n=== Section Break ===\n\n".join(summaries)
        
        # If combined summary is still too long, recursively summarize
        if count_tokens(combined_summary, target_model) > target_max_tokens:
            # Add context about this being a meta-summary
            meta_context = (
                "This is a meta-summary combining multiple detailed section summaries. "
                "Each section represents a distinct part of the original content.\n\n"
                f"{combined_summary}"
            )
            return await summarize_long_text(meta_context, target_model, summarizer_model)
        
        return combined_summary
    
    # Text fits in summarizer's context window, summarize directly
    messages = prompt.format_messages(text=text)
    response = await summarizer.ainvoke(messages)
    return response.content
