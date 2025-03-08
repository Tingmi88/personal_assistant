from dotenv import load_dotenv
from search_tools import get_search_tool, is_general_knowledge_query, is_current_book_trend_query
import os

# Load environment variables
load_dotenv()

def test_query_classification():
    """Test the query classification functions."""
    # Test general knowledge queries
    general_queries = [
        "what day is today",
        "what is the weather like",
        "who is the president",
        "how to make pasta",
        "what time is it in New York"
    ]
    
    for query in general_queries:
        result = is_general_knowledge_query(query)
        print(f"Query: '{query}' - Is general knowledge: {result}")
    
    # Test book trend queries
    trend_queries = [
        "what's currently on the New York Times bestseller list",
        "what are the top books this week",
        "what are the bestselling books right now",
        "current popular fiction books",
        "trending novels this month"
    ]
    
    for query in trend_queries:
        result = is_current_book_trend_query(query)
        print(f"Query: '{query}' - Is book trend: {result}")

def test_search_tool():
    """Test the search tool functionality."""
    # Check if API keys are set
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if not google_api_key:
        print("\nGoogle API Key is missing. Please set the GOOGLE_API_KEY environment variable.")
    else:
        print(f"\nGoogle API Key found: {google_api_key[:5]}...{google_api_key[-5:]}")
        
    if not google_cse_id:
        print("\nGoogle CSE ID is missing. Please set the GOOGLE_CSE_ID environment variable.")
    else:
        print(f"\nGoogle CSE ID found: {google_cse_id[:5]}...{google_cse_id[-5:]}")
    
    search_tool = get_search_tool()
    
    if not search_tool:
        print("\nSearch tool not available. Check your API keys and make sure they're correctly set in your .env file.")
        return
    else:
        print("\nSearch tool initialized successfully.")
    
    # Test a bestseller query with a more specific search term
    query = "current New York Times fiction bestseller list"
    print(f"\nTesting search for: '{query}'")
    
    # Create a query engine from the search tool
    search_query_engine = search_tool.as_query_engine()
    
    # Execute the query
    try:
        response = search_query_engine.query(query)
        print("\nSearch Results:")
        print(response.response)
    except Exception as e:
        print(f"\nError executing search query: {e}")
        print("\nThis could be due to API rate limits, invalid credentials, or network issues.")

def test_direct_search():
    """Test direct search without using the query engine."""
    search_tool = get_search_tool()
    
    if not search_tool:
        print("\nSearch tool not available.")
        return
    
    # Test direct search method if available
    try:
        # This is a more direct way to use the search tool
        search_results = search_tool._run("New York Times bestseller list fiction")
        print("\nDirect Search Results:")
        print(search_results)
    except Exception as e:
        print(f"\nError with direct search: {e}")

if __name__ == "__main__":
    print("Testing query classification:")
    test_query_classification()
    
    print("\nTesting search tool:")
    test_search_tool()
    
    print("\nTesting direct search:")
    test_direct_search() 