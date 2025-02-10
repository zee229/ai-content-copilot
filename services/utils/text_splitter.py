from typing import List, Dict
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Model configurations for context windows and max output tokens
MODEL_CONFIGS = {
    "gpt-4o": {"context_window": 128000, "max_output_tokens": 16384},
    "gpt-4o-mini": {"context_window": 128000, "max_output_tokens": 16384},
    "o1": {"context_window": 200000, "max_output_tokens": 100000},
    "o1-mini": {"context_window": 200000, "max_output_tokens": 100000},
    "o3-mini": {"context_window": 200000, "max_output_tokens": 100000},
}

def get_model_config(model_name: str) -> Dict[str, int]:
    """Get the configuration for a specific model."""
    return MODEL_CONFIGS.get(model_name, {"context_window": 128000, "max_output_tokens": 16384})  # Default to gpt-4o settings

def count_tokens(text: str, model_name: str = "gpt-4o") -> int:
    """Count the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-4")  # Using gpt-4 encoding as base
    return len(encoding.encode(text))

def split_text_by_tokens(text: str, model_name: str, chunk_overlap: int = 100) -> List[str]:
    """Split text into chunks that fit within the model's context window."""
    model_config = get_model_config(model_name)
    max_tokens = model_config["context_window"]
    
    # Calculate chunk size to leave room for model response
    chunk_size = max_tokens - model_config["max_output_tokens"]
    
    # Use RecursiveCharacterTextSplitter with tiktoken
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
    
    # Convert messages to text to count tokens
    full_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
    total_tokens = count_tokens(full_text, model_name)
    
    if total_tokens <= max_tokens:
        return messages
    
    # If we exceed the limit, keep the most recent messages that fit
    truncated_messages = []
    current_tokens = 0
    
    for msg in reversed(messages):
        msg_text = f"{msg.get('role', 'user')}: {msg.get('content', '')}"
        msg_tokens = count_tokens(msg_text, model_name)
        
        if current_tokens + msg_tokens > max_tokens - model_config["max_output_tokens"]:
            break
            
        current_tokens += msg_tokens
        truncated_messages.insert(0, msg)
    
    return truncated_messages
