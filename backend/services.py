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
  <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
    <h1 style="color: #3b82f6; text-align: center;">Login to Prompt Repository</h1>
    <p style="font-size: 16px; line-height: 1.5; text-align: center; color: #555;">Click the button below to log in. This link is valid for 15 minutes.</p>
    <div style="text-align: center; margin: 30px 0;">
      <!-- Using solid background color for better email client compatibility -->
      <a href='{magic_link}' style="display: inline-block; padding: 14px 28px; background-color: #3b82f6; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">Login to Repository</a>
    </div>
    <p style="font-size: 16px; color: #888; text-align: center;">If you didn't request this, please ignore this email.</p>
  </div>
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

    def _normalize(self, vector):
        """Normalizes a vector to unit length."""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _load_all_embeddings(self):
        """
        Downloads vectors.npy and ids.json from S3.
        Returns (ids, matrix, etag_vectors).
        matrix is memory-mapped.
        """
        if self.mock_mode or self.s3_service.mock_mode:
            return [], None, None

        try:
            import tempfile
            
            # 1. Load IDs (Small, load into memory)
            ids = []
            try:
                response = self.s3.get_object(Bucket=self.bucket_name, Key="embeddings/ids.json")
                ids = json.loads(response['Body'].read().decode('utf-8'))
            except ClientError as e:
                if e.response['Error']['Code'] != "NoSuchKey":
                    print(f"Error loading IDs: {e}")
            
            # 2. Load Vectors (Large, mmap)
            matrix = None
            etag = None
            try:
                # Create a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.npy') as tmp:
                    temp_path = tmp.name
                
                response = self.s3.get_object(Bucket=self.bucket_name, Key="embeddings/vectors.npy")
                etag = response['ETag']
                content = response['Body'].read()
                with open(temp_path, 'wb') as f:
                    f.write(content)
                
                # Load with mmap_mode
                matrix = np.load(temp_path, mmap_mode='r')
            except ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    matrix = np.empty((0, 768), dtype=np.float32)
                else:
                    raise e
            
            return ids, matrix, etag
            
        except Exception as e:
            print(f"Error loading all embeddings: {e}")
            return [], np.empty((0, 768), dtype=np.float32), None

    def _save_embedding_to_s3(self, prompt_id: str, embedding: list):
        """
        Saves embedding to S3 by appending to vectors.npy and ids.json.
        Uses Optimistic Locking (ETag of vectors.npy) to handle concurrency.
        """
        if self.mock_mode or self.s3_service.mock_mode:
            return
        
        import tempfile
        import random
        
        max_retries = 3
        
        # Normalize the new vector
        new_vector = self._normalize(np.array(embedding, dtype=np.float32))
        
        for attempt in range(max_retries):
            try:
                # 1. Load existing data
                ids, matrix, etag = self._load_all_embeddings()
                
                # 2. Prepare data for modification
                if hasattr(matrix, 'files'): # Handle np.load return types if any
                    matrix = np.array(matrix)
                else:
                    # If it's mmap, copy to RAM to modify
                    matrix = np.array(matrix)
                
                # 3. Check if ID exists and Update or Append
                if prompt_id in ids:
                    # Update existing
                    idx = ids.index(prompt_id)
                    matrix[idx] = new_vector
                    print(f"Updated existing embedding for {prompt_id} at index {idx}")
                else:
                    # Append new
                    ids.append(prompt_id)
                    if matrix.shape[0] == 0:
                        matrix = np.array([new_vector])
                    else:
                        matrix = np.vstack([matrix, new_vector])
                    print(f"Appended new embedding for {prompt_id}")
                
                # 4. Save IDs to JSON
                self.s3.put_object(
                    Bucket=self.bucket_name,
                    Key="embeddings/ids.json",
                    Body=json.dumps(ids),
                    ContentType='application/json'
                )
                
                # 5. Save Matrix to Buffer
                buffer = io.BytesIO()
                np.save(buffer, matrix)
                buffer.seek(0)
                
                # 6. Upload Matrix with If-Match
                put_kwargs = {
                    'Bucket': self.bucket_name,
                    'Key': "embeddings/vectors.npy",
                    'Body': buffer.getvalue(),
                    'ContentType': 'application/octet-stream'
                }
                
                if etag:
                    put_kwargs['IfMatch'] = etag
                
                self.s3.put_object(**put_kwargs)
                print(f"Successfully saved embedding for {prompt_id} (Attempt {attempt+1})")
                return
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'PreconditionFailed':
                    print(f"Concurrency conflict saving embedding (Attempt {attempt+1}). Retrying...")
                    time.sleep(random.uniform(0.1, 0.5)) # Jitter
                    continue
                else:
                    print(f"Error saving embedding to S3: {e}")
                    return
            except Exception as e:
                print(f"Unexpected error saving embedding: {e}")
                return
        
        print(f"Failed to save embedding after {max_retries} attempts due to concurrency.")

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

        # 2. Save embedding to S3 (Optimized)
        prompt_id = metadata.get("id")
        self._save_embedding_to_s3(prompt_id, vector)
        print(f"Successfully saved embedding for: {metadata.get('title')}")
        return True

    def search(self, query_text: str, limit: int = 5):
        """Searches using S3-stored embeddings (Optimized Matrix Search)."""
        if self.mock_mode:
            return self._mock_search(query_text)

        # 1. Get query embedding
        query_vector = self._get_embedding_rest(query_text)
        
        if not query_vector:
            print("Fallback to mock search (no embedding)")
            return self._mock_search(query_text)

        # 2. Load all embeddings (Matrix)
        ids, matrix, _ = self._load_all_embeddings()
        
        if not ids or matrix is None or len(ids) == 0:
            print("No embeddings found, falling back to mock search")
            return self._mock_search(query_text)

        # 3. Normalize query vector
        query_vector = self._normalize(np.array(query_vector, dtype=np.float32))

        # 4. Compute similarities (Dot Product)
        # Matrix shape: (N, D), Query shape: (D,) -> Result: (N,)
        try:
            similarities = np.dot(matrix, query_vector)
        except ValueError as e:
            print(f"Shape mismatch in dot product: {e}")
            return []
        
        # 5. Sort and get top K
        # Get indices of top K scores (unsorted)
        if len(similarities) <= limit:
            top_indices = np.arange(len(similarities))
        else:
            # argpartition is faster than argsort for top K
            top_indices = np.argpartition(similarities, -limit)[-limit:]
        
        # Sort the top K indices by score descending
        top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
        
        # 6. Fetch metadata
        results = []
        all_prompts = self.s3_service.list_prompts()
        prompt_dict = {p["id"]: p for p in all_prompts}
        
        for idx in top_indices:
            if idx < len(ids):
                prompt_id = ids[idx]
                score = float(similarities[idx])
                
                if prompt_id in prompt_dict:
                    result = prompt_dict[prompt_id].copy()
                    result["score"] = score
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

