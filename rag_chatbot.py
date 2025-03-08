import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
import pandas as pd
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import TextNode
from llama_index.core import StorageContext, load_index_from_storage
from dotenv import load_dotenv
import shutil
from search_tools import get_search_tool, get_current_date, is_general_knowledge_query, is_current_book_trend_query
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import QueryEngineTool, ToolMetadata

# Load environment variables
load_dotenv()

# Define embedding model - use the same model consistently
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Configure global settings
Settings.embed_model = embed_model

# Force recreate the index to ensure consistent embeddings
PERSIST_DIR = "./storage"
if os.path.exists(PERSIST_DIR):
    # Remove the existing index to recreate it with the correct embeddings
    shutil.rmtree(PERSIST_DIR)

# Create a new index from the CSV data
try:
    # Load the CSV file
    df = pd.read_csv('data/goodreads_sample_100.csv')
    
    # Create nodes from the dataframe
    nodes = []
    for _, row in df.iterrows():
        # Prioritize the description in the text representation
        # Put description first to give it more weight in the embedding
        text = f"Description: {str(row['Description']) if pd.notna(row['Description']) else 'No description available'}\n\n"
        text += f"Title: {row['Book']}\nAuthor: {row['Author']}\n"
        text += f"Genres: {row['Genres'] if pd.notna(row['Genres']) else 'Unknown'}\n"
        text += f"Average Rating: {row['Avg_Rating'] if pd.notna(row['Avg_Rating']) else 'Not rated'}\n"
        text += f"Number of Ratings: {row['Num_Ratings'] if pd.notna(row['Num_Ratings']) else '0'}\n"
        text += f"URL: {row['URL'] if pd.notna(row['URL']) else 'No URL available'}"
        
        # Create metadata for better retrieval
        metadata = {
            "title": row['Book'],
            "author": row['Author'],
            "genres": row['Genres'] if pd.notna(row['Genres']) else "Unknown",
            "avg_rating": row['Avg_Rating'] if pd.notna(row['Avg_Rating']) else "Not rated",
            "num_ratings": row['Num_Ratings'] if pd.notna(row['Num_Ratings']) else 0,
            "url": row['URL'] if pd.notna(row['URL']) else "No URL available",
            # Add a snippet of the description to metadata for filtering
            "description_snippet": (row['Description'][:100] + "..." if len(str(row['Description'])) > 100 else str(row['Description'])) 
                                   if pd.notna(row['Description']) else "No description available"
        }
        
        # Create a node with the text and metadata
        node = TextNode(text=text, metadata=metadata)
        nodes.append(node)
    
    # Create the index with the nodes using our consistent embedding model
    # Adjust chunk size to accommodate longer descriptions (default is often 1024)
    index = VectorStoreIndex(nodes)
    
    # Save the index
    index.storage_context.persist(PERSIST_DIR)
    
except FileNotFoundError:
    print("CSV file not found. Please make sure the data file exists.")
    # Create a simple index with dummy data so the app doesn't crash
    dummy_nodes = [TextNode(text="Sample book data not found")]
    index = VectorStoreIndex(dummy_nodes)
    index.storage_context.persist(PERSIST_DIR)

# Now load the index with the same embedding model
storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
index = load_index_from_storage(storage_context)

def get_diverse_recommendations(query, top_k=10):
    """Get diverse book recommendations by combining semantic search with filtering."""
    # Get the base retriever
    retriever = index.as_retriever(similarity_top_k=top_k)
    
    # Retrieve documents
    nodes = retriever.retrieve(query)
    
    # Track seen books to avoid duplicates
    seen_books = set()
    diverse_nodes = []
    
    for node in nodes:
        book_title = node.metadata.get("title", "")
        if book_title and book_title not in seen_books:
            seen_books.add(book_title)
            diverse_nodes.append(node)
    
    return diverse_nodes

