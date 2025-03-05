from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

# Set up the embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name='BAAI/bge-small-en-v1.5')

# Define the directory for storing the index
PERSIST_DIR = "./storage"

# Load or create the index
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

# Create a query engine
query_engine = index.as_query_engine() 