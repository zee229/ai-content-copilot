from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from services.prompts.text.prompt_manager import load_prompt, get_current_prompt
from .tools import tool_prompt

def create_chat_prompt() -> ChatPromptTemplate:
    # Get the current prompt content or use default tool prompt
    current_prompt_name = get_current_prompt()
    system_content = load_prompt(current_prompt_name)

    system_message = SystemMessage(content=system_content)
    tool_system_message = SystemMessage(content=tool_prompt)
    chat_history_placeholder = MessagesPlaceholder(variable_name="chat_history")
    message_input_placeholder = HumanMessagePromptTemplate.from_template("{input}")
    agent_scratchpad = MessagesPlaceholder(variable_name="agent_scratchpad")

    return ChatPromptTemplate.from_messages([
        system_message,
        tool_system_message,
        chat_history_placeholder,
        message_input_placeholder,
        agent_scratchpad,
    ])

# Initialize default prompt
prompt = create_chat_prompt()
