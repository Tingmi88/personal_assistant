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
        # Create a rich text representation of each book
        text = f"Title: {row['Book']}\nAuthor: {row['Author']}\nDescription: {row['Description']}\n"
        text += f"Genres: {row['Genres']}\n"
        text += f"Average Rating: {row['Avg_Rating']}\nNumber of Ratings: {row['Num_Ratings']}\n"
        text += f"URL: {row['URL']}"
        
        # Create metadata for better retrieval
        metadata = {
            "title": row['Book'],
            "author": row['Author'],
            "genres": row['Genres'],
            "avg_rating": row['Avg_Rating'],
            "num_ratings": row['Num_Ratings'],
            "url": row['URL']
        }
        
        # Create a node with the text and metadata
        node = TextNode(text=text, metadata=metadata)
        nodes.append(node)
    
    # Create the index with the nodes using our consistent embedding model
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

def generate_book_recommendation(user_input, conversation_history=None):
    """Generate book recommendations based on user input and conversation history."""
    # Create a query engine with more specific parameters
    query_engine = index.as_query_engine(
        similarity_top_k=8,  # Retrieve more documents for diversity
        response_mode="compact"
    )
    
    # Prepare the prompt based on conversation history
    if conversation_history and len(conversation_history) > 0:
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
        
        Conversation history:
        {conversation_history}
        
        Current query: {user_input}
        
        Provide thoughtful, personalized recommendations that explain why each book matches what the user is looking for.
        """
    else:
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
        
        Provide thoughtful, personalized recommendations that explain why each book matches what the user is looking for.
        """
    
    # Generate a recommendation based on the user input
    response = query_engine.query(prompt)
    
    return response.response