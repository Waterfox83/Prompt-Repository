import boto3
import json
import uuid
from typing import List, Dict, Any
from datetime import datetime

class S3Service:
    def __init__(self, bucket_name: str = "llm-prompt-repository"):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3')

    def save_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """Saves prompt data to S3 and returns the key."""
        prompt_id = str(uuid.uuid4())
        prompt_data['id'] = prompt_id
        prompt_data['created_at'] = datetime.now().isoformat()
        
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
        """Returns all prompts from S3."""
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

import os
import time
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models

class VectorService:
    def __init__(self, s3_service: S3Service = None):
        # s3_service is kept for compatibility but not used for search anymore
        self.s3_service = s3_service
        
        # Initialize Gemini
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        self.embedding_model = "models/text-embedding-004"
        
        # Initialize Qdrant
        print("Initializing Qdrant Client...")
        start = time.time()
        self.qdrant = QdrantClient(
            url=os.environ.get("QDRANT_URL"),
            api_key=os.environ.get("QDRANT_API_KEY"),
        )
        print(f"Qdrant Client Initialized in {time.time() - start:.2f}s")
        self.collection_name = "prompts"
        self._collection_checked = False

    def _ensure_collection(self):
        if self._collection_checked:
            return

        print("Checking Qdrant Collection...")
        start = time.time()
        try:
            self.qdrant.get_collection(self.collection_name)
            print(f"Collection found in {time.time() - start:.2f}s")
        except Exception:
            print("Collection not found, creating...")
            # Create collection if it doesn't exist
            # Vector size for text-embedding-004 is 768
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )
            print(f"Collection created in {time.time() - start:.2f}s")
        self._collection_checked = True

    def _get_embedding(self, text: str) -> List[float]:
        print("Generating Embedding...")
        start = time.time()
        result = genai.embed_content(
            model=self.embedding_model,
            content=text,
            task_type="retrieval_document",
        )
        print(f"Embedding generated in {time.time() - start:.2f}s")
        return result['embedding']

    def add_point(self, text: str, metadata: Dict[str, Any]):
        """Generates embedding and saves to Qdrant."""
        self._ensure_collection() # Lazy check
        try:
            vector = self._get_embedding(text)
            
            # Qdrant requires an integer or UUID for point ID. 
            # Our metadata['id'] is a UUID string, which works.
            point_id = metadata['id']
            
            print("Upserting to Qdrant...")
            start = time.time()
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=metadata
                    )
                ]
            )
            print(f"Upsert completed in {time.time() - start:.2f}s")
            return True
        except Exception as e:
            print(f"Error adding to Qdrant: {e}")
            # We don't raise here to avoid failing the main save operation if vector DB is down
            # But in production you might want to handle this differently (e.g. DLQ)
            return False

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Semantic search using Qdrant."""
        self._ensure_collection() # Lazy check
        try:
            # Generate query embedding
            print("Generating Query Embedding...")
            start = time.time()
            query_vector = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query",
            )['embedding']
            print(f"Query embedding generated in {time.time() - start:.2f}s")
            
            print("Searching Qdrant...")
            start = time.time()
            search_result = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=10
            )
            print(f"Search completed in {time.time() - start:.2f}s")
            
            # Extract payload (metadata)
            return [hit.payload for hit in search_result]
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return []
