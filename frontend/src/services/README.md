# ToolMetadataService

A utility service for managing AI tool metadata and information in the educational portal.

## Usage

```javascript
import toolMetadataService from './services/ToolMetadataService.js';

// Get all tools
const allTools = toolMetadataService.getAllTools();

// Get a specific tool by ID
const chatgpt = toolMetadataService.getToolById('chatgpt');

// Get tools by category
const codingTools = toolMetadataService.getToolsByCategory('coding');

// Search tools
const searchResults = toolMetadataService.searchTools('code review');

// Get enhanced tool information
const enhanced = toolMetadataService.getEnhancedToolInfo('midjourney');

// Get tools grouped by category
const grouped = toolMetadataService.getToolsGroupedByCategory();
```

## Available Methods

- `getAllTools()` - Get all available tools
- `getToolById(id)` - Get tool by ID
- `getToolByDisplayName(name)` - Get tool by display name (case-insensitive)
- `getToolsByCategory(category)` - Get tools in a specific category
- `getCategories()` - Get all available categories
- `getCategoryInfo(categoryName)` - Get category information
- `searchTools(query)` - Search tools by name, description, or use cases
- `getEnhancedToolInfo(id)` - Get tool with additional computed properties
- `getToolsGroupedByCategory()` - Get tools organized by category
- `getSuggestedTools(context, limit)` - Get suggested tools based on context
- `validateToolData(toolData)` - Validate tool data structure
- `createFallbackTool(toolName)` - Create fallback tool for unknown tools

## Tool Data Structure

Each tool contains:
- `id` - Unique identifier
- `displayName` - Human-readable name
- `description` - Short description
- `detailedDescription` - Extended description
- `category` - Tool category (coding, writing, design, automation)
- `icon` - Emoji icon
- `accessUrl` - Link to the tool
- `useCases` - Array of use case examples
- `gettingStartedUrl` - Optional link to documentation
- `popularPrompts` - Array of popular prompt IDs

## Categories

Available categories:
- `coding` - Coding & Development tools
- `writing` - Writing & Content tools  
- `design` - Design & Creative tools
- `automation` - Automation & Workflows tools