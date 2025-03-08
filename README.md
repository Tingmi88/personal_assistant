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

## Technical Architecture

### Models and Embeddings
- **Embedding Model**: BAAI/bge-small-en-v1.5 (Hugging Face)
- **LLM**: OpenAI GPT-3.5-Turbo for query routing and response generation
- **Vector Store**: LlamaIndex's built-in vector store for document retrieval

### Data Processing
- **Data Source**: Goodreads book dataset (CSV format)
- **Text Representation**: Prioritizes book descriptions in the embedding to improve semantic matching
- **Metadata Extraction**: Extracts book titles, authors, genres, ratings, and URLs for filtering and display

### Query Pipeline
1. **Query Classification**: Determines if the query is about:
   - Book recommendations (uses local vector database)
   - Current book trends (uses web search)
   - General knowledge (uses web search)
   
2. **Router Query Engine**: Directs queries to the appropriate tool based on classification:
   - Book database tool for recommendations
   - Web search tool for current trends
   - Web search tool for general knowledge

3. **Response Generation**: Formats responses with:
   - Book title and author
   - Brief description
   - Relevance explanation
   - Rating information
   - Purchase links

### Web Search Integration
- **Search Provider**: Google Custom Search API
- **Implementation**: Uses LlamaIndex's GoogleSearchToolSpec
- **Use Cases**: Current bestsellers, new releases, and general knowledge questions

### Conversation Management
- **History Tracking**: Maintains conversation context for follow-up questions
- **Context Window**: Uses the most recent 10 messages to keep context relevant

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