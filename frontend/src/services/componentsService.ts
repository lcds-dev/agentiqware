/**
 * Service for loading components dynamically from the backend API
 */

// Enhanced Component Interface based on our AI metadata structure
export interface ComponentMetadata {
  natural_language_description: string;
  intent_keywords: string[];
  use_cases: string[];
  input_requirements: {
    required_inputs: string[];
    optional_inputs: string[];
    input_types: Record<string, string>;
    input_descriptions?: Record<string, string>;
  };
  output_description: {
    output_type: string;
    output_description: string;
    output_variable: string;
  };
  complexity_level: 'basic' | 'intermediate' | 'advanced';
  dependencies: string[];
  typical_next_steps: string[];
  error_scenarios: string[];
  performance_notes: string;
}

export interface EnhancedComponent {
  id: number;
  uid: string;
  packageName: string;
  actionName: string;
  actionDescription: string;
  actionGroup: string;
  actionLabel: string;
  actionIcon: string;
  storageEntity?: string;
  info?: string;
  code: string;
  parameters: string;
  origin: string;
  global: number;
  canHaveChildren?: boolean;
  status: string;
  childrenIdent?: string;
  blockPropName?: string;
  ai_metadata: ComponentMetadata;
}

// Frontend Component Interface (transformed for FlowEditor)
export interface FlowEditorComponent {
  id: string;
  nameKey: string;
  name: string;
  icon: string;
  categoryKey: string;
  category: string;
  description: string;
  keywords: string[];
  complexity: 'basic' | 'intermediate' | 'advanced';
  config: {
    type: string;
    fields: string[];
    parameters: any;
  };
  ai_metadata: ComponentMetadata;
}

class ComponentsService {
  private baseURL: string;
  private cache: Map<string, FlowEditorComponent[]> = new Map();
  private cacheExpiry: number = 5 * 60 * 1000; // 5 minutes
  private lastFetch: number = 0;

  constructor() {
    // Get backend URL from environment or default to localhost
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8080';
    
    // Clear cache on construction for development
    this.clearCache();
  }

