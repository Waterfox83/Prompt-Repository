import toolsData from '../data/tools.json' with { type: 'json' };

/**
 * Service class for managing AI tool metadata and information
 * Provides methods to retrieve, filter, and search tool information
 */
class ToolMetadataService {
  constructor() {
    this.tools = toolsData.tools;
    this.categories = toolsData.categories;
    this.toolsById = this._createToolsIndex();
  }

  /**
   * Create an index of tools by ID for faster lookups
   * @private
   */
  _createToolsIndex() {
    const index = {};
    this.tools.forEach(tool => {
      index[tool.id] = tool;
    });
    return index;
  }

  /**
   * Get all available tools
   * @returns {Array} Array of all tool objects
   */
  getAllTools() {
    return [...this.tools];
  }

  /**
   * Get tool by ID
   * @param {string} toolId - The tool identifier
   * @returns {Object|null} Tool object or null if not found
   */
  getToolById(toolId) {
    return this.toolsById[toolId] || null;
  }

  /**
   * Get tool by display name (case-insensitive)
   * @param {string} displayName - The tool display name
   * @returns {Object|null} Tool object or null if not found
   */
  getToolByDisplayName(displayName) {
    const normalizedName = displayName.toLowerCase().trim();
    return this.tools.find(tool => 
      tool.displayName.toLowerCase() === normalizedName
    ) || null;
  }

  /**
   * Get all tools in a specific category
   * @param {string} category - The category name (coding, writing, design, automation)
   * @returns {Array} Array of tools in the specified category
   */
  getToolsByCategory(category) {
    return this.tools.filter(tool => tool.category === category);
  }

  /**
   * Get all available categories
   * @returns {Object} Categories object with metadata
   */
  getCategories() {
    return { ...this.categories };
  }

  /**
   * Get category information by name
   * @param {string} categoryName - The category name
   * @returns {Object|null} Category object or null if not found
   */
  getCategoryInfo(categoryName) {
    return this.categories[categoryName] || null;
  }

  /**
   * Search tools by name or description
   * @param {string} query - Search query
   * @returns {Array} Array of matching tools
   */
  searchTools(query) {
    if (!query || query.trim().length === 0) {
      return this.getAllTools();
    }

    const normalizedQuery = query.toLowerCase().trim();
    
    return this.tools.filter(tool => {
      const matchesName = tool.displayName.toLowerCase().includes(normalizedQuery);
      const matchesDescription = tool.description.toLowerCase().includes(normalizedQuery);
      const matchesDetailedDescription = tool.detailedDescription.toLowerCase().includes(normalizedQuery);
      const matchesUseCases = tool.useCases.some(useCase => 
        useCase.toLowerCase().includes(normalizedQuery)
      );
      
      return matchesName || matchesDescription || matchesDetailedDescription || matchesUseCases;
    });
  }

  /**
   * Get tools with enhanced metadata for display
   * @param {string} toolId - The tool identifier
   * @returns {Object|null} Enhanced tool object with additional computed properties
   */
  getEnhancedToolInfo(toolId) {
    const tool = this.getToolById(toolId);
    if (!tool) return null;

    const category = this.getCategoryInfo(tool.category);
    
    return {
      ...tool,
      categoryInfo: category,
      hasGettingStarted: !!tool.gettingStartedUrl,
      hasPopularPrompts: tool.popularPrompts && tool.popularPrompts.length > 0,
      useCaseCount: tool.useCases.length
    };
  }

  /**
   * Get tools grouped by category
   * @returns {Object} Object with categories as keys and arrays of tools as values
   */
  getToolsGroupedByCategory() {
    const grouped = {};
    
    // Initialize with empty arrays for all categories
    Object.keys(this.categories).forEach(categoryName => {
      grouped[categoryName] = [];
    });
    
    // Group tools by category
    this.tools.forEach(tool => {
      if (grouped[tool.category]) {
        grouped[tool.category].push(tool);
      }
    });
    
    return grouped;
  }

  /**
   * Get suggested tools based on a category or use case
   * @param {string} context - Context for suggestions (category name or use case)
   * @param {number} limit - Maximum number of suggestions (default: 3)
   * @returns {Array} Array of suggested tools
   */
  getSuggestedTools(context, limit = 3) {
    const normalizedContext = context.toLowerCase().trim();
    
    // First try to match by category
    const categoryTools = this.getToolsByCategory(normalizedContext);
    if (categoryTools.length > 0) {
      return categoryTools.slice(0, limit);
    }
    
    // Then try to match by use cases or descriptions
    const matchingTools = this.tools.filter(tool => {
      const matchesUseCases = tool.useCases.some(useCase => 
        useCase.toLowerCase().includes(normalizedContext)
      );
      const matchesDescription = tool.description.toLowerCase().includes(normalizedContext) ||
                                tool.detailedDescription.toLowerCase().includes(normalizedContext);
      
      return matchesUseCases || matchesDescription;
    });
    
    return matchingTools.slice(0, limit);
  }

  /**
   * Validate tool data structure
   * @param {Object} toolData - Tool data to validate
   * @returns {Object} Validation result with isValid boolean and errors array
   */
  validateToolData(toolData) {
    const errors = [];
    const requiredFields = ['id', 'displayName', 'description', 'category', 'accessUrl'];
    
    requiredFields.forEach(field => {
      if (!toolData[field] || toolData[field].trim().length === 0) {
        errors.push(`Missing required field: ${field}`);
      }
    });
    
    if (toolData.category && !this.categories[toolData.category]) {
      errors.push(`Invalid category: ${toolData.category}`);
    }
    
    if (toolData.accessUrl && !this._isValidUrl(toolData.accessUrl)) {
      errors.push(`Invalid access URL: ${toolData.accessUrl}`);
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  /**
   * Check if a URL is valid
   * @private
   * @param {string} url - URL to validate
   * @returns {boolean} True if valid URL
   */
  _isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get fallback tool info for unknown tools
   * @param {string} toolName - Name of unknown tool
   * @returns {Object} Basic tool object with fallback data
   */
  createFallbackTool(toolName) {
    return {
      id: toolName.toLowerCase().replace(/\s+/g, '-'),
      displayName: toolName,
      description: `AI tool: ${toolName}`,
      detailedDescription: `${toolName} is an AI tool. More information may be available on their official website.`,
      category: 'coding', // Default category
      accessUrl: '#',
      useCases: ['General AI assistance'],
      gettingStartedUrl: null,
      popularPrompts: [],
      isFallback: true
    };
  }
}

// Create and export a singleton instance
const toolMetadataService = new ToolMetadataService();
export default toolMetadataService;

// Also export the class for testing purposes
export { ToolMetadataService };