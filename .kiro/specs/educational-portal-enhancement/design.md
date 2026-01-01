# Design Document

## Overview

This design transforms the existing AI prompt repository from a basic search interface into a comprehensive educational portal. The enhancement addresses user onboarding challenges and integrates tool discovery directly into the prompt browsing experience. The design maintains the current three-tier architecture (React frontend, FastAPI backend, S3 storage) while adding new components for guided discovery and educational content.

## Architecture

### Current Architecture Analysis
The application currently uses:
- **Frontend**: React with component-based architecture (App.jsx orchestrates state, individual components handle specific UI concerns)
- **Backend**: FastAPI with S3Service, VectorService, and SESService
- **Storage**: S3 for prompt data, vector embeddings for semantic search
- **Authentication**: Magic link authentication with session cookies

### Enhanced Architecture Components

#### 1. Frontend Architecture Enhancements

**State Management Expansion**
- Add `uiState` for managing dashboard views, onboarding flow, and educational overlays
- Extend existing `activeFilter` to support tool-specific contexts
- Add `onboardingState` to track user's first-time experience

**New Component Structure**
```
components/
├── dashboard/
│   ├── DashboardLayout.jsx (three-zone layout wrapper)
│   ├── TopBar.jsx (breadcrumbs, user profile, actions)
│   └── MainCanvas.jsx (content area with context switching)
├── onboarding/
│   ├── HeroMissionStatement.jsx
│   └── SearchSuggestionChips.jsx
├── tools/
│   ├── ToolHeader.jsx (tool information display for filtered views)
│   └── ToolSelector.jsx (enhanced form component)
└── educational/
    ├── ContributionGuide.jsx
    └── EmptyStateGuide.jsx
```

#### 2. Backend Architecture Enhancements

**New Service Layer**
- `ToolMetadataService`: Manages tool information, descriptions, and educational content
- `OnboardingService`: Handles user onboarding state and guided experience tracking
- Enhanced `S3Service` methods for user preferences and onboarding data

**API Endpoints Expansion**
```python
# Tool Discovery
GET /tools - List all available tools with metadata
GET /tools/{tool_id}/prompts - Get prompts filtered by specific tool
GET /tools/{tool_id}/stats - Get usage statistics for tool

# User Experience
GET /users/me/onboarding - Get user's onboarding progress
PUT /users/me/onboarding - Update onboarding state
GET /users/me/preferences - Get user dashboard preferences
PUT /users/me/preferences - Update user preferences

# Enhanced Search
GET /search/suggestions - Get popular search terms and suggestions
GET /prompts/categories - Get categorized prompt collections
```

## Components and Interfaces

### 1. Dashboard Layout System

**DashboardLayout Component**
```jsx
interface DashboardLayoutProps {
  sidebar: ReactNode;
  topBar: ReactNode;
  mainContent: ReactNode;
  breadcrumbs?: BreadcrumbItem[];
}

interface BreadcrumbItem {
  label: string;
  path?: string;
  active?: boolean;
}
```

**Three-Zone Implementation**
- **Zone 1 (Sidebar)**: Fixed 260px width, persistent navigation, tool directory
- **Zone 2 (TopBar)**: 60px height, breadcrumbs, user actions, context-aware buttons
- **Zone 3 (MainCanvas)**: Flexible content area, context-sensitive layouts

### 2. Tool Discovery System

**Enhanced Tool Metadata Structure**
```typescript
interface ToolMetadata {
  id: string;
  displayName: string;
  description: string;
  detailedDescription: string; // New: Extended educational content
  accessUrl: string;
  icon: string;
  category: 'coding' | 'writing' | 'design' | 'automation'; // New: Categorization
  useCases: string[]; // New: Specific use case examples
  gettingStartedUrl?: string; // New: Link to internal documentation
  popularPrompts?: string[]; // New: IDs of most popular prompts for this tool
}
```

**Tool Card Overlay Component**
```jsx
interface ToolCardProps {
  tool: ToolMetadata;
  onViewPrompts: (toolId: string) => void;
  onClose: () => void;
  promptCount?: number;
  topPrompts?: Prompt[];
}
```

### 3. Onboarding and Guidance System

**Mission Statement Component**
- Displays above search bar when no active search/filter
- Two-sentence value proposition with clear call-to-action
- Animated entrance for first-time users

**Search Suggestion Chips**
```jsx
interface SearchChip {
  label: string;
  query: string;
  category: 'popular' | 'beginner' | 'advanced';
  icon?: string;
}
```

**Tool Header Component**
```jsx
interface ToolHeaderProps {
  toolName: string;
  promptCount: number;
}
```

### 4. Enhanced Contribution Flow

**Multi-Step Tool Selection**
```jsx
interface ContributionStep {
  stepNumber: number;
  title: string;
  description: string;
  component: ReactNode;
  validation: (data: any) => boolean;
}
```

