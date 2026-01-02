# Design Document

## Overview

This design document outlines the implementation of a simple one-time migration API endpoint for updating tool names in existing prompts. The solution adds a new PATCH endpoint to the existing FastAPI backend that updates the `tool_used` field for a specific prompt and regenerates its vector embedding.

## Architecture

### System Components

The implementation leverages existing system components:

1. **FastAPI Application** (`backend/main.py`): Hosts the new PATCH endpoint
2. **S3Service** (`backend/services.py`): Handles prompt data persistence
3. **VectorService** (`backend/services.py`): Manages vector embeddings for search

### Data Flow

```
Client Request → FastAPI Endpoint → Validation → Fetch Prompt → Update Prompt → 
Update S3 → Regenerate Embedding → Update Vector Store → Return Response
```

## Components and Interfaces

### API Endpoint

**Endpoint:** `PATCH /prompts/{prompt_id}/tools`

**Request Model:**
```python
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
```

**Response Model:**
```python
{
    "status": "success",
    "prompt_id": str,
    "old_tool_names": List[str],
    "new_tool_names": List[str],
    "embedding_updated": bool,
    "message": str
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input (empty list, non-string values, empty strings after trim)
- `404 Not Found`: Prompt ID does not exist
- `500 Internal Server Error`: S3 or system failure

### Implementation Details

#### Endpoint Handler

The endpoint handler will:
1. Accept `prompt_id` as a path parameter
2. Parse and validate the `UpdateToolsRequest` body
3. Fetch the existing prompt from S3 using `s3_service.list_prompts()`
4. Validate that the prompt exists
5. Store the old `tool_used` value for the response
6. Update the prompt's `tool_used` field with the new tool names
7. Call `s3_service.update_prompt()` to persist changes
8. Regenerate the vector embedding using `vector_service.add_point()`
9. Return a success response with old/new values and embedding status

#### Validation Logic

Input validation will occur at two levels:

1. **Pydantic Model Validation**: Ensures `tool_names` is a list of strings
2. **Custom Validator**: 
   - Checks that the list is not empty
   - Trims whitespace from each tool name
   - Rejects empty strings after trimming

#### Prompt Retrieval

Since there's no direct `get_prompt()` method, the implementation will:
```python
all_prompts = s3_service.list_prompts()
prompt = next((p for p in all_prompts if p['id'] == prompt_id), None)
```

This follows the existing pattern used in the `update_prompt` endpoint.

#### Vector Embedding Update

The embedding update will use the existing `vector_service.add_point()` method:

```python
searchable_text = vector_service._construct_searchable_text(
    prompt['title'],
    prompt['description'],
    prompt['prompt_text'],
    new_tool_names,  # Updated tool names
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
        "tool_used": new_tool_names,  # Updated tool names
        "prompt_text": prompt['prompt_text']
    }
)
```

## Data Models

### Existing Prompt Structure
```python
{
    "id": str,
    "title": str,
    "description": str,
    "tool_used": List[str],  # Field to be updated
    "prompt_text": str,
    "tags": List[str],
    "username": Optional[str],
    "owner_email": Optional[str],
    "upvotes": int,
    "upvoted_by": List[str],
    "created_at": str (ISO format)
}
```

Only the `tool_used` field will be modified; all other fields remain unchanged.

## Error Handling

### Validation Errors (400)

Handled by Pydantic and custom validators:
- Empty `tool_names` list
- Non-string values in list
- Empty strings after whitespace trimming

FastAPI automatically returns 422 for Pydantic validation errors, but we'll catch these and return 400 for consistency.

### Not Found Errors (404)

When the prompt_id doesn't exist in S3:
```python
if not prompt:
    raise HTTPException(status_code=404, detail=f"Prompt {prompt_id} not found")
```

### Server Errors (500)

Wrapped in try-except to catch:
- S3 service failures
- Unexpected exceptions

If vector embedding update fails, the S3 update still succeeds, and the response includes `embedding_updated: false` with a warning message.

### Error Response Format
```python
{
    "detail": str  # Error message
}
```

## Testing Strategy

### Unit Testing

Test cases should cover:

1. **Successful Update**
   - Valid prompt_id and tool_names
   - Verify S3 update called with correct data
   - Verify vector service called with new tool names
   - Verify response includes old and new tool names

2. **Validation Errors**
   - Empty tool_names list → 400
   - List with empty strings → 400
   - List with whitespace-only strings → 400
   - Non-list input → 400

3. **Not Found**
   - Non-existent prompt_id → 404

4. **Partial Failure**
   - S3 update succeeds but vector update fails
   - Verify response indicates embedding_updated: false

5. **Complete Failure**
   - S3 update fails → 500

### Integration Testing

Test with actual S3 and vector services (or mocks):
- End-to-end flow with real prompt data
- Verify embedding regeneration with different tool names
- Verify search results reflect updated tool names

### Manual Testing

Use curl or Postman to test:
```bash
curl -X PATCH http://localhost:8000/prompts/{prompt_id}/tools \
  -H "Content-Type: application/json" \
  -d '{"tool_names": ["ChatGPT", "Claude"]}'
```

## Implementation Notes

### Existing Code Patterns

The implementation follows existing patterns in `backend/main.py`:
- Uses `HTTPException` for error responses
- Uses `s3_service.list_prompts()` to fetch prompts
- Uses `s3_service.update_prompt()` for persistence
- Uses `vector_service.add_point()` for embedding updates
- Follows the same structure as the `update_prompt` endpoint

### Mock Mode Support

The endpoint will work in both real and mock modes since it uses the existing service abstractions that already handle mock mode.

### No Authentication Required

Since this is a one-time migration tool, authentication is not implemented. In a production scenario, this endpoint should be protected or removed after migration.

## Deployment Considerations

### One-Time Use

This endpoint is designed for one-time migration:
- Can be called multiple times for different prompts
- Idempotent: calling with the same tool_names multiple times has the same effect
- Should be removed or protected after migration is complete

### Performance

- Each request processes one prompt
- Vector embedding generation adds ~1-2 seconds per request
- For bulk migrations, consider calling the endpoint sequentially with delays to avoid rate limits

### Rollback

If incorrect tool names are applied:
- Call the endpoint again with the correct tool names
- The old tool names are returned in the response for reference
- No built-in rollback mechanism since this is a simple one-time tool
