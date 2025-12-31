from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Request, Response, Depends, Cookie
from fastapi.responses import RedirectResponse
from .services import S3Service, VectorService, SESService
from .auth_utils import create_magic_link_token, create_session_token, verify_token
import os

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost:5173",  # Local development
    "http://127.0.0.1:5173",
]

# Add production frontend URL if set
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)

# Initialize services
s3_service = S3Service()
vector_service = VectorService(s3_service)
ses_service = SESService()

# Auth Models
class LoginRequest(BaseModel):
    email: str

@app.post("/auth/login")
def login(request: LoginRequest):
    email = request.email.lower().strip()
    
    # Domain validation
    if not (email.endswith("@pega.com") or email.endswith("@in.pega.com")):
        raise HTTPException(status_code=403, detail="Access restricted to Pega employees.")
    
    # 1. Check SES Verification Status (Sandbox Support)
    status = ses_service.get_identity_status(email)
    
    if status != "Success":
        # Trigger verification email
        if ses_service.verify_email(email):
            return {
                "status": "verification_required",
                "message": "Verification email sent. Please check your inbox from Amazon Web Services."
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send verification email.")

    # 2. If Verified, Send Magic Link
    token = create_magic_link_token(email)
    
    # Construct link
    api_base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
    magic_link = f"{api_base_url}/auth/verify?token={token}"
    
    # Send email
    if ses_service.send_magic_link(email, magic_link):
        return {"status": "success", "message": "Magic link sent. Check your email."}
    else:
        raise HTTPException(status_code=500, detail="Failed to send magic link.")

@app.get("/auth/verify")
def verify(token: str):
    email = verify_token(token, "magic_link")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    
    # Generate session token
    session_token = create_session_token(email)
    
    # Redirect to frontend
    frontend_url = os.environ.get("FRONTEND_URL", "http://127.0.0.1:5173")
    response = RedirectResponse(url=frontend_url)
    
    # Set cookie
    is_production = os.environ.get("ENVIRONMENT", "development") == "production"
    print("Is production:", is_production)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=is_production, # True for prod (required for SameSite=None)
        samesite="none" if is_production else "lax", # None for cross-domain (prod), Lax for local
        max_age=90 * 24 * 60 * 60 # 90 days
    )
    return response