def create_router_query_engine():
    """Create a router query engine that can choose between local index and web search."""
    # Get the base query engine from our book index
    book_query_engine = index.as_query_engine(
        similarity_top_k=8,
        response_mode="compact"
    )
    
    # Get the search tool
    search_tool = get_search_tool()
    
    if not search_tool:
        # If search tool isn't available, just return the book query engine
        return book_query_engine
    
    # Create a wrapper function to adapt the search tool to a query engine interface
    def search_query_wrapper(query_str):
        from llama_index.core.response_synthesizers import get_response_synthesizer
        from llama_index.core.schema import Response
        
        try:
            # Use the call method of the search tool
            search_result = search_tool.call(query_str)
            
            # If the result is a list of documents, extract text from them
            if isinstance(search_result, list) and len(search_result) > 0:
                # Extract text from all documents
                texts = [doc.get_text() for doc in search_result]
                combined_text = "\n\n".join(texts)
                return Response(response=combined_text)
            else:
                # Return the result as is
                return Response(response=str(search_result))
        except Exception as e:
            print(f"Error in search query: {e}")
            return Response(response=f"Error performing search: {str(e)}")
    
    # Create a simple wrapper class that mimics a query engine
    class SearchToolQueryEngine:
        def query(self, query_str):
            return search_query_wrapper(query_str)
    
    # Create the search query engine
    search_query_engine = SearchToolQueryEngine()
    
    # Create tool for the book index
    book_tool = QueryEngineTool(
        query_engine=book_query_engine,
        metadata=ToolMetadata(
            name="book_database",
            description="Useful for answering questions about books in the local database. Use this for general book recommendations based on genres, authors, or themes."
        )
    )
    
    # Create tool for the search engine for book trends
    book_trends_tool = QueryEngineTool(
        query_engine=search_query_engine,
        metadata=ToolMetadata(
            name="book_trends_search",
            description="Useful for answering questions about current book trends, bestsellers, new releases, or popular books that might not be in the local database. Use this when the user asks about what's popular or trending now."
        )
    )
    
    # Create tool for general knowledge questions
    general_knowledge_tool = QueryEngineTool(
        query_engine=search_query_engine,
        metadata=ToolMetadata(
            name="general_knowledge",
            description="Useful for answering general knowledge questions not related to books, such as current date, news, facts, or other information. Use this when the user asks questions that aren't about book recommendations."
        )
    )
    
    # Create the LLM for selection
    llm = OpenAI(model="gpt-3.5-turbo")
    
    # Create the router query engine with all three tools
    router_query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(llm=llm),
        query_engine_tools=[book_tool, book_trends_tool, general_knowledge_tool],
    )
    
    return router_query_engine

