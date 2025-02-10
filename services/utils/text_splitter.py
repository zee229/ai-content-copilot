from typing import List, Dict
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from anthropic import Anthropic

# Model configurations for context windows and max output tokens
MODEL_CONFIGS = {
    "gpt-4o": {"context_window": 128000, "max_output_tokens": 16384},
    "gpt-4o-mini": {"context_window": 128000, "max_output_tokens": 16384},
    "o1": {"context_window": 200000, "max_output_tokens": 100000},
    "o1-mini": {"context_window": 200000, "max_output_tokens": 100000},
    "o3-mini": {"context_window": 200000, "max_output_tokens": 100000},
    "claude-3-5-sonnet-latest": {"context_window": 200000, "max_output_tokens": 8192},
    "claude-3-5-haiku-latest": {"context_window": 200000, "max_output_tokens": 8192}
}


def get_model_config(model_name: str) -> Dict[str, int]:
    """Get the configuration for a specific model."""
    return MODEL_CONFIGS.get(model_name,
                             {"context_window": 128000, "max_output_tokens": 16384})  # Default to gpt-4o settings


def count_tokens(text: str, model_name: str = "gpt-4o") -> int:
    """Count the number of tokens in a text string."""
    if "claude" in model_name.lower():
        client = Anthropic()
        response = client.messages.count_tokens(
            model=model_name,
            messages=[{"role": "user", "content": text}]
        )
        return response.input_tokens
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def split_text_by_tokens(text: str, model_name: str, chunk_overlap: int = 100) -> List[str]:
    """Split text into chunks that fit within the model's context window."""
    model_config = get_model_config(model_name)
    max_tokens = model_config["context_window"]

    # Calculate chunk size to leave room for model response
    chunk_size = max_tokens - model_config["max_output_tokens"]

    # Use RecursiveCharacterTextSplitter with appropriate tokenizer
    if "claude" in model_name.lower():
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: count_tokens(x, model_name)
        )
    else:
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-4",  # Using gpt-4 encoding as base
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda x: count_tokens(x, model_name)
        )

    return text_splitter.split_text(text)


def ensure_context_length(messages: List[dict], model_name: str) -> List[dict]:
    """Ensure that the total context length fits within model limits."""
    model_config = get_model_config(model_name)
    max_tokens = model_config["context_window"]

    # Count total tokens in messages
    total_tokens = 0
    for message in messages:
        total_tokens += count_tokens(message["content"], model_name)

    # If within limits, return original messages
    if total_tokens <= max_tokens:
        return messages

    # If over limit, remove oldest messages until under limit
    while total_tokens > max_tokens and len(messages) > 1:
        removed_message = messages.pop(0)
        total_tokens -= count_tokens(removed_message["content"], model_name)

    return messages
