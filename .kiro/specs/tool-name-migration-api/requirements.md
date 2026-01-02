# Requirements Document

## Introduction

Create a simple one-time data migration API endpoint that allows updating tool names in existing prompts. This addresses the need to correct or standardize tool names across the prompt repository. The API will accept a prompt ID and a list of new tool names, replacing the existing tool names for that prompt.

## Requirements

### Requirement 1: Tool Name Update API Endpoint

**User Story:** As an administrator, I want to update the tool names associated with a specific prompt, so that I can correct outdated or incorrect tool references in the repository.

#### Acceptance Criteria

1. WHEN an administrator sends a PATCH request to `/prompts/{prompt_id}/tools` with a list of tool names THEN the system SHALL update the prompt's `tool_used` field with the provided list
2. WHEN the tool names are updated THEN the system SHALL preserve all other prompt metadata including title, description, tags, owner_email, upvotes, and created_at
3. WHEN the update is successful THEN the system SHALL return a 200 status code with the updated prompt data
4. IF the prompt_id does not exist THEN the system SHALL return a 404 status code with an error message
5. WHEN the tool names are updated THEN the system SHALL regenerate and update the vector embedding for the prompt to reflect the new tool associations

### Requirement 2: Input Validation

**User Story:** As a system administrator, I want the migration API to validate inputs, so that invalid data is rejected and data integrity is maintained.

#### Acceptance Criteria

1. WHEN a request is made THEN the system SHALL validate that the tool_names parameter is a list of strings
2. IF the tool_names list is empty THEN the system SHALL return a 400 status code with an error message
3. IF the tool_names list contains non-string values THEN the system SHALL return a 400 status code with validation error details
4. WHEN validating tool names THEN the system SHALL trim whitespace from each tool name and reject empty strings after trimming

### Requirement 3: Error Handling

**User Story:** As a system operator, I want the migration API to handle errors gracefully and provide clear error messages, so that I can troubleshoot issues and ensure data integrity.

#### Acceptance Criteria

1. IF the S3 update fails THEN the system SHALL return a 500 status code with details about the failure
2. IF the vector embedding update fails THEN the system SHALL still complete the S3 update and return a 200 status with a warning flag
3. WHEN an error occurs THEN the system SHALL include a descriptive error message in the response
4. IF the prompt is not found THEN the system SHALL return a 404 status code with a clear error message
