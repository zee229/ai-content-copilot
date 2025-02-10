import streamlit as st
import asyncio
from services.response_generation import LLMResponseGenerator
from langchain_core.messages import AIMessage, HumanMessage
from services.prompts.agent import create_chat_prompt
from services.prompts.text.prompt_manager import get_all_prompts, get_current_prompt, set_current_prompt
from services.prompts.text.model_manager import get_available_models, get_current_model, set_current_model


def initialize_chat_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_generator" not in st.session_state:
        st.session_state.llm_generator = LLMResponseGenerator(model_name=get_current_model())


def display_chat_messages():
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            st.chat_message("user").markdown(message.content)
        elif isinstance(message, AIMessage):
            st.chat_message("assistant").markdown(message.content)


async def main():
    try:
        # Custom CSS for header alignment
        st.markdown("""
            <style>
            [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
                padding-top: 0;
                padding-bottom: 0;
            }
            .big-title {
                font-size: 48px !important;
                margin-top: 0 !important;
                margin-bottom: 0 !important;
                padding: 0 !important;
            }
            .error-message {
                color: #ff4b4b;
                padding: 10px;
                border-radius: 4px;
                background-color: #ffe5e5;
                margin: 10px 0;
            }
            </style>
        """, unsafe_allow_html=True)

        # Create columns for all elements in the same row
        col1, col2, col3, col4 = st.columns([0.4, 0.10, 0.15, 0.15])

        with col1:
            st.markdown("<h1 class='big-title'>AI Content Generation Assistant</h1>", unsafe_allow_html=True)
        
        with col2:
            try:
                # Get available models and current selection
                models = get_available_models()
                current_model = get_current_model()
                
                if models:
                    selected_model = st.selectbox(
                        "Select Model",
                        options=models,
                        index=models.index(current_model) if current_model in models else 0,
                        label_visibility="collapsed"
                    )
                    if selected_model != current_model:
                        set_current_model(selected_model)
                        st.session_state.llm_generator = LLMResponseGenerator(model_name=selected_model)
                        st.rerun()
            except Exception as e:
                st.error(f"Error loading models: {str(e)}")
        
        with col3:
            try:
                # Get available prompts and current selection
                prompts = get_all_prompts()
                current_prompt = get_current_prompt()
                
                if prompts:
                    selected_prompt = st.selectbox(
                        "Select Prompt",
                        options=prompts,
                        index=prompts.index(current_prompt) if current_prompt in prompts else 0,
                        label_visibility="collapsed"
                    )
                    if selected_prompt != current_prompt:
                        set_current_prompt(selected_prompt)
                        # Create new prompt with updated selection
                        st.session_state.prompt = create_chat_prompt()
                        st.rerun()
            except Exception as e:
                st.error(f"Error loading prompts: {str(e)}")
        
        with col4:
            st.page_link("pages/1_Prompt_Editor.py", label="✏️ Edit Prompt", use_container_width=True)

        initialize_chat_state()
        display_chat_messages()

        if prompt := st.chat_input("What would you like me to help you with?"):
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.chat_message("user").markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Use the current prompt template
                        if "prompt" not in st.session_state:
                            st.session_state.prompt = create_chat_prompt()
                        
                        response = await st.session_state.llm_generator.generate_response(
                            prompt,
                            st.session_state.prompt,
                            st.session_state.messages[:-1]  # Pass previous messages excluding the current one
                        )
                        st.session_state.messages.append(AIMessage(content=response))
                        st.markdown(response)
                    except Exception as e:
                        error_message = str(e)
                        if "context_length" in error_message.lower():
                            st.markdown(
                                "<div class='error-message'>"
                                "The conversation has become too long for the model to process. "
                                "Please try starting a new conversation or reducing your message length."
                                "</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"<div class='error-message'>"
                                f"An error occurred while generating the response: {error_message}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="AI Content Generation Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={}
    )
    asyncio.run(main())
