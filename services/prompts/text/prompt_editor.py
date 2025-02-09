import streamlit as st
import os


def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), 'agent_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""


def save_prompt(content):
    prompt_path = os.path.join(os.path.dirname(__file__), 'agent_prompt.txt')
    with open(prompt_path, 'w', encoding='utf-8') as file:
        file.write(content)


def main():
    st.title("Agent Prompt Editor")

    # Load current prompt
    current_prompt = load_prompt()

    # Create a text area for editing
    new_prompt = st.text_area(
        "Edit Prompt",
        value=current_prompt,
        height=600,
        key="prompt_editor"
    )

    # Add a save button
    if st.button("Save Changes"):
        save_prompt(new_prompt)
        st.success("Prompt saved successfully!")


if __name__ == "__main__":
    main()
