# Book Recommendation Assistant

This application uses LlamaIndex to recommend books based on user input. The application is deployed through Streamlit.

## Overview

The Book Recommendation Assistant is a RAG (Retrieval-Augmented Generation) based application that helps users discover books matching their interests. The system uses vector embeddings to find semantically similar books based on genre, author, or thematic preferences.

## Features

- Natural language book recommendations based on user input
- Semantic matching using vector similarity search
- Easy-to-use Streamlit interface
- Powered by LlamaIndex and Hugging Face embedding technology
- Conversational chat interface for interactive recommendations

## How to Use

1. Enter a book genre, author, or topic in the input box
2. Click "Get Recommendations"
3. The application will provide book recommendations based on your input
4. Explore the recommendations to discover your next great read!
5. Ask follow-up questions about the recommendations

## Installation Steps

1. Clone this repository:
   ```
   git clone <repository-url>
   cd book-recommendation-agent
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_api_key_here`

## Running the Application

Start the Streamlit application:
```
streamlit run streamlit_app.py
```

## Dependencies

The application depends on the following packages: