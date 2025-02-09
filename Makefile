.PHONY: install run setup clean

# Install Python dependencies
install:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && playwright install

# Run Streamlit application
run:
	. venv/bin/activate && streamlit run app.py

# Setup the project (install dependencies and prepare environment)
setup: install

# Clean temporary files and caches
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type f -name ".DS_Store" -delete
