from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel, validator
from typing import List, Optional
from fastapi import Request, Response, Depends, Cookie
from fastapi.responses import RedirectResponse
from .services import S3Service, VectorService, SESService
from .tool_metadata_service import ToolMetadataService
from .auth_utils import create_magic_link_token, create_session_token, verify_token
import os
import json

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
tool_metadata_service = ToolMetadataService(s3_service)

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

# Dependency for optional authentication
def get_current_user_optional(session_token: Optional[str] = Cookie(None)):
    if not session_token:
        return None
    email = verify_token(session_token, "session")
    return email

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
    upvotes: Optional[int] = 0

class GenerateRequest(BaseModel):
    title: str
    prompt_text: str

class UpdateToolsRequest(BaseModel):
    tool_names: List[str]
    
    @validator('tool_names')
    def validate_tool_names(cls, v):
        if not v:
            raise ValueError('tool_names cannot be empty')
        # Trim whitespace and validate
        cleaned = [name.strip() for name in v]
        if any(not name for name in cleaned):
            raise ValueError('tool_names cannot contain empty strings')
        return cleaned

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
def list_prompts(user_email: Optional[str] = Depends(get_current_user_optional)):
    """List all prompts with user context for upvotes and favorites"""
    try:
        prompts = s3_service.list_prompts()
        
        # Add user context if authenticated
        if user_email:
            # Get user favorites
            if s3_service.mock_mode:
                user_favorites = s3_service.get_user_favorites(user_email)
            else:
                user_favorites = []
                try:
                    user_data = s3_service.s3.get_object(
                        Bucket=s3_service.bucket_name,
                        Key=f"users/{user_email}/favorites.json"
                    )
                    user_favorites = json.loads(user_data['Body'].read().decode('utf-8'))
                except:
                    user_favorites = []
            
            # Add user context to each prompt
            for prompt in prompts:
                # Initialize upvote fields if missing
                if 'upvotes' not in prompt:
                    prompt['upvotes'] = 0
                if 'upvoted_by' not in prompt:
                    prompt['upvoted_by'] = []
                
                # Add user context
                prompt['user_context'] = {
                    'is_upvoted': user_email in prompt.get('upvoted_by', []),
                    'is_favorited': prompt['id'] in user_favorites,
                    'can_edit': prompt.get('owner_email') == user_email
                }
        else:
            # Add basic context for unauthenticated users
            for prompt in prompts:
                if 'upvotes' not in prompt:
                    prompt['upvotes'] = 0
                prompt['user_context'] = {
                    'is_upvoted': False,
                    'is_favorited': False,
                    'can_edit': False
                }
        
        return {"results": prompts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/prompts/{prompt_id}")
def update_prompt(prompt_id: str, prompt: Prompt, user_email: str = Depends(get_current_user_dep)):
    try:
        # Verify ownership (optimized - fetch only the specific prompt)
        existing_prompt = s3_service.get_prompt_by_id(prompt_id)
        
        if not existing_prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
            
        # Check if current user is the owner
        # Note: Old prompts might not have owner_email, so they are uneditable by default
        if existing_prompt.get('owner_email') != user_email:
            raise HTTPException(status_code=403, detail="You are not authorized to edit this prompt")

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

@app.patch("/prompts/{prompt_id}/tools")
def update_prompt_tools(prompt_id: str, request: UpdateToolsRequest):
    """Update tool names for a specific prompt (one-time migration endpoint, optimized)"""
    try:
        # Fetch the specific prompt (optimized - no need to fetch all prompts)
        prompt = s3_service.get_prompt_by_id(prompt_id)
        
        # Raise 404 if prompt not found
        if not prompt:
            raise HTTPException(status_code=404, detail=f"Prompt {prompt_id} not found")
        
        # Store old tool names for response
        old_tool_names = prompt.get('tool_used', [])
        
        # Update the prompt with new tool names
        prompt['tool_used'] = request.tool_names
        
        # Update in S3 (preserving all other fields)
        s3_service.update_prompt(prompt_id, prompt)
        
        # Regenerate vector embedding with new tool names
        searchable_text = vector_service._construct_searchable_text(
            prompt['title'],
            prompt['description'],
            prompt['prompt_text'],
            request.tool_names,
            prompt['tags']
        )
        
        embedding_updated = vector_service.add_point(
            text=searchable_text,
            metadata={
                "id": prompt_id,
                "title": prompt['title'],
                "description": prompt['description'],
                "tags": prompt['tags'],
                "username": prompt.get('username'),
                "tool_used": request.tool_names,
                "prompt_text": prompt['prompt_text']
            }
        )
        
        # Return response with old and new tool names
        return {
            "status": "success",
            "prompt_id": prompt_id,
            "old_tool_names": old_tool_names,
            "new_tool_names": request.tool_names,
            "embedding_updated": bool(embedding_updated),
            "message": "Tool names updated successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Failed to update tool names: {str(e)}")

@app.get("/search")
def search_prompts(q: str, user_email: Optional[str] = Depends(get_current_user_optional)):
    """Search prompts with user context"""
    try:
        results = vector_service.search(q)
        
        # Add user context if authenticated
        if user_email:
            # Get user favorites
            if s3_service.mock_mode:
                user_favorites = s3_service.get_user_favorites(user_email)
            else:
                user_favorites = []
                try:
                    user_data = s3_service.s3.get_object(
                        Bucket=s3_service.bucket_name,
                        Key=f"users/{user_email}/favorites.json"
                    )
                    user_favorites = json.loads(user_data['Body'].read().decode('utf-8'))
                except:
                    user_favorites = []
            
            # Add user context to each result
            for result in results:
                # Initialize upvote fields if missing
                if 'upvotes' not in result:
                    result['upvotes'] = 0
                if 'upvoted_by' not in result:
                    result['upvoted_by'] = []
                
                # Add user context
                result['user_context'] = {
                    'is_upvoted': user_email in result.get('upvoted_by', []),
                    'is_favorited': result['id'] in user_favorites,
                    'can_edit': result.get('owner_email') == user_email
                }
        else:
            # Add basic context for unauthenticated users
            for result in results:
                if 'upvotes' not in result:
                    result['upvotes'] = 0
                result['user_context'] = {
                    'is_upvoted': False,
                    'is_favorited': False,
                    'can_edit': False
                }
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# Tool Metadata API Endpoints

@app.get("/tools")
def get_all_tools():
    """Get all available AI tools with metadata"""
    try:
        tools = tool_metadata_service.get_all_tools()
        categories = tool_metadata_service.get_categories()
        
        return {
            "tools": tools,
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/{tool_id}")
def get_tool_by_id(tool_id: str):
    """Get detailed information about a specific tool"""
    try:
        tool = tool_metadata_service.get_tool_by_id(tool_id)
        if not tool:
            # Try by display name as fallback
            tool = tool_metadata_service.get_tool_by_display_name(tool_id)
        
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        # Get statistics for this tool
        stats = tool_metadata_service.get_tool_statistics(tool_id)
        
        return {
            "tool": tool,
            "statistics": stats
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/{tool_id}/prompts")
def get_tool_prompts(tool_id: str, limit: Optional[int] = None):
    """Get all prompts that use a specific tool"""
    try:
        prompts = tool_metadata_service.get_prompts_by_tool(tool_id, limit)
        
        # Get tool metadata for context
        tool = tool_metadata_service.get_tool_by_id(tool_id)
        if not tool:
            tool = tool_metadata_service.get_tool_by_display_name(tool_id)
        
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        return {
            "tool": {
                "id": tool["id"],
                "displayName": tool["displayName"],
                "description": tool["description"],
                "category": tool["category"],
                "icon": tool["icon"]
            },
            "prompts": prompts,
            "total_count": len(prompts)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/{tool_id}/stats")
def get_tool_statistics(tool_id: str):
    """Get usage statistics for a specific tool"""
    try:
        stats = tool_metadata_service.get_tool_statistics(tool_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return stats
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
def get_categories():
    """Get all tool categories with metadata and tool counts"""
    try:
        categories = tool_metadata_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories/{category_id}/tools")
def get_tools_by_category(category_id: str):
    """Get all tools in a specific category"""
    try:
        tools = tool_metadata_service.get_tools_by_category(category_id)
        category_info = tool_metadata_service.get_categories().get(category_id)
        
        if not category_info:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return {
            "category": category_info,
            "tools": tools
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Interaction Endpoints (Upvotes and Favorites)

@app.post("/prompts/{prompt_id}/upvote")
def upvote_prompt(prompt_id: str, user_email: str = Depends(get_current_user_dep)):
    """Upvote a prompt (optimized)"""
    try:
        # Get the specific prompt (optimized - no need to fetch all prompts)
        prompt = s3_service.get_prompt_by_id(prompt_id)
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Initialize upvotes if not present
        if 'upvotes' not in prompt:
            prompt['upvotes'] = 0
        
        # Initialize upvoted_by list if not present
        if 'upvoted_by' not in prompt:
            prompt['upvoted_by'] = []
        
        # Check if user already upvoted
        if user_email in prompt['upvoted_by']:
            raise HTTPException(status_code=400, detail="Already upvoted")
        
        # Add upvote
        prompt['upvotes'] += 1
        prompt['upvoted_by'].append(user_email)
        
        # Update in S3
        s3_service.update_prompt(prompt_id, prompt)
        
        return {
            "status": "success",
            "upvotes": prompt['upvotes'],
            "message": "Prompt upvoted successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/prompts/{prompt_id}/upvote")
def remove_upvote(prompt_id: str, user_email: str = Depends(get_current_user_dep)):
    """Remove upvote from a prompt (optimized)"""
    try:
        # Get the specific prompt (optimized - no need to fetch all prompts)
        prompt = s3_service.get_prompt_by_id(prompt_id)
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Initialize fields if not present
        if 'upvotes' not in prompt:
            prompt['upvotes'] = 0
        if 'upvoted_by' not in prompt:
            prompt['upvoted_by'] = []
        
        # Check if user has upvoted
        if user_email not in prompt['upvoted_by']:
            raise HTTPException(status_code=400, detail="Not upvoted")
        
        # Remove upvote
        prompt['upvotes'] = max(0, prompt['upvotes'] - 1)
        prompt['upvoted_by'].remove(user_email)
        
        # Update in S3
        s3_service.update_prompt(prompt_id, prompt)
        
        return {
            "status": "success",
            "upvotes": prompt['upvotes'],
            "message": "Upvote removed successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/me/favorites")
def get_user_favorites(user_email: str = Depends(get_current_user_dep)):
    """Get user's favorite prompts (optimized)"""
    try:
        if s3_service.mock_mode:
            # Get favorites from in-memory storage
            favorite_ids = s3_service.get_user_favorites(user_email)
            favorite_prompts = s3_service.get_prompts_by_ids(favorite_ids)
            return {
                "favorites": favorite_prompts,
                "count": len(favorite_prompts)
            }
        
        # Real S3 implementation - get favorite IDs first
        try:
            user_data = s3_service.s3.get_object(
                Bucket=s3_service.bucket_name,
                Key=f"users/{user_email}/favorites.json"
            )
            favorite_ids = json.loads(user_data['Body'].read().decode('utf-8'))
        except:
            favorite_ids = []
        
        # Fetch only the favorited prompts (optimized - no need to fetch all prompts)
        favorite_prompts = s3_service.get_prompts_by_ids(favorite_ids)
        
        return {
            "favorites": favorite_prompts,
            "count": len(favorite_prompts)
        }
    except Exception as e:
        if s3_service.mock_mode:
            return {"favorites": [], "count": 0}
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/me/favorites/{prompt_id}")
def add_to_favorites(prompt_id: str, user_email: str = Depends(get_current_user_dep)):
    """Add a prompt to user's favorites (optimized - no prompt existence check)"""
    try:
        # Note: We skip the prompt existence check to avoid fetching all prompts
        # The prompt will simply not appear if it doesn't exist or gets deleted later
        
        if s3_service.mock_mode:
            # Use in-memory storage for mock mode
            success = s3_service.add_user_favorite(user_email, prompt_id)
            favorite_ids = s3_service.get_user_favorites(user_email)
            return {
                "status": "success",
                "message": "Added to favorites" if success else "Already in favorites",
                "favorites_count": len(favorite_ids)
            }
        
        # Real S3 implementation
        try:
            user_data = s3_service.s3.get_object(
                Bucket=s3_service.bucket_name,
                Key=f"users/{user_email}/favorites.json"
            )
            favorites = json.loads(user_data['Body'].read().decode('utf-8'))
        except:
            favorites = []
        
        # Add to favorites if not already there
        if prompt_id not in favorites:
            favorites.append(prompt_id)
            
            # Save back to S3
            s3_service.s3.put_object(
                Bucket=s3_service.bucket_name,
                Key=f"users/{user_email}/favorites.json",
                Body=json.dumps(favorites),
                ContentType='application/json'
            )
        
        return {
            "status": "success",
            "message": "Added to favorites",
            "favorites_count": len(favorites)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/me/favorites/{prompt_id}")
def remove_from_favorites(prompt_id: str, user_email: str = Depends(get_current_user_dep)):
    """Remove a prompt from user's favorites"""
    try:
        if s3_service.mock_mode:
            # Use in-memory storage for mock mode
            success = s3_service.remove_user_favorite(user_email, prompt_id)
            favorite_ids = s3_service.get_user_favorites(user_email)
            return {
                "status": "success",
                "message": "Removed from favorites" if success else "Not in favorites",
                "favorites_count": len(favorite_ids)
            }
        
        # Real S3 implementation
        try:
            user_data = s3_service.s3.get_object(
                Bucket=s3_service.bucket_name,
                Key=f"users/{user_email}/favorites.json"
            )
            favorites = json.loads(user_data['Body'].read().decode('utf-8'))
        except:
            favorites = []
        
        # Remove from favorites if present
        if prompt_id in favorites:
            favorites.remove(prompt_id)
            
            # Save back to S3
            s3_service.s3.put_object(
                Bucket=s3_service.bucket_name,
                Key=f"users/{user_email}/favorites.json",
                Body=json.dumps(favorites),
                ContentType='application/json'
            )
        
        return {
            "status": "success",
            "message": "Removed from favorites",
            "favorites_count": len(favorites)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
