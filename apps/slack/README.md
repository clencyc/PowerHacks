# SafeSpace Slack App

This directory contains the Slack bot implementation for SafeSpace AI.

## Structure

- **`app.py`**: The main application file.
    - Initializes the Slack Bolt app.
    - Listens for messages (`@app.message()`) and runs toxicity detection.
    - Handles the `/safespace` command to query the RAG service.
    - Manages interactive components like buttons and modals.
- **`detection.py`**: Logic for detecting harmful content.
    - Currently contains a mock implementation.
    - Intended to use Google's Perspective API and HuggingFace models.
- **`rag.py`**: Retrieval-Augmented Generation service.
    - Uses LangChain and OpenAI to answer questions based on company policies.
    - Connects to Qdrant for vector search.

## Setup

1.  **Environment Variables**: Copy `.env.example` to `.env` and fill in:
    - `SLACK_BOT_TOKEN`
    - `SLACK_APP_TOKEN`
    - `GEMINI_API_KEY`
    - `PERSPECTIVE_API_KEY`
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run**:
    ```bash
    python app.py
    ```
