import os
import json
from typing import List, Optional


# Constants
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), 'prompts')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

# Ensure prompts directory exists
os.makedirs(PROMPTS_DIR, exist_ok=True)


def get_all_prompts() -> List[str]:
    """Returns list of available prompt names (without extension)"""
    if not os.path.exists(PROMPTS_DIR):
        print(f"Prompts directory does not exist: {PROMPTS_DIR}")
        return []

    prompts = []
    for file in os.listdir(PROMPTS_DIR):
        if file.endswith('.txt') and not file.startswith('.'):
            prompts.append(os.path.splitext(file)[0])
    return sorted(prompts)


def get_current_prompt() -> Optional[str]:
    """Returns name of currently selected prompt from config"""
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file does not exist: {CONFIG_FILE}")
        return None

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            current = config.get('current_prompt')
            return current
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading config: {e}")
        return None


def set_current_prompt(name: str) -> None:
    """Sets current prompt in config"""
    config = {'current_prompt': name}
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def load_prompt(name: str) -> Optional[str]:
    """Loads prompt content from file"""
    if not name:
        print("No prompt name provided")
        return None

    file_path = os.path.join(PROMPTS_DIR, f"{name}.txt")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        print(f"Prompt file not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error loading prompt: {e}")
        return None


def save_prompt(name: str, content: str) -> None:
    """Saves prompt content to file"""
    # Ensure prompts directory exists
    os.makedirs(PROMPTS_DIR, exist_ok=True)

    file_path = os.path.join(PROMPTS_DIR, f"{name}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def delete_prompt(name: str) -> bool:
    """Deletes prompt file. Returns True if successful."""
    file_path = os.path.join(PROMPTS_DIR, f"{name}.txt")
    print(f"Deleting prompt: {file_path}")
    try:
        os.remove(file_path)

        # If this was the current prompt, clear the setting
        current = get_current_prompt()
        if current == name:
            set_current_prompt("")
        return True
    except FileNotFoundError:
        print(f"File not found when trying to delete: {file_path}")
        return False
    except Exception as e:
        print(f"Error deleting prompt: {e}")
        return False


def test_prompt(content: str) -> str:
    """Tests prompt with a sample input. Returns the formatted test result."""
    sample_input = "Hello! This is a test message."
    return f"""Test Results:
---
Sample Input: "{sample_input}"

Your Prompt:
---
{content}
"""