  /**
   * Fetch all components from the backend
   */
  async fetchComponents(): Promise<FlowEditorComponent[]> {
    try {
      console.log('Fetching components from:', `${this.baseURL}/api/components`);
      
      const response = await fetch(`${this.baseURL}/api/components`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const components: EnhancedComponent[] = await response.json();
      console.log('Received components:', components.length);

      // Transform backend components to frontend format
      const transformedComponents = components
        .filter(comp => comp.status === 'S') // Only active components
        .map(comp => this.transformComponent(comp));

      this.lastFetch = Date.now();
      return transformedComponents;

    } catch (error) {
      console.error('Error fetching components:', error);
      
      // Fallback to enhanced components from file
      console.log('Falling back to enhanced components from enhanced_components_full.json');
      return await this.loadEnhancedComponentsFromFile();
    }
  }

  /**
   * Get components with caching
   */
  async getComponents(): Promise<FlowEditorComponent[]> {
    const now = Date.now();
    const cacheKey = 'all_components';
    
    // Check if we have fresh cached data
    if (this.cache.has(cacheKey) && (now - this.lastFetch) < this.cacheExpiry) {
      console.log('Returning cached components');
      return this.cache.get(cacheKey)!;
    }

    // Fetch fresh data
    const components = await this.fetchComponents();
    this.cache.set(cacheKey, components);
    
    return components;
  }

  /**
   * Get components by category
   */
  async getComponentsByCategory(category: string): Promise<FlowEditorComponent[]> {
    const allComponents = await this.getComponents();
    return allComponents.filter(comp => comp.categoryKey === category);
  }

  /**
   * Search components by keywords
   */
  async searchComponents(query: string): Promise<FlowEditorComponent[]> {
    const allComponents = await this.getComponents();
    const searchTerm = query.toLowerCase();
    
    return allComponents.filter(comp => {
      return (
        comp.name.toLowerCase().includes(searchTerm) ||
        comp.description.toLowerCase().includes(searchTerm) ||
        comp.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm)) ||
        comp.ai_metadata.intent_keywords.some(keyword => keyword.toLowerCase().includes(searchTerm))
      );
    });
  }

  /**
   * Get component by ID
   */
  async getComponentById(id: string): Promise<FlowEditorComponent | null> {
    const allComponents = await this.getComponents();
    return allComponents.find(comp => comp.id === id) || null;
  }

  /**
   * Transform backend component to frontend format
   */
  private transformComponent(backendComp: EnhancedComponent): FlowEditorComponent {
    // Use actionGroup directly as the category key (normalized)
    const normalizedCategoryKey = this.normalizeCategoryKey(backendComp.actionGroup);

    // Extract icon from SVG or use emoji fallback
    const icon = this.extractIconFromSvg(backendComp.actionIcon) || this.getCategoryIcon(backendComp.actionGroup);

    // Parse parameters to extract fields
    const fields = this.extractFieldsFromParameters(backendComp.parameters);

    return {
      id: backendComp.actionName,
      nameKey: backendComp.actionName,
      name: backendComp.actionLabel,
      icon: icon,
      categoryKey: normalizedCategoryKey,
      category: backendComp.actionGroup,
      description: backendComp.ai_metadata.natural_language_description,
      keywords: backendComp.ai_metadata.intent_keywords,
      complexity: backendComp.ai_metadata.complexity_level,
      config: {
        type: "wrap",
        fields: fields,
        parameters: backendComp.parameters ? JSON.parse(backendComp.parameters) : {}
      },
      ai_metadata: backendComp.ai_metadata
    };
  }

  /**
   * Normalize actionGroup to valid category key
   */
  private normalizeCategoryKey(actionGroup: string): string {
    return actionGroup
      .toLowerCase()
      .replace(/\s+/g, '_')
      .replace(/[^a-z0-9_]/g, '')
      .replace(/_+/g, '_')
      .replace(/^_|_$/g, '');
  }

  /**
   * Extract simple icon from SVG or return emoji
   */
  private extractIconFromSvg(svgString: string): string {
    // For now, return category-based emoji
    // TODO: Could implement SVG to emoji conversion or use SVG directly
    return '';
  }

  /**
   * Get emoji icon based on category
   */
  private getCategoryIcon(category: string): string {
    const iconMap: Record<string, string> = {
      'Excel': '📊',
      'Excel Application': '📈',
      'Data': '🔄',
      'Dataframe': '📋',
      'Web': '🌐',
      'RPA': '🤖',
      'Application': '💻',
      'Files': '📁',
      'File': '📄',
      'Statements': '🔀',
      'Logic': '🔀',
      'API': '🔗',
      'Database': '🗄️',
      'Email': '📧',
      'AWS': '☁️',
      'UI Interface': '🖥️',
      'UI': '🖥️',
      'System': '⚙️',
      'Strings': '🔤',
      'Convert': '🔄',
      'Variable': '📦',
      'Scripts': '📜',
      'Arrays': '📚',
      'Messages': '💬',
      'JSON': '📋',
      'AI': '🤖'
    };
    return iconMap[category] || '⚙️';
  }

  /**
   * Extract field names from parameters JSON
   */
  private extractFieldsFromParameters(parametersJson: string): string[] {
    if (!parametersJson) return [];
    
    try {
      const params = JSON.parse(parametersJson);
      const fields: string[] = [];
      
      const extractFields = (obj: any) => {
        if (typeof obj === 'object' && obj !== null) {
          if (obj.type === 'text_form_field' && obj.id) {
            fields.push(obj.id);
          } else if (obj.type === 'dropdown_button_form_field' && obj.id) {
            fields.push(obj.id);
          }
          
          // Recursively search in children
          if (obj.children) {
            obj.children.forEach(extractFields);
          }
          if (obj.args && obj.args.children) {
            obj.args.children.forEach(extractFields);
          }
        }
      };
      
      extractFields(params);
      return fields;
      
    } catch (error) {
      console.error('Error parsing parameters JSON:', error);
      return [];
    }
  }

  /**
   * Load all enhanced components from the generated file
   */
  private async loadEnhancedComponentsFromFile(): Promise<FlowEditorComponent[]> {
    try {
      console.log('🔄 Attempting to load components from /enhanced_components_full.json');
      
      // Try to load from the enhanced components file
      const response = await fetch('/enhanced_components_full.json');
      console.log('📡 Fetch response:', response.status, response.statusText);
      
      if (response.ok) {
        const enhancedComponents: EnhancedComponent[] = await response.json();
        console.log('✅ Loaded enhanced components from file:', enhancedComponents.length);
        
        const transformed = enhancedComponents.map(comp => this.transformComponent(comp));
        console.log('🔄 Transformed components:', transformed.length);
        console.log('📊 Component categories:', Array.from(new Set(transformed.map(c => c.categoryKey))));
        
        return transformed;
      } else {
        console.error('❌ Failed to fetch components file:', response.status);
      }
    } catch (error) {
      console.error('💥 Error loading enhanced components from file:', error);
    }
    
    // Fallback to hardcoded enhanced components
    console.log('🔙 Falling back to hardcoded components');
    return this.getEnhancedFallbackComponents();
  }

  /**
   * Enhanced fallback components with AI metadata (sample)
   */
  private getEnhancedFallbackComponents(): FlowEditorComponent[] {
    // These are sample components with full AI metadata for testing
    const enhancedComponents: EnhancedComponent[] = [
      {
        id: 32,
        uid: "d6518cf3-f8f9-4b4a-8415-fb3a9b4d105e",
        packageName: "SmartBots",
        actionName: "excel_read_sheet_to_dataframe",
        actionDescription: "Reads an Excel file and converts it to a pandas DataFrame for data processing",
        actionGroup: "Excel",
        actionLabel: "Read Excel to DataFrame",
        actionIcon: "📊",
        storageEntity: "",
        info: "",
        code: "",
        parameters: JSON.stringify({
          type: "wrap",
          args: {
            runSpacing: 12.0,
            children: [
              {
                type: "text_form_field",
                id: "handler",
                args: {
                  decoration: { labelText: "Handler" },
                  content_sources: ["variable"]
                },
                validators: [{ type: "required" }]
              },
              {
                type: "text_form_field", 
                id: "excel_filename",
                args: {
                  decoration: { labelText: "Excel filename" },
                  content_sources: ["variable", "local_filename", "cloud_filename"]
                },
                validators: [{ type: "required" }]
              },
              {
                type: "text_form_field",
                id: "sheet_name", 
                args: {
                  decoration: { labelText: "Sheet name" },
                  content_sources: ["variable"]
                }
              }
            ]
          }
        }),
        origin: "SmartBots",
        global: 1,
        canHaveChildren: false,
        status: "S",
        ai_metadata: {
          natural_language_description: "Reads data from an Excel spreadsheet file and converts it into a structured data table (DataFrame) that can be processed and analyzed",
          intent_keywords: ["read excel", "load spreadsheet", "import excel data", "excel to dataframe", "open excel file"],
          use_cases: ["Reading financial reports and budgets", "Processing customer data from Excel files", "Importing inventory lists and product catalogs"],
          input_requirements: {
            required_inputs: ["handler", "excel_filename"],
            optional_inputs: ["sheet_name"],
            input_types: {
              handler: "variable_name",
              excel_filename: "file_path", 
              sheet_name: "string"
            }
          },
          output_description: {
            output_type: "dataframe",
            output_description: "A pandas DataFrame containing all data from the specified Excel sheet",
            output_variable: "handler"
          },
          complexity_level: "basic",
          dependencies: ["pandas_library", "openpyxl_library"],
          typical_next_steps: ["data_filter", "data_transform", "data_analysis"],
          error_scenarios: ["File not found", "Invalid Excel format", "Sheet not found"],
          performance_notes: "Memory usage scales with file size"
        }
      },
      {
        id: 33,
        uid: "c641394c-5d94-4400-909f-3fde2042b7c4",
        packageName: "SmartBots", 
        actionName: "data_concat_multi_dataframes",
        actionDescription: "Combines multiple DataFrames into a single DataFrame either vertically or horizontally",
        actionGroup: "Data",
        actionLabel: "Concatenate DataFrames",
        actionIcon: "🔗",
        storageEntity: "",
        info: "",
        code: "",
        parameters: JSON.stringify({
          type: "wrap",
          args: {
            runSpacing: 12.0,
            children: [
              {
                type: "text_form_field",
                id: "handler",
                args: {
                  decoration: { labelText: "Handler" },
                  content_sources: ["variable"]
                },
                validators: [{ type: "required" }]
              },
              {
                type: "text_form_field",
                id: "dataframes",
                args: {
                  decoration: { labelText: "Dataframes" },
                  content_sources: ["variable"]
                },
                validators: [{ type: "required" }]
              },
              {
                type: "dropdown_button_form_field",
                id: "direction",
                args: {
                  decoration: { labelText: "Direction" },
                  items: ["horizontal", "vertical"],
                  value: "horizontal"
                },
                validators: [{ type: "required" }]
              }
            ]
          }
        }),
        origin: "SmartBots",
        global: 1,
        canHaveChildren: false,
        status: "S",
        ai_metadata: {
          natural_language_description: "Combines multiple data tables (DataFrames) into one larger table, either by stacking them vertically (adding rows) or joining them horizontally (adding columns)",
          intent_keywords: ["combine dataframes", "merge multiple tables", "concatenate data", "join dataframes", "stack data tables"],
          use_cases: ["Combining monthly sales reports into yearly data", "Merging data from multiple departments", "Joining customer data from different sources"],
          input_requirements: {
            required_inputs: ["handler", "dataframes", "direction"],
            optional_inputs: [],
            input_types: {
              handler: "variable_name",
              dataframes: "list_of_dataframes",
              direction: "selection"
            }
          },
          output_description: {
            output_type: "dataframe",
            output_description: "A single DataFrame containing all data from the input DataFrames combined according to the specified direction",
            output_variable: "handler"
          },
          complexity_level: "intermediate",
          dependencies: ["pandas_library"],
          typical_next_steps: ["data_filter", "data_transform", "data_analysis"],
          error_scenarios: ["Column mismatch", "Index conflicts", "Memory error"],
          performance_notes: "Performance decreases with larger and more numerous DataFrames"
        }
      },
      {
        id: 19,
        uid: "40702344-3fae-41db-b394-b7baf71def23",
        packageName: "SmartBots",
        actionName: "web_find_element",
        actionDescription: "Locates a specific element on a web page using various search methods",
        actionGroup: "Web",
        actionLabel: "Find Web Element",
        actionIcon: "🌐",
        storageEntity: "",
        info: "",
        code: "",
        parameters: JSON.stringify({
          type: "wrap",
          args: {
            runSpacing: 12.0,
            children: [
              {
                type: "text_form_field",
                id: "handler",
                args: {
                  decoration: { labelText: "Handler" },
                  content_sources: ["variable"]
                },
                validators: [{ type: "required" }]
              },
              {
                type: "text_form_field",
                id: "find_by",
                args: {
                  decoration: { labelText: "Find By" },
                  content_sources: ["variable"]
                },
                validators: [{ type: "required" }]
              },
              {
                type: "text_form_field",
                id: "find_value",
                args: {
                  decoration: { labelText: "Find Value" },
                  content_sources: ["variable"]
                },
                validators: [{ type: "required" }]
              },
              {
                type: "text_form_field",
                id: "result",
                args: {
                  decoration: { labelText: "Result" },
                  content_sources: ["variable"]
                },
                validators: [{ type: "required" }]
              }
            ]
          }
        }),
        origin: "SmartBots",
        global: 1,
        canHaveChildren: false,
        status: "S",
        ai_metadata: {
          natural_language_description: "Searches for and locates a specific element on a web page using various identification methods such as ID, class name, text content, or CSS selectors",
          intent_keywords: ["find element", "locate element", "search element", "find button", "locate button", "get element"],
          use_cases: ["Finding a login button to click", "Locating an input field to type into", "Finding a specific link to navigate"],
          input_requirements: {
            required_inputs: ["handler", "find_by", "find_value", "result"],
            optional_inputs: [],
            input_types: {
              handler: "browser_instance",
              find_by: "locator_method",
              find_value: "string",
              result: "variable_name"
            }
          },
          output_description: {
            output_type: "web_element",
            output_description: "A Selenium WebElement object representing the found element on the page",
            output_variable: "result"
          },
          complexity_level: "intermediate",
          dependencies: ["selenium_library"],
          typical_next_steps: ["web_click_element", "web_type_text", "web_get_text"],
          error_scenarios: ["Element not found", "Multiple elements found", "Page not loaded"],
          performance_notes: "ID and NAME locators are fastest"
        }
      }
    ];

    return enhancedComponents.map(comp => this.transformComponent(comp));
  }

  /**
   * Fallback components if API is not available
   */
  private getFallbackComponents(): FlowEditorComponent[] {
    return [
      {
        id: 'excel_read_sheet_to_dataframe',
        nameKey: 'readExcel',
        name: 'Read Excel',
        icon: '📊',
        categoryKey: 'dataInput',
        category: 'Excel',
        description: 'Reads data from an Excel spreadsheet file and converts it into a structured data table',
        keywords: ['read', 'excel', 'import', 'spreadsheet'],
        complexity: 'basic',
        config: {
          type: "wrap",
          fields: ['handler', 'excel_filename', 'sheet_name'],
          parameters: {}
        },
        ai_metadata: {
          natural_language_description: 'Reads data from an Excel spreadsheet file and converts it into a structured data table',
          intent_keywords: ['read excel', 'load spreadsheet', 'import excel data'],
          use_cases: ['Reading financial reports', 'Processing customer data'],
          input_requirements: {
            required_inputs: ['handler', 'excel_filename'],
            optional_inputs: ['sheet_name'],
            input_types: {
              handler: 'variable_name',
              excel_filename: 'file_path',
              sheet_name: 'string'
            }
          },
          output_description: {
            output_type: 'dataframe',
            output_description: 'A pandas DataFrame with Excel data',
            output_variable: 'handler'
          },
          complexity_level: 'basic',
          dependencies: ['pandas_library'],
          typical_next_steps: ['data_filter', 'data_transform'],
          error_scenarios: ['File not found', 'Invalid Excel format'],
          performance_notes: 'Memory usage scales with file size'
        }
      },
      {
        id: 'data_concat_multi_dataframes',
        nameKey: 'mergeDataFrames',
        name: 'Concatenate DataFrames',
        icon: '🔗',
        categoryKey: 'dataProcessing',
        category: 'Data',
        description: 'Combines multiple data tables into one larger table',
        keywords: ['merge', 'combine', 'concatenate', 'join'],
        complexity: 'intermediate',
        config: {
          type: "wrap",
          fields: ['handler', 'dataframes', 'direction'],
          parameters: {}
        },
        ai_metadata: {
          natural_language_description: 'Combines multiple data tables into one larger table',
          intent_keywords: ['combine dataframes', 'merge tables', 'concatenate data'],
          use_cases: ['Combining monthly reports', 'Merging department data'],
          input_requirements: {
            required_inputs: ['handler', 'dataframes', 'direction'],
            optional_inputs: [],
            input_types: {
              handler: 'variable_name',
              dataframes: 'list_of_dataframes',
              direction: 'selection'
            }
          },
          output_description: {
            output_type: 'dataframe',
            output_description: 'Combined DataFrame',
            output_variable: 'handler'
          },
          complexity_level: 'intermediate',
          dependencies: ['pandas_library'],
          typical_next_steps: ['data_analysis', 'excel_save'],
          error_scenarios: ['Column mismatch', 'Memory error'],
          performance_notes: 'Performance decreases with larger datasets'
        }
      },
      {
        id: 'web_find_element',
        nameKey: 'findElement',
        name: 'Find Web Element',
        icon: '🌐',
        categoryKey: 'automation',
        category: 'Web',
        description: 'Locates a specific element on a web page',
        keywords: ['find', 'element', 'web', 'locate'],
        complexity: 'intermediate',
        config: {
          type: "wrap",
          fields: ['handler', 'find_by', 'find_value', 'result'],
          parameters: {}
        },
        ai_metadata: {
          natural_language_description: 'Locates a specific element on a web page',
          intent_keywords: ['find element', 'locate button', 'search element'],
          use_cases: ['Finding login buttons', 'Locating form fields'],
          input_requirements: {
            required_inputs: ['handler', 'find_by', 'find_value', 'result'],
            optional_inputs: [],
            input_types: {
              handler: 'browser_instance',
              find_by: 'locator_method',
              find_value: 'string',
              result: 'variable_name'
            }
          },
          output_description: {
            output_type: 'web_element',
            output_description: 'Selenium WebElement object',
            output_variable: 'result'
          },
          complexity_level: 'intermediate',
          dependencies: ['selenium_library'],
          typical_next_steps: ['web_click', 'web_type'],
          error_scenarios: ['Element not found', 'Page not loaded'],
          performance_notes: 'ID locators are fastest'
        }
      }
    ];
  }

  /**
   * Clear cache (useful for development)
   */
  clearCache(): void {
    this.cache.clear();
    this.lastFetch = 0;
  }
}

// Export singleton instance
export const componentsService = new ComponentsService();
export default componentsService;