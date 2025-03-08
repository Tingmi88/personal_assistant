from search_tools import get_search_tool
import inspect

# Get the search tool
search_tool = get_search_tool()

if search_tool:
    print("Search tool initialized successfully!")
    
    # Print the type of the search tool
    print(f"Tool type: {type(search_tool)}")
    
    # Print the available methods and attributes
    print("\nAvailable methods and attributes:")
    for name in dir(search_tool):
        if not name.startswith('__'):
            print(f"- {name}")
    
    # Try to find the method that executes the search
    if hasattr(search_tool, 'invoke'):
        print("\nFound 'invoke' method. Let's try it.")
        try:
            query = "current bestseller books 2024"
            print(f"Testing query: '{query}'")
            response = search_tool.invoke(query)
            print("\nSearch Results:")
            print(response)
        except Exception as e:
            print(f"Error with invoke: {e}")
    
    # Try other potential methods
    for method_name in ['run', 'execute', 'call', '__call__']:
        if hasattr(search_tool, method_name):
            print(f"\nFound '{method_name}' method. Let's try it.")
            try:
                method = getattr(search_tool, method_name)
                query = "current bestseller books 2024"
                print(f"Testing query: '{query}'")
                response = method(query)
                print("\nSearch Results:")
                print(response)
            except Exception as e:
                print(f"Error with {method_name}: {e}")
else:
    print("Search tool initialization failed.") 