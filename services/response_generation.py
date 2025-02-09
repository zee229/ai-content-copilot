from typing import List, Optional

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from services.agent_tools import toolkit

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

    def _parse_chat_history(self, chat_history) -> List[AIMessage | HumanMessage]:
        pass

    async def generate_response(self, user_query: str, prompt: ChatPromptTemplate,
                                chat_history=List[AIMessage | HumanMessage]) -> str:
        llm = ChatOpenAI(model_name=self.model_name)

        input_dict = {
            "agent_scratchpad": "",
            "chat_history": chat_history,
            "input": user_query,
        }

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

        response = await runnable.ainvoke(input_dict)

        if "output" not in response:
            msg = "Output key not found in result. Tried 'output'."
            raise ValueError(msg)

        return response.get("output")


async def generate_response(user_query: str, chat_history: List[AIMessage | HumanMessage]) -> str:
    print(agent_prompt)
    return await LLMResponseGenerator().generate_response(user_query, chat_history=chat_history, prompt=agent_prompt)