def generate_book_recommendation(user_input, conversation_history=None):
    """Generate book recommendations based on user input and conversation history."""
    # Normalize input for pattern matching
    normalized_input = user_input.lower().strip()
    
    # Check if the input is a simple greeting
    greeting_phrases = ["hi", "hello", "hey", "greetings", "howdy", "hi there", "hello there"]
    if normalized_input in greeting_phrases or normalized_input.startswith(tuple(greeting_phrases)):
        return """Hello! I'm your book recommendation assistant. I can help you find books based on:
        
- Genres you enjoy
- Authors similar to ones you like
- Specific themes or topics
- Your reading preferences
- Current bestsellers and popular books

What kind of books are you interested in today?"""
    
    # Handle compliments and positive feedback
    compliment_phrases = ["you are good", "you're good", "that's great", "that was helpful", 
                         "thank you", "thanks", "good job", "well done", "awesome", "excellent"]
    if any(phrase in normalized_input for phrase in compliment_phrases):
        return """Thank you for the kind words! I'm glad I could help.

Is there a specific type of book you're looking for today? Or would you like more recommendations similar to ones we've discussed?"""
    
    # Handle goodbyes
    goodbye_phrases = ["bye", "goodbye", "see you", "farewell", "that's all", "exit", "quit"]
    if any(phrase in normalized_input for phrase in goodbye_phrases):
        return """It was a pleasure helping you find books today! Feel free to come back anytime you need new reading recommendations. Happy reading!"""
    
    # Handle general questions about the assistant
    about_assistant_phrases = ["who are you", "what can you do", "how do you work", "what are you"]
    if any(phrase in normalized_input for phrase in about_assistant_phrases):
        return """I'm a book recommendation assistant designed to help you discover books you might enjoy. 
        
I can suggest books based on:
- Authors you like
- Genres you enjoy
- Themes or topics you're interested in
- Your reading preferences and past favorites
- Current bestsellers and popular books (I can search the web for this!)

I can also answer general questions about dates, news, and other information.

What kind of books would you like me to recommend today?"""
    
    # Handle date/time questions directly
    if "what day is today" in normalized_input or "what is today" in normalized_input or "current date" in normalized_input:
        current_date = get_current_date()
        return f"Today is {current_date}. How can I help you with book recommendations today?"
    
    # Handle specific bestseller list requests directly
    nyt_patterns = ["new york times bestseller", "nyt bestseller", "ny times bestseller"]
    amazon_patterns = ["amazon bestseller", "amazon best seller", "amazon top books"]
    bn_patterns = ["barnes", "noble", "b&n", "barnes & noble"]
    
    if any(pattern in normalized_input for pattern in nyt_patterns):
        from search_tools import get_bestseller_list
        return get_bestseller_list("nyt")
    elif any(pattern in normalized_input for pattern in amazon_patterns):
        from search_tools import get_bestseller_list
        return get_bestseller_list("amazon")
    elif any(pattern in normalized_input for pattern in bn_patterns) and ("bestseller" in normalized_input or "best seller" in normalized_input):
        from search_tools import get_bestseller_list
        return get_bestseller_list("barnes_noble")
    
    # Get the router query engine that can choose between local data and web search
    query_engine = create_router_query_engine()
    
    # Determine the type of query
    is_general = is_general_knowledge_query(user_input)
    is_trend = is_current_book_trend_query(user_input)
    
    # Prepare the prompt based on conversation history and query type
    if is_general:
        # For general knowledge questions
        prompt = f"""
        You are an intelligent assistant. The user has asked: "{user_input}"
        
        This appears to be a general knowledge question not directly related to book recommendations.
        Please answer this question accurately and concisely using the search tool.
        
        After answering their question, you can gently remind them that you're primarily a book recommendation
        assistant and ask if they'd like book recommendations.
        """
    elif is_trend:
        # For current book trends
        prompt = f"""
        You are an intelligent book recommendation assistant. The user has asked about current book trends: "{user_input}"
        
        This is a request for CURRENT bestsellers or popular books. You MUST use the book_trends_search tool to search 
        the web for up-to-date information about current bestsellers, popular books, or recent releases.
        
        DO NOT rely on your internal knowledge or the book database for this query, as that information may be outdated.
        
        When searching, use specific search terms like "current New York Times bestseller list" or "Amazon top books this week"
        to get the most recent information.
        
        For each book you recommend, include:
        - Title and author
        - Brief description
        - Why it's currently popular or trending
        - Rating information if available
        - Purchase link if available
        
        Present the information in a clear, organized format with 3-5 relevant recommendations.
        
        If you're unable to find current bestseller information, clearly state that you couldn't retrieve 
        the latest bestseller data and suggest the user check official sources like the New York Times 
        bestseller list website or Amazon's bestseller page.
        """
    elif conversation_history and len(conversation_history) > 0:
        # For regular book recommendations with conversation history
        prompt = f"""
        You are an intelligent book recommendation agent. Based on the following conversation history and the current query, 
        recommend 3-5 diverse and relevant books that match the user's interests.
        
        Consider these factors in your recommendations:
        1. Content similarity to what the user is looking for
        2. Author style if the user mentions an author they like
        3. Genre preferences expressed by the user
        4. Book ratings and popularity when relevant
        
        For each recommendation, include:
        - Title and author
        - Brief description
        - Why you're recommending it (based on their query)
        - Rating information if relevant
        - Purchase link (use the URL from the metadata or search results)
        
        Conversation history:
        {conversation_history}
        
        Current query: {user_input}
        
        Provide thoughtful, personalized recommendations that explain why each book matches what the user is looking for.
        Always include the purchase link for each book if available.
        """
    else:
        # For regular book recommendations without conversation history
        prompt = f"""
        You are an intelligent book recommendation agent. Based on the query: "{user_input}", 
        recommend 3-5 diverse and relevant books.
        
        Consider these factors in your recommendations:
        1. Content similarity to what the user is looking for
        2. Author style if the user mentions an author they like
        3. Genre preferences expressed by the user
        4. Book ratings and popularity when relevant
        
        For each recommendation, include:
        - Title and author
        - Brief description
        - Why you're recommending it (based on their query)
        - Rating information if relevant
        - Purchase link (use the URL from the metadata or search results)
        
        Provide thoughtful, personalized recommendations that explain why each book matches what the user is looking for.
        Always include the purchase link for each book if available.
        """
    
    # Generate a response based on the user input
    response = query_engine.query(prompt)
    
    return response.response