import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Waiting for API to start...")
    time.sleep(2) # Give uvicorn a moment if we just started it (though we will start it separately)

    # 1. Test Root
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"Root: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Failed to connect to API: {e}")
        return

    # 2. Test Create Prompt
    new_prompt = {
        "title": "Test Prompt",
        "description": "A test prompt for verification",
        "tool_used": "TestTool",
        "prompt_text": "This is a test prompt.",
        "tags": ["test", "verification"]
    }
    resp = requests.post(f"{BASE_URL}/prompts", json=new_prompt)
    print(f"Create: {resp.status_code} - {resp.json()}")
    
    if resp.status_code == 200:
        # 3. Test Search
        # Search for "verification" which is in the tags
        resp = requests.get(f"{BASE_URL}/search?q=verification")
        print(f"Search 'verification': {resp.status_code} - {resp.json()}")
        
        # Search for "TestTool" which is not in the searchable text logic I implemented?
        # Wait, I implemented: f"{prompt.title} {prompt.description} {prompt.prompt_text} {' '.join(prompt.tags)}"
        # So "TestTool" is NOT in the searchable text.
        # Let's search for "Test Prompt"
        resp = requests.get(f"{BASE_URL}/search?q=Test Prompt")
        print(f"Search 'Test Prompt': {resp.status_code} - {resp.json()}")

if __name__ == "__main__":
    test_api()
