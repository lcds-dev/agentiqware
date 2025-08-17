import React, { useState, useRef, useCallback, useEffect, createContext, useContext, useMemo } from 'react';
import useUndoable from 'use-undoable';
import { Plus, Search, Save, Play, Undo, Redo, ZoomIn, ZoomOut, GitBranch, Code, Copy, Trash2, Edit3, Home, FileText, Activity, Settings, LogOut, Clock, X, Check, AlertCircle, Globe, Scissors, Clipboard, Moon, Sun } from 'lucide-react';

// ============================================
// Sistema de Internacionalización (i18n)
// ============================================

const translations = {
  en: {
    // Navigation
    dashboard: 'Dashboard',
    flows: 'Flows',
    logs: 'Logs',
    settings: 'Settings',
    logout: 'Logout',
    
    // Dashboard
    welcomeTitle: 'Welcome to Agentiqware',
    activeFlows: 'Active Flows',
    totalExecutions: 'Total Executions',
    timeSaved: 'Time Saved',
    errors: 'Errors',
    thisWeek: 'this week',
    successRate: 'success rate',
    thisMonth: 'This month',
    needsAttention: 'Needs attention',
    recentEvents: 'Recent Events',
    completedSuccessfully: 'completed successfully',
    started: 'started',
    failed: 'failed',
    minutesAgo: 'minutes ago',
    hourAgo: 'hour ago',
    connectionTimeout: 'Connection timeout',
    
    // Flows List
    myFlows: 'My Flows',
    newFlow: 'New Flow',
    lastRun: 'Last run',
    totalRuns: 'Total runs',
    active: 'active',
    inactive: 'inactive',
    edit: 'Edit',
    copy: 'Copy',
    delete: 'Delete',
    hoursAgo: 'hours ago',
    dayAgo: 'day ago',
    
    // Flow Editor
    searchComponents: 'Search components...',
    save: 'Save',
    undo: 'Undo',
    redo: 'Redo',
    zoomIn: 'Zoom In',
    zoomOut: 'Zoom Out',
    generateWithAI: 'Generate with AI',
    runFlow: 'Run Flow',
    saveProperties: 'Save Properties',
    
    // AI Prompt Dialog
    generateFlowWithAI: 'Generate Flow with AI',
    describeAutomation: 'Describe your automation flow in natural language...',
    generateFlow: 'Generate Flow',
    cancel: 'Cancel',
    
    // Component Categories
    fileSystem: 'File System',
    dataProcessing: 'Data Processing',
    dataInput: 'Data Input',
    controlFlow: 'Control Flow',
    automation: 'Automation',
    
    // Components
    fileSearch: 'File Search',
    mergeDataFrames: 'Merge DataFrames',
    readExcel: 'Read Excel',
    ifCondition: 'If Condition',
    mouseClick: 'Mouse Click',
    keyboardInput: 'Keyboard Input',
    
    // Component Fields
    folderForSearch: 'Folder for search',
    filesPatternToSearch: 'Files pattern to search',
    includeSubFolders: 'Include sub folders',
    result: 'Result',
    handler: 'Handler',
    dataframes: 'Dataframes',
    direction: 'Direction',
    horizontal: 'Horizontal',
    vertical: 'Vertical',
    excelFileName: 'Excel file name',
    sheet: 'Sheet',
    destinationHandler: 'Destination Handler',
    condition: 'Condition',
    operator: 'Operator',
    value: 'Value',
    text: 'Text',
    delay: 'Delay',
    specialKeys: 'Special keys',
    button: 'Button',
    clicks: 'Clicks',
    
    // Common
    yes: 'Yes',
    no: 'No',
    select: 'Select...',
    enter: 'Enter',
    processing: 'Processing',
    
    // Status Messages
    flowProcessingCompleted: 'Flow processing completed',
    dataMigrationStarted: 'Data migration started',
    reportGenerationFailed: 'Report generation failed',
    
    // Multi-selection
    selectedNodes: 'Selected Nodes',
    deleteAll: 'Delete All',
    duplicateAll: 'Duplicate All',
    selectAll: 'Select All',
    clearSelection: 'Clear Selection',
    copyNodes: 'Copy',
    cutNodes: 'Cut',
    pasteNodes: 'Paste',
    
    // Platform Description
    platformSubtitle: 'RPA & Digital Agents Platform'
  },
  
  es: {
    // Navigation
    dashboard: 'Tablero',
    flows: 'Flujos',
    logs: 'Registros',
    settings: 'Configuración',
    logout: 'Cerrar Sesión',
    
    // Dashboard
    welcomeTitle: 'Bienvenido a Agentiqware',
    activeFlows: 'Flujos Activos',
    totalExecutions: 'Ejecuciones Totales',
    timeSaved: 'Tiempo Ahorrado',
    errors: 'Errores',
    thisWeek: 'esta semana',
    successRate: 'tasa de éxito',
    thisMonth: 'Este mes',
    needsAttention: 'Necesita atención',
    recentEvents: 'Eventos Recientes',
    completedSuccessfully: 'completado exitosamente',
    started: 'iniciado',
    failed: 'falló',
    minutesAgo: 'minutos atrás',
    hourAgo: 'hora atrás',
    connectionTimeout: 'Tiempo de conexión agotado',
    
    // Flows List
    myFlows: 'Mis Flujos',
    newFlow: 'Nuevo Flujo',
    lastRun: 'Última ejecución',
    totalRuns: 'Total de ejecuciones',
    active: 'activo',
    inactive: 'inactivo',
    edit: 'Editar',
    copy: 'Copiar',
    delete: 'Eliminar',
    hoursAgo: 'horas atrás',
    dayAgo: 'día atrás',
    
    // Flow Editor
    searchComponents: 'Buscar componentes...',
    save: 'Guardar',
    undo: 'Deshacer',
    redo: 'Rehacer',
    zoomIn: 'Acercar',
    zoomOut: 'Alejar',
    generateWithAI: 'Generar con IA',
    runFlow: 'Ejecutar Flujo',
    saveProperties: 'Guardar Propiedades',
    
    // AI Prompt Dialog
    generateFlowWithAI: 'Generar Flujo con IA',
    describeAutomation: 'Describe tu flujo de automatización en lenguaje natural...',
    generateFlow: 'Generar Flujo',
    cancel: 'Cancelar',
    
    // Component Categories
    fileSystem: 'Sistema de Archivos',
    dataProcessing: 'Procesamiento de Datos',
    dataInput: 'Entrada de Datos',
    controlFlow: 'Control de Flujo',
    automation: 'Automatización',
    
    // Components
    fileSearch: 'Búsqueda de Archivos',
    mergeDataFrames: 'Combinar DataFrames',
    readExcel: 'Leer Excel',
    ifCondition: 'Condición Si',
    mouseClick: 'Click del Ratón',
    keyboardInput: 'Entrada de Teclado',
    
    // Component Fields
    folderForSearch: 'Carpeta para buscar',
    filesPatternToSearch: 'Patrón de archivos a buscar',
    includeSubFolders: 'Incluir subcarpetas',
    result: 'Resultado',
    handler: 'Manejador',
    dataframes: 'Dataframes',
    direction: 'Dirección',
    horizontal: 'Horizontal',
    vertical: 'Vertical',
    excelFileName: 'Nombre del archivo Excel',
    sheet: 'Hoja',
    destinationHandler: 'Manejador de Destino',
    condition: 'Condición',
    operator: 'Operador',
    value: 'Valor',
    text: 'Texto',
    delay: 'Retraso',
    specialKeys: 'Teclas especiales',
    button: 'Botón',
    clicks: 'Clicks',
    
    // Common
    yes: 'Sí',
    no: 'No',
    select: 'Seleccionar...',
    enter: 'Ingresar',
    processing: 'Procesando',
    
    // Status Messages
    flowProcessingCompleted: 'Procesamiento de flujo completado',
    dataMigrationStarted: 'Migración de datos iniciada',
    reportGenerationFailed: 'Generación de reporte falló',
    
    // Multi-selection
    selectedNodes: 'Nodos Seleccionados',
    deleteAll: 'Eliminar Todos',
    duplicateAll: 'Duplicar Todos',
    selectAll: 'Seleccionar Todo',
    clearSelection: 'Limpiar Selección',
    copyNodes: 'Copiar',
    cutNodes: 'Cortar',
    pasteNodes: 'Pegar',
    
    // Platform Description
    platformSubtitle: 'Plataforma de RPA y Agentes Digitales'
  }
};

// Contexto de idioma
const LanguageContext = createContext<any>(null);

// ============================================
// Sistema de Temas (Theme System)
// ============================================

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

// Hook personalizado para usar tema
const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Proveedor de tema
const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Obtener tema guardado o usar preferencia del sistema
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) return savedTheme;
    
    // Detectar preferencia del sistema
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    console.log('Toggling theme from', theme, 'to', newTheme);
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  const isDark = theme === 'dark';

  // Aplicar clase al document element para Tailwind
  useEffect(() => {
    console.log('Theme effect running, isDark:', isDark, 'theme:', theme);
    if (isDark) {
      document.documentElement.classList.add('dark');
      console.log('Added dark class to document');
    } else {
      document.documentElement.classList.remove('dark');
      console.log('Removed dark class from document');
    }
  }, [isDark, theme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, isDark }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook personalizado para usar traducciones
const useTranslation = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};

// Proveedor de idioma
const LanguageProvider = ({ children }: { children: React.ReactNode }) => {
  const [language, setLanguage] = useState(() => {
    // Obtener idioma guardado o detectar del navegador
    const savedLang = localStorage.getItem('language');
    if (savedLang) return savedLang;
    
    const browserLang = navigator.language.split('-')[0];
    return browserLang === 'es' ? 'es' : 'en';
  });

  const t = (key: string) => {
    return (translations as any)[language][key] || (translations as any)['en'][key] || key;
  };

  const changeLanguage = (newLang: string) => {
    setLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Selector de tema
const ThemeSelector = () => {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={() => {
        console.log('Theme selector clicked, current theme:', theme);
        toggleTheme();
      }}
      className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-yellow-500" />
      ) : (
        <Moon className="w-4 h-4 text-gray-600 dark:text-gray-300" />
      )}
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {isDark ? 'Light' : 'Dark'}
      </span>
    </button>
  );
};

