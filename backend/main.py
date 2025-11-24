from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from typing import List, Optional
from .services import S3Service, VectorService

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (dev/S3)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)

# Initialize services
s3_service = S3Service()
vector_service = VectorService(s3_service)

class Prompt(BaseModel):
    title: str
    description: str
    tool_used: List[str]
    prompt_text: str
    tags: List[str]
    username: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "AI Prompt Repository API is running"}

@app.post("/prompts")
def create_prompt(prompt: Prompt):
    try:
        # 1. Save full details to S3
        prompt_dict = prompt.dict()
        prompt_id = s3_service.save_prompt(prompt_dict)
        
        # 2. Save vector embedding (mock)
        # We construct a text representation for semantic search
        tools_str = " ".join(prompt.tool_used)
        searchable_text = f"{prompt.title} {prompt.description} {prompt.prompt_text} {tools_str} {' '.join(prompt.tags)}"
        vector_service.add_point(
            text=searchable_text,
            metadata={
                "id": prompt_id,
                "title": prompt.title,
                "description": prompt.description,
                "tags": prompt.tags,
                "username": prompt.username,
                "tool_used": prompt.tool_used
            }
        )
        
        return {"status": "success", "id": prompt_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts")
def list_prompts():
    return {"results": s3_service.list_prompts()}

@app.get("/search")
def search_prompts(q: str):
    results = vector_service.search(q)
    return {"results": results}
