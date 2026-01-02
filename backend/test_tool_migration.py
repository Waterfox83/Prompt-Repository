"""
Simple test script for the tool migration endpoint.
Run this with: python3 test_tool_migration.py
"""
import os
os.environ["MOCK_MODE"] = "true"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_update_tools_success():
    """Test successful tool name update"""
    # Get a prompt ID from the mock data
    response = client.get("/prompts")
    assert response.status_code == 200
    prompts = response.json()["results"]
    assert len(prompts) > 0
    
    prompt_id = prompts[0]["id"]
    old_tools = prompts[0]["tool_used"]
    
    print(f"Testing with prompt ID: {prompt_id}")
    print(f"Old tools: {old_tools}")
    
    # Update the tools
    new_tools = ["ChatGPT", "Claude", "Gemini"]
    response = client.patch(
        f"/prompts/{prompt_id}/tools",
        json={"tool_names": new_tools}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["prompt_id"] == prompt_id
    assert data["old_tool_names"] == old_tools
    assert data["new_tool_names"] == new_tools
    assert "embedding_updated" in data
    
    print("✓ Test passed: Successful tool update")

def test_update_tools_not_found():
    """Test with non-existent prompt ID"""
    response = client.patch(
        "/prompts/non-existent-id/tools",
        json={"tool_names": ["ChatGPT"]}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    
    print("✓ Test passed: 404 for non-existent prompt")

def test_update_tools_empty_list():
    """Test with empty tool_names list"""
    response = client.get("/prompts")
    prompts = response.json()["results"]
    prompt_id = prompts[0]["id"]
    
    response = client.patch(
        f"/prompts/{prompt_id}/tools",
        json={"tool_names": []}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 422  # Pydantic validation error
    
    print("✓ Test passed: Validation error for empty list")

def test_update_tools_empty_strings():
    """Test with empty strings in tool_names"""
    response = client.get("/prompts")
    prompts = response.json()["results"]
    prompt_id = prompts[0]["id"]
    
    response = client.patch(
        f"/prompts/{prompt_id}/tools",
        json={"tool_names": ["ChatGPT", "", "Claude"]}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 422  # Pydantic validation error
    
    print("✓ Test passed: Validation error for empty strings")

def test_update_tools_whitespace_strings():
    """Test with whitespace-only strings in tool_names"""
    response = client.get("/prompts")
    prompts = response.json()["results"]
    prompt_id = prompts[0]["id"]
    
    response = client.patch(
        f"/prompts/{prompt_id}/tools",
        json={"tool_names": ["ChatGPT", "   ", "Claude"]}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    assert response.status_code == 422  # Pydantic validation error
    
    print("✓ Test passed: Validation error for whitespace-only strings")

if __name__ == "__main__":
    print("Running tool migration endpoint tests...\n")
    
    try:
        test_update_tools_success()
        print()
        test_update_tools_not_found()
        print()
        test_update_tools_empty_list()
        print()
        test_update_tools_empty_strings()
        print()
        test_update_tools_whitespace_strings()
        print()
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
