from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from services.prompts.text.prompt_editor import load_prompt

system_message = SystemMessage(content=load_prompt())
chat_history_placeholder = MessagesPlaceholder(variable_name="chat_history")
message_input_placeholder = HumanMessagePromptTemplate.from_template("{input}")
agent_scratchpad_placeholder = MessagesPlaceholder(variable_name="agent_scratchpad")

prompt = ChatPromptTemplate.from_messages(
    [
        system_message,
        chat_history_placeholder,
        message_input_placeholder,
        agent_scratchpad_placeholder,
    ]
)
