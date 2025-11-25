import boto3
import json
import uuid
import os
import time
import requests
from typing import List, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self, bucket_name: str = "llm-prompt-repository"):
        self.bucket_name = bucket_name
        self.mock_mode = os.environ.get("MOCK_MODE", "false").lower() == "true"
        
        if self.mock_mode:
            print("S3Service: Initialized in MOCK MODE (In-Memory Storage)")
            self._local_storage = [
                {
                    "id": "dummy-1",
                    "title": "Python Fibonacci Generator",
                    "description": "A highly efficient Fibonacci sequence generator using memoization to optimize performance for large numbers. This implementation avoids recursion depth issues.",
                    "tool_used": ["ChatGPT"],
                    "prompt_text": "Write a python function for fibonacci sequence using memoization. Ensure it handles large inputs efficiently.",
                    "tags": ["python", "algorithm", "optimization"],
                    "username": "Alice",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "dummy-2",
                    "title": "React Loading Button",
                    "description": "A reusable React button component that accepts a loading prop. It disables the button and shows a spinning loader icon when the loading state is true, preventing multiple submissions.",
                    "tool_used": ["Claude", "Cursor"],
                    "prompt_text": "Create a React button component that accepts a loading prop and shows a spinner. Use Tailwind CSS for styling.",
                    "tags": ["react", "frontend", "ui", "components"],
                    "username": "Bob",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "dummy-3",
                    "title": "SQL Join Masterclass",
                    "description": "A comprehensive explanation of different types of SQL joins (INNER, LEFT, RIGHT, FULL) with clear, practical examples using two sample tables: 'Customers' and 'Orders'.",
                    "tool_used": ["Gemini"],
                    "prompt_text": "Explain INNER, LEFT, RIGHT, and FULL OUTER joins in SQL with simple examples using Customers and Orders tables.",
                    "tags": ["sql", "database", "tutorial", "backend"],
                    "username": "Charlie",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "dummy-4",
                    "title": "AWS Lambda Deployment Script",
                    "description": "A shell script to package a Python FastAPI application and deploy it to AWS Lambda via S3. It handles dependency installation, zipping, and AWS CLI commands.",
                    "tool_used": ["Copilot"],
                    "prompt_text": "Write a bash script to zip a python lambda function with dependencies and upload to S3.",
                    "tags": ["aws", "devops", "bash", "lambda"],
                    "username": "Dave",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "dummy-5",
                    "title": "FastAPI CRUD Boilerplate",
                    "description": "A complete starter template for a FastAPI backend with SQLAlchemy, Pydantic models, and CRUD operations for a 'User' resource. Includes Dockerfile.",
                    "tool_used": ["ChatGPT", "Cursor"],
                    "prompt_text": "Generate a production-ready FastAPI boilerplate with SQLAlchemy, Pydantic, and Docker support.",
                    "tags": ["python", "fastapi", "backend", "docker"],
                    "username": "Eve",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": "dummy-6",
                    "title": "Midjourney Portrait Prompts",
                    "description": "A collection of high-quality prompts for generating realistic cyberpunk portraits in Midjourney v6. Focuses on lighting, texture, and color grading.",
                    "tool_used": ["Midjourney"],
                    "prompt_text": "Cyberpunk street samurai, neon rain, cinematic lighting, 8k resolution, photorealistic --v 6.0",
                    "tags": ["art", "midjourney", "generative-ai", "cyberpunk"],
                    "username": "Frank",
                    "created_at": datetime.now().isoformat()
                }
            ]
        else:
            self.s3 = boto3.client('s3')

    def save_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """Saves prompt data to S3 or local memory and returns the key."""
        prompt_id = str(uuid.uuid4())
        prompt_data['id'] = prompt_id
        prompt_data['created_at'] = datetime.now().isoformat()
        
        if self.mock_mode:
            self._local_storage.append(prompt_data)
            print(f"S3Service (Mock): Saved prompt {prompt_id}")
            return prompt_id
        
        key = f"prompts/{prompt_id}.json"
        
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(prompt_data),
                ContentType='application/json'
            )
            return prompt_id
        except Exception as e:
            print(f"Error saving to S3: {e}")
            raise e

    def list_prompts(self) -> List[Dict[str, Any]]:
        """Returns all prompts from S3 or local memory."""
        if self.mock_mode:
            return self._local_storage

        try:
            # List objects in the bucket
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix='prompts/')
            prompts = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.json'):
                        # Get each object (Note: Inefficient for large datasets, but fine for MVP)
                        obj_resp = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                        content = obj_resp['Body'].read().decode('utf-8')
                        prompts.append(json.loads(content))
            return prompts
        except Exception as e:
            print(f"Error listing from S3: {e}")
            return []

import time

