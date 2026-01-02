# Implementation Plan

- [x] 1. Create Pydantic request model with validation
  - Define `UpdateToolsRequest` model in `backend/main.py`
  - Add `tool_names: List[str]` field
  - Implement custom validator to check for empty list
  - Implement validator to trim whitespace and reject empty strings
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2. Implement PATCH endpoint handler
  - Add `@app.patch("/prompts/{prompt_id}/tools")` route in `backend/main.py`
  - Accept `prompt_id` as path parameter and `UpdateToolsRequest` as body
  - Fetch all prompts using `s3_service.list_prompts()`
  - Find the target prompt by ID using list comprehension
  - Raise 404 HTTPException if prompt not found
  - _Requirements: 1.1, 1.4, 3.4_

- [x] 3. Update prompt data in S3
  - Store the old `tool_used` value before updating
  - Update the prompt dictionary with new `tool_names`
  - Preserve all other prompt fields (title, description, tags, owner_email, upvotes, created_at)
  - Call `s3_service.update_prompt(prompt_id, prompt)` to persist changes
  - _Requirements: 1.1, 1.2_

- [x] 4. Regenerate vector embedding
  - Construct searchable text using `vector_service._construct_searchable_text()` with new tool names
  - Create metadata dictionary with updated `tool_used` field
  - Call `vector_service.add_point()` with searchable text and metadata
  - Capture the return value to determine if embedding update succeeded
  - _Requirements: 1.5_

- [x] 5. Build and return response
  - Create response dictionary with status, prompt_id, old_tool_names, new_tool_names
  - Include `embedding_updated` boolean flag based on vector service result
  - Add descriptive message indicating success
  - Return response with 200 status code
  - _Requirements: 1.3_

- [x] 6. Implement error handling
  - Wrap main logic in try-except block
  - Catch and re-raise HTTPException instances
  - Catch S3 service exceptions and return 500 with error details
  - Handle vector service failures gracefully (still return 200 but flag embedding_updated as false)
  - Ensure all error responses include descriptive messages
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 7. Test the endpoint
  - Test with valid prompt_id and tool_names list
  - Test with non-existent prompt_id (expect 404)
  - Test with empty tool_names list (expect 400)
  - Test with tool_names containing empty strings (expect 400)
  - Test with tool_names containing whitespace-only strings (expect 400)
  - Verify S3 prompt data is updated correctly
  - Verify vector embedding is regenerated
  - Verify response includes old and new tool names
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4, 3.1, 3.2, 3.4_
