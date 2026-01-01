import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class ToolMetadataService:
    def __init__(self, s3_service):
        self.s3_service = s3_service
        self.mock_mode = os.environ.get("MOCK_MODE", "false").lower() == "true"
        
        # Load tools metadata from the frontend tools.json structure
        self._tools_metadata = self._load_tools_metadata()
        
        if self.mock_mode:
            print("ToolMetadataService: Initialized in MOCK MODE")

    def _load_tools_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load tools metadata from frontend/src/data/tools.json structure"""
        # In a real deployment, this would be loaded from a shared location
        # For now, we'll embed the structure or load from a local copy
        tools_data = {
            "chatgpt": {
                "id": "chatgpt",
                "displayName": "ChatGPT",
                "description": "OpenAI's conversational AI for general-purpose text generation and problem-solving",
                "detailedDescription": "ChatGPT is a versatile AI assistant that excels at writing, coding, analysis, and creative tasks. It can help with code reviews, documentation, debugging, and explaining complex concepts.",
                "category": "coding",
                "icon": "🤖",
                "accessUrl": "https://chat.openai.com",
                "useCases": [
                    "Code review and debugging",
                    "Writing documentation", 
                    "Explaining complex algorithms",
                    "Generating test cases",
                    "Refactoring code"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "claude": {
                "id": "claude",
                "displayName": "Claude",
                "description": "Anthropic's AI assistant focused on helpful, harmless, and honest interactions",
                "detailedDescription": "Claude excels at analytical thinking, code analysis, and detailed explanations. It's particularly strong at understanding context and providing thorough, well-reasoned responses.",
                "category": "coding",
                "icon": "🧠",
                "accessUrl": "https://claude.ai",
                "useCases": [
                    "Code analysis and optimization",
                    "Technical writing",
                    "System design discussions",
                    "Code architecture reviews",
                    "Complex problem solving"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "gemini": {
                "id": "gemini",
                "displayName": "Gemini",
                "description": "Google's multimodal AI model for text, code, and image understanding",
                "detailedDescription": "Gemini combines text and visual understanding, making it excellent for projects involving both code and visual elements. It integrates well with Google's ecosystem.",
                "category": "coding",
                "icon": "💎",
                "accessUrl": "https://gemini.google.com",
                "useCases": [
                    "Multimodal code analysis",
                    "Image-to-code generation",
                    "Google Cloud integration",
                    "Data analysis with charts",
                    "API documentation with visuals"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "copilot": {
                "id": "copilot",
                "displayName": "GitHub Copilot",
                "description": "AI pair programmer that suggests code completions and entire functions",
                "detailedDescription": "GitHub Copilot is integrated directly into your IDE, providing real-time code suggestions, function completions, and helping with boilerplate code generation.",
                "category": "coding",
                "icon": "🚁",
                "accessUrl": "https://github.com/features/copilot",
                "useCases": [
                    "Real-time code completion",
                    "Function generation",
                    "Boilerplate code creation",
                    "Unit test generation",
                    "Code pattern suggestions"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "cursor": {
                "id": "cursor",
                "displayName": "Cursor",
                "description": "AI-powered code editor with built-in AI assistance",
                "detailedDescription": "Cursor is a code editor that integrates AI directly into the development workflow, offering contextual code suggestions and AI-powered editing capabilities.",
                "category": "coding",
                "icon": "📝",
                "accessUrl": "https://cursor.sh",
                "useCases": [
                    "AI-assisted code editing",
                    "Contextual code suggestions",
                    "Codebase understanding",
                    "Refactoring assistance",
                    "Code explanation"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "grammarly": {
                "id": "grammarly",
                "displayName": "Grammarly",
                "description": "AI writing assistant for grammar, style, and clarity improvements",
                "detailedDescription": "Grammarly helps improve writing quality by checking grammar, suggesting style improvements, and ensuring clarity in communication.",
                "category": "writing",
                "icon": "✍️",
                "accessUrl": "https://grammarly.com",
                "useCases": [
                    "Grammar and spell checking",
                    "Style improvement suggestions",
                    "Tone adjustment",
                    "Clarity enhancement",
                    "Professional writing"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "jasper": {
                "id": "jasper",
                "displayName": "Jasper",
                "description": "AI content creation platform for marketing and business writing",
                "detailedDescription": "Jasper specializes in marketing content, blog posts, social media content, and business communications with brand voice consistency.",
                "category": "writing",
                "icon": "📄",
                "accessUrl": "https://jasper.ai",
                "useCases": [
                    "Marketing copy creation",
                    "Blog post writing",
                    "Social media content",
                    "Email campaigns",
                    "Brand voice consistency"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "notion-ai": {
                "id": "notion-ai",
                "displayName": "Notion AI",
                "description": "Integrated AI assistant within Notion for content creation and organization",
                "detailedDescription": "Notion AI helps with writing, brainstorming, and organizing content directly within your Notion workspace, making it perfect for documentation and project management.",
                "category": "writing",
                "icon": "📋",
                "accessUrl": "https://notion.so",
                "useCases": [
                    "Documentation writing",
                    "Meeting notes summarization",
                    "Project planning",
                    "Content brainstorming",
                    "Task organization"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "midjourney": {
                "id": "midjourney",
                "displayName": "Midjourney",
                "description": "AI image generation tool for creating artistic and professional visuals",
                "detailedDescription": "Midjourney excels at creating high-quality, artistic images from text descriptions. It's particularly strong at stylized artwork and creative visuals.",
                "category": "design",
                "icon": "🎨",
                "accessUrl": "https://midjourney.com",
                "useCases": [
                    "Concept art creation",
                    "Marketing visuals",
                    "Artistic illustrations",
                    "Product mockups",
                    "Creative brainstorming"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "dall-e": {
                "id": "dall-e",
                "displayName": "DALL-E",
                "description": "OpenAI's image generation model for creating images from text descriptions",
                "detailedDescription": "DALL-E creates realistic and artistic images from natural language descriptions, with strong capabilities in photorealistic and creative imagery.",
                "category": "design",
                "icon": "🖼️",
                "accessUrl": "https://openai.com/dall-e-2",
                "useCases": [
                    "Photorealistic image generation",
                    "Product visualization",
                    "Creative artwork",
                    "Concept illustrations",
                    "Marketing imagery"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "figma-ai": {
                "id": "figma-ai",
                "displayName": "Figma AI",
                "description": "AI-powered design assistance within Figma for UI/UX design",
                "detailedDescription": "Figma AI helps with design workflows, generating design variations, and automating repetitive design tasks within the Figma interface.",
                "category": "design",
                "icon": "🎯",
                "accessUrl": "https://figma.com",
                "useCases": [
                    "UI component generation",
                    "Design system creation",
                    "Layout suggestions",
                    "Color palette generation",
                    "Design automation"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "canva-ai": {
                "id": "canva-ai",
                "displayName": "Canva AI",
                "description": "AI design tools within Canva for quick graphic creation",
                "detailedDescription": "Canva AI provides automated design suggestions, background removal, and content generation within Canva's user-friendly design platform.",
                "category": "design",
                "icon": "🌈",
                "accessUrl": "https://canva.com",
                "useCases": [
                    "Social media graphics",
                    "Presentation design",
                    "Marketing materials",
                    "Logo creation",
                    "Brand asset generation"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "zapier": {
                "id": "zapier",
                "displayName": "Zapier AI",
                "description": "AI-powered workflow automation connecting different apps and services",
                "detailedDescription": "Zapier AI helps create automated workflows between different applications, reducing manual tasks and improving productivity through intelligent automation.",
                "category": "automation",
                "icon": "⚡",
                "accessUrl": "https://zapier.com",
                "useCases": [
                    "Workflow automation",
                    "App integration",
                    "Data synchronization",
                    "Task automation",
                    "Process optimization"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "make": {
                "id": "make",
                "displayName": "Make (Integromat)",
                "description": "Visual automation platform for connecting apps and automating workflows",
                "detailedDescription": "Make provides a visual interface for creating complex automation scenarios, with AI assistance for workflow optimization and error handling.",
                "category": "automation",
                "icon": "🔧",
                "accessUrl": "https://make.com",
                "useCases": [
                    "Complex workflow automation",
                    "Data processing pipelines",
                    "API integrations",
                    "Business process automation",
                    "Multi-step workflows"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "github-actions": {
                "id": "github-actions",
                "displayName": "GitHub Actions",
                "description": "CI/CD automation platform with AI-assisted workflow creation",
                "detailedDescription": "GitHub Actions automates software development workflows with AI assistance for creating, optimizing, and troubleshooting CI/CD pipelines.",
                "category": "automation",
                "icon": "🔄",
                "accessUrl": "https://github.com/features/actions",
                "useCases": [
                    "CI/CD pipeline automation",
                    "Code deployment",
                    "Testing automation",
                    "Release management",
                    "Code quality checks"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            },
            "n8n": {
                "id": "n8n",
                "displayName": "n8n",
                "description": "Open-source workflow automation tool with AI integration capabilities",
                "detailedDescription": "n8n is a self-hosted automation platform that can integrate AI services and create complex workflows with visual node-based editing.",
                "category": "automation",
                "icon": "🌐",
                "accessUrl": "https://n8n.io",
                "useCases": [
                    "Self-hosted automation",
                    "AI service integration",
                    "Custom workflow creation",
                    "Data processing",
                    "API orchestration"
                ],
                "gettingStartedUrl": None,
                "popularPrompts": []
            }
        }
        
        return tools_data

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools with metadata"""
        return list(self._tools_metadata.values())

    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata by ID"""
        return self._tools_metadata.get(tool_id)

    def get_tool_by_display_name(self, display_name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata by display name (case-insensitive)"""
        for tool in self._tools_metadata.values():
            if tool["displayName"].lower() == display_name.lower():
                return tool
        return None

    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all tools in a specific category"""
        return [tool for tool in self._tools_metadata.values() if tool["category"] == category]

    def get_tool_statistics(self, tool_id: str) -> Dict[str, Any]:
        """Calculate usage statistics for a specific tool"""
        all_prompts = self.s3_service.list_prompts()
        
        # Find tool metadata
        tool_metadata = self.get_tool_by_id(tool_id)
        if not tool_metadata:
            # Try to find by display name
            tool_metadata = self.get_tool_by_display_name(tool_id)
        
        if not tool_metadata:
            return {
                "tool_id": tool_id,
                "prompt_count": 0,
                "total_upvotes": 0,
                "unique_contributors": 0,
                "recent_activity": {
                    "weekly_prompts": 0,
                    "weekly_upvotes": 0
                },
                "top_contributors": [],
                "error": "Tool not found"
            }

        display_name = tool_metadata["displayName"]
        
        # Filter prompts for this tool
        tool_prompts = []
        for prompt in all_prompts:
            tool_used = prompt.get("tool_used", [])
            if isinstance(tool_used, str):
                tool_used = [tool_used]
            
            # Check if tool matches by display name (case-insensitive)
            if any(tool.lower() == display_name.lower() for tool in tool_used):
                tool_prompts.append(prompt)

        # Calculate statistics
        prompt_count = len(tool_prompts)
        total_upvotes = sum(prompt.get("upvotes", 0) for prompt in tool_prompts)
        
        # Get unique contributors
        contributors = set()
        for prompt in tool_prompts:
            if prompt.get("username"):
                contributors.add(prompt["username"])
            elif prompt.get("owner_email"):
                contributors.add(prompt["owner_email"])
        
        unique_contributors = len(contributors)
        
        # Calculate recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        weekly_prompts = 0
        weekly_upvotes = 0
        
        for prompt in tool_prompts:
            created_at = prompt.get("created_at")
            if created_at:
                try:
                    prompt_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if prompt_date >= week_ago:
                        weekly_prompts += 1
                        weekly_upvotes += prompt.get("upvotes", 0)
                except:
                    pass  # Skip invalid dates
        
        # Get top contributors
        contributor_counts = Counter()
        for prompt in tool_prompts:
            contributor = prompt.get("username") or prompt.get("owner_email")
            if contributor:
                contributor_counts[contributor] += 1
        
        top_contributors = [{"name": name, "count": count} 
                          for name, count in contributor_counts.most_common(5)]

        return {
            "tool_id": tool_id,
            "display_name": display_name,
            "prompt_count": prompt_count,
            "total_upvotes": total_upvotes,
            "unique_contributors": unique_contributors,
            "recent_activity": {
                "weekly_prompts": weekly_prompts,
                "weekly_upvotes": weekly_upvotes
            },
            "top_contributors": top_contributors
        }

    def get_prompts_by_tool(self, tool_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all prompts that use a specific tool"""
        all_prompts = self.s3_service.list_prompts()
        
        # Find tool metadata
        tool_metadata = self.get_tool_by_id(tool_id)
        if not tool_metadata:
            tool_metadata = self.get_tool_by_display_name(tool_id)
        
        if not tool_metadata:
            return []

        display_name = tool_metadata["displayName"]
        
        # Filter prompts for this tool
        tool_prompts = []
        for prompt in all_prompts:
            tool_used = prompt.get("tool_used", [])
            if isinstance(tool_used, str):
                tool_used = [tool_used]
            
            # Check if tool matches by display name (case-insensitive)
            if any(tool.lower() == display_name.lower() for tool in tool_used):
                tool_prompts.append(prompt)

        # Sort by creation date (newest first)
        tool_prompts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply limit if specified
        if limit:
            tool_prompts = tool_prompts[:limit]
        
        return tool_prompts

    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all tool categories with metadata"""
        categories = {
            "coding": {
                "name": "Coding & Development",
                "description": "AI tools for software development, code review, and programming assistance",
                "icon": "💻"
            },
            "writing": {
                "name": "Writing & Content",
                "description": "AI assistants for writing, editing, and content creation",
                "icon": "✍️"
            },
            "design": {
                "name": "Design & Creative",
                "description": "AI tools for visual design, image generation, and creative work",
                "icon": "🎨"
            },
            "automation": {
                "name": "Automation & Workflows",
                "description": "AI-powered tools for automating tasks and creating workflows",
                "icon": "⚡"
            }
        }
        
        # Add tool counts to each category
        for category_id, category_info in categories.items():
            tools_in_category = self.get_tools_by_category(category_id)
            category_info["tool_count"] = len(tools_in_category)
            category_info["tools"] = [tool["id"] for tool in tools_in_category]
        
        return categories

    def normalize_tool_name(self, tool_name: str) -> Optional[str]:
        """Normalize a tool name to match our metadata (returns tool ID)"""
        # First try exact match by display name
        for tool_id, tool in self._tools_metadata.items():
            if tool["displayName"].lower() == tool_name.lower():
                return tool_id
        
        # Try partial matches for common variations
        tool_name_lower = tool_name.lower()
        for tool_id, tool in self._tools_metadata.items():
            display_name_lower = tool["displayName"].lower()
            
            # Handle common variations
            if ("chatgpt" in tool_name_lower or "chat gpt" in tool_name_lower) and tool_id == "chatgpt":
                return tool_id
            elif "github copilot" in tool_name_lower and tool_id == "copilot":
                return tool_id
            elif "dall-e" in tool_name_lower or "dalle" in tool_name_lower and tool_id == "dall-e":
                return tool_id
            elif tool_name_lower in display_name_lower or display_name_lower in tool_name_lower:
                return tool_id
        
        return None