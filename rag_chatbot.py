import pandas as pd
from llama_index.core import VectorStoreIndex, Document, Settings
import streamlit as st
from dotenv import load_dotenv
import os
from llama_index.embeddings.openai import OpenAIEmbedding

# Load environment variables
load_dotenv()

# Now you can access the API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up the embedding model
Settings.embed_model = OpenAIEmbedding(api_key=openai_api_key)

# Load the CSV file into a DataFrame with explicit encoding
try:
    # Try UTF-8 encoding first
    csv_file_path = "data/goodreads_data.csv"
    df = pd.read_csv(csv_file_path, encoding='utf-8')
except UnicodeDecodeError:
    # If UTF-8 fails, try with a different encoding
    df = pd.read_csv(csv_file_path, encoding='latin1')

# Clean the data to handle potential Unicode issues
def clean_text(text):
    if isinstance(text, str):
        # Replace problematic characters or normalize Unicode
        return text.encode('ascii', 'ignore').decode('ascii')
    return str(text)

# Helper function to safely convert string numbers with commas to integers
def safe_int_convert(value):
    if pd.isna(value):
        return 1  # Default to 1 rating if missing
    try:
        # Remove commas and convert to int
        result = int(str(value).replace(',', ''))
        return max(1, result)  # Ensure at least 1 rating
    except (ValueError, TypeError):
        return 1

# Helper function to safely convert to float within rating range
def safe_rating_convert(value):
    if pd.isna(value):
        return 3.0  # Default to neutral rating if missing
    try:
        result = float(value)
        return max(0, min(5, result))  # Clamp between 0 and 5
    except (ValueError, TypeError):
        return 3.0

# Convert the DataFrame into a list of LlamaIndex Document objects
documents = []
for index, row in df.iterrows():
    # Clean the text data for all relevant fields
    book = clean_text(row['Book'])
    author = clean_text(row['Author'])
    description = clean_text(row['Description'])
    genres = clean_text(row['Genres'])
    
    # Convert numerical ratings with appropriate constraints
    avg_rating = safe_rating_convert(row['Avg_Rating'])
    num_ratings = safe_int_convert(row['Num_Ratings'])
    
    # Add rating information as contextual text
    rating_tier = "highly rated" if avg_rating >= 4.5 else \
                 "well rated" if avg_rating >= 4.0 else \
                 "positively rated" if avg_rating >= 3.5 else \
                 "moderately rated"
                 
    popularity = "extremely popular" if num_ratings > 1000000 else \
                "very popular" if num_ratings > 100000 else \
                "popular" if num_ratings > 10000 else \
                "somewhat known" if num_ratings > 1000 else \
                "niche"
                
    rating_context = f"This book is {rating_tier} with an average of {avg_rating:.1f}/5 from {num_ratings:,} readers, making it {popularity}."
    
    # Create rich content for embedding by combining multiple fields
    content = f"Book: {book}\nAuthor: {author}\nDescription: {description}\nGenres: {genres}\n{rating_context}"
    
    # Store all relevant fields in metadata
    metadata = {
        "id": row['ID'],
        "title": book,
        "author": author,
        "genres": genres,
        "avg_rating": avg_rating,
        "num_ratings": num_ratings
    }
    
    doc = Document(text=content, metadata=metadata)
    documents.append(doc)

# Initialize LlamaIndex with documents
index = VectorStoreIndex.from_documents(documents)

# Define a function to handle user input and generate book recommendations
def generate_book_recommendation(user_input):
    # Create a query engine
    query_engine = index.as_query_engine()
    
    # Generate a recommendation based on the user input
    response = query_engine.query(user_input)
    
    return response.response