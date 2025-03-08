from llama_index.tools.google import GoogleSearchToolSpec
import inspect

def inspect_google_search_tool():
    """Inspect the GoogleSearchToolSpec class to see its parameters."""
    # Print the signature of the constructor
    print("GoogleSearchToolSpec constructor signature:")
    print(inspect.signature(GoogleSearchToolSpec.__init__))
    
    # Print the docstring if available
    print("\nDocstring:")
    print(GoogleSearchToolSpec.__init__.__doc__)
    
    # Print the source code if possible
    try:
        print("\nSource code:")
        print(inspect.getsource(GoogleSearchToolSpec.__init__))
    except Exception as e:
        print(f"Couldn't get source code: {e}")
    
    # Print the module path
    print("\nModule path:")
    print(GoogleSearchToolSpec.__module__)

if __name__ == "__main__":
    inspect_google_search_tool() 