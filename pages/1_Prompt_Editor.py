import streamlit as st
import os


def load_prompt():
    prompt_path = os.path.join('services', 'prompts', 'text', 'linkedin_agent_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""


def save_prompt(content):
    prompt_path = os.path.join('services', 'prompts', 'text', 'linkedin_agent_prompt.txt')
    with open(prompt_path, 'w', encoding='utf-8') as file:
        file.write(content)


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

# Load current prompt
current_prompt = load_prompt()

# Create two columns for editor and preview
editor_col, preview_col = st.columns(2)

with editor_col:
    st.subheader("Edit Prompt")
    new_prompt = st.text_area(
        "Edit markdown content below",
        value=current_prompt,
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