class VectorService:
    def __init__(self, s3_service):
        self.s3_service = s3_service
        self.mock_mode = os.environ.get("MOCK_MODE", "false").lower() == "true"
        
        if self.mock_mode:
            print("VectorService: Initialized in MOCK MODE (Simple Text Search)")
            return

        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.qdrant_url = os.environ.get("QDRANT_URL")
        self.qdrant_api_key = os.environ.get("QDRANT_API_KEY")
        self.collection_name = "prompt_collection"
        
        if not self.gemini_api_key or not self.qdrant_url or not self.qdrant_api_key:
            print("WARNING: Vector DB credentials missing. Semantic search will fallback to mock.")

    def _get_embedding_rest(self, text: str):
        """Generates embedding using Gemini REST API."""
        if not self.gemini_api_key:
            return None
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "models/text-embedding-004",
            "content": {"parts": [{"text": text}]}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data["embedding"]["values"]
        except Exception as e:
            print(f"Error generating embedding via REST: {e}")
            return None

    def _ensure_collection(self):
        """Checks if collection exists via REST, creates if not."""
        if not self.qdrant_url or not self.qdrant_api_key:
            return

        headers = {"api-key": self.qdrant_api_key}
        # Check if collection exists
        check_url = f"{self.qdrant_url}/collections/{self.collection_name}"
        try:
            resp = requests.get(check_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return # Exists
        except Exception as e:
            print(f"Error checking collection: {e}")
            return

        # Create collection
        print(f"Creating collection {self.collection_name}...")
        create_url = f"{self.qdrant_url}/collections/{self.collection_name}"
        payload = {
            "vectors": {
                "size": 768,
                "distance": "Cosine"
            }
        }
        try:
            requests.put(create_url, headers=headers, json=payload, timeout=10)
        except Exception as e:
            print(f"Error creating collection: {e}")

    def add_point(self, text: str, metadata: dict):
        """Adds a point to Qdrant via REST."""
        if self.mock_mode:
            print(f"VectorService (Mock): Added point for {metadata.get('title')}")
            return True

        # 1. Get embedding
        vector = self._get_embedding_rest(text)
        if not vector:
            print("Skipping vector add: No embedding generated.")
            return False

        self._ensure_collection()

        # 2. Upsert to Qdrant
        url = f"{self.qdrant_url}/collections/{self.collection_name}/points?wait=true"
        headers = {
            "api-key": self.qdrant_api_key,
            "Content-Type": "application/json"
        }
        
        point_id = metadata.get("id")
        
        payload = {
            "points": [
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": metadata
                }
            ]
        }
        
        try:
            print(f"Upserting to collection: {self.collection_name}")
            resp = requests.put(url, headers=headers, json=payload, timeout=10)
            print(f"Qdrant Response Status: {resp.status_code}")
            print(f"Qdrant Response Body: {resp.text}")
            resp.raise_for_status()
            print(f"Successfully indexed prompt: {metadata.get('title')}")
            return True
        except Exception as e:
            print(f"Error upserting to Qdrant: {e}")
            return False

    def search(self, query_text: str, limit: int = 5):
        """Searches Qdrant via REST."""
        if self.mock_mode:
            return self._mock_search(query_text)

        # 1. Get query embedding
        vector = self._get_embedding_rest(query_text)
        
        if not vector:
            print("Fallback to mock search (no embedding)")
            return self._mock_search(query_text)

        self._ensure_collection()

        # 2. Search Qdrant
        url = f"{self.qdrant_url}/collections/{self.collection_name}/points/search"
        headers = {
            "api-key": self.qdrant_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "vector": vector,
            "limit": limit,
            "with_payload": True,
            "score_threshold": 0.01  # Lowered threshold to debug search issues
        }
        
        try:
            print(f"Searching Qdrant with query: {query_text}")
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"Qdrant Search Response: {resp.status_code} - {resp.text}")
            resp.raise_for_status()
            results = resp.json().get("result", [])
            
            # Map back to our format
            mapped_results = []
            for hit in results:
                payload = hit.get("payload", {})
                mapped_results.append({
                    "id": hit.get("id"),
                    "score": hit.get("score"),
                    **payload
                })
            return mapped_results
            
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return self._mock_search(query_text)

    def _mock_search(self, query_text: str):
        print("Performing MOCK search (substring match)")
        all_prompts = self.s3_service.list_prompts()
        results = []
        query_lower = query_text.lower()
        for p in all_prompts:
            # Simple substring match
            if (query_lower in p.get('title', '').lower() or 
                query_lower in p.get('description', '').lower() or
                query_lower in p.get('prompt_text', '').lower()):
                results.append(p)
        return results

    def generate_details(self, title: str, prompt_text: str) -> Dict[str, Any]:
        """Generates tags and description using Gemini."""
        if self.mock_mode:
            return {
                "tags": ["mock", "generated", "ai"],
                "description": f"This is a mock description for {title}. It would normally be generated by AI based on the prompt text."
            }

        if not self.gemini_api_key:
            raise Exception("GEMINI_API_KEY not set")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Construct a prompt for the model
        model_prompt = f"""
        You are a helpful assistant for a Prompt Repository which is a collection of utilities using AI and their prompts.
        When users give their utility name and the AI prompt, you will generate tags and description for them.
        Based on the following Title and Prompt Text, please generate:
        1. A concise Description (max 2 sentences). This should give an idea of what the utility does.
        2. A list of 3-5 relevant Tags (lowercase, single words).

        Title: {title}
        Prompt Text: {prompt_text}

        Output ONLY valid JSON in the following format:
        {{
            "description": "...",
            "tags": ["tag1", "tag2", "tag3"]
        }}
        """

        payload = {
            "contents": [{"parts": [{"text": model_prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            text_content = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text_content)
            
        except Exception as e:
            print(f"Error generating details: {e}")
            # Fallback
            return {
                "tags": ["error", "generation-failed"],
                "description": "Failed to generate description. Please try again."
            }

