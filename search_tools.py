import os
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.tools.google import GoogleSearchToolSpec
from dotenv import load_dotenv
import datetime
import re

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
        # Initialize the Google Search tool with the correct parameters
        # The API has changed, so we need to use the correct parameter names
        search_tool_spec = GoogleSearchToolSpec(
            google_api_key=google_api_key,  # Changed from api_key
            google_cse_id=google_cse_id,    # Changed from cse_id
            num_results=10  # Increase number of results for better coverage
        )
        search_tools = search_tool_spec.to_tool_list()
        
        # Return the search tool
        return search_tools[0]  # The first tool is the search tool
    except Exception as e:
        print(f"Error initializing Google Search tool: {e}")
        return None

def get_current_date():
    """Return the current date as a formatted string."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y")

def is_general_knowledge_query(query):
    """Determine if a query is asking for general knowledge rather than book recommendations."""
    query = query.lower().strip()
    
    # Direct general knowledge patterns
    direct_patterns = [
        r"what (day|date) is (it|today)",
        r"what is (the current|today's) date",
        r"what time is it",
        r"what is the weather",
        r"who is [^a-z]",  # "who is X" where X is not a book-related term
        r"where is [^a-z]",
        r"when (did|was) [^a-z]",
        r"why (does|do|is|are) [^a-z]",
        r"how (to|do|does|can) [^a-z]",
        r"what happened",
        r"tell me about [^a-z](?!.*book)",  # "tell me about X" where X is not followed by "book"
        r"explain [^a-z](?!.*book)",
        r"define [^a-z]",
        r"meaning of [^a-z]",
        r"calculate [^a-z]",
        r"convert [^a-z]",
        r"translate [^a-z]"
    ]
    
    # Check direct patterns
    for pattern in direct_patterns:
        if re.search(pattern, query):
            return True
    
    # Keywords that suggest general knowledge questions
    general_knowledge_keywords = [
        "what day is", "what is today", "current date", "today's date",
        "what time is", "weather", "news", "who is", "where is",
        "how to", "when did", "why does", "explain", "definition of",
        "meaning of", "calculate", "convert", "translate"
    ]
    
    # Check if any general knowledge keywords are in the query
    if any(keyword in query for keyword in general_knowledge_keywords):
        return True
    
    # Check for question words not followed by book-related terms
    question_patterns = [
        "what is", "what are", "who is", "who are", "where is", 
        "where are", "when is", "when are", "why is", "why are",
        "how is", "how are", "can you tell me"
    ]
    
    book_related_terms = [
        "book", "novel", "author", "read", "genre", "fiction", "nonfiction",
        "bestseller", "literature", "story", "series", "character", "publish",
        "writer", "writing", "plot", "chapter", "page", "volume", "edition",
        "library", "bookstore", "ebook", "audiobook", "hardcover", "paperback"
    ]
    
    for pattern in question_patterns:
        if pattern in query:
            # Check if any book-related term follows the question pattern
            query_after_pattern = query[query.find(pattern) + len(pattern):]
            if not any(term in query_after_pattern for term in book_related_terms):
                return True
    
    return False

def is_current_book_trend_query(query):
    """Determine if a query is asking about current book trends or bestsellers."""
    query = query.lower().strip()
    
    # Direct bestseller list patterns
    bestseller_patterns = [
        r"(what('s| is)|which are) (the )?(current|latest|today's|this week'?s|this month'?s|recent|new) (bestsell(er|ing)|best[ -]sell(er|ing))",
        r"(what('s| is)|which are) (the )?(bestsell(er|ing)|best[ -]sell(er|ing)) (list|books|novels)",
        r"(new york times|nyt|amazon|barnes(\s|&|\sand\s)noble|usa today|wall street journal|wsj) bestsell(er|ing)",
        r"(top|most popular|trending) books (right now|currently|today|this week|this month|this year)",
        r"what books are (trending|popular|hot|bestsell(er|ing)) (right now|currently|today|this week|this month)"
    ]
    
    # Check direct bestseller patterns
    for pattern in bestseller_patterns:
        if re.search(pattern, query):
            return True
    
    # Keywords that suggest current book trends
    trend_keywords = [
        "bestseller", "best seller", "best-seller", "trending", "popular",
        "top books", "new release", "just published", "this week", "this month",
        "this year", "latest", "current", "now", "recent", "upcoming",
        "hot", "award", "prize", "most read", "most popular", "new york times",
        "nyt", "amazon", "barnes & noble", "usa today"
    ]
    
    # Check if any trend keywords are in the query and it's about books
    has_trend_keyword = any(keyword in query for keyword in trend_keywords)
    has_book_keyword = any(word in query for word in ["book", "novel", "read", "author", "bestseller", "list"])
    
    return has_trend_keyword and has_book_keyword 

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
            fiction_results = search_tool._run("current New York Times fiction bestseller list top 5")
            
            # Search for NYT nonfiction bestsellers
            nonfiction_results = search_tool._run("current New York Times nonfiction bestseller list top 5")
            
            # Combine the results
            combined_results = "# Current New York Times Bestsellers\n\n"
            combined_results += "## Fiction\n" + fiction_results + "\n\n"
            combined_results += "## Nonfiction\n" + nonfiction_results
            
            return combined_results
        
        elif list_type == "amazon":
            return search_tool._run("current Amazon bestselling books top 10")
        
        elif list_type == "barnes_noble":
            return search_tool._run("current Barnes and Noble bestselling books top 10")
        
        else:
            return search_tool._run(f"current {list_type} bestselling books top 10")
    
    except Exception as e:
        return f"Error retrieving bestseller information: {e}" 