@app.get("/auth/me")
def get_current_user(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    email = verify_token(session_token, "session")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid session")
        
    return {"email": email}

# Dependency for protected routes
def get_current_user_dep(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    email = verify_token(session_token, "session")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid session")
    return email

class Prompt(BaseModel):
    title: str
    description: str
    tool_used: List[str]
    prompt_text: str
    tags: List[str]
    username: Optional[str] = None
    owner_email: Optional[str] = None

class GenerateRequest(BaseModel):
    title: str
    prompt_text: str

@app.get("/")
def read_root():
    return {"message": "AI Prompt Repository API is running"}

@app.post("/prompts")
def create_prompt(prompt: Prompt, user_email: str = Depends(get_current_user_dep)):
    try:
        # Set owner email
        prompt.owner_email = user_email
        
        # 1. Save full details to S3
        prompt_dict = prompt.dict()
        prompt_id = s3_service.save_prompt(prompt_dict)
        
        # 2. Save vector embedding (mock)
        # We construct a text representation for semantic search
        searchable_text = vector_service._construct_searchable_text(
            prompt.title, 
            prompt.description, 
            prompt.prompt_text, 
            prompt.tool_used, 
            prompt.tags
        )
        
        vector_service.add_point(
            text=searchable_text,
            metadata={
                "id": prompt_id,
                "title": prompt.title,
                "description": prompt.description,
                "tags": prompt.tags,
                "username": prompt.username,
                "tool_used": prompt.tool_used, # Already validated as List[str] by Pydantic
                "prompt_text": prompt.prompt_text
            }
        )
        
        return {"status": "success", "id": prompt_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts")
def list_prompts():
    return {"results": s3_service.list_prompts()}

@app.put("/prompts/{prompt_id}")
def update_prompt(prompt_id: str, prompt: Prompt, user_email: str = Depends(get_current_user_dep)):
    try:
        # Verify ownership
        try:
            # We need to fetch the existing prompt to check ownership
            # Since s3_service.list_prompts() might be heavy, we should ideally have get_prompt
            # But for now, we can rely on list_prompts filtering or add get_prompt to service
            # Let's use list_prompts and filter for now as it's MVP
            all_prompts = s3_service.list_prompts()
            existing_prompt = next((p for p in all_prompts if p['id'] == prompt_id), None)
            
            if not existing_prompt:
                raise HTTPException(status_code=404, detail="Prompt not found")
                
            # Check if current user is the owner
            # Note: Old prompts might not have owner_email, so they are uneditable by default
            if existing_prompt.get('owner_email') != user_email:
                raise HTTPException(status_code=403, detail="You are not authorized to edit this prompt")
                
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            # If any other error (e.g. S3 down), let it bubble up or handle
            pass

        # Update in S3
        prompt_dict = prompt.dict()
        prompt_dict['id'] = prompt_id
        prompt_dict['owner_email'] = user_email # Ensure owner is preserved/set

        s3_service.update_prompt(prompt_id, prompt_dict)
        
        # Update vector database
        searchable_text = vector_service._construct_searchable_text(
            prompt.title, 
            prompt.description, 
            prompt.prompt_text, 
            prompt.tool_used, 
            prompt.tags
        )
        
        vector_service.add_point(
            text=searchable_text,
            metadata={
                "id": prompt_id,
                "title": prompt.title,
                "description": prompt.description,
                "tags": prompt.tags,
                "username": prompt.username,
                "tool_used": prompt.tool_used,
                "prompt_text": prompt.prompt_text
            }
        )
        
        return {"status": "success", "id": prompt_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search_prompts(q: str):
    results = vector_service.search(q)
    return {"results": results}

@app.post("/generate-details")
def generate_details(request: GenerateRequest):
    try:
        result = vector_service.generate_details(request.title, request.prompt_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/migrate")
def migrate_embeddings():
    """
    One-time migration endpoint to generate embeddings for all existing prompts.
    Rebuilds the 'all_embeddings.npy' file from scratch.
    """
    try:
        import numpy as np
        import io
        
        # Get all prompts from S3
        all_prompts = s3_service.list_prompts()
        
        total = len(all_prompts)
        processed = 0
        errors = 0
        
        ids = []
        vectors = []
        
        results = {
            "total_prompts": total,
            "processed": [],
            "errors": []
        }
        
        for prompt in all_prompts:
            prompt_id = prompt.get("id")
            title = prompt.get("title", "Untitled")
            
            try:
                # Generate searchable text
                # Ensure tool_used is a list for the helper
                tool_used_val = prompt.get("tool_used", [])
                if not isinstance(tool_used_val, list):
                    tool_used_val = [str(tool_used_val)] if tool_used_val else []
                    
                searchable_text = vector_service._construct_searchable_text(
                    prompt.get('title', ''), 
                    prompt.get('description', ''), 
                    prompt.get('prompt_text', ''), 
                    tool_used_val, 
                    prompt.get('tags', [])
                )
                
                # Generate embedding
                vector = vector_service._get_embedding_rest(searchable_text)
                
                if vector:
                    # Normalize
                    vec_array = np.array(vector, dtype=np.float32)
                    norm = np.linalg.norm(vec_array)
                    if norm > 0:
                        vec_array = vec_array / norm
                        
                    ids.append(prompt_id)
                    vectors.append(vec_array)
                    
                    processed += 1
                    results["processed"].append({"id": prompt_id, "title": title})
                else:
                    errors += 1
                    results["errors"].append({"id": prompt_id, "title": title, "error": "Failed to generate embedding"})
                    
            except Exception as e:
                errors += 1
                results["errors"].append({"id": prompt_id, "title": title, "error": str(e)})
        
        # Save to S3
        if not s3_service.mock_mode and len(vectors) > 0:
            import json
            
            # 1. Save Matrix (vectors.npy)
            matrix = np.vstack(vectors)
            buffer = io.BytesIO()
            np.save(buffer, matrix)
            buffer.seek(0)
            
            s3_service.s3.put_object(
                Bucket=s3_service.bucket_name,
                Key="embeddings/vectors.npy",
                Body=buffer.getvalue(),
                ContentType='application/octet-stream'
            )
            
            # 2. Save IDs (ids.json)
            s3_service.s3.put_object(
                Bucket=s3_service.bucket_name,
                Key="embeddings/ids.json",
                Body=json.dumps(ids),
                ContentType='application/json'
            )
            
            print(f"Successfully migrated {len(vectors)} embeddings to vectors.npy and ids.json.")
        
        return {
            "status": "success",
            "summary": {
                "total": total,
                "processed": processed,
                "errors": errors
            },
            "details": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.post("/migrate-owners")
def migrate_owners():
    """
    One-time migration to backfill owner_email based on username.
    """
    try:
        MAPPING = {
            "Rahul Singh Rathore": "RahulSingh.Rathore@in.pega.com",
            "Devi Vara Prasad B": "DeviVaraPrasad.Bandaru@in.pega.com",
            "Stuti": "Stuti.Bhushan@in.pega.com",
            "Abhishek": "abhishek.asthana@pega.com",
            "Parth": "ParthPandya.Alkeshbhai@in.pega.com"
        }
        
        all_prompts = s3_service.list_prompts()
        updated_count = 0
        updated_prompts = []
        
        for prompt in all_prompts:
            username = prompt.get("username")
            # Check if username matches (case-insensitive or exact? Let's do exact as per request, maybe strip)
            if username:
                username_clean = username.strip()
                if username_clean in MAPPING:
                    new_email = MAPPING[username_clean]
                    # Only update if different or missing
                    if prompt.get("owner_email") != new_email:
                        prompt["owner_email"] = new_email
                        s3_service.update_prompt(prompt["id"], prompt)
                        updated_count += 1
                        updated_prompts.append({"id": prompt["id"], "title": prompt.get("title"), "username": username, "new_email": new_email})
        
        return {
            "status": "success",
            "message": f"Updated {updated_count} prompts with owner emails.",
            "details": updated_prompts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Owner migration failed: {str(e)}")

@app.post("/migrate-tools")
def migrate_tools():
    """
    One-time migration to convert 'tool_used' from string to list[str].
    """
    try:
        all_prompts = s3_service.list_prompts()
        updated_count = 0
        updated_prompts = []
        
        for prompt in all_prompts:
            tool_used = prompt.get("tool_used")
            
            # Check if it's a string (legacy format) or None
            if tool_used is None or isinstance(tool_used, str):
                # Convert to list
                if isinstance(tool_used, str):
                    new_tool_used = [tool_used] if tool_used.strip() else []
                else:
                    new_tool_used = []
                
                # Only update if it actually changed (avoid unnecessary writes)
                # Note: We compare against the original value. 
                # If original was None, new is []. They are different.
                # If original was "foo", new is ["foo"]. They are different.
                
                prompt["tool_used"] = new_tool_used
                
                # Update in S3
                s3_service.update_prompt(prompt["id"], prompt)
                
                # We should also update the embedding because the metadata has changed
                searchable_text = vector_service._construct_searchable_text(
                    prompt.get('title', ''), 
                    prompt.get('description', ''), 
                    prompt.get('prompt_text', ''), 
                    new_tool_used, 
                    prompt.get('tags', [])
                )
                
                vector_service.add_point(
                    text=searchable_text,
                    metadata={
                        "id": prompt["id"],
                        "title": prompt.get("title"),
                        "description": prompt.get("description"),
                        "tags": prompt.get("tags"),
                        "username": prompt.get("username"),
                        "tool_used": new_tool_used,
                        "prompt_text": prompt.get("prompt_text")
                    }
                )
                
                updated_count += 1
                updated_prompts.append({"id": prompt["id"], "title": prompt.get("title"), "old_tool": tool_used, "new_tool": new_tool_used})
                
        return {
            "status": "success",
            "message": f"Scanned {len(all_prompts)} prompts. Updated {updated_count} prompts with list-type tool_used.",
            "total_scanned": len(all_prompts),
            "updated_count": updated_count,
            "details": updated_prompts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool migration failed: {str(e)}")

@app.delete("/admin/prompts/{prompt_id}")
def delete_prompt_admin(prompt_id: str, x_admin_secret: str = Header(None)):
    """
    Admin endpoint to delete a prompt and its embedding.
    Protected by X-Admin-Secret header.
    """
    admin_secret = os.environ.get("ADMIN_SECRET_KEY", "admin-secret-dev")
    if x_admin_secret != admin_secret:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    try:
        # 1. Delete from S3 (JSON)
        s3_deleted = s3_service.delete_prompt(prompt_id)
        if not s3_deleted:
            raise HTTPException(status_code=404, detail="Prompt not found")

        # 2. Delete from Vector Store (Embedding)
        # We don't fail hard if vector delete fails, but we log it
        vector_deleted = vector_service.delete_point(prompt_id)
        
        return {
            "status": "success",
            "message": f"Prompt {prompt_id} deleted.",
            "details": {
                "s3_deleted": s3_deleted,
                "vector_deleted": vector_deleted
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