// Selector de idioma
const LanguageSelector = () => {
  const { language, changeLanguage } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      >
        <Globe className="w-4 h-4 text-gray-600 dark:text-gray-300" />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{language.toUpperCase()}</span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-32 bg-white dark:bg-gray-800 rounded-lg shadow-lg border dark:border-gray-700 z-50">
          <button
            onClick={() => {
              changeLanguage('en');
              setIsOpen(false);
            }}
            className={`w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition ${
              language === 'en' ? 'bg-blue-50 text-blue-600 dark:bg-blue-900 dark:text-blue-300' : 'text-gray-700 dark:text-gray-300'
            }`}
          >
            English
          </button>
          <button
            onClick={() => {
              changeLanguage('es');
              setIsOpen(false);
            }}
            className={`w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition ${
              language === 'es' ? 'bg-blue-50 text-blue-600 dark:bg-blue-900 dark:text-blue-300' : 'text-gray-700 dark:text-gray-300'
            }`}
          >
            Español
          </button>
        </div>
      )}
    </div>
  );
};

// Componente principal del editor con i18n
const FlowEditor = ({ 
  globalPropertyPanelState, 
  setGlobalPropertyPanelState 
}: {
  globalPropertyPanelState: any;
  setGlobalPropertyPanelState: any;
}) => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const canvasRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes, { undo: undoNodes, redo: redoNodes, canUndo: canUndoNodes, canRedo: canRedoNodes }] = useUndoable<any[]>([]);
  const [connections, setConnections, { undo: undoConnections, redo: redoConnections, canUndo: canUndoConnections, canRedo: canRedoConnections }] = useUndoable<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set());
  const [isSelecting, setIsSelecting] = useState(false);
  const [selectionBox, setSelectionBox] = useState<{x: number, y: number, width: number, height: number} | null>(null);
  const [selectionStart, setSelectionStart] = useState({ x: 0, y: 0 });
  const [clipboard, setClipboard] = useState<{nodes: any[], operation: 'copy' | 'cut'} | null>(null);
  const [cutNodes, setCutNodes] = useState<Set<string>>(new Set());
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [draggedNode, setDraggedNode] = useState<any>(null);
  const [draggedNodes, setDraggedNodes] = useState<any[]>([]);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isDraggingCanvas, setIsDraggingCanvas] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });
  const [connectingFrom, setConnectingFrom] = useState<any>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  // Removed unused tempConnection state
  const [showProperties, setShowProperties] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAIPrompt, setShowAIPrompt] = useState(false);
  const [aiPrompt, setAIPrompt] = useState('');
  const [connectionOrientation, setConnectionOrientation] = useState<'horizontal' | 'vertical'>('horizontal');
  const [showInsertMenu, setShowInsertMenu] = useState<{connectionId: string, x: number, y: number, canvasX?: number, canvasY?: number} | null>(null);

  // Componentes disponibles con traducciones
  const availableComponents = [
    {
      id: 'file_search',
      nameKey: 'fileSearch',
      icon: '📁',
      categoryKey: 'fileSystem',
      config: {
        type: "wrap",
        fields: ['folder', 'pattern', 'include_subfolders', 'result']
      }
    },
    {
      id: 'dataframe_merge',
      nameKey: 'mergeDataFrames',
      icon: '🔗',
      categoryKey: 'dataProcessing',
      config: {
        type: "wrap",
        fields: ['handler', 'dataframes', 'direction']
      }
    },
    {
      id: 'excel_reader',
      nameKey: 'readExcel',
      icon: '📊',
      categoryKey: 'dataInput',
      config: {
        type: "wrap",
        fields: ['excel_file_name', 'sheet_name', 'destination']
      }
    },
    {
      id: 'condition',
      nameKey: 'ifCondition',
      icon: '🔀',
      categoryKey: 'controlFlow',
      config: {
        type: "condition",
        fields: ['condition', 'operator', 'value']
      }
    },
    {
      id: 'mouse_click',
      nameKey: 'mouseClick',
      icon: '🖱️',
      categoryKey: 'automation',
      config: {
        type: "automation",
        fields: ['x', 'y', 'button', 'clicks']
      }
    },
    {
      id: 'keyboard_input',
      nameKey: 'keyboardInput',
      icon: '⌨️',
      categoryKey: 'automation',
      config: {
        type: "automation",
        fields: ['text', 'delay', 'special_keys']
      }
    }
  ];

  // Obtener categorías únicas
  const categories = Array.from(new Set(availableComponents.map(c => c.categoryKey)));

  // Agregar nodo al canvas
  const addNode = (component: any, position: any) => {
    const newNode = {
      id: `node_${Date.now()}`,
      type: component.id,
      name: t(component.nameKey),
      icon: component.icon,
      position: position || { x: 300 + Math.random() * 200, y: 150 + Math.random() * 200 },
      config: { ...component.config },
      data: {}
    };
    setNodes([...nodes, newNode]);
    return newNode;
  };

  // Funciones para manejo de selección múltiple
  const selectNode = (nodeId: string, isCtrlPressed: boolean = false) => {
    if (isCtrlPressed) {
      const newSelected = new Set(selectedNodes);
      if (newSelected.has(nodeId)) {
        newSelected.delete(nodeId);
      } else {
        newSelected.add(nodeId);
      }
      setSelectedNodes(newSelected);
    } else {
      setSelectedNodes(new Set([nodeId]));
    }
  };

  const clearSelection = useCallback(() => {
    setSelectedNodes(new Set());
    setSelectedNode(null);
    setSelectedNodeId(null);
  }, []);

  // Sync selectedNode with current node data
  useEffect(() => {
    if (selectedNodeId) {
      const currentNode = nodes.find(n => n.id === selectedNodeId);
      if (currentNode) {
        setSelectedNode(currentNode);
      }
    }
  }, [nodes, selectedNodeId]);

  const selectNodesInBox = (box: {x: number, y: number, width: number, height: number}) => {
    const selected = new Set<string>();
    nodes.forEach(node => {
      const nodeX = node.position.x;
      const nodeY = node.position.y;
      const nodeWidth = 120; // minWidth del nodo
      const nodeHeight = 80; // altura estimada del nodo
      
      // Verificar si el nodo está dentro del área de selección
      if (nodeX + nodeWidth > box.x && 
          nodeX < box.x + box.width &&
          nodeY + nodeHeight > box.y &&
          nodeY < box.y + box.height) {
        selected.add(node.id);
      }
    });
    setSelectedNodes(selected);
  };



  // Funciones de clipboard
  const copySelectedNodes = useCallback(() => {
    if (selectedNodes.size > 0) {
      const nodesToCopy = nodes.filter(node => selectedNodes.has(node.id));
      setClipboard({ nodes: nodesToCopy, operation: 'copy' });
      // Limpiar nodos cortados si había alguno
      setCutNodes(new Set());
    }
  }, [selectedNodes, nodes]);

  const cutSelectedNodes = useCallback(() => {
    if (selectedNodes.size > 0) {
      const nodesToCut = nodes.filter(node => selectedNodes.has(node.id));
      setClipboard({ nodes: nodesToCut, operation: 'cut' });
      // Marcar nodos como cortados para el estilo visual
      setCutNodes(new Set(selectedNodes));
    }
  }, [selectedNodes, nodes]);

  const pasteNodes = useCallback(() => {
    if (clipboard && clipboard.nodes.length > 0) {
      // Generar nuevos IDs para los nodos pegados
      const pastedNodes = clipboard.nodes.map(node => ({
        ...node,
        id: `node_${Date.now()}_${Math.random()}`,
        position: {
          x: node.position.x + 50, // Offset para que no se superpongan
          y: node.position.y + 50
        }
      }));

      // Si era cortar, eliminar los nodos originales
      if (clipboard.operation === 'cut') {
        const cutNodeIds = new Set(clipboard.nodes.map(n => n.id));
        setNodes(prev => prev.filter(node => !cutNodeIds.has(node.id)));
        
        // Eliminar conexiones relacionadas con los nodos cortados
        setConnections(prev => prev.filter(conn => 
          !cutNodeIds.has(conn.from) && !cutNodeIds.has(conn.to)
        ));
        
        // Limpiar estado de cortado
        setCutNodes(new Set());
        setClipboard(null);
      }

      // Agregar los nodos pegados
      setNodes(prev => [...prev, ...pastedNodes]);
      
      // Seleccionar los nodos pegados
      const pastedNodeIds = new Set(pastedNodes.map(node => node.id));
      setSelectedNodes(pastedNodeIds);
    }
  }, [clipboard]);

  // Funciones unificadas de undo/redo
  const handleUndo = useCallback(() => {
    undoNodes();
    undoConnections();
  }, [undoNodes, undoConnections]);

  const handleRedo = useCallback(() => {
    redoNodes();
    redoConnections();
  }, [redoNodes, redoConnections]);

  // Verificar si se puede hacer undo/redo
  const canUndo = canUndoNodes || canUndoConnections;
  const canRedo = canRedoNodes || canRedoConnections;

  // Manejar drag & drop desde sidebar
  const handleDragStart = (e: any, component: any) => {
    e.dataTransfer.setData('component', JSON.stringify(component));
  };

  // Manejar drag de nodos en el canvas
  const handleNodeMouseDown = (e: any, node: any) => {
    if ((e.target as any).classList?.contains('connection-point')) return;
    
    e.preventDefault();
    
    const isCtrlPressed = e.ctrlKey || e.metaKey;
    
    // Manejo de selección
    if (isCtrlPressed) {
      selectNode(node.id, true);
    } else if (!selectedNodes.has(node.id)) {
      selectNode(node.id, false);
    }
    
    // Preparar arrastre
    setDraggedNode(node);
    setIsDragging(true);
    
    // Si hay múltiples nodos seleccionados y este nodo está seleccionado, arrastrar todos
    if (selectedNodes.has(node.id) && selectedNodes.size > 1) {
      const nodesToDrag = nodes.filter(n => selectedNodes.has(n.id));
      setDraggedNodes(nodesToDrag);
    } else {
      setDraggedNodes([node]);
    }
    
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    setDragStart({
      x: e.clientX - node.position.x * scale - offset.x,
      y: e.clientY - node.position.y * scale - offset.y
    });
  };

  // Manejar movimiento del mouse
  const handleMouseMove = useCallback((e: MouseEvent) => {
    // Skip if interacting with PropertyPanel
    const target = e.target as HTMLElement;
    if (target.closest('[data-property-panel]')) {
      return;
    }
    
    // Obtener rect una vez para usar en todas las operaciones
    const rect = canvasRef.current?.getBoundingClientRect();
    
    // Solo actualizar posición del mouse si se está conectando
    if (connectingFrom && rect) {
      setMousePosition({
        x: (e.clientX - rect.left - offset.x) / scale,
        y: (e.clientY - rect.top - offset.y) / scale
      });
    }
    
    if (isDragging && draggedNode) {
      if (!rect) return;
      
      const newX = (e.clientX - dragStart.x - offset.x) / scale;
      const newY = (e.clientY - dragStart.y - offset.y) / scale;
      
      // Calcular el desplazamiento del nodo principal
      const deltaX = newX - draggedNode.position.x;
      const deltaY = newY - draggedNode.position.y;
      
      // Mover todos los nodos seleccionados
      setNodes(prev => prev.map(node => {
        if (draggedNodes.some(draggedNode => draggedNode.id === node.id)) {
          return { 
            ...node, 
            position: { 
              x: node.position.x + deltaX, 
              y: node.position.y + deltaY 
            } 
          };
        }
        return node;
      }));
      
      // Actualizar la posición del nodo arrastrado para la próxima iteración
      setDraggedNode((prev: any) => ({
        ...prev,
        position: { x: newX, y: newY }
      }));
    } else if (isSelecting) {
      // Manejar selección por arrastre
      if (!rect) return;
      
      const currentX = (e.clientX - rect.left - offset.x) / scale;
      const currentY = (e.clientY - rect.top - offset.y) / scale;
      
      
      const box = {
        x: Math.min(selectionStart.x, currentX),
        y: Math.min(selectionStart.y, currentY),
        width: Math.abs(currentX - selectionStart.x),
        height: Math.abs(currentY - selectionStart.y)
      };
      
      setSelectionBox(box);
      selectNodesInBox(box);
    } else if (isDraggingCanvas) {
      const deltaX = e.clientX - lastMousePos.x;
      const deltaY = e.clientY - lastMousePos.y;
      
      console.log('Moving canvas:', { deltaX, deltaY, isDraggingCanvas });
      
      setOffset(prev => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }));
      
      setLastMousePos({ x: e.clientX, y: e.clientY });
    }
  }, [isDragging, draggedNode, dragStart, offset, scale, isDraggingCanvas, lastMousePos, isSelecting, selectionStart, draggedNodes, selectNodesInBox, connectingFrom]);

  // Manejar fin del drag
  const handleMouseUp = useCallback((e: MouseEvent) => {
    // No interferir si el clic es en el panel de selección múltiple
    const target = e.target as HTMLElement;
    if (target?.closest('.multi-selection-panel')) {
      console.log('MouseUp ignored - click in multi-selection panel');
      return;
    }
    
    setIsDragging(false);
    setDraggedNode(null);
    setDraggedNodes([]);
    setIsDraggingCanvas(false);
    setIsSelecting(false);
    setSelectionBox(null);
  }, []);

  // Manejar drag del canvas
  const handleCanvasMouseDown = (e: any) => {
    // Verificar si el clic es en elementos que NO deberían ser interceptados
    const isNodeClick = e.target.closest('[data-node-id]');
    const isConnectionPoint = e.target.classList?.contains('connection-point');
    const isMultiSelectionPanel = e.target.closest('.multi-selection-panel');
    const isPropertyPanel = e.target.closest('[data-property-panel]');
    const isFixedElement = e.target.closest('[style*="position: fixed"]') || 
                          e.target.style?.position === 'fixed' ||
                          getComputedStyle(e.target).position === 'fixed';
    
    // Solo proceder si el clic es en el canvas (fondo) y no en otros elementos
    if (!isNodeClick && !isConnectionPoint && !isMultiSelectionPanel && !isPropertyPanel && !isFixedElement) {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      
      const isCtrlPressed = e.ctrlKey || e.metaKey;
      const isShiftPressed = e.shiftKey;
      
      if (isShiftPressed) {
        // Prevenir comportamiento por defecto y propagación
        e.preventDefault();
        e.stopPropagation();
        
        // Iniciar arrastre del canvas con Shift
        setIsDraggingCanvas(true);
        setLastMousePos({ x: e.clientX, y: e.clientY });
        
        // Limpiar otros estados
        setIsSelecting(false);
        setIsDragging(false);
        
        console.log('Canvas dragging started with Shift');
      } else if (!isCtrlPressed) {
        // Solo iniciar selección por arrastre si no se presiona Ctrl ni Shift
        const startX = (e.clientX - rect.left - offset.x) / scale;
        const startY = (e.clientY - rect.top - offset.y) / scale;
        
        setIsSelecting(true);
        setSelectionStart({ x: startX, y: startY });
        setIsDraggingCanvas(false);
      }
    }
  };

  const handleDrop = (e: any) => {
    e.preventDefault();
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const component = JSON.parse(e.dataTransfer.getData('component'));
    const position = {
      x: (e.clientX - rect.left - offset.x) / scale,
      y: (e.clientY - rect.top - offset.y) / scale
    };
    addNode(component, position);
  };

  const handleDragOver = (e: any) => {
    e.preventDefault();
  };

  // Manejo del zoom
  const handleZoom = useCallback((delta: number, mousePos?: { x: number, y: number }) => {
    const newScale = Math.max(0.3, Math.min(2, scale + delta));
    
    if (mousePos && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const mouseX = mousePos.x - rect.left;
      const mouseY = mousePos.y - rect.top;
      
      // Ajustar offset para que el zoom se centre en la posición del mouse
      const deltaScale = newScale - scale;
      setOffset(prev => ({
        x: prev.x - (mouseX * deltaScale) / newScale,
        y: prev.y - (mouseY * deltaScale) / newScale
      }));
    }
    
    setScale(newScale);
  }, [scale]);

  // Manejar wheel para zoom
  const handleWheel = useCallback((e: WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      const delta = -e.deltaY * 0.001;
      handleZoom(delta, { x: e.clientX, y: e.clientY });
    }
  }, [handleZoom]);

  // Conectar nodos
  const startConnection = (nodeId: string, output = 'default') => {
    setConnectingFrom({ nodeId, output });
  };

  const completeConnection = (nodeId: string, input = 'default') => {
    if (connectingFrom && connectingFrom.nodeId !== nodeId) {
      // Verificar que no exista ya una conexión
      const existingConnection = connections.find(conn => 
        conn.from === connectingFrom.nodeId && 
        conn.to === nodeId &&
        conn.fromOutput === connectingFrom.output &&
        conn.toInput === input
      );
      
      if (!existingConnection) {
        const newConnection = {
          id: `conn_${Date.now()}`,
          from: connectingFrom.nodeId,
          fromOutput: connectingFrom.output,
          to: nodeId,
          toInput: input
        };
        setConnections([...connections, newConnection]);
      }
      setConnectingFrom(null);
    }
  };

  // Cancelar conexión
  const cancelConnection = () => {
    setConnectingFrom(null);
  };

  // Manejar clic en canvas (para deseleccionar y cancelar conexiones)
  const handleCanvasClick = (e: any) => {
    // Verificar si el clic NO fue en elementos que deberían manejar sus propios eventos
    const isNodeClick = e.target.closest('[data-node-id]');
    const isConnectionPoint = e.target.classList?.contains('connection-point');
    const isMultiSelectionPanel = e.target.closest('.multi-selection-panel');
    const isPropertyPanel = e.target.closest('[data-property-panel]');
    const isFixedElement = e.target.closest('[style*="position: fixed"]') || 
                          e.target.style?.position === 'fixed' ||
                          getComputedStyle(e.target).position === 'fixed';
    
    if (!isNodeClick && !isConnectionPoint && !isMultiSelectionPanel && !isPropertyPanel && !isFixedElement) {
      // Cerrar menú de inserción si está abierto
      setShowInsertMenu(null);
      
      // Solo deseleccionar en un clic simple (no después de arrastrar)
      setTimeout(() => {
        if (selectedNodes.size > 0) {
          clearSelection();
        }
        cancelConnection();
      }, 0);
    }
  };

  // Eliminar conexión
  const removeConnection = (connectionId: string) => {
    setConnections(prev => prev.filter(conn => conn.id !== connectionId));
  };

  // Insertar nodo en conexión
  const insertNodeInConnection = (connectionId: string, component: any, insertPosition: {x: number, y: number}) => {
    console.log('insertNodeInConnection called:', { connectionId, component: component.nameKey, insertPosition });
    const connection = connections.find(conn => conn.id === connectionId);
    if (!connection) {
      console.log('Connection not found:', connectionId);
      return;
    }

    console.log('Found connection:', connection);
    // Crear el nuevo nodo
    const newNode = addNode(component, insertPosition);
    console.log('Created new node:', newNode);

    // Eliminar la conexión original
    setConnections(prev => prev.filter(conn => conn.id !== connectionId));

    // Crear dos nuevas conexiones
    const conn1 = {
      id: `conn_${Date.now()}_1`,
      from: connection.from,
      fromOutput: connection.fromOutput,
      to: newNode.id,
      toInput: 'default'
    };

    const conn2 = {
      id: `conn_${Date.now()}_2`,
      from: newNode.id,
      fromOutput: 'default',
      to: connection.to,
      toInput: connection.toInput
    };

    setConnections(prev => [...prev, conn1, conn2]);
    setShowInsertMenu(null);
  };

  // Manejar teclas
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Skip if typing in PropertyPanel
    const target = e.target as HTMLElement;
    if (target.closest('[data-property-panel]') || target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
      return;
    }
    
    if (e.key === 'Delete' || e.key === 'Backspace') {
      if (selectedNodes.size > 0) {
        // Eliminar nodos seleccionados
        setNodes(prev => prev.filter(node => !selectedNodes.has(node.id)));
        
        // Eliminar conexiones relacionadas
        setConnections(prev => prev.filter(conn => 
          !selectedNodes.has(conn.from) && !selectedNodes.has(conn.to)
        ));
        
        clearSelection();
      }
    } else if (e.key === 'Escape') {
      clearSelection();
      setConnectingFrom(null);
    } else if (e.ctrlKey || e.metaKey) {
      if (e.key === 'a') {
        e.preventDefault();
        // Seleccionar todos los nodos
        const allNodeIds = new Set(nodes.map(node => node.id));
        setSelectedNodes(allNodeIds);
      } else if (e.key === 'c') {
        e.preventDefault();
        copySelectedNodes();
      } else if (e.key === 'x') {
        e.preventDefault();
        cutSelectedNodes();
      } else if (e.key === 'v') {
        e.preventDefault();
        pasteNodes();
      } else if (e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        handleUndo();
      } else if ((e.key === 'z' && e.shiftKey) || e.key === 'y') {
        e.preventDefault();
        handleRedo();
      }
    }
  }, [selectedNodes, nodes, clearSelection, setConnectingFrom, copySelectedNodes, cutSelectedNodes, pasteNodes, handleUndo, handleRedo]);

  // Efectos para event listeners
  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('keydown', handleKeyDown);
    
    const currentCanvas = canvasRef.current;
    if (currentCanvas) {
      currentCanvas.addEventListener('wheel', handleWheel, { passive: false });
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.removeEventListener('keydown', handleKeyDown);
      
      if (currentCanvas) {
        currentCanvas.removeEventListener('wheel', handleWheel);
      }
    };
  }, [handleMouseMove, handleMouseUp, handleWheel, handleKeyDown]);

  // Renderizar conexiones
  const renderedConnections = useMemo(() => {
    const allConnections = [...connections];
    
    // Añadir conexión temporal si se está conectando
    if (connectingFrom) {
      const fromNode = nodes.find(n => n.id === connectingFrom.nodeId);
      if (fromNode) {
        const tempConn = {
          id: 'temp',
          from: connectingFrom.nodeId,
          fromOutput: connectingFrom.output,
          to: 'mouse',
          toInput: 'default',
          isTemp: true
        };
        allConnections.push(tempConn);
      }
    }
    
    return allConnections.map(conn => {
      const fromNode = nodes.find(n => n.id === conn.from);
      if (!fromNode) return null;
      
      let x1, y1, x2, y2;
      
      // Calcular punto de salida basado en orientación
      if (connectionOrientation === 'horizontal') {
        // Horizontal: salida por la derecha
        if (conn.fromOutput === 'true') {
          x1 = fromNode.position.x + 40;
          y1 = fromNode.position.y + 80;
        } else if (conn.fromOutput === 'false') {
          x1 = fromNode.position.x + 80;
          y1 = fromNode.position.y + 80;
        } else {
          x1 = fromNode.position.x + 120;
          y1 = fromNode.position.y + 40;
        }
      } else {
        // Vertical: salida por abajo
        if (conn.fromOutput === 'true') {
          x1 = fromNode.position.x + 40;
          y1 = fromNode.position.y + 80;
        } else if (conn.fromOutput === 'false') {
          x1 = fromNode.position.x + 80;
          y1 = fromNode.position.y + 80;
        } else {
          x1 = fromNode.position.x + 60;
          y1 = fromNode.position.y + 80;
        }
      }
      
      // Calcular punto de llegada basado en orientación
      if (conn.to === 'mouse') {
        x2 = mousePosition.x;
        y2 = mousePosition.y;
      } else {
        const toNode = nodes.find(n => n.id === conn.to);
        if (!toNode) return null;
        if (connectionOrientation === 'horizontal') {
          // Horizontal: entrada por la izquierda
          x2 = toNode.position.x;
          y2 = toNode.position.y + 40;
        } else {
          // Vertical: entrada por arriba
          x2 = toNode.position.x + 60;
          y2 = toNode.position.y;
        }
      }

      let cp1x, cp1y, cp2x, cp2y;
      
      if (connectionOrientation === 'horizontal') {
        const dx = x2 - x1;
        cp1x = x1 + dx * 0.5;
        cp1y = y1;
        cp2x = x2 - dx * 0.5;
        cp2y = y2;
      } else {
        // Vertical orientation
        const dy = y2 - y1;
        cp1x = x1;
        cp1y = y1 + dy * 0.5;
        cp2x = x2;
        cp2y = y2 - dy * 0.5;
      }

      return (
        <g key={conn.id}>
          {/* Línea de conexión visible */}
          <path
            d={`M ${x1} ${y1} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`}
            stroke={conn.isTemp ? '#94a3b8' : conn.fromOutput === 'true' ? '#22c55e' : conn.fromOutput === 'false' ? '#ef4444' : '#6366f1'}
            strokeWidth={conn.isTemp ? '1' : '2'}
            strokeDasharray={conn.isTemp ? '5,5' : 'none'}
            fill="none"
            className={`transition-all ${
              conn.isTemp ? 'opacity-60' : 'hover:stroke-opacity-80 cursor-pointer'
            }`}
            onClick={(e) => {
              e.stopPropagation();
              if (conn.isTemp) return;
              
              // Si es doble clic, mostrar menú de inserción
              if (e.detail === 2) {
                const rect = canvasRef.current?.getBoundingClientRect();
                if (rect) {
                  const x = (e.clientX - rect.left - offset.x) / scale;
                  const y = (e.clientY - rect.top - offset.y) / scale;
                  setShowInsertMenu({ connectionId: conn.id, x, y });
                }
              } else {
                // Un solo clic elimina la conexión
                removeConnection(conn.id);
              }
            }}
          />
        </g>
      );
    });
  }, [connections, connectingFrom, nodes, connectionOrientation, mousePosition]);

  // Mapeo de campos a claves de traducción
  const fieldTranslationMap = {
    'folder': 'folderForSearch',
    'pattern': 'filesPatternToSearch',
    'include_subfolders': 'includeSubFolders',
    'result': 'result',
    'handler': 'handler',
    'dataframes': 'dataframes',
    'direction': 'direction',
    'excel_file_name': 'excelFileName',
    'sheet_name': 'sheet',
    'destination': 'destinationHandler',
    'condition': 'condition',
    'operator': 'operator',
    'value': 'value',
    'text': 'text',
    'delay': 'delay',
    'special_keys': 'specialKeys',
    'x': 'X',
    'y': 'Y',
    'button': 'button',
    'clicks': 'clicks'
  };

  // Panel de selección múltiple
  const MultiSelectionPanel = () => {
    if (selectedNodes.size <= 1) return null;

    return (
      <div 
        className="multi-selection-panel fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-600 p-4 z-50 min-w-80" 
        style={{ 
          pointerEvents: 'auto', 
          boxShadow: '0 40px 80px -20px rgba(0, 0, 0, 0.4), 0 20px 25px -8px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(0, 0, 0, 0.05)',
          position: 'fixed',
          zIndex: 9999
        }}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          console.log('MultiSelectionPanel clicked');
        }}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="font-medium text-gray-900 dark:text-gray-100">{t('selectedNodes')}: {selectedNodes.size}</span>
          </div>
          <button
            onClick={clearSelection}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            title={t('clearSelection')}
          >
            <X className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </button>
        </div>
        
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              console.log('Copy button clicked! selectedNodes.size:', selectedNodes.size);
              if (selectedNodes.size > 0) {
                const nodesToCopy = nodes.filter(node => selectedNodes.has(node.id));
                console.log('Copying nodes:', nodesToCopy);
                setClipboard({ nodes: nodesToCopy, operation: 'copy' });
                setCutNodes(new Set());
              } else {
                console.log('No nodes selected to copy');
              }
            }}
            className="flex items-center gap-2 px-3 py-2 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/50 transition text-sm"
            title={t('copyNodes')}
          >
            <Copy className="w-4 h-4" />
            {t('copyNodes')}
          </button>
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              console.log('Cut button clicked! selectedNodes.size:', selectedNodes.size);
              if (selectedNodes.size > 0) {
                const nodesToCut = nodes.filter(node => selectedNodes.has(node.id));
                console.log('Cutting nodes:', nodesToCut);
                setClipboard({ nodes: nodesToCut, operation: 'cut' });
                setCutNodes(new Set(selectedNodes));
              } else {
                console.log('No nodes selected to cut');
              }
            }}
            className="flex items-center gap-2 px-3 py-2 bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/50 transition text-sm"
            title={t('cutNodes')}
          >
            <Scissors className="w-4 h-4" />
            {t('cutNodes')}
          </button>
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              console.log('Paste button clicked! clipboard:', clipboard);
              if (clipboard && clipboard.nodes.length > 0) {
                console.log('Pasting nodes:', clipboard.nodes);
                // Generar nuevos IDs para los nodos pegados
                const pastedNodes = clipboard.nodes.map(node => ({
                  ...node,
                  id: `node_${Date.now()}_${Math.random()}`,
                  position: {
                    x: node.position.x + 50,
                    y: node.position.y + 50
                  }
                }));

                // Si era cortar, eliminar los nodos originales
                if (clipboard.operation === 'cut') {
                  const cutNodeIds = new Set(clipboard.nodes.map(n => n.id));
                  setNodes(prev => prev.filter(node => !cutNodeIds.has(node.id)));
                  
                  setConnections(prev => prev.filter(conn => 
                    !cutNodeIds.has(conn.from) && !cutNodeIds.has(conn.to)
                  ));
                  
                  setCutNodes(new Set());
                  setClipboard(null);
                }

                // Agregar los nodos pegados
                setNodes(prev => [...prev, ...pastedNodes]);
                
                // Seleccionar los nodos pegados
                const pastedNodeIds = new Set(pastedNodes.map(node => node.id));
                setSelectedNodes(pastedNodeIds);
              } else {
                console.log('No clipboard content to paste');
              }
            }}
            disabled={!clipboard || clipboard.nodes.length === 0}
            className="flex items-center gap-2 px-3 py-2 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            title={t('pasteNodes')}
          >
            <Clipboard className="w-4 h-4" />
            {t('pasteNodes')}
          </button>
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              console.log('Duplicate button clicked! selectedNodes.size:', selectedNodes.size);
              if (selectedNodes.size > 0) {
                const nodesToDuplicate = nodes.filter(node => selectedNodes.has(node.id));
                console.log('Duplicating nodes:', nodesToDuplicate);
                const newNodes = nodesToDuplicate.map(node => ({
                  ...node,
                  id: `node_${Date.now()}_${Math.random()}`,
                  position: {
                    x: node.position.x + 150,
                    y: node.position.y + 50
                  }
                }));
                
                setNodes(prev => [...prev, ...newNodes]);
                
                // Seleccionar los nuevos nodos duplicados
                const newNodeIds = new Set(newNodes.map(node => node.id));
                setSelectedNodes(newNodeIds);
              } else {
                console.log('No nodes selected to duplicate');
              }
            }}
            className="flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition text-sm"
            title={t('duplicateAll')}
          >
            <Copy className="w-4 h-4" />
            {t('duplicateAll')}
          </button>
          <button
            onMouseEnter={() => console.log('Delete button hovered')}
            onMouseDown={(e) => {
              console.log('Delete button mouse down');
              e.preventDefault();
              e.stopPropagation();
            }}
            onMouseUp={(e) => {
              console.log('Delete button mouse up - executing delete');
              e.preventDefault();
              e.stopPropagation();
              
              console.log('Delete action triggered!', {
                selectedNodesSize: selectedNodes.size,
                selectedNodesArray: Array.from(selectedNodes),
                nodesLength: nodes.length
              });
              
              if (selectedNodes.size > 0) {
                const nodesToDelete = Array.from(selectedNodes);
                console.log('Deleting nodes:', nodesToDelete);
                
                // Eliminar nodos seleccionados
                setNodes(prev => {
                  const filtered = prev.filter(node => !selectedNodes.has(node.id));
                  console.log('Nodes after deletion:', filtered.length, 'from', prev.length);
                  return filtered;
                });
                
                // Eliminar conexiones relacionadas
                setConnections(prev => {
                  const filtered = prev.filter(conn => 
                    !selectedNodes.has(conn.from) && !selectedNodes.has(conn.to)
                  );
                  console.log('Connections after deletion:', filtered.length, 'from', prev.length);
                  return filtered;
                });
                
                // Limpiar selección
                console.log('Clearing selection...');
                clearSelection();
              } else {
                console.log('No nodes selected to delete');
              }
            }}
            onClick={(e) => {
              console.log('Delete button clicked! EVENT FIRED');
              e.preventDefault();
              e.stopPropagation();
            }}
            className="flex items-center gap-2 px-3 py-2 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/50 transition text-sm"
            title={t('deleteAll')}
            style={{ pointerEvents: 'auto', zIndex: 10000 }}
          >
            <Trash2 className="w-4 h-4" />
            {t('deleteAll')}
          </button>
        </div>
      </div>
    );
  };


  // Panel de propiedades dinámico con traducciones
  const PropertyPanel = ({ node }: { node: any }) => {
    const [formData, setFormData] = useState<any>(node.data || {});

    const handleFieldChange = (field: string, value: any) => {
      console.log('=== handleFieldChange called ===');
      console.log('Field:', field, 'Value:', value);
      console.log('Current formData:', formData);
      
      const newFormData = { ...formData, [field]: value };
      console.log('New formData:', newFormData);
      
      setFormData(newFormData);
      
      setNodes(prevNodes => 
        prevNodes.map(n => 
          n.id === node.id 
            ? { ...n, data: newFormData }
            : n
        )
      );
      
      console.log('=== handleFieldChange completed ===');
    };

    const getFieldLabel = (field: string) => {
      return field.replace(/_/g, ' ').charAt(0).toUpperCase() + field.replace(/_/g, ' ').slice(1);
    };

    const fields = node.config?.fields || [];

    return (
      <div 
        data-property-panel="true"
        className="fixed right-0 top-16 h-full w-80 bg-white dark:bg-gray-800 shadow-xl dark:shadow-gray-900/50 p-6 overflow-y-auto property-panel-internal"
        style={{ 
          zIndex: 9999,
          pointerEvents: 'auto'
        }}
        onClick={(e) => {
          console.log('Panel clicked!');
          e.stopPropagation();
        }}
      >
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold flex items-center gap-2 text-gray-900 dark:text-gray-100">
            <span className="text-2xl">{node.icon}</span>
            {node.name}
          </h3>
          <button
            onClick={() => setShowProperties(false)}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>
        
        <div className="space-y-4">
          {/* Test button */}
          <button
            onClick={() => {
              console.log('TEST BUTTON CLICKED!');
              alert('Button works!');
            }}
            className="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600"
            style={{ pointerEvents: 'auto' }}
          >
            Click Test (Should Work)
          </button>
          
          {/* Simple test input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Test Input (should work)
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-red-500 rounded-lg focus:ring-2 focus:ring-red-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              defaultValue=""
              placeholder="Type here to test..."
              style={{ pointerEvents: 'auto' }}
              onFocus={() => console.log('Input focused!')}
              onKeyDown={(e) => console.log('Key pressed:', e.key)}
              onChange={(e) => console.log('Input changed:', e.target.value)}
            />
          </div>
          
          {/* Actual fields */}
          {fields.map((field: string) => (
            <div key={field}>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {getFieldLabel(field)}
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                value={formData[field] || ''}
                onChange={(e) => {
                  console.log('Input changed:', field, e.target.value);
                  handleFieldChange(field, e.target.value);
                }}
                placeholder={`Enter ${field}`}
              />
            </div>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t dark:border-gray-700">
          <button 
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
            onClick={() => setShowProperties(false)}
          >
            {t('saveProperties')}
          </button>
        </div>
      </div>
    );
  };

  // Insert Node Menu
  const InsertNodeMenu = () => {
    if (!showInsertMenu) return null;

    return (
      <div 
        className="fixed bg-white dark:bg-gray-800 rounded-lg shadow-xl dark:shadow-gray-900/50 border dark:border-gray-600 p-2 z-50 max-h-60 overflow-y-auto insert-menu"
        style={{
          left: showInsertMenu.x,
          top: showInsertMenu.y,
          transform: 'translate(-50%, -50%)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-2">Insert Node</div>
        <div className="space-y-1">
          {availableComponents.map(component => (
            <button
              key={component.id}
              onMouseDown={(e) => {
                console.log('Menu button mousedown:', component.nameKey);
                e.preventDefault();
                e.stopPropagation();
                
                console.log('Inserting component:', component.nameKey, 'for connection:', showInsertMenu?.connectionId);
                if (!showInsertMenu) {
                  console.log('No showInsertMenu state!');
                  return;
                }
                const insertX = showInsertMenu.canvasX ?? showInsertMenu.x;
                const insertY = showInsertMenu.canvasY ?? showInsertMenu.y;
                insertNodeInConnection(
                  showInsertMenu.connectionId, 
                  component, 
                  { x: insertX - 60, y: insertY - 40 }
                );
              }}
              className="w-full flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-left text-sm cursor-pointer text-gray-900 dark:text-gray-100"
              style={{ pointerEvents: 'auto' }}
            >
              <span className="text-lg">{component.icon}</span>
              <span>{t(component.nameKey)}</span>
            </button>
          ))}
        </div>
      </div>
    );
  };

  // AI Prompt Dialog con traducciones
  const AIPromptDialog = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-900 dark:text-gray-100">
          <Code className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          {t('generateFlowWithAI')}
        </h3>
        <textarea
          className="w-full h-32 p-3 border dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
          placeholder={t('describeAutomation')}
          value={aiPrompt}
          onChange={(e) => setAIPrompt(e.target.value)}
        />
        <div className="flex gap-2 mt-4">
          <button
            onClick={() => {
              console.log('Processing AI prompt:', aiPrompt);
              setShowAIPrompt(false);
              setAIPrompt('');
            }}
            className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
          >
            {t('generateFlow')}
          </button>
          <button
            onClick={() => setShowAIPrompt(false)}
            className="flex-1 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 py-2 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
          >
            {t('cancel')}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Sidebar de componentes */}
      <div className="w-64 bg-white dark:bg-gray-800 shadow-lg p-4 overflow-y-auto component-sidebar">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-4 h-4" />
            <input
              type="text"
              placeholder={t('searchComponents')}
              className="w-full pl-10 pr-3 py-2 border dark:border-gray-600 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="space-y-4">
          {categories.map(categoryKey => (
            <div key={categoryKey}>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                {t(categoryKey)}
              </h3>
              <div className="space-y-1">
                {availableComponents
                  .filter(c => c.categoryKey === categoryKey)
                  .filter(c => t(c.nameKey).toLowerCase().includes(searchQuery.toLowerCase()))
                  .map(component => (
                    <div
                      key={component.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, component)}
                      className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-grab hover:bg-blue-50 dark:hover:bg-blue-900 hover:scale-105 transition-all duration-200 active:cursor-grabbing active:scale-95"
                    >
                      <span className="text-xl">{component.icon}</span>
                      <span className="text-sm text-gray-700 dark:text-gray-200">{t(component.nameKey)}</span>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Canvas principal */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition" title={t('save')}>
              <Save className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <button 
              onClick={handleUndo}
              disabled={!canUndo}
              className={`p-2 rounded-lg transition ${
                canUndo 
                  ? 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300' 
                  : 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
              }`} 
              title={t('undo')}
            >
              <Undo className="w-5 h-5" />
            </button>
            <button 
              onClick={handleRedo}
              disabled={!canRedo}
              className={`p-2 rounded-lg transition ${
                canRedo 
                  ? 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300' 
                  : 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
              }`} 
              title={t('redo')}
            >
              <Redo className="w-5 h-5" />
            </button>
            <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-2" />
            <button
              onClick={() => handleZoom(0.1)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              title={t('zoomIn')}
            >
              <ZoomIn className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <span className="text-sm font-medium px-2 text-gray-900 dark:text-gray-100">{Math.round(scale * 100)}%</span>
            <button
              onClick={() => handleZoom(-0.1)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              title={t('zoomOut')}
            >
              <ZoomOut className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
            <button
              onClick={() => {
                setScale(1);
                setOffset({ x: 0, y: 0 });
              }}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition text-xs font-medium text-gray-700 dark:text-gray-300"
              title="Reset View"
            >
              Reset
            </button>
            <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-2" />
            <button
              onClick={() => {
                const allNodeIds = new Set(nodes.map(node => node.id));
                setSelectedNodes(allNodeIds);
              }}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition text-xs font-medium text-gray-700 dark:text-gray-300"
              title={t('selectAll')}
            >
              {t('selectAll')}
            </button>
            <button
              onClick={clearSelection}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition text-xs font-medium text-gray-700 dark:text-gray-300"
              title={t('clearSelection')}
            >
              {t('clearSelection')}
            </button>
            <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-2" />
            <button
              onClick={() => setConnectionOrientation(connectionOrientation === 'horizontal' ? 'vertical' : 'horizontal')}
              className="flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition text-xs font-medium text-gray-700 dark:text-gray-300"
              title={`Connection orientation: ${connectionOrientation}`}
            >
              {connectionOrientation === 'horizontal' ? '↔' : '↕'}
              {connectionOrientation === 'horizontal' ? 'Horizontal' : 'Vertical'}
            </button>
            {clipboard && clipboard.nodes.length > 0 && (
              <>
                <div className="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-2" />
                <button
                  onClick={pasteNodes}
                  className="flex items-center gap-2 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition text-xs font-medium text-gray-700 dark:text-gray-300"
                  title={t('pasteNodes')}
                >
                  <Clipboard className="w-4 h-4" />
                  {t('pasteNodes')} ({clipboard.nodes.length})
                </button>
              </>
            )}
          </div>

          <div className="flex items-center gap-2">
            <ThemeSelector />
            <LanguageSelector />
            <button
              onClick={() => setShowAIPrompt(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition"
            >
              <Code className="w-4 h-4" />
              {t('generateWithAI')}
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
              <Play className="w-4 h-4" />
              {t('runFlow')}
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div
          ref={canvasRef}
          className="flex-1 relative overflow-hidden bg-gray-50 dark:bg-gray-900 cursor-grab"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onMouseDown={handleCanvasMouseDown}
          onClick={handleCanvasClick}
          style={{
            backgroundImage: `
              linear-gradient(to right, ${isDark ? '#374151' : '#d1d5db'} 1px, transparent 1px),
              linear-gradient(to bottom, ${isDark ? '#374151' : '#d1d5db'} 1px, transparent 1px)
            `,
            backgroundSize: `${20 * scale}px ${20 * scale}px`,
            backgroundPosition: `${offset.x}px ${offset.y}px`,
            cursor: isDraggingCanvas ? 'grabbing' : 'grab'
          }}
        >
          {/* Fondo del canvas para detectar clics */}
          <div 
            className="canvas-background absolute inset-0 w-full h-full"
            style={{ pointerEvents: 'auto' }}
          />
          <svg
            className="absolute inset-0 w-full h-full"
            style={{
              transform: `scale(${scale}) translate(${offset.x / scale}px, ${offset.y / scale}px)`,
              transformOrigin: '0 0',
              pointerEvents: 'none'
            }}
          >
            {renderedConnections}
          </svg>

          {/* Nodos */}
          <div
            className="absolute inset-0"
            style={{
              transform: `scale(${scale}) translate(${offset.x / scale}px, ${offset.y / scale}px)`,
              transformOrigin: '0 0'
            }}
          >
            {nodes.map(node => (
              <div
                key={node.id}
                data-node-id={node.id}
                className={`absolute bg-white dark:bg-gray-800 rounded-lg shadow-lg border-2 border-gray-400 dark:border-gray-600 p-4 transition-all hover:shadow-xl dark:hover:shadow-gray-900/50 ${
                  selectedNodes.has(node.id) ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600' : ''
                } ${
                  selectedNode?.id === node.id ? 'ring-2 ring-purple-500 border-purple-300 dark:border-purple-600' : ''
                } ${
                  cutNodes.has(node.id) ? 'opacity-50 bg-gray-100 dark:bg-gray-700 ring-2 ring-dashed ring-orange-400 border-orange-300 dark:border-orange-600' : ''
                } ${
                  isDragging && draggedNodes.some(dn => dn.id === node.id)
                    ? 'cursor-grabbing shadow-2xl scale-105 ring-2 ring-blue-400 border-blue-400 dark:border-blue-500 z-50' 
                    : 'cursor-grab hover:shadow-xl hover:border-gray-500 dark:hover:border-gray-400'
                }`}
                style={{
                  left: node.position.x,
                  top: node.position.y,
                  minWidth: '120px'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedNodeId(node.id);
                  
                  // Abrir PropertyPanel fuera del FlowEditor
                  setGlobalPropertyPanelState({
                    showProperties: true,
                    selectedNode: node,
                    onFieldChange: (field: string, value: any) => {
                      setNodes(prevNodes => 
                        prevNodes.map(n => 
                          n.id === node.id 
                            ? { ...n, data: { ...n.data, [field]: value } }
                            : n
                        )
                      );
                    },
                    onClose: () => {
                      setGlobalPropertyPanelState((prev: any) => ({ ...prev, showProperties: false }));
                      setShowProperties(false);
                    }
                  });
                  
                  setShowProperties(true);
                }}
                onMouseDown={(e) => handleNodeMouseDown(e, node)}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{node.icon}</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">{node.name}</span>
                </div>
                
                {/* Connection points - adaptan según orientación */}
                {connectionOrientation === 'horizontal' ? (
                  <>
                    {/* Horizontal: entrada izquierda, salida derecha */}
                    <div
                      className={`connection-point absolute -left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-blue-500 rounded-full cursor-pointer hover:scale-125 transition-all duration-200 ${
                        connectingFrom ? 'animate-pulse ring-2 ring-blue-300' : ''
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        completeConnection(node.id);
                      }}
                    />
                    <div
                      className={`connection-point absolute -right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-blue-500 rounded-full cursor-pointer hover:scale-125 transition-all duration-200 ${
                        connectingFrom?.nodeId === node.id ? 'ring-2 ring-blue-400 bg-blue-600' : ''
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        startConnection(node.id);
                      }}
                    />
                  </>
                ) : (
                  <>
                    {/* Vertical: entrada arriba, salida abajo */}
                    <div
                      className={`connection-point absolute left-1/2 -top-2 transform -translate-x-1/2 w-4 h-4 bg-blue-500 rounded-full cursor-pointer hover:scale-125 transition-all duration-200 ${
                        connectingFrom ? 'animate-pulse ring-2 ring-blue-300' : ''
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        completeConnection(node.id);
                      }}
                    />
                    <div
                      className={`connection-point absolute left-1/2 -bottom-2 transform -translate-x-1/2 w-4 h-4 bg-blue-500 rounded-full cursor-pointer hover:scale-125 transition-all duration-200 ${
                        connectingFrom?.nodeId === node.id ? 'ring-2 ring-blue-400 bg-blue-600' : ''
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        startConnection(node.id);
                      }}
                    />
                  </>
                )}
                
                {/* Conditional outputs for IF nodes - adaptan según orientación */}
                {node.type === 'condition' && (
                  <>
                    {connectionOrientation === 'horizontal' ? (
                      <>
                        <div
                          className="connection-point absolute -bottom-2 left-1/3 w-4 h-4 bg-green-500 rounded-full cursor-pointer hover:scale-125 transition"
                          onClick={(e) => {
                            e.stopPropagation();
                            startConnection(node.id, 'true');
                          }}
                          title="True"
                        />
                        <div
                          className="connection-point absolute -bottom-2 right-1/3 w-4 h-4 bg-red-500 rounded-full cursor-pointer hover:scale-125 transition"
                          onClick={(e) => {
                            e.stopPropagation();
                            startConnection(node.id, 'false');
                          }}
                          title="False"
                        />
                      </>
                    ) : (
                      <>
                        <div
                          className="connection-point absolute -bottom-2 left-1/3 w-4 h-4 bg-green-500 rounded-full cursor-pointer hover:scale-125 transition"
                          onClick={(e) => {
                            e.stopPropagation();
                            startConnection(node.id, 'true');
                          }}
                          title="True"
                        />
                        <div
                          className="connection-point absolute -bottom-2 right-1/3 w-4 h-4 bg-red-500 rounded-full cursor-pointer hover:scale-125 transition"
                          onClick={(e) => {
                            e.stopPropagation();
                            startConnection(node.id, 'false');
                          }}
                          title="False"
                        />
                      </>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>

          {/* Cuadro de selección */}
          {selectionBox && (
            <div
              className="absolute border-2 border-blue-500 bg-blue-100 bg-opacity-20 pointer-events-none"
              style={{
                left: selectionBox.x * scale + offset.x,
                top: selectionBox.y * scale + offset.y,
                width: selectionBox.width * scale,
                height: selectionBox.height * scale,
                transform: `scale(1)`,
                transformOrigin: '0 0'
              }}
            />
          )}

          {/* Panel de propiedades */}
          {showProperties && selectedNode && (
            <PropertyPanel 
              key={selectedNode.id} 
              node={selectedNode} 
            />
          )}

          {/* Botones + como elementos HTML absolutos */}
          {connections.map(conn => {
            const fromNode = nodes.find(n => n.id === conn.from);
            const toNode = nodes.find(n => n.id === conn.to);
            if (!fromNode || !toNode) return null;
            
            // Calcular posiciones de conexión exactas (igual que en SVG)
            let x1, y1, x2, y2;
            
            if (connectionOrientation === 'horizontal') {
              // Horizontal: salida por la derecha, entrada por la izquierda
              if (conn.fromOutput === 'true') {
                x1 = fromNode.position.x + 40;
                y1 = fromNode.position.y + 80;
              } else if (conn.fromOutput === 'false') {
                x1 = fromNode.position.x + 80;
                y1 = fromNode.position.y + 80;
              } else {
                x1 = fromNode.position.x + 120;
                y1 = fromNode.position.y + 40;
              }
              x2 = toNode.position.x;
              y2 = toNode.position.y + 40;
            } else {
              // Vertical: salida por abajo, entrada por arriba
              if (conn.fromOutput === 'true') {
                x1 = fromNode.position.x + 40;
                y1 = fromNode.position.y + 80;
              } else if (conn.fromOutput === 'false') {
                x1 = fromNode.position.x + 80;
                y1 = fromNode.position.y + 80;
              } else {
                x1 = fromNode.position.x + 60;
                y1 = fromNode.position.y + 80;
              }
              x2 = toNode.position.x + 60;
              y2 = toNode.position.y;
            }
            
            // Calcular punto medio de la curva Bézier
            const midX = (x1 + x2) / 2;
            const midY = (y1 + y2) / 2;
            
            return (
              <button
                key={`btn-${conn.id}`}
                onClick={(e) => {
                  e.stopPropagation();
                  console.log('Opening insert menu for connection:', conn.id);
                  // Coordenadas en pantalla para el menú
                  const screenX = midX * scale + offset.x;
                  const screenY = midY * scale + offset.y;
                  setShowInsertMenu({ 
                    connectionId: conn.id, 
                    x: screenX,
                    y: screenY,
                    canvasX: midX,
                    canvasY: midY
                  });
                }}
                className="absolute w-6 h-6 bg-blue-500 hover:bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold cursor-pointer transition-all duration-200 hover:scale-110 shadow-lg hover:shadow-xl z-20 opacity-30 hover:opacity-100"
                style={{
                  left: midX * scale + offset.x - 12,
                  top: midY * scale + offset.y - 12,
                }}
                title="Click to insert node"
              >
                +
              </button>
            );
          })}

          {/* Panel de selección múltiple */}
          <MultiSelectionPanel />

          {/* Insert Node Menu */}
          <InsertNodeMenu />

          {/* AI Prompt Dialog */}
          {showAIPrompt && <AIPromptDialog />}
          </div>
        </div>
      </div>
    );
};

// Test component completamente aislado (movido fuera de FlowEditor)
const TestPanel = () => {
  const [testValue, setTestValue] = useState('');
  
  return (
    <div 
      style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '300px',
        height: '200px',
        backgroundColor: 'red',
        color: 'white',
        padding: '20px',
        zIndex: 99999,
        border: '5px solid yellow'
      }}
      onClick={() => console.log('TestPanel clicked!')}
    >
      <h1>TEST PANEL (OUTSIDE)</h1>
      <button 
        onClick={() => {
          console.log('OUTSIDE TEST BUTTON CLICKED!');
          alert('OUTSIDE TEST BUTTON WORKS!');
        }}
        style={{
          padding: '10px',
          fontSize: '16px',
          backgroundColor: 'green',
          color: 'white',
          border: 'none',
          cursor: 'pointer'
        }}
      >
        CLICK ME OUTSIDE
      </button>
      <br/><br/>
      <input 
        type="text" 
        value={testValue}
        onChange={(e) => {
          console.log('Outside Input changed:', e.target.value);
          setTestValue(e.target.value);
        }}
        style={{
          padding: '5px',
          fontSize: '14px',
          backgroundColor: 'white',
          color: 'black'
        }}
        placeholder="Type here..."
      />
      <div>Value: {testValue}</div>
    </div>
  );
};

// Mapeo de campos a claves de traducción
const fieldTranslationMap = {
  'folder': 'folderForSearch',
  'pattern': 'filesPatternToSearch',
  'include_subfolders': 'includeSubFolders',
  'result': 'result',
  'handler': 'handler',
  'dataframes': 'dataframes',
  'direction': 'direction',
  'excel_file_name': 'excelFileName',
  'sheet_name': 'sheet',
  'destination': 'destinationHandler',
  'condition': 'condition',
  'operator': 'operator',
  'value': 'value',
  'text': 'text',
  'delay': 'delay',
  'special_keys': 'specialKeys',
  'x': 'X',
  'y': 'Y',
  'button': 'button',
  'clicks': 'clicks'
};

// Hook para aplicar scrollbars personalizados
const useCustomScrollbars = () => {
  const { isDark } = useTheme();
  
  useEffect(() => {
    const styleId = 'global-custom-scrollbars';
    
    // Remover estilo existente
    const existingStyle = document.getElementById(styleId);
    if (existingStyle) {
      existingStyle.remove();
    }
    
    const styleElement = document.createElement('style');
    styleElement.id = styleId;
    
    const scrollbarCSS = `
      /* Scrollbars para sidebar de componentes */
      .component-sidebar::-webkit-scrollbar {
        width: 4px !important;
      }
      .component-sidebar::-webkit-scrollbar-track {
        background: ${isDark ? '#1f2937' : '#f9fafb'} !important;
        border-radius: 2px !important;
      }
      .component-sidebar::-webkit-scrollbar-thumb {
        background: ${isDark ? '#6b7280' : '#d1d5db'} !important;
        border-radius: 2px !important;
      }
      .component-sidebar::-webkit-scrollbar-thumb:hover {
        background: ${isDark ? '#9ca3af' : '#9ca3af'} !important;
      }
      
      /* Scrollbars para menú de inserción */
      .insert-menu::-webkit-scrollbar {
        width: 3px !important;
      }
      .insert-menu::-webkit-scrollbar-track {
        background: ${isDark ? '#374151' : '#f3f4f6'} !important;
        border-radius: 2px !important;
      }
      .insert-menu::-webkit-scrollbar-thumb {
        background: ${isDark ? '#6b7280' : '#d1d5db'} !important;
        border-radius: 2px !important;
      }
      .insert-menu::-webkit-scrollbar-thumb:hover {
        background: ${isDark ? '#9ca3af' : '#9ca3af'} !important;
      }
      
      /* Scrollbars para contenido principal */
      .main-content::-webkit-scrollbar {
        width: 4px !important;
      }
      .main-content::-webkit-scrollbar-track {
        background: ${isDark ? '#111827' : '#ffffff'} !important;
        border-radius: 2px !important;
      }
      .main-content::-webkit-scrollbar-thumb {
        background: ${isDark ? '#6b7280' : '#d1d5db'} !important;
        border-radius: 2px !important;
      }
      .main-content::-webkit-scrollbar-thumb:hover {
        background: ${isDark ? '#9ca3af' : '#9ca3af'} !important;
      }
      
      /* Scrollbars para panel de propiedades interno */
      .property-panel-internal::-webkit-scrollbar {
        width: 3px !important;
      }
      .property-panel-internal::-webkit-scrollbar-track {
        background: ${isDark ? '#1f2937' : '#f9fafb'} !important;
        border-radius: 2px !important;
      }
      .property-panel-internal::-webkit-scrollbar-thumb {
        background: ${isDark ? '#6b7280' : '#d1d5db'} !important;
        border-radius: 2px !important;
      }
      .property-panel-internal::-webkit-scrollbar-thumb:hover {
        background: ${isDark ? '#9ca3af' : '#9ca3af'} !important;
      }
    `;
    
    styleElement.innerHTML = scrollbarCSS;
    document.head.appendChild(styleElement);
    
    return () => {
      const style = document.getElementById(styleId);
      if (style) {
        style.remove();
      }
    };
  }, [isDark]);
};

// PropertyPanel external que funciona fuera del FlowEditor
const ExternalPropertyPanel = ({ node, onFieldChange, onClose }: any) => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const [formData, setFormData] = useState<any>(node.data || {});
  
  const handleFieldChange = (field: string, value: any) => {
    const newFormData = { ...formData, [field]: value };
    setFormData(newFormData);
    if (onFieldChange) {
      onFieldChange(field, value);
    }
  };

  const getFieldLabel = (field: string) => {
    const translationKey = (fieldTranslationMap as any)[field];
    return translationKey ? t(translationKey) : field.replace(/_/g, ' ').charAt(0).toUpperCase() + field.replace(/_/g, ' ').slice(1);
  };

  const fields = node.config?.fields || [];

  // ID único para el panel
  const panelId = `property-panel-${node.id}`;
  
  // Crear un contenedor interno con scrollbar personalizado
  const scrollableContentRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Crear CSS dinámico cada vez que cambie el tema
    const timestamp = Date.now();
    const uniqueClass = `scrollable-content-${timestamp}`;
    
    if (scrollableContentRef.current) {
      scrollableContentRef.current.className = uniqueClass;
    }
    
    const styleElement = document.createElement('style');
    styleElement.innerHTML = `
      .${uniqueClass} {
        height: 100%;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        padding-right: 4px;
      }
      
      .${uniqueClass}::-webkit-scrollbar {
        width: 4px !important;
      }
      
      .${uniqueClass}::-webkit-scrollbar-track {
        background: ${isDark ? '#1f2937' : '#f9fafb'} !important;
        border-radius: 2px !important;
      }
      
      .${uniqueClass}::-webkit-scrollbar-thumb {
        background: ${isDark ? '#6b7280' : '#d1d5db'} !important;
        border-radius: 2px !important;
      }
      
      .${uniqueClass}::-webkit-scrollbar-thumb:hover {
        background: ${isDark ? '#9ca3af' : '#9ca3af'} !important;
      }
    `;
    
    document.head.appendChild(styleElement);
    console.log('Nuevo scrollbar creado:', uniqueClass, 'isDark:', isDark);
    
    return () => {
      if (styleElement.parentNode) {
        styleElement.parentNode.removeChild(styleElement);
      }
    };
  }, [isDark]);

  return (
    <div 
      id={panelId}
      data-property-panel
      style={{
        position: 'fixed',
        right: '0',
        top: '64px',
        width: '320px',
        height: 'calc(100vh - 64px)',
        backgroundColor: isDark ? '#1f2937' : 'white',
        color: isDark ? '#f9fafb' : '#111827',
        padding: '24px',
        zIndex: 99999,
        border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
        boxShadow: isDark 
          ? '-4px 0 6px -1px rgba(0, 0, 0, 0.3), -10px 0 15px -3px rgba(0, 0, 0, 0.2)' 
          : '-4px 0 6px -1px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden' // El contenedor padre no hace scroll
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 'bold', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '24px' }}>{node.icon}</span>
          {node.name}
        </h3>
        <button 
          onClick={() => onClose && onClose()}
          style={{
            padding: '8px',
            backgroundColor: 'transparent',
            border: 'none',
            cursor: 'pointer',
            borderRadius: '6px',
            color: isDark ? '#9ca3af' : '#6b7280',
            fontSize: '16px',
            fontWeight: 'bold',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = isDark ? '#374151' : '#f3f4f6';
            e.currentTarget.style.color = isDark ? '#f9fafb' : '#111827';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = isDark ? '#9ca3af' : '#6b7280';
          }}
        >
          ✕
        </button>
      </div>
      
      {/* Contenido scrollable */}
      <div 
        ref={scrollableContentRef}
        style={{ 
          height: 'calc(100% - 80px)', // Restar altura del header
          display: 'flex', 
          flexDirection: 'column', 
          gap: '16px' 
        }}
      >
        {fields.map((field: string) => (
          <div key={field}>
            <label style={{ 
              display: 'block', 
              fontSize: '14px', 
              fontWeight: '500', 
              color: isDark ? '#d1d5db' : '#374151', 
              marginBottom: '4px' 
            }}>
              {getFieldLabel(field)}
            </label>
            {field === 'include_subfolders' || field === 'direction' ? (
              <select
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: `1px solid ${isDark ? '#4b5563' : '#d1d5db'}`,
                  borderRadius: '8px',
                  fontSize: '14px',
                  backgroundColor: isDark ? '#374151' : 'white',
                  color: isDark ? '#f9fafb' : '#111827',
                  outline: 'none',
                  transition: 'border-color 0.2s, box-shadow 0.2s'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.boxShadow = `0 0 0 3px ${isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.1)'}`;
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = isDark ? '#4b5563' : '#d1d5db';
                  e.currentTarget.style.boxShadow = 'none';
                }}
                value={formData[field] || ''}
                onChange={(e) => handleFieldChange(field, e.target.value)}
              >
                <option value="">{t('select')}</option>
                {field === 'include_subfolders' ? (
                  <>
                    <option value="yes">{t('yes')}</option>
                    <option value="no">{t('no')}</option>
                  </>
                ) : (
                  <>
                    <option value="horizontal">{t('horizontal')}</option>
                    <option value="vertical">{t('vertical')}</option>
                  </>
                )}
              </select>
            ) : (
              <input
                type="text"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: `1px solid ${isDark ? '#4b5563' : '#d1d5db'}`,
                  borderRadius: '8px',
                  fontSize: '14px',
                  backgroundColor: isDark ? '#374151' : 'white',
                  color: isDark ? '#f9fafb' : '#111827',
                  outline: 'none',
                  transition: 'border-color 0.2s, box-shadow 0.2s'
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#3b82f6';
                  e.currentTarget.style.boxShadow = `0 0 0 3px ${isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.1)'}`;
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = isDark ? '#4b5563' : '#d1d5db';
                  e.currentTarget.style.boxShadow = 'none';
                }}
                value={formData[field] || ''}
                onChange={(e) => handleFieldChange(field, e.target.value)}
                placeholder={`Enter ${getFieldLabel(field).toLowerCase()}`}
              />
            )}
          </div>
        ))}
      </div>
      {/* Fin del contenido scrollable */}

      <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: `1px solid ${isDark ? '#374151' : '#e5e7eb'}` }}>
        <button 
          style={{
            width: '100%',
            backgroundColor: '#2563eb',
            color: 'white',
            padding: '12px 16px',
            borderRadius: '8px',
            border: 'none',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#1d4ed8';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#2563eb';
          }}
          onClick={() => onClose && onClose()}
        >
          {t('saveProperties')}
        </button>
      </div>
    </div>
  );
};

// Test global completamente independiente
const GlobalTest = () => {
  const [value, setValue] = useState('');
  
  return (
    <div style={{
      position: 'fixed',
      top: '10px',
      left: '10px',
      width: '200px',
      height: '150px',
      backgroundColor: 'purple',
      color: 'white',
      padding: '10px',
      zIndex: 999999,
      border: '3px solid orange'
    }}>
      <h2>GLOBAL TEST</h2>
      <button 
        onClick={() => {
          console.log('GLOBAL BUTTON CLICKED!');
          window.alert('GLOBAL BUTTON WORKS!');
        }}
        style={{
          backgroundColor: 'yellow',
          color: 'black',
          padding: '5px',
          border: 'none',
          cursor: 'pointer'
        }}
      >
        GLOBAL CLICK
      </button>
      <br/><br/>
      <input 
        value={value}
        onChange={(e) => {
          console.log('GLOBAL INPUT:', e.target.value);
          setValue(e.target.value);
        }}
        style={{ width: '100%' }}
      />
      <div>Val: {value}</div>
    </div>
  );
};

// Componente principal de la aplicación con i18n
const App = () => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const [currentView, setCurrentView] = useState('dashboard');
  
  // Aplicar scrollbars personalizados globalmente
  useCustomScrollbars();
  
  // Estado global para PropertyPanel
  const [globalPropertyPanelState, setGlobalPropertyPanelState] = useState<{
    showProperties: boolean;
    selectedNode: any;
    onFieldChange: ((field: string, value: any) => void) | null;
    onClose: (() => void) | null;
  }>({
    showProperties: false,
    selectedNode: null,
    onFieldChange: null,
    onClose: null
  });
  const [flows] = useState([
    { id: 1, name: 'Invoice Processing', status: 'active', lastRun: '2', runs: 45 },
    { id: 2, name: 'Data Migration', status: 'inactive', lastRun: '1', runs: 12 },
    { id: 3, name: 'Report Generation', status: 'active', lastRun: '30', runs: 128 }
  ]);

  const renderDashboard = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        {t('welcomeTitle')}
      </h1>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 dark:text-gray-400 text-sm">{t('activeFlows')}</span>
            <Activity className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">12</div>
          <div className="text-xs text-green-600 mt-1">+2 {t('thisWeek')}</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 dark:text-gray-400 text-sm">{t('totalExecutions')}</span>
            <Play className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">1,284</div>
          <div className="text-xs text-blue-600 mt-1">98% {t('successRate')}</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 dark:text-gray-400 text-sm">{t('timeSaved')}</span>
            <Clock className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">47h</div>
          <div className="text-xs text-purple-600 mt-1">{t('thisMonth')}</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 dark:text-gray-400 text-sm">{t('errors')}</span>
            <AlertCircle className="w-5 h-5 text-red-500" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">3</div>
          <div className="text-xs text-red-600 mt-1">{t('needsAttention')}</div>
        </div>
      </div>

      {/* Recent Events */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 p-6">
        <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">{t('recentEvents')}</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <Check className="w-5 h-5 text-green-600" />
            <div className="flex-1">
              <div className="font-medium text-sm text-gray-900 dark:text-white">Invoice Processing {t('completedSuccessfully')}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">2 {t('minutesAgo')}</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <Activity className="w-5 h-5 text-blue-600" />
            <div className="flex-1">
              <div className="font-medium text-sm text-gray-900 dark:text-white">Data Migration {t('started')}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">15 {t('minutesAgo')}</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div className="flex-1">
              <div className="font-medium text-sm text-gray-900 dark:text-white">Report Generation {t('failed')} - {t('connectionTimeout')}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">1 {t('hourAgo')}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFlowsList = () => (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t('myFlows')}</h1>
        <button
          onClick={() => setCurrentView('editor')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus className="w-5 h-5" />
          {t('newFlow')}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {flows.map(flow => (
          <div key={flow.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 p-6 hover:shadow-lg transition">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-semibold text-lg text-gray-900 dark:text-white">{flow.name}</h3>
              <span className={`px-2 py-1 text-xs rounded-full ${
                flow.status === 'active' 
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' 
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}>
                {t(flow.status)}
              </span>
            </div>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
              <div className="flex justify-between">
                <span>{t('lastRun')}:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {flow.lastRun} {parseInt(flow.lastRun) === 1 ? t('hourAgo') : t('hoursAgo')}
                </span>
              </div>
              <div className="flex justify-between">
                <span>{t('totalRuns')}:</span>
                <span className="font-medium text-gray-900 dark:text-white">{flow.runs}</span>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentView('editor')}
                className="flex-1 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition text-sm"
              >
                <Edit3 className="w-4 h-4 inline mr-1" />
                {t('edit')}
              </button>
              <button className="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
                <Copy className="w-4 h-4" />
              </button>
              <button className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="h-screen flex">
      {/* Sidebar Navigation */}
      {currentView !== 'editor' && (
        <div className="w-64 bg-gray-900 dark:bg-gray-950 text-white p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Agentiqware
            </h1>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{t('platformSubtitle')}</p>
          </div>

          <nav className="space-y-2">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition ${
                currentView === 'dashboard' ? 'bg-gray-800 dark:bg-gray-900' : 'hover:bg-gray-800 dark:hover:bg-gray-900'
              }`}
            >
              <Home className="w-5 h-5" />
              {t('dashboard')}
            </button>
            <button
              onClick={() => setCurrentView('flows')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition ${
                currentView === 'flows' ? 'bg-gray-800 dark:bg-gray-900' : 'hover:bg-gray-800 dark:hover:bg-gray-900'
              }`}
            >
              <GitBranch className="w-5 h-5" />
              {t('flows')}
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-900 transition">
              <FileText className="w-5 h-5" />
              {t('logs')}
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-900 transition">
              <Settings className="w-5 h-5" />
              {t('settings')}
            </button>
          </nav>

          <div className="mt-auto pt-8 border-t border-gray-800 dark:border-gray-700 space-y-2">
            <ThemeSelector />
            <LanguageSelector />
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition text-red-400">
              <LogOut className="w-5 h-5" />
              {t('logout')}
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 bg-gray-50 dark:bg-gray-900 overflow-auto main-content">
        {currentView === 'dashboard' && renderDashboard()}
        {currentView === 'flows' && renderFlowsList()}
        {currentView === 'editor' && (
          <FlowEditor 
            globalPropertyPanelState={globalPropertyPanelState}
            setGlobalPropertyPanelState={setGlobalPropertyPanelState}
          />
        )}
      </div>
      
      
      {/* Property Panel REAL fuera del FlowEditor */}
      {currentView === 'editor' && globalPropertyPanelState.showProperties && globalPropertyPanelState.selectedNode && (
        <ExternalPropertyPanel 
          node={globalPropertyPanelState.selectedNode}
          onFieldChange={globalPropertyPanelState.onFieldChange}
          onClose={globalPropertyPanelState.onClose}
        />
      )}
    </div>
  );
};

// Componente raíz con proveedores de idioma y tema
const RootApp = () => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <App />
      </LanguageProvider>
    </ThemeProvider>
  );
};

export default RootApp;