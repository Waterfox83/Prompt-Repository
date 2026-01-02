# Design Document

## Overview

This design outlines the implementation of hiding the favorites feature from the frontend UI while preserving backend functionality, and implementing a new upvote system. The upvote system will allow users to vote on prompts without tracking individual user votes on the frontend, displaying only aggregate counts.

## Architecture

### Current State Analysis

**Favorites System:**
- Backend has complete favorites functionality with endpoints for add/remove/list favorites
- Frontend displays StarButton component in PromptList with favorites functionality
- User context includes `is_favorited` field for each prompt
- S3 storage maintains user favorites in `users/{email}/favorites.json`

**Existing Upvote System:**
- Backend already has upvote endpoints (`POST /prompts/{id}/upvote`, `DELETE /prompts/{id}/upvote`)
- Prompts have `upvotes` count and `upvoted_by` array fields
- User context includes `is_upvoted` field
- No frontend UI currently exists for upvotes

### Design Approach

**Phase 1: Hide Favorites**
- Remove StarButton component from PromptList display
- Keep all backend favorites endpoints functional
- Remove favorites-related UI elements from modals and other components

**Phase 2: Implement Upvote UI**
- Create new UpvoteButton component
- Display upvote counts prominently
- Use existing backend upvote endpoints
- Hide individual user upvote status from UI (show only aggregate counts)

## Components and Interfaces

### Frontend Components

#### UpvoteButton Component
```jsx
// New component to replace StarButton functionality
const UpvoteButton = ({ 
  promptId, 
  upvotes = 0, 
  isUpvoted = false, 
  onUpvote, 
  size = 'medium' 
}) => {
  // Handles upvote/remove upvote logic
  // Shows only upvote count, not user's upvote status
}
```

#### Modified PromptList Component
- Remove StarButton import and usage
- Add UpvoteButton component
- Remove favorites-related props and handlers
- Display upvote counts prominently

### Backend Interfaces

**Existing Endpoints (Keep Unchanged):**
- `GET /users/me/favorites` - Keep for potential future use
- `POST /users/me/favorites/{prompt_id}` - Keep for potential future use  
- `DELETE /users/me/favorites/{prompt_id}` - Keep for potential future use
- `POST /prompts/{prompt_id}/upvote` - Use for upvote functionality
- `DELETE /prompts/{prompt_id}/upvote` - Use for remove upvote functionality

**Modified Response Format:**
- Continue including `is_favorited` in user_context but don't use in frontend
- Use `upvotes` count for display
- Use `is_upvoted` for backend logic but hide from frontend UI

## Data Models

### Prompt Model (Unchanged)
```python
class Prompt(BaseModel):
    title: str
    description: str
    tool_used: List[str]
    prompt_text: str
    tags: List[str]
    username: Optional[str] = None
    owner_email: Optional[str] = None
    upvotes: Optional[int] = 0
    upvoted_by: Optional[List[str]] = []  # Keep for backend tracking
```

### Frontend Prompt Display
```javascript
// Frontend will use these fields:
{
  id: string,
  title: string,
  description: string,
  upvotes: number,  // Display this prominently
  user_context: {
    is_upvoted: boolean,  // Use for backend calls but don't show in UI
    is_favorited: boolean,  // Ignore in frontend
    can_edit: boolean
  }
}
```

## Error Handling

### Upvote Error Scenarios
- **Already upvoted**: Show toast message "You have already upvoted this prompt"
- **Network error**: Show toast message "Failed to update upvote. Please try again."
- **Authentication error**: Redirect to login or show authentication required message
- **Prompt not found**: Show toast message "Prompt not found"

### Graceful Degradation
- If upvote count is missing, default to 0
- If upvote operation fails, revert UI state
- Maintain optimistic UI updates with rollback on failure

## Testing Strategy

### Frontend Testing
1. **Component Tests**
   - UpvoteButton component renders correctly
   - Upvote count displays properly
   - Click handlers work correctly
   - Loading states function properly

2. **Integration Tests**
   - PromptList displays upvote buttons instead of star buttons
   - Upvote functionality works end-to-end
   - Error handling displays appropriate messages
   - No favorites UI elements are visible

3. **Visual Regression Tests**
   - Verify StarButton is completely hidden
   - Verify UpvoteButton displays correctly in all contexts
   - Verify upvote counts are prominently displayed

### Backend Testing
1. **API Tests**
   - Existing upvote endpoints continue to work
   - Favorites endpoints remain functional (for future use)
   - User context continues to include all fields

2. **Data Integrity Tests**
   - Upvote counts increment/decrement correctly
   - User upvote tracking works properly
   - Favorites data remains intact

## Implementation Phases

### Phase 1: Hide Favorites (Priority: High)
1. Remove StarButton from PromptList component
2. Remove favorites-related imports and props
3. Remove favorites UI from modal views
4. Test that no favorites functionality is visible

### Phase 2: Implement Upvote UI (Priority: High)  
1. Create UpvoteButton component
2. Add UpvoteButton to PromptList
3. Implement upvote/remove upvote handlers
4. Add upvote count display
5. Add error handling and toast messages
6. Test upvote functionality end-to-end

### Phase 3: Polish and Testing (Priority: Medium)
1. Style upvote button to match design system
2. Add loading states and animations
3. Comprehensive testing
4. Documentation updates