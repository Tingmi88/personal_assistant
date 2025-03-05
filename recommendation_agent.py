from llama_index_config import query_engine

def generate_recommendation(user_input, category='books'):
    # Retrieve relevant documents
    documents = query_engine.retrieve(user_input, category=category)
    
    # Generate a recommendation based on the retrieved documents
    recommendation = query_engine.generate(user_input, documents)
    
    return recommendation 