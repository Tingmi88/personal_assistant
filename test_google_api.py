import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_api():
    """Test Google Custom Search API directly with requests."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if not google_api_key or not google_cse_id:
        print("Error: Missing API credentials")
        print(f"API Key present: {'Yes' if google_api_key else 'No'}")
        print(f"CSE ID present: {'Yes' if google_cse_id else 'No'}")
        return False
    
    # Print first and last few characters of credentials (for debugging)
    print(f"API Key: {google_api_key[:4]}...{google_api_key[-4:]}")
    print(f"CSE ID: {google_cse_id[:4]}...{google_cse_id[-4:]}")
    
    # Construct the API URL
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": google_api_key,
        "cx": google_cse_id,
        "q": "current bestseller books"
    }
    
    try:
        # Make the request
        response = requests.get(url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            print("API request successful!")
            print(f"Found {len(data.get('items', []))} search results")
            
            # Print the first result title
            if data.get('items'):
                print(f"First result: {data['items'][0]['title']}")
            return True
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("Testing Google API...")
    test_google_api()