# Book Recommendation & Information Assistant

This application uses LlamaIndex to recommend books based on user input and provide information through web search. The application is deployed through Streamlit.

## Overview

The Book Recommendation Assistant is a RAG (Retrieval-Augmented Generation) based application that helps users discover books matching their interests. The system uses vector embeddings to find semantically similar books based on genre, author, or thematic preferences, and can also search the web for current information.

## Features

- Natural language book recommendations based on user input
- Semantic matching using vector similarity search
- Web search for current bestsellers and popular books
- Ability to answer general knowledge questions
- Easy-to-use Streamlit interface
- Powered by LlamaIndex and Hugging Face embedding technology
- Conversational chat interface for interactive recommendations

## How to Use

1. Enter a book genre, author, or topic in the chat input
2. Ask about current bestsellers or popular books
3. Get information about new releases
4. Ask general questions when you need quick information
5. Follow up on recommendations for more details

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
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     GOOGLE_API_KEY=your_google_api_key_here
     GOOGLE_CSE_ID=your_google_cse_id_here
     ```

## Running the Application

Start the Streamlit application:
```
streamlit run streamlit_app.py
```

## Dependencies

The application depends on the following packages: