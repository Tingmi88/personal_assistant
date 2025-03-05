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

# Load the CSV file into a DataFrame
csv_file_path = "data/books.csv"  # Adjust the path to your CSV file
df = pd.read_csv(csv_file_path)

# Convert the DataFrame into a list of LlamaIndex Document objects
documents = []
for index, row in df.iterrows():
    content = f"{row['title']} by {row['authors']}"
    metadata = {
        "id": row['id'],
        "title": row['title'],
        "authors": row['authors']
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