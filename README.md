# AI Content Generation Assistant

A powerful Streamlit-based web application that serves as an AI content generation assistant, leveraging the capabilities of LangChain and various AI models for content generation and information retrieval.

## Features

- Interactive chat interface for content generation
- Support for multiple AI models:
  - OpenAI models
  - Anthropic Claude 3.5 models (Sonnet and Haiku)
- Custom prompt editing capabilities
- Integration with multiple data sources:
  - YouTube integration:
    - Video search functionality
    - Transcript extraction from video links
  - DuckDuckGo search with two modes:
    - Direct search results with summaries
    - Detailed results with previews and source links
  - Web scraping
  - Wikipedia
- Real-time response generation
- User-friendly interface with Streamlit

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/zee229/ai-content-copilot
cd content-generation-agent
```

2. Set up the project using Make (recommended):
```bash
make setup
```
This command will:
- Create a Python virtual environment
- Install all required dependencies
- Set up Playwright for web scraping

Alternatively, you can perform the steps manually:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

3. Set up environment variables:
- Copy `.env-example` to `.env`
- Add your API keys and configuration settings:
  ```
  OPENAI_API_KEY=your_openai_api_key
  ANTHROPIC_API_KEY=your_anthropic_api_key
  ```

## Usage

1. Start the application using Make:
```bash
make run
```

Or manually:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
streamlit run app.py
```

2. Access the web interface through your browser (typically at `http://localhost:8501`)

3. Use the chat interface to interact with the AI assistant:
   - Select your preferred model (OpenAI or Claude 3)
   - Start chatting and use available tools for content generation

4. Access the Prompt Editor through the "Edit Prompt" button to customize the agent's behavior

## Project Structure

- `app.py` - Main application file with Streamlit interface
- `pages/` - Additional Streamlit pages (including Prompt Editor)
- `services/` - Core functionality and tools
  - `agent_tools/` - Custom tools for web scraping and data retrieval
  - `prompts/` - System prompts and configurations
  - `utils/` - Utility functions for text processing and token management
- `requirements.txt` - Python dependencies
- `Makefile` - Build and development commands

## Dependencies

Key dependencies include:
- `langchain` - For AI model integration and chains
- `openai` - OpenAI API integration
- `anthropic` - Anthropic Claude API integration
- `streamlit` - Web interface
- `playwright` - Web scraping capabilities
- `youtube-search` - YouTube data retrieval
- `duckduckgo-search` - Web search functionality
- `wikipedia` - Wikipedia data access

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