**Educational Tool Selector**
- Visual tool grid with icons and descriptions
- Real-time educational content based on selection
- Progressive disclosure of tool-specific guidance

### 5. Social Features Enhancement

**Enhanced Prompt Card Interface**
```jsx
interface EnhancedPromptCard extends PromptCard {
  socialSignals: {
    upvotes: number;
    favorites: number;
    isUpvoted: boolean;
    isFavorited: boolean;
  };
  toolContext?: ToolMetadata; // When viewing in tool-filtered context
  educationalTags?: string[]; // Beginner-friendly, Advanced, etc.
}
```

## Data Models

### 1. User Onboarding State
```typescript
interface UserOnboardingState {
  userId: string;
  hasCompletedTour: boolean;
  hasAddedFirstPrompt: boolean;
  hasUsedSearch: boolean;
  hasExploredTools: boolean;
  preferredTools: string[];
  lastVisitDate: string;
  onboardingVersion: string; // For future onboarding updates
}
```

### 2. Enhanced Tool Usage Analytics
```typescript
interface ToolUsageStats {
  toolId: string;
  promptCount: number;
  totalUpvotes: number;
  uniqueContributors: number;
  recentActivity: {
    weeklyPrompts: number;
    weeklyUpvotes: number;
  };
  topContributors: string[];
}
```

### 3. Search Enhancement Data
```typescript
interface SearchSuggestion {
  query: string;
  category: 'popular' | 'recent' | 'recommended';
  frequency: number;
  relatedTools: string[];
}

interface CategoryCollection {
  id: string;
  name: string;
  description: string;
  promptIds: string[];
  targetAudience: 'beginner' | 'intermediate' | 'advanced' | 'all';
}
```

## Error Handling

### 1. Progressive Enhancement Strategy
- Core functionality (search, view, add prompts) works without educational features
- Educational overlays and guidance degrade gracefully if metadata is unavailable
- Tool filtering falls back to basic tag-based filtering if enhanced metadata fails

### 2. Onboarding Resilience
- Onboarding state stored locally with S3 backup
- Missing onboarding data defaults to "experienced user" mode
- Educational content cached locally to prevent repeated API calls

### 3. Tool Metadata Fallbacks
```typescript
const getToolInfo = (toolName: string): ToolMetadata => {
  const enhanced = toolMetadataService.get(toolName);
  if (enhanced) return enhanced;
  
  // Fallback to basic info from existing tools.json
  const basic = basicToolsData.find(t => t.displayName === toolName);
  return basic ? convertToEnhanced(basic) : createDefaultTool(toolName);
};
```

## Testing Strategy

### 1. Component Testing
- **Onboarding Flow**: Test each step of guided experience, skip functionality, completion tracking
- **Tool Discovery**: Test tool card overlays, filtering, educational content display
- **Dashboard Layout**: Test responsive behavior, sidebar collapse, breadcrumb navigation
- **Enhanced Forms**: Test multi-step contribution flow, tool selection, educational hints

### 2. Integration Testing
- **User Journey Testing**: Complete flows from first visit to successful contribution
- **Cross-Component Communication**: Tool selection → filtering → prompt display chain
- **State Management**: Onboarding state persistence, user preferences, session handling

### 3. User Experience Testing
- **A/B Testing Framework**: Compare onboarding completion rates with/without guidance
- **Analytics Integration**: Track user engagement with educational features
- **Performance Testing**: Ensure educational overlays don't impact core functionality performance

### 4. Accessibility Testing
- **Keyboard Navigation**: All educational overlays and guided flows accessible via keyboard
- **Screen Reader Compatibility**: Tool descriptions and onboarding content properly labeled
- **Color Contrast**: Educational highlighting and category sections meet WCAG standards

### 5. Backend Testing
- **Tool Metadata API**: Test CRUD operations, caching, fallback behavior
- **Onboarding State**: Test user state persistence, migration, privacy compliance
- **Enhanced Search**: Test suggestion generation, category filtering, performance with large datasets

## Implementation Phases

### Phase 1: Dashboard Architecture (Foundation)
- Implement three-zone layout system
- Create enhanced sidebar with tool directory
- Add breadcrumb navigation and context-aware top bar
- Migrate existing components to new layout system

### Phase 2: Onboarding and Intent Clarity (User Experience)
- Add mission statement above search bar
- Implement search suggestion chips
- Ensure clean empty state without overwhelming guidance sections

### Phase 3: Tool Discovery Integration (Educational Features)
- Enhance tool metadata system
- Create tool header component for filtered views
- Implement tool information display when accessing tools from sidebar
- Add tool selection guidance in contribution flow

### Phase 4: Social Features and Quality Signals (Engagement)
- Implement favorites system with sidebar integration
- Add upvoting with sorting capabilities
- Create "Most Popular" and quality-based discovery
- Add user contribution tracking and recognition

This design maintains backward compatibility while providing a clear path for transforming the application into an educational portal that guides users through AI tool discovery and prompt sharing.