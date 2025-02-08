import streamlit as st
import asyncio
from services.response_generation import LLMResponseGenerator
from langchain_core.messages import AIMessage, HumanMessage
from services.prompts import agent_prompt

def initialize_chat_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_generator" not in st.session_state:
        st.session_state.llm_generator = LLMResponseGenerator()

def display_chat_messages():
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            st.chat_message("user").markdown(message.content)
        elif isinstance(message, AIMessage):
            st.chat_message("assistant").markdown(message.content)

async def main():
    st.title("AI Content Generation Assistant")
    
    initialize_chat_state()
    display_chat_messages()

    if prompt := st.chat_input("What would you like me to help you with?"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.chat_message("user").markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = await st.session_state.llm_generator.generate_response(
                    prompt,
                    agent_prompt,
                    st.session_state.messages
                )
                st.session_state.messages.append(AIMessage(content=response))
                st.markdown(response)

if __name__ == "__main__":
    st.set_page_config(
        page_title="AI Content Generation Assistant",
        page_icon="💬",
        layout="wide"
    )
    asyncio.run(main())
