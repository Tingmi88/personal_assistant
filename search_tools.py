import os
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.tools.google import GoogleSearchToolSpec
from dotenv import load_dotenv
import datetime
import re
import inspect

# Load environment variables
load_dotenv()

def get_search_tool():
    """Create and return a Google Search tool for external information retrieval."""
    # Make sure you have GOOGLE_API_KEY and GOOGLE_CSE_ID in your .env file
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if not google_api_key or not google_cse_id:
        print("Warning: Google Search API credentials not found. External search disabled.")
        return None
    
    try:
        # Use the exact parameter names from the constructor signature:
        # key, engine, and num
        search_tool_spec = GoogleSearchToolSpec(
            key=google_api_key,
            engine=google_cse_id,
            num=10
        )
        
        # Print success message
        print("Successfully created GoogleSearchToolSpec")
        
        # Get the tool list
        search_tools = search_tool_spec.to_tool_list()
        
        # Return the search tool
        return search_tools[0]  # The first tool is the search tool
    except Exception as e:
        print(f"Error initializing Google Search tool: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_current_date():
    """Return the current date as a formatted string."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y")

def is_general_knowledge_query(query):
    """Determine if a query is asking for general knowledge rather than book recommendations."""
    query = query.lower().strip()
    
    # Direct general knowledge indicators
    general_knowledge_indicators = [
        "what day is", "what time is", "who is", "where is", "when is",
        "how to", "how do", "what does", "what is the weather", "what is today",
        "current events", "news about", "tell me about", "explain"
    ]
    
    # Check for general knowledge indicators
    for indicator in general_knowledge_indicators:
        if indicator in query:
            return True
    
    return False

def is_current_book_trend_query(query):
    """Determine if a query is asking about current book trends or bestsellers."""
    query = query.lower().strip()
    
    # Book trend indicators
    trend_indicators = [
        "bestseller", "trending", "popular", "new release", "just published",
        "top selling", "this year", "this month", "this week", "recent",
        "current", "latest", "now", "today", "2023", "2024"
    ]
    
    # Book-related terms
    book_terms = [
        "book", "novel", "author", "read", "fiction", "nonfiction", 
        "bestseller", "series", "publish"
    ]
    
    # Check for trend indicators
    has_trend_term = any(term in query for term in trend_indicators)
    has_book_term = any(term in query for term in book_terms)
    
    # If the query contains both a trend indicator and a book term, it's likely about current book trends
    return has_trend_term and has_book_term

def get_bestseller_list(list_type="nyt"):
    """
    Get the current bestseller list directly.
    
    Args:
        list_type (str): The type of bestseller list to retrieve. Options: "nyt" (New York Times),
                         "amazon", "barnes_noble"
    
    Returns:
        str: A formatted string containing the bestseller information
    """
    search_tool = get_search_tool()
    if not search_tool:
        return "Unable to retrieve bestseller information. Search tool not available."
    
    try:
        if list_type == "nyt":
            # Search for NYT fiction bestsellers
            fiction_results = search_tool.call("current New York Times fiction bestseller list top 5")
            
            # Search for NYT nonfiction bestsellers
            nonfiction_results = search_tool.call("current New York Times nonfiction bestseller list top 5")
            
            # Convert results to string if they're not already
            fiction_str = str(fiction_results)
            nonfiction_str = str(nonfiction_results)
            
            # If the results are a list of documents, extract text from them
            if isinstance(fiction_results, list) and len(fiction_results) > 0:
                fiction_str = "\n".join([doc.get_text() for doc in fiction_results])

            if isinstance(nonfiction_results, list) and len(nonfiction_results) > 0:
                nonfiction_str = "\n".join([doc.get_text() for doc in nonfiction_results])
            
            # Combine the results
            combined_results = "# Current New York Times Bestsellers\n\n"
            combined_results += "## Fiction\n" + fiction_str + "\n\n"
            combined_results += "## Nonfiction\n" + nonfiction_str
            
            return combined_results
        
        elif list_type == "amazon":
            results = search_tool.call("current Amazon bestselling books top 10")
            if isinstance(results, list) and len(results) > 0:
                return "\n".join([doc.get_text() for doc in results])
            return str(results)
        
        elif list_type == "barnes_noble":
            results = search_tool.call("current Barnes and Noble bestselling books top 10")
            if isinstance(results, list) and len(results) > 0:
                return "\n".join([doc.get_text() for doc in results])
            return str(results)
        
        else:
            results = search_tool.call(f"current {list_type} bestselling books top 10")
            if isinstance(results, list) and len(results) > 0:
                return "\n".join([doc.get_text() for doc in results])
            return str(results)
    
    except Exception as e:
        return f"Error retrieving bestseller information: {e}"

def inspect_google_search_tool():
    """Inspect the GoogleSearchToolSpec class to see its parameters."""
    # Print the signature of the constructor
    print("GoogleSearchToolSpec constructor signature:")
    print(inspect.signature(GoogleSearchToolSpec.__init__))
    
    # Try to create an instance with different parameter combinations
    print("\nTrying different parameter combinations:")
    
    # Test 1: Positional arguments
    try:
        spec1 = GoogleSearchToolSpec("test_key", "test_id")
        print("✓ Created with positional arguments")
    except Exception as e:
        print(f"✗ Failed with positional arguments: {e}")
    
    # Test 2: Named arguments (google_api_key, google_cse_id)
    try:
        spec2 = GoogleSearchToolSpec(google_api_key="test_key", google_cse_id="test_id")
        print("✓ Created with google_api_key and google_cse_id")
    except Exception as e:
        print(f"✗ Failed with google_api_key and google_cse_id: {e}")
    
    # Test 3: Named arguments (api_key, cse_id)
    try:
        spec3 = GoogleSearchToolSpec(api_key="test_key", cse_id="test_id")
        print("✓ Created with api_key and cse_id")
    except Exception as e:
        print(f"✗ Failed with api_key and cse_id: {e}")

if __name__ == "__main__":
    inspect_google_search_tool()

# Get the search tool
search_tool = get_search_tool()

if search_tool:
    print("Search tool initialized successfully!")
    
    # Test a simple query using the call method
    query = "current bestseller books 2024"
    print(f"Testing query: '{query}'")
    
    try:
        # Use the call method instead of _run
        response = search_tool.call(query)
        print("\nSearch Results:")
        print(response)
        
        # If the response is a list of documents, extract the text
        if isinstance(response, list) and len(response) > 0:
            print("\nExtracted text from first document:")
            print(response[0].get_text())
    except Exception as e:
        print(f"Error executing search: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Search tool initialization failed.") 