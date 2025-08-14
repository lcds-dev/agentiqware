import React, { useState, useRef, useCallback, useEffect, createContext, useContext } from 'react';
import { Plus, Search, Save, Play, Undo, Redo, ZoomIn, ZoomOut, GitBranch, Code, Copy, Trash2, Edit3, Home, FileText, Activity, Settings, LogOut, Clock, X, Check, AlertCircle, Globe, Scissors, Clipboard } from 'lucide-react';

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

// Selector de idioma
const LanguageSelector = () => {
  const { language, changeLanguage } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
      >
        <Globe className="w-4 h-4" />
        <span className="text-sm font-medium">{language.toUpperCase()}</span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-32 bg-white rounded-lg shadow-lg border z-50">
          <button
            onClick={() => {
              changeLanguage('en');
              setIsOpen(false);
            }}
            className={`w-full text-left px-4 py-2 hover:bg-gray-100 transition ${
              language === 'en' ? 'bg-blue-50 text-blue-600' : ''
            }`}
          >
            English
          </button>
          <button
            onClick={() => {
              changeLanguage('es');
              setIsOpen(false);
            }}
            className={`w-full text-left px-4 py-2 hover:bg-gray-100 transition ${
              language === 'es' ? 'bg-blue-50 text-blue-600' : ''
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
const FlowEditor = () => {
  const { t } = useTranslation();
  const canvasRef = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<any[]>([]);
  const [connections, setConnections] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
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
  }, []);

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


  const duplicateSelectedNodes = useCallback(() => {
    if (selectedNodes.size > 0) {
      const nodesToDuplicate = nodes.filter(node => selectedNodes.has(node.id));
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
    }
  }, [selectedNodes, nodes]);

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
    // Actualizar posición del mouse para conexiones temporales
    const rect = canvasRef.current?.getBoundingClientRect();
    if (rect) {
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
      
      setOffset(prev => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }));
      
      setLastMousePos({ x: e.clientX, y: e.clientY });
    }
  }, [isDragging, draggedNode, dragStart, offset, scale, isDraggingCanvas, lastMousePos]);

  // Manejar fin del drag
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setDraggedNode(null);
    setDraggedNodes([]);
    setIsDraggingCanvas(false);
    setIsSelecting(false);
    setSelectionBox(null);
  }, []);

  // Manejar drag del canvas
  const handleCanvasMouseDown = (e: any) => {
    if (e.target === canvasRef.current || e.target.closest('.canvas-background')) {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      
      const isCtrlPressed = e.ctrlKey || e.metaKey;
      
      
      // Solo iniciar selección por arrastre si no se presiona Ctrl
      if (!isCtrlPressed) {
        // Iniciar selección por arrastre
        const startX = (e.clientX - rect.left - offset.x) / scale;
        const startY = (e.clientY - rect.top - offset.y) / scale;
        
        setIsSelecting(true);
        setSelectionStart({ x: startX, y: startY });
      }
      
      setIsDraggingCanvas(false);
      setLastMousePos({ x: e.clientX, y: e.clientY });
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
    // Verificar si el clic NO fue en un nodo o connection point
    const isNodeClick = e.target.closest('[data-node-id]');
    const isConnectionPoint = e.target.classList?.contains('connection-point');
    
    if (!isNodeClick && !isConnectionPoint) {
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

  // Manejar teclas
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
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
      }
    }
  }, [selectedNodes, nodes, clearSelection, setConnectingFrom, copySelectedNodes, cutSelectedNodes, pasteNodes]);

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
  const renderConnections = () => {
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
      
      // Calcular punto de salida
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
      
      // Calcular punto de llegada
      if (conn.to === 'mouse') {
        x2 = mousePosition.x;
        y2 = mousePosition.y;
      } else {
        const toNode = nodes.find(n => n.id === conn.to);
        if (!toNode) return null;
        x2 = toNode.position.x;
        y2 = toNode.position.y + 40;
      }

      const dx = x2 - x1;
      const cp1x = x1 + dx * 0.5;
      const cp1y = y1;
      const cp2x = x2 - dx * 0.5;
      const cp2y = y2;

      return (
        <g key={conn.id}>
          <path
            d={`M ${x1} ${y1} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`}
            stroke={conn.isTemp ? '#94a3b8' : conn.fromOutput === 'true' ? '#22c55e' : conn.fromOutput === 'false' ? '#ef4444' : '#6366f1'}
            strokeWidth={conn.isTemp ? '1' : '2'}
            strokeDasharray={conn.isTemp ? '5,5' : 'none'}
            fill="none"
            className={`transition-all ${
              conn.isTemp ? 'opacity-60' : 'hover:stroke-opacity-80 cursor-pointer'
            }`}
            onClick={() => !conn.isTemp && removeConnection(conn.id)}
          />
          {/* Punto medio para eliminar conexión */}
          {!conn.isTemp && (
            <circle
              cx={(x1 + x2) / 2}
              cy={(y1 + y2) / 2}
              r="6"
              fill="#ef4444"
              className="opacity-0 hover:opacity-100 cursor-pointer transition-opacity"
              onClick={(e) => {
                e.stopPropagation();
                removeConnection(conn.id);
              }}
            >
              <title>Click to remove connection</title>
            </circle>
          )}
        </g>
      );
    });
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

  // Panel de selección múltiple
  const MultiSelectionPanel = () => {
    if (selectedNodes.size <= 1) return null;

    return (
      <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-xl border p-4 z-50 min-w-80">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="font-medium">{t('selectedNodes')}: {selectedNodes.size}</span>
          </div>
          <button
            onClick={clearSelection}
            className="p-1 hover:bg-gray-100 rounded"
            title={t('clearSelection')}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={copySelectedNodes}
            className="flex items-center gap-2 px-3 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition text-sm"
            title={t('copyNodes')}
          >
            <Copy className="w-4 h-4" />
            {t('copyNodes')}
          </button>
          <button
            onClick={cutSelectedNodes}
            className="flex items-center gap-2 px-3 py-2 bg-orange-50 text-orange-600 rounded-lg hover:bg-orange-100 transition text-sm"
            title={t('cutNodes')}
          >
            <Scissors className="w-4 h-4" />
            {t('cutNodes')}
          </button>
          <button
            onClick={pasteNodes}
            disabled={!clipboard || clipboard.nodes.length === 0}
            className="flex items-center gap-2 px-3 py-2 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            title={t('pasteNodes')}
          >
            <Clipboard className="w-4 h-4" />
            {t('pasteNodes')}
          </button>
          <button
            onClick={duplicateSelectedNodes}
            className="flex items-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition text-sm"
            title={t('duplicateAll')}
          >
            <Copy className="w-4 h-4" />
            {t('duplicateAll')}
          </button>
          <button
            onClick={() => {
              if (selectedNodes.size > 0) {
                // Eliminar nodos seleccionados
                setNodes(prev => prev.filter(node => !selectedNodes.has(node.id)));
                
                // Eliminar conexiones relacionadas
                setConnections(prev => prev.filter(conn => 
                  !selectedNodes.has(conn.from) && !selectedNodes.has(conn.to)
                ));
                
                clearSelection();
              }
            }}
            className="flex items-center gap-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition text-sm"
            title={t('deleteAll')}
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
    const [formData, setFormData] = useState(node.data || {});

    const handleFieldChange = (field: string, value: any) => {
      setFormData({ ...formData, [field]: value });
      node.data = { ...formData, [field]: value };
    };

    const getFieldLabel = (field: string) => {
      const translationKey = (fieldTranslationMap as any)[field];
      return translationKey ? t(translationKey) : field.replace(/_/g, ' ').charAt(0).toUpperCase() + field.replace(/_/g, ' ').slice(1);
    };

    return (
      <div className="fixed right-0 top-16 h-full w-80 bg-white shadow-xl p-6 overflow-y-auto z-50">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <span className="text-2xl">{node.icon}</span>
            {node.name}
          </h3>
          <button
            onClick={() => setShowProperties(false)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-4">
          {node.config.fields?.map((field: string) => (
            <div key={field}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {getFieldLabel(field)}
              </label>
              {field === 'include_subfolders' || field === 'direction' ? (
                <select
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
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
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={formData[field] || ''}
                  onChange={(e) => handleFieldChange(field, e.target.value)}
                  placeholder={`${t('enter')} ${getFieldLabel(field).toLowerCase()}`}
                />
              )}
            </div>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t">
          <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">
            {t('saveProperties')}
          </button>
        </div>
      </div>
    );
  };

  // AI Prompt Dialog con traducciones
  const AIPromptDialog = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-2xl">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Code className="w-5 h-5" />
          {t('generateFlowWithAI')}
        </h3>
        <textarea
          className="w-full h-32 p-3 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500"
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
            className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300 transition"
          >
            {t('cancel')}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-gray-50 flex">
      {/* Sidebar de componentes */}
      <div className="w-64 bg-white shadow-lg p-4 overflow-y-auto">
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder={t('searchComponents')}
              className="w-full pl-10 pr-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="space-y-4">
          {categories.map(categoryKey => (
            <div key={categoryKey}>
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">
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
                      className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg cursor-grab hover:bg-blue-50 hover:scale-105 transition-all duration-200 active:cursor-grabbing active:scale-95"
                    >
                      <span className="text-xl">{component.icon}</span>
                      <span className="text-sm">{t(component.nameKey)}</span>
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
        <div className="bg-white shadow-sm border-b px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-gray-100 rounded-lg transition" title={t('save')}>
              <Save className="w-5 h-5" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg transition" title={t('undo')}>
              <Undo className="w-5 h-5" />
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-lg transition" title={t('redo')}>
              <Redo className="w-5 h-5" />
            </button>
            <div className="w-px h-6 bg-gray-300 mx-2" />
            <button
              onClick={() => handleZoom(0.1)}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
              title={t('zoomIn')}
            >
              <ZoomIn className="w-5 h-5" />
            </button>
            <span className="text-sm font-medium px-2">{Math.round(scale * 100)}%</span>
            <button
              onClick={() => handleZoom(-0.1)}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
              title={t('zoomOut')}
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <button
              onClick={() => {
                setScale(1);
                setOffset({ x: 0, y: 0 });
              }}
              className="p-2 hover:bg-gray-100 rounded-lg transition text-xs font-medium"
              title="Reset View"
            >
              Reset
            </button>
            <div className="w-px h-6 bg-gray-300 mx-2" />
            <button
              onClick={() => {
                const allNodeIds = new Set(nodes.map(node => node.id));
                setSelectedNodes(allNodeIds);
              }}
              className="p-2 hover:bg-gray-100 rounded-lg transition text-xs font-medium"
              title={t('selectAll')}
            >
              {t('selectAll')}
            </button>
            <button
              onClick={clearSelection}
              className="p-2 hover:bg-gray-100 rounded-lg transition text-xs font-medium"
              title={t('clearSelection')}
            >
              {t('clearSelection')}
            </button>
            {clipboard && clipboard.nodes.length > 0 && (
              <>
                <div className="w-px h-6 bg-gray-300 mx-2" />
                <button
                  onClick={pasteNodes}
                  className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition text-xs font-medium"
                  title={t('pasteNodes')}
                >
                  <Clipboard className="w-4 h-4" />
                  {t('pasteNodes')} ({clipboard.nodes.length})
                </button>
              </>
            )}
          </div>

          <div className="flex items-center gap-2">
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
          className="flex-1 relative overflow-hidden bg-gray-50 cursor-grab"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onMouseDown={handleCanvasMouseDown}
          onClick={handleCanvasClick}
          style={{
            backgroundImage: 'radial-gradient(circle, #e5e7eb 1px, transparent 1px)',
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
            className="absolute inset-0 w-full h-full pointer-events-none"
            style={{
              transform: `scale(${scale}) translate(${offset.x / scale}px, ${offset.y / scale}px)`,
              transformOrigin: '0 0'
            }}
          >
            {renderConnections()}
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
                className={`absolute bg-white rounded-lg shadow-lg p-4 transition-all hover:shadow-xl ${
                  selectedNodes.has(node.id) ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                } ${
                  selectedNode?.id === node.id ? 'ring-2 ring-purple-500' : ''
                } ${
                  cutNodes.has(node.id) ? 'opacity-50 bg-gray-100 ring-2 ring-dashed ring-orange-400' : ''
                } ${
                  isDragging && draggedNodes.some(dn => dn.id === node.id)
                    ? 'cursor-grabbing shadow-2xl scale-105 ring-2 ring-blue-400 z-50' 
                    : 'cursor-grab hover:shadow-xl'
                }`}
                style={{
                  left: node.position.x,
                  top: node.position.y,
                  minWidth: '120px'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedNode(node);
                  setShowProperties(true);
                }}
                onMouseDown={(e) => handleNodeMouseDown(e, node)}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{node.icon}</span>
                  <span className="text-sm font-medium">{node.name}</span>
                </div>
                
                {/* Connection points */}
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
                
                {/* Conditional outputs for IF nodes */}
                {node.type === 'condition' && (
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
          {showProperties && selectedNode && <PropertyPanel node={selectedNode} />}

          {/* Panel de selección múltiple */}
          <MultiSelectionPanel />

          {/* AI Prompt Dialog */}
          {showAIPrompt && <AIPromptDialog />}
        </div>
      </div>
    </div>
  );
};

// Componente principal de la aplicación con i18n
const App = () => {
  const { t } = useTranslation();
  const [currentView, setCurrentView] = useState('dashboard');
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
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 text-sm">{t('activeFlows')}</span>
            <Activity className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold">12</div>
          <div className="text-xs text-green-600 mt-1">+2 {t('thisWeek')}</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 text-sm">{t('totalExecutions')}</span>
            <Play className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold">1,284</div>
          <div className="text-xs text-blue-600 mt-1">98% {t('successRate')}</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 text-sm">{t('timeSaved')}</span>
            <Clock className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold">47h</div>
          <div className="text-xs text-purple-600 mt-1">{t('thisMonth')}</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-500 text-sm">{t('errors')}</span>
            <AlertCircle className="w-5 h-5 text-red-500" />
          </div>
          <div className="text-2xl font-bold">3</div>
          <div className="text-xs text-red-600 mt-1">{t('needsAttention')}</div>
        </div>
      </div>

      {/* Recent Events */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">{t('recentEvents')}</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <Check className="w-5 h-5 text-green-600" />
            <div className="flex-1">
              <div className="font-medium text-sm">Invoice Processing {t('completedSuccessfully')}</div>
              <div className="text-xs text-gray-500">2 {t('minutesAgo')}</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <Activity className="w-5 h-5 text-blue-600" />
            <div className="flex-1">
              <div className="font-medium text-sm">Data Migration {t('started')}</div>
              <div className="text-xs text-gray-500">15 {t('minutesAgo')}</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div className="flex-1">
              <div className="font-medium text-sm">Report Generation {t('failed')} - {t('connectionTimeout')}</div>
              <div className="text-xs text-gray-500">1 {t('hourAgo')}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFlowsList = () => (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">{t('myFlows')}</h1>
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
          <div key={flow.id} className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-lg transition">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-semibold text-lg">{flow.name}</h3>
              <span className={`px-2 py-1 text-xs rounded-full ${
                flow.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
              }`}>
                {t(flow.status)}
              </span>
            </div>
            <div className="space-y-2 text-sm text-gray-600 mb-4">
              <div className="flex justify-between">
                <span>{t('lastRun')}:</span>
                <span className="font-medium">
                  {flow.lastRun} {parseInt(flow.lastRun) === 1 ? t('hourAgo') : t('hoursAgo')}
                </span>
              </div>
              <div className="flex justify-between">
                <span>{t('totalRuns')}:</span>
                <span className="font-medium">{flow.runs}</span>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentView('editor')}
                className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition text-sm"
              >
                <Edit3 className="w-4 h-4 inline mr-1" />
                {t('edit')}
              </button>
              <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition">
                <Copy className="w-4 h-4" />
              </button>
              <button className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition">
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
        <div className="w-64 bg-gray-900 text-white p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Agentiqware
            </h1>
            <p className="text-xs text-gray-400 mt-1">{t('platformSubtitle')}</p>
          </div>

          <nav className="space-y-2">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition ${
                currentView === 'dashboard' ? 'bg-gray-800' : 'hover:bg-gray-800'
              }`}
            >
              <Home className="w-5 h-5" />
              {t('dashboard')}
            </button>
            <button
              onClick={() => setCurrentView('flows')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition ${
                currentView === 'flows' ? 'bg-gray-800' : 'hover:bg-gray-800'
              }`}
            >
              <GitBranch className="w-5 h-5" />
              {t('flows')}
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition">
              <FileText className="w-5 h-5" />
              {t('logs')}
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition">
              <Settings className="w-5 h-5" />
              {t('settings')}
            </button>
          </nav>

          <div className="mt-auto pt-8 border-t border-gray-800 space-y-2">
            <LanguageSelector />
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition text-red-400">
              <LogOut className="w-5 h-5" />
              {t('logout')}
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 bg-gray-50 overflow-auto">
        {currentView === 'dashboard' && renderDashboard()}
        {currentView === 'flows' && renderFlowsList()}
        {currentView === 'editor' && <FlowEditor />}
      </div>
    </div>
  );
};

// Componente raíz con proveedor de idioma
const RootApp = () => {
  return (
    <LanguageProvider>
      <App />
    </LanguageProvider>
  );
};

export default RootApp;