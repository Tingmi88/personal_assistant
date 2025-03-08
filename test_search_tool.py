from search_tools import get_search_tool

# Get the search tool
search_tool = get_search_tool()

if search_tool:
    print("Search tool initialized successfully!")
    
    # Test a simple query using the call method
    query = "current bestseller books 2024"
    print(f"Testing query: '{query}'")
    
    try:
        # Use the call method
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