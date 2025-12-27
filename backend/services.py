import boto3
import json
import uuid
import os
import time
import requests
import numpy as np
import io
from typing import List, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError

class SESService:
    def __init__(self):
        self.mock_mode = os.environ.get("MOCK_MODE", "false").lower() == "true"
        self.sender_email = os.environ.get("SES_SENDER_EMAIL", "no-reply@pega.com")
        self._mock_verified_emails = set() # Track verified emails in mock mode
        
        if self.mock_mode:
            print("SESService: Initialized in MOCK MODE")
        else:
            self.ses = boto3.client('ses')

    def get_identity_status(self, email: str) -> str:
        """Checks if the email is verified in SES."""
        if self.mock_mode:
            # If we've "verified" it in this session, return Success
            if email in self._mock_verified_emails:
                return "Success"
                
            # Simulate unverified for specific test email
            if email.lower() == "unverified@pega.com":
                print(f"SESService (Mock): Checking status for {email} -> Pending")
                return "Pending"
            print(f"SESService (Mock): Checking status for {email} -> Success")
            return "Success"

        try:
            response = self.ses.get_identity_verification_attributes(Identities=[email])
            attributes = response.get('VerificationAttributes', {})
            if email in attributes:
                return attributes[email]['VerificationStatus']
            return "NotFound"
        except ClientError as e:
            print(f"Error checking identity status: {e}")
            return "Error"

    def verify_email(self, email: str) -> bool:
        """Triggers SES verification email."""
        if self.mock_mode:
            print(f"SESService (Mock): Triggering verification email for {email}")
            # Auto-verify in mock mode so next check succeeds
            self._mock_verified_emails.add(email)
            return True

        try:
            self.ses.verify_email_identity(EmailAddress=email)
            print(f"Verification email sent to {email}")
            return True
        except ClientError as e:
            print(f"Error triggering verification: {e}")
            return False

    def send_magic_link(self, recipient_email: str, magic_link: str):
        """Sends the magic link via SES."""
        subject = "Your Login Link"
        body_text = f"Click here to log in: {magic_link}\n\nThis link expires in 15 minutes."
        body_html = f"""<html>
<head></head>
<body>
  <h1>Login to Prompt Repository</h1>
  <p>Click the link below to log in. This link is valid for 15 minutes.</p>
  <p><a href='{magic_link}'>Log In</a></p>
  <p>If you didn't request this, please ignore this email.</p>
</body>
</html>"""

        if self.mock_mode:
            print(f"SESService (Mock): Sending email to {recipient_email}")
            print(f"Subject: {subject}")
            print(f"Link: {magic_link}")
            return True

        try:
            self.ses.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [recipient_email],
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body_text,
                            'Charset': 'UTF-8'
                        },
                        'Html': {
                            'Data': body_html,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            print(f"Email sent to {recipient_email}")
            return True
        except ClientError as e:
            print(f"Error sending email: {e.response['Error']['Message']}")
            return False

class S3Service:
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.environ.get("S3_BUCKET_NAME", "llm-prompt-repository")
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

    def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> None:
        """Updates an existing prompt in S3 or local memory."""
        # Preserve created_at if updating
        if 'created_at' not in prompt_data:
            prompt_data['created_at'] = datetime.now().isoformat()
        
        if self.mock_mode:
            for i, p in enumerate(self._local_storage):
                if p.get('id') == prompt_id:
                    # Preserve original created_at
                    if 'created_at' in p:
                        prompt_data['created_at'] = p['created_at']
                    self._local_storage[i] = prompt_data
                    print(f"S3Service (Mock): Updated prompt {prompt_id}")
                    return
            raise Exception(f"Prompt {prompt_id} not found in mock storage")
        
        key = f"prompts/{prompt_id}.json"
        
        try:
            # Try to get existing prompt to preserve created_at
            try:
                obj_resp = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                existing_data = json.loads(obj_resp['Body'].read().decode('utf-8'))
                if 'created_at' in existing_data:
                    prompt_data['created_at'] = existing_data['created_at']
            except:
                pass  # If can't get existing, use new timestamp
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(prompt_data),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error updating S3: {e}")
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
        self.bucket_name = s3_service.bucket_name
        
        if self.mock_mode:
            print("VectorService: Initialized in MOCK MODE (Simple Text Search)")
            return

        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        
        if not self.mock_mode and not self.s3_service.mock_mode:
            self.s3 = boto3.client('s3')
        
        if not self.gemini_api_key:
            print("WARNING: GEMINI_API_KEY missing. Semantic search will fallback to mock.")

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

    def _save_embedding_to_s3(self, prompt_id: str, embedding: list):
        """Saves embedding vector to S3 as numpy array."""
        if self.mock_mode or self.s3_service.mock_mode:
            return
        
        try:
            # Convert to numpy array
            embedding_array = np.array(embedding, dtype=np.float32)
            
            # Save to bytes buffer
            buffer = io.BytesIO()
            np.save(buffer, embedding_array)
            buffer.seek(0)
            
            # Upload to S3
            key = f"embeddings/{prompt_id}.npy"
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=buffer.getvalue(),
                ContentType='application/octet-stream'
            )
            print(f"Saved embedding to S3: {key}")
        except Exception as e:
            print(f"Error saving embedding to S3: {e}")

    def _load_embedding_from_s3(self, prompt_id: str):
        """Loads embedding vector from S3."""
        try:
            key = f"embeddings/{prompt_id}.npy"
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            buffer = io.BytesIO(response['Body'].read())
            embedding = np.load(buffer)
            return embedding
        except Exception as e:
            print(f"Error loading embedding from S3 for {prompt_id}: {e}")
            return None

    def _load_all_embeddings(self):
        """Loads all embeddings from S3."""
        embeddings = {}
        try:
            # List all embedding files
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix='embeddings/')
            
            if 'Contents' not in response:
                return embeddings
            
            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith('.npy'):
                    # Extract prompt_id from filename
                    prompt_id = key.split('/')[-1].replace('.npy', '')
                    embedding = self._load_embedding_from_s3(prompt_id)
                    if embedding is not None:
                        embeddings[prompt_id] = embedding
            
            print(f"Loaded {len(embeddings)} embeddings from S3")
            return embeddings
        except Exception as e:
            print(f"Error loading embeddings from S3: {e}")
            return {}

    def _cosine_similarity(self, vec1, vec2):
        """Computes cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def add_point(self, text: str, metadata: dict):
        """Generates and saves embedding to S3."""
        if self.mock_mode:
            print(f"VectorService (Mock): Added point for {metadata.get('title')}")
            return True

        # 1. Get embedding
        vector = self._get_embedding_rest(text)
        if not vector:
            print("Skipping vector add: No embedding generated.")
            return False

        # 2. Save embedding to S3
        prompt_id = metadata.get("id")
        self._save_embedding_to_s3(prompt_id, vector)
        print(f"Successfully saved embedding for: {metadata.get('title')}")
        return True

    def search(self, query_text: str, limit: int = 5):
        """Searches using S3-stored embeddings."""
        if self.mock_mode:
            return self._mock_search(query_text)

        # 1. Get query embedding
        query_vector = self._get_embedding_rest(query_text)
        
        if not query_vector:
            print("Fallback to mock search (no embedding)")
            return self._mock_search(query_text)

        # 2. Load all embeddings from S3
        all_embeddings = self._load_all_embeddings()
        
        if not all_embeddings:
            print("No embeddings found, falling back to mock search")
            return self._mock_search(query_text)

        # 3. Compute similarities
        similarities = []
        for prompt_id, embedding in all_embeddings.items():
            similarity = self._cosine_similarity(query_vector, embedding)
            similarities.append({
                "id": prompt_id,
                "score": float(similarity)
            })
        
        # 4. Sort by similarity (highest first)
        similarities.sort(key=lambda x: x["score"], reverse=True)
        
        # 5. Get top K results and fetch metadata from S3
        results = []
        all_prompts = self.s3_service.list_prompts()
        prompt_dict = {p["id"]: p for p in all_prompts}
        
        for item in similarities[:limit]:
            prompt_id = item["id"]
            if prompt_id in prompt_dict:
                result = prompt_dict[prompt_id].copy()
                result["score"] = item["score"]
                results.append(result)
        
        print(f"Found {len(results)} results for query: {query_text}")
        return results

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

