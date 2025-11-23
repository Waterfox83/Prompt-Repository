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
        self.s3_service = s3_service
        print("VectorService: Initialized in MOCK mode (S3 scan only).")
        # Qdrant/Gemini disabled for debugging
        # genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        # self.qdrant = ...

    def add_point(self, text: str, metadata: Dict[str, Any]):
        """
        Mock add_point: Does nothing because we just scan S3 for search.
        """
        print(f"VectorService: Mock add_point called for {metadata.get('title')}")
        return True

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Mock search: Scans all prompts in S3 and does a substring match.
        """
        print(f"VectorService: Mock search for '{query}'")
        try:
            all_prompts = self.s3_service.list_prompts()
            results = []
            query_lower = query.lower()
            
            for prompt in all_prompts:
                # Simple text matching
                text_content = f"{prompt.get('title', '')} {prompt.get('description', '')} {prompt.get('prompt_text', '')} {' '.join(prompt.get('tags', []))}"
                
                if query_lower in text_content.lower():
                    results.append(prompt)
            
            print(f"VectorService: Found {len(results)} matches in S3.")
            return results
        except Exception as e:
            print(f"VectorService: Error during mock search: {e}")
            return []
