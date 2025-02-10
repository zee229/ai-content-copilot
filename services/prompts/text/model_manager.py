import os
import json
from typing import List, Optional

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')


def get_available_models() -> List[str]:
    """Returns list of available models"""
    if not os.path.exists(CONFIG_FILE):
        return []

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('model_config', {}).get('available_models', [])
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def get_current_model() -> str:
    """Returns currently selected model from config"""
    if not os.path.exists(CONFIG_FILE):
        return "gpt-4o"

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('model_config', {}).get('current_model', "gpt-4o")
    except (json.JSONDecodeError, FileNotFoundError):
        return "gpt-4o"


def set_current_model(model_name: str) -> None:
    """Sets current model in config"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}

        if 'model_config' not in config:
            config['model_config'] = {
                'available_models': ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini", "o3-mini"],
                'current_model': model_name
            }
        else:
            config['model_config']['current_model'] = model_name

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error updating model config: {e}")
