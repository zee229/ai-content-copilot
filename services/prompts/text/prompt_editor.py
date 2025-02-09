import streamlit as st
import os
from services.prompts.text import prompt_manager

def load_file_directly(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"DEBUG: Loaded content length: {len(content)}")
            print(f"DEBUG: First 100 chars: {content[:100]}")
            return content
    except Exception as e:
        print(f"DEBUG: Error loading file: {e}")
        return None

def main():
    st.title("Agent Prompt Editor")

    # Debug information at the top level
    st.sidebar.write("Debug Info:")

    # Create two columns - sidebar for prompt list and main area for editing
    prompts = prompt_manager.get_all_prompts()
    current_prompt = prompt_manager.get_current_prompt()
    
    st.sidebar.write(f"Available prompts: {prompts}")
    st.sidebar.write(f"Current prompt: {current_prompt}")

    # Load current content
    if current_prompt:
        current_content = load_file_directly(os.path.join(os.path.dirname(__file__), 'prompts', f"{current_prompt}.txt"))
        st.sidebar.write(f"Loaded content length: {len(current_content) if current_content else 0}")
        st.sidebar.write(f"First 100 chars: {current_content[:100] if current_content else 'empty'}")
    else:
        current_content = ""
        st.sidebar.write("No current prompt selected")

    # Sidebar with prompt list and controls
    with st.sidebar:
        st.header("Prompts")
        
        # New prompt button
        if st.button("➕ New Prompt"):
            current_prompt = ""
            current_content = ""
            st.rerun()
        
        # List all prompts
        for prompt in prompts:
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                if st.button(prompt, key=f"select_{prompt}", use_container_width=True):
                    content = load_file_directly(os.path.join(os.path.dirname(__file__), 'prompts', f"{prompt}.txt"))
                    if content:
                        current_prompt = prompt
                        current_content = content
                        st.rerun()
                    else:
                        st.error(f"Failed to load prompt: {prompt}")
            with col2:
                if st.button("🗑️", key=f"delete_{prompt}"):
                    if prompt_manager.delete_prompt(prompt):
                        if prompt == current_prompt:
                            current_prompt = ""
                            current_content = ""
                        st.success(f"Deleted {prompt}")
                        st.rerun()

    # Main editing area
    prompt_name = st.text_input(
        "Prompt Name",
        value=current_prompt,
        placeholder="Enter prompt name"
    )

    # Prompt content editor
    prompt_content = st.text_area(
        "Edit Prompt",
        value=current_content,
        height=400,
        placeholder="Enter prompt content",
        key="prompt_editor"
    )

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        if st.button("Save Changes", type="primary", use_container_width=True):
            if not prompt_name:
                st.error("Please enter a prompt name")
            else:
                with open(os.path.join(os.path.dirname(__file__), 'prompts', f"{prompt_name}.txt"), 'w', encoding='utf-8') as f:
                    f.write(prompt_content)
                if prompt_name != current_prompt:
                    prompt_manager.set_current_prompt(prompt_name)
                st.success(f"Saved prompt: {prompt_name}")
                st.rerun()

    with col2:
        if st.button("Test Prompt", use_container_width=True):
            st.code(prompt_manager.test_prompt(prompt_content), language="markdown")

    # Show the same content in a different way
    st.write("Content preview:")
    st.code(prompt_content)

if __name__ == "__main__":
    main()
