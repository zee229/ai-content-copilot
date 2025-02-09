import streamlit as st
from services.prompts.text import prompt_manager


def load_prompt():
    current_name = prompt_manager.get_current_prompt()
    if current_name:
        return prompt_manager.load_prompt(current_name)
    return ""


def save_prompt(content):
    current_name = prompt_manager.get_current_prompt()
    if current_name:
        prompt_manager.save_prompt(current_name, content)


st.set_page_config(
    page_title="Prompt Editor",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)

# Header with back button
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.page_link("app.py", label="← Back", use_container_width=True)
with col2:
    st.title("Agent Prompt Editor")

# Prompt selection and creation
prompt_col1, prompt_col2 = st.columns([0.7, 0.3])
with prompt_col1:
    available_prompts = prompt_manager.get_all_prompts()
    current_prompt = prompt_manager.get_current_prompt()
    selected_prompt = st.selectbox(
        "Select Prompt",
        options=available_prompts,
        index=available_prompts.index(current_prompt) if current_prompt in available_prompts else 0
    )
    if selected_prompt != current_prompt:
        prompt_manager.set_current_prompt(selected_prompt)
        st.rerun()

with prompt_col2:
    new_prompt_name = st.text_input("New Prompt Name", key="new_prompt_name")
    if st.button("Create Prompt"):
        if new_prompt_name:
            if new_prompt_name not in available_prompts:
                # Create new empty prompt
                prompt_manager.save_prompt(new_prompt_name, "")
                prompt_manager.set_current_prompt(new_prompt_name)
                st.rerun()
            else:
                st.error("Prompt with this name already exists")

# Load current prompt
current_content = load_prompt()

# Create two columns for editor and preview
editor_col, preview_col = st.columns(2)

with editor_col:
    st.subheader("Edit Prompt")
    new_prompt = st.text_area(
        "Edit markdown content below",
        value=current_content,
        height=600,
        key="prompt_editor",
        help="Use markdown syntax for formatting"
    )
    if st.button("Save Changes"):
        save_prompt(new_prompt)
        st.success("Prompt saved successfully!")

with preview_col:
    st.subheader("Preview")
    st.markdown(new_prompt)
