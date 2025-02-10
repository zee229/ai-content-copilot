from typing import List, Optional

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from services.agent_tools import toolkit
from services.utils.text_splitter import ensure_context_length, count_tokens, get_model_config

from dotenv import load_dotenv

from services.prompts import agent_prompt

load_dotenv()


class LLMResponseGenerator:
    def __init__(self, model_name="gpt-4o", tools: Optional[List[BaseTool]] = None):
        if tools is None:
            self.tools = toolkit
        else:
            self.tools = toolkit + tools
        self.model_name = model_name
        self.model_config = get_model_config(model_name)

    def _parse_chat_history(self, chat_history) -> List[dict]:
        """Convert chat history to a format suitable for token counting."""
        parsed_history = []
        for message in chat_history:
            if isinstance(message, (AIMessage, HumanMessage)):
                role = "assistant" if isinstance(message, AIMessage) else "user"
                parsed_history.append({
                    "role": role,
                    "content": message.content
                })
        return parsed_history

    async def generate_response(self, user_query: str, prompt: ChatPromptTemplate,
                              chat_history: List[AIMessage | HumanMessage]) -> str:
        """Generate a response while ensuring context fits within model's token limits."""
        
        # Convert chat history to countable format
        parsed_history = self._parse_chat_history(chat_history)
        
        # Add current query to history for token counting
        current_context = parsed_history + [{"role": "user", "content": user_query}]
        
        # Ensure context fits within model limits
        truncated_context = ensure_context_length(current_context, self.model_name)
        
        # If context was truncated, add a note about it
        context_truncated = len(truncated_context) < len(current_context)
        if context_truncated:
            user_query = (
                "Note: Some earlier conversation history has been truncated to fit within "
                "model's context window.\n\n" + user_query
            )
        
        # Initialize LLM with appropriate parameters
        llm = ChatOpenAI(
            model_name=self.model_name,
            max_tokens=self.model_config["max_output_tokens"]
        )

        # Prepare input for the agent
        input_dict = {
            "agent_scratchpad": "",
            "chat_history": chat_history[-len(truncated_context)+1:] if context_truncated else chat_history,
            "input": user_query,
        }

        # Create and run the agent
        agent = create_tool_calling_agent(
            llm=llm,
            tools=self.tools,
            prompt=prompt,
        )

        runnable = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            verbose=True
        )

        try:
            response = await runnable.ainvoke(input_dict)
            return response.get("output", "I apologize, but I was unable to generate a response.")
        except Exception as e:
            error_msg = str(e)
            if "maximum context length" in error_msg.lower():
                return (
                    "I apologize, but the conversation has become too long for me to process. "
                    "Please try starting a new conversation or breaking your request into smaller parts."
                )
            raise  # Re-raise other exceptions to be handled by the main error handler


async def generate_response(user_query: str, chat_history: List[AIMessage | HumanMessage]) -> str:
    return await LLMResponseGenerator().generate_response(user_query, chat_history=chat_history, prompt=agent_prompt)
