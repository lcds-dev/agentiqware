import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  Plus, Search, Save, Edit3, Trash2, Eye, EyeOff, Download, Upload, 
  X, Check, AlertCircle, Database, Key, Mail, 
  Globe, Calendar, Type, Hash, ToggleLeft, List, Lock, Copy,
  Bell, Cog, Package
} from 'lucide-react';
import { useFlowTranslation } from './FlowEditor';

// ============================================
// Types and Constants
// ============================================

interface Variable {
  id: string;
  name: string;
  type: VariableType;
  label: string;
  description: string;
  defaultValue: any;
  required: boolean;
  category: VariableCategory;
  options?: string[]; // Only for select type
  createdAt: string;
  updatedAt: string;
}

type VariableType = 'string' | 'number' | 'boolean' | 'password' | 'email' | 'url' | 'date' | 'select';
type VariableCategory = 'Authentication' | 'Configuration' | 'Notifications' | 'Data' | 'Custom';

// Variable types will be populated with translations inside component
const VARIABLE_TYPES_BASE: { value: VariableType; key: string; icon: React.ReactNode }[] = [
  { value: 'string', key: 'textType', icon: <Type size={16} /> },
  { value: 'number', key: 'number', icon: <Hash size={16} /> },
  { value: 'boolean', key: 'boolean', icon: <ToggleLeft size={16} /> },
  { value: 'password', key: 'password', icon: <Lock size={16} /> },
  { value: 'email', key: 'email', icon: <Mail size={16} /> },
  { value: 'url', key: 'url', icon: <Globe size={16} /> },
  { value: 'date', key: 'date', icon: <Calendar size={16} /> },
  { value: 'select', key: 'selectType', icon: <List size={16} /> }
];

// Variable categories will be populated with translations inside component
const VARIABLE_CATEGORIES_BASE: { value: VariableCategory; key: string; icon: React.ReactNode }[] = [
  { value: 'Authentication', key: 'authentication', icon: <Key size={16} /> },
  { value: 'Configuration', key: 'configuration', icon: <Cog size={16} /> },
  { value: 'Notifications', key: 'notifications', icon: <Bell size={16} /> },
  { value: 'Data', key: 'data', icon: <Database size={16} /> },
  { value: 'Custom', key: 'custom', icon: <Package size={16} /> }
];

// ============================================
// Validation Functions
// ============================================

const validateVariableName = (name: string): boolean => /^[a-z][a-z0-9_]*$/.test(name);
const validateEmail = (email: string): boolean => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
const validateURL = (url: string): boolean => /^https?:\/\/.+/.test(url);

const validateVariableValue = (value: any, type: VariableType): boolean => {
  if (value === '' || value === null || value === undefined) return true; // Allow empty values
  
  switch (type) {
    case 'string':
      return typeof value === 'string';
    case 'number':
      return !isNaN(Number(value));
    case 'boolean':
      return typeof value === 'boolean';
    case 'email':
      return validateEmail(value);
    case 'url':
      return validateURL(value);
    case 'date':
      return !isNaN(Date.parse(value));
    case 'password':
      return typeof value === 'string';
    case 'select':
      return typeof value === 'string';
    default:
      return true;
  }
};

// ============================================
// Utility Functions for Flow-specific Variables
// ============================================

export const getVariableValue = (name: string, flowId: string): any => {
  try {
    const flowVariables = JSON.parse(localStorage.getItem(`agentiqware_variables_${flowId}`) || '[]');
    const variable = flowVariables.find((v: Variable) => v.name === name);
    return variable ? variable.defaultValue : null;
  } catch (error) {
    console.error('Error getting variable value:', error);
    return null;
  }
};

export const replaceVariables = (text: string, flowId: string): string => {
  try {
    const flowVariables = JSON.parse(localStorage.getItem(`agentiqware_variables_${flowId}`) || '[]');
    let result = text;
    
    flowVariables.forEach((variable: Variable) => {
      const pattern = new RegExp(`\\{\\{${variable.name}\\}\\}`, 'g');
      result = result.replace(pattern, variable.defaultValue || '');
    });
    
    return result;
  } catch (error) {
    console.error('Error replacing variables:', error);
    return text;
  }
};

export const getFlowVariables = (flowId: string): Variable[] => {
  try {
    return JSON.parse(localStorage.getItem(`agentiqware_variables_${flowId}`) || '[]');
  } catch (error) {
    console.error('Error getting flow variables:', error);
    return [];
  }
};

// ============================================
// Main Component
// ============================================

interface VariablesManagerProps {
  flowId: string;
  flowName?: string;
  onClose?: () => void;
  compact?: boolean;
}

const VariablesManager: React.FC<VariablesManagerProps> = ({ 
  flowId, 
  flowName, 
  onClose,
  compact = false 
}) => {
  // Get translation function
  const { t } = useFlowTranslation();
  
  // Helper function to format translation with parameters
  const formatMessage = (key: string, params?: Record<string, string | number>): string => {
    let message = t(key);
    if (params) {
      Object.entries(params).forEach(([param, value]) => {
        message = message.replace(`{${param}}`, String(value));
      });
    }
    return message;
  };
  
  // Create translated types and categories
  const VARIABLE_TYPES = VARIABLE_TYPES_BASE.map(type => ({
    value: type.value,
    label: t(type.key),
    icon: type.icon
  }));
  
  const VARIABLE_CATEGORIES = VARIABLE_CATEGORIES_BASE.map(cat => ({
    value: cat.value,
    label: t(cat.key),
    icon: cat.icon
  }));
  
  // Main States
  const [variables, setVariables] = useState<Variable[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingVariable, setEditingVariable] = useState<Variable | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  
  // Form States
  const [formData, setFormData] = useState<Partial<Variable>>({
    name: '',
    type: 'string',
    label: '',
    description: '',
    defaultValue: '',
    required: false,
    category: 'Custom',
    options: []
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [showPassword, setShowPassword] = useState<Record<string, boolean>>({});
  
  // UI States
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ============================================
  // Helper Functions
  // ============================================

  const showNotification = useCallback((type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
  }, []);

  // ============================================
  // Data Management
  // ============================================

  const loadVariables = useCallback(() => {
    try {
      const storageKey = `agentiqware_variables_${flowId}`;
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        setVariables(JSON.parse(stored));
      } else {
        // Initialize with basic sample data for new flows
        const sampleVariables: Variable[] = [
          {
            id: '1',
            name: 'flow_name',
            type: 'string',
            label: 'Flow Name',
            description: `${t('variablesFor')} ${flowName || t('currentFlow')}`,
            defaultValue: flowName || t('currentFlow'),
            required: false,
            category: 'Configuration',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        ];
        setVariables(sampleVariables);
        localStorage.setItem(storageKey, JSON.stringify(sampleVariables));
      }
    } catch (error) {
      showNotification('error', t('errorLoadingVariables'));
    }
  }, [flowId, flowName, showNotification, t]);

  // ============================================
  // Effects
  // ============================================

  useEffect(() => {
    loadVariables();
  }, [loadVariables]);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const saveVariables = useCallback((newVariables: Variable[]) => {
    try {
      const storageKey = `agentiqware_variables_${flowId}`;
      localStorage.setItem(storageKey, JSON.stringify(newVariables));
      setVariables(newVariables);
    } catch (error) {
      showNotification('error', t('errorSavingVariables'));
    }
  }, [flowId, showNotification, t]);

  // ============================================
  // Form Management
  // ============================================

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name?.trim()) {
      errors.name = t('nameIsRequired');
    } else if (formData.name && !validateVariableName(formData.name)) {
      errors.name = t('nameValidationMessage');
    } else if (formData.name && variables.some(v => v.name.toLowerCase() === formData.name!.toLowerCase() && v.id !== editingVariable?.id)) {
      errors.name = t('variableNameExists');
    }

    if (!formData.label?.trim()) {
      errors.label = t('labelIsRequired');
    }

    if (formData.defaultValue !== '' && formData.defaultValue !== null && formData.defaultValue !== undefined) {
      if (!validateVariableValue(formData.defaultValue, formData.type!)) {
        errors.defaultValue = formatMessage('invalidFormat', { type: formData.type! });
      }
    }

    if (formData.type === 'select' && (!formData.options || formData.options.length === 0)) {
      errors.options = t('selectRequiresOptions');
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const resetForm = () => {
    setFormData({
      name: '',
      type: 'string',
      label: '',
      description: '',
      defaultValue: '',
      required: false,
      category: 'Custom',
      options: []
    });
    setFormErrors({});
    setEditingVariable(null);
  };

  const handleSaveVariable = () => {
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      const now = new Date().toISOString();
      const variableData: Variable = {
        id: editingVariable?.id || Date.now().toString(),
        name: formData.name!,
        type: formData.type!,
        label: formData.label!,
        description: formData.description!,
        defaultValue: formData.defaultValue,
        required: formData.required!,
        category: formData.category!,
        options: formData.type === 'select' ? formData.options : undefined,
        createdAt: editingVariable?.createdAt || now,
        updatedAt: now
      };

      const newVariables = editingVariable
        ? variables.map(v => v.id === editingVariable.id ? variableData : v)
        : [...variables, variableData];

      saveVariables(newVariables);
      setShowForm(false);
      resetForm();
      showNotification('success', editingVariable ? t('variableUpdatedSuccessfully') : t('variableCreatedSuccessfully'));
    } catch (error) {
      showNotification('error', t('errorSavingVariables'));
    } finally {
      setLoading(false);
    }
  };

  const handleEditVariable = (variable: Variable) => {
    setEditingVariable(variable);
    setFormData({
      name: variable.name,
      type: variable.type,
      label: variable.label,
      description: variable.description,
      defaultValue: variable.defaultValue,
      required: variable.required,
      category: variable.category,
      options: variable.options || []
    });
    setShowForm(true);
  };

  const handleDeleteVariable = (id: string) => {
    try {
      const newVariables = variables.filter(v => v.id !== id);
      saveVariables(newVariables);
      setDeleteConfirmId(null);
      showNotification('success', t('variableDeletedSuccessfully'));
    } catch (error) {
      showNotification('error', t('errorSavingVariables'));
    }
  };

  // ============================================
  // Import/Export Functions
  // ============================================

  const handleExportVariables = () => {
    try {
      const dataStr = JSON.stringify(variables, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `agentiqware-variables-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
      showNotification('success', t('variablesExportedSuccessfully'));
    } catch (error) {
      showNotification('error', t('errorExportingVariables'));
    }
  };

  const handleImportVariables = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedVariables = JSON.parse(e.target?.result as string);
        if (Array.isArray(importedVariables)) {
          const validVariables = importedVariables.filter(v => 
            v.name && v.type && v.label && VARIABLE_TYPES.some(type => type.value === v.type)
          );
          
          if (validVariables.length > 0) {
            saveVariables(validVariables);
            showNotification('success', formatMessage('variablesImportedSuccessfully', { count: validVariables.length }));
          } else {
            showNotification('error', t('noValidVariablesFound'));
          }
        } else {
          showNotification('error', t('invalidFileFormat'));
        }
      } catch (error) {
        showNotification('error', t('errorImportingVariables'));
      }
    };
    reader.readAsText(file);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const togglePasswordVisibility = (variableId: string) => {
    setShowPassword(prev => ({
      ...prev,
      [variableId]: !prev[variableId]
    }));
  };

  const copyVariableSyntax = (name: string) => {
    navigator.clipboard.writeText(`{{${name}}}`);
    showNotification('success', t('copyVariableSyntax'));
  };

  const addSelectOption = () => {
    setFormData(prev => ({
      ...prev,
      options: [...(prev.options || []), '']
    }));
  };

  const updateSelectOption = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      options: prev.options?.map((opt, i) => i === index ? value : opt) || []
    }));
  };

  const removeSelectOption = (index: number) => {
    setFormData(prev => ({
      ...prev,
      options: prev.options?.filter((_, i) => i !== index) || []
    }));
  };

  // ============================================
  // Filtered Variables
  // ============================================

  const filteredVariables = variables.filter(variable => {
    const matchesSearch = variable.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         variable.label.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || variable.category === filterCategory;
    const matchesType = filterType === 'all' || variable.type === filterType;
    
    return matchesSearch && matchesCategory && matchesType;
  });

  // ============================================
  // Render Functions
  // ============================================

  const renderVariableValue = (variable: Variable) => {
    if (variable.type === 'password') {
      return (
        <div className="flex items-center space-x-2">
          <span className="font-mono text-sm">
            {showPassword[variable.id] ? variable.defaultValue || t('empty') : '••••••••'}
          </span>
          <button
            onClick={() => togglePasswordVisibility(variable.id)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            {showPassword[variable.id] ? <EyeOff size={14} /> : <Eye size={14} />}
          </button>
        </div>
      );
    }

    if (variable.type === 'boolean') {
      return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          variable.defaultValue ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {variable.defaultValue ? 'true' : 'false'}
        </span>
      );
    }

    return (
      <span className="font-mono text-sm text-gray-700">
        {variable.defaultValue || t('empty')}
      </span>
    );
  };

  const renderFormInput = () => {
    const type = formData.type!;
    
    switch (type) {
      case 'boolean':
        return (
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={!!formData.defaultValue}
              onChange={(e) => setFormData(prev => ({ ...prev, defaultValue: e.target.checked }))}
              className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">{t('value')}</span>
          </label>
        );
      
      case 'select':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('options')}
              </label>
              {formData.options?.map((option, index) => (
                <div key={index} className="flex items-center space-x-2 mb-2">
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => updateSelectOption(index, e.target.value)}
                    placeholder={formatMessage('optionPlaceholder', { index: index + 1 })}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button
                    type="button"
                    onClick={() => removeSelectOption(index)}
                    className="text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                  >
                    <X size={16} />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={addSelectOption}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm flex items-center space-x-1"
              >
                <Plus size={14} />
                <span>{t('addOption')}</span>
              </button>
              {formErrors.options && (
                <p className="text-red-500 dark:text-red-400 text-xs mt-1">{formErrors.options}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Default Value
              </label>
              <select
                value={formData.defaultValue || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, defaultValue: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option value="">{t('selectDefaultValue')}</option>
                {formData.options?.filter(opt => opt.trim()).map((option, index) => (
                  <option key={index} value={option}>{option}</option>
                ))}
              </select>
            </div>
          </div>
        );
      
      case 'password':
        return (
          <div className="relative">
            <input
              type={showPassword.form ? 'text' : 'password'}
              value={formData.defaultValue || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, defaultValue: e.target.value }))}
              placeholder={t('enterPassword')}
              className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
            <button
              type="button"
              onClick={() => togglePasswordVisibility('form')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
            >
              {showPassword.form ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        );
      
      case 'date':
        return (
          <input
            type="date"
            value={formData.defaultValue || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, defaultValue: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        );
      
      case 'number':
        return (
          <input
            type="number"
            value={formData.defaultValue || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, defaultValue: e.target.value }))}
            placeholder={t('enterNumber')}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
          />
        );
      
      default:
        return (
          <input
            type={type === 'email' ? 'email' : type === 'url' ? 'url' : 'text'}
            value={formData.defaultValue || ''}
            onChange={(e) => setFormData(prev => ({ ...prev, defaultValue: e.target.value }))}
            placeholder={formatMessage('enterType', { type })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
          />
        );
    }
  };

  // ============================================
  // Main Render
  // ============================================

  return (
    <div className="max-w-7xl mx-auto p-6 bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
                <Database className="mr-3 text-blue-600 dark:text-blue-400" size={28} />
                {t('flowVariables')}
                {onClose && (
                  <button
                    onClick={onClose}
                    className="ml-4 p-1 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
                    title={t('closeVariablesPanel')}
                  >
                    <X size={24} />
                  </button>
                )}
              </h1>
            </div>
            <p className="text-gray-600 dark:text-gray-300 mt-1">
              {t('variablesFor')} {flowName ? `"${flowName}"` : t('currentFlow')} • {t('syntax')}: {'{'}{'{'} variable_name {'}'}{'}'}
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {t('flowId')}: {flowId}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleExportVariables}
              className="flex items-center space-x-2 px-3 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              disabled={variables.length === 0}
            >
              <Download size={16} />
              <span>{t('export')}</span>
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center space-x-2 px-3 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <Upload size={16} />
              <span>{t('import')}</span>
            </button>
            <button
              onClick={() => {
                resetForm();
                setShowForm(true);
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-md transition-colors"
            >
              <Plus size={16} />
              <span>{t('createVariable')}</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 dark:text-blue-400 text-sm font-medium">{t('totalVariables')}</p>
                <p className="text-2xl font-bold text-blue-800 dark:text-blue-300">{variables.length}</p>
              </div>
              <Database className="text-blue-600 dark:text-blue-400" size={24} />
            </div>
          </div>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 dark:text-green-400 text-sm font-medium">{t('required')}</p>
                <p className="text-2xl font-bold text-green-800 dark:text-green-300">
                  {variables.filter(v => v.required).length}
                </p>
              </div>
              <AlertCircle className="text-green-600 dark:text-green-400" size={24} />
            </div>
          </div>
          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 dark:text-purple-400 text-sm font-medium">{t('categories')}</p>
                <p className="text-2xl font-bold text-purple-800 dark:text-purple-300">
                  {new Set(variables.map(v => v.category)).size}
                </p>
              </div>
              <Package className="text-purple-600 dark:text-purple-400" size={24} />
            </div>
          </div>
          <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 dark:text-orange-400 text-sm font-medium">{t('types')}</p>
                <p className="text-2xl font-bold text-orange-800 dark:text-orange-300">
                  {new Set(variables.map(v => v.type)).size}
                </p>
              </div>
              <Type className="text-orange-600 dark:text-orange-400" size={24} />
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500" size={16} />
            <input
              type="text"
              placeholder={t('searchVariables')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
            />
          </div>
          
          <div className="flex items-center space-x-3">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="all">{t('allCategories')}</option>
              {VARIABLE_CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
            
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="all">{t('allTypes')}</option>
              {VARIABLE_TYPES.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Variables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-6">
        {filteredVariables.map(variable => (
          <div
            key={variable.id}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:shadow-md dark:hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">{variable.label}</h3>
                  {variable.required && (
                    <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 text-xs font-medium rounded">
                      {t('required')}
                    </span>
                  )}
                </div>
                <div className="flex items-center space-x-2 mb-2">
                  <code className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm font-mono rounded">
                    {`{{${variable.name}}}`}
                  </code>
                  <button
                    onClick={() => copyVariableSyntax(variable.name)}
                    className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
                    title={t('copySyntax')}
                  >
                    <Copy size={14} />
                  </button>
                </div>
                <p className="text-gray-600 dark:text-gray-300 text-sm mb-3">{variable.description}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500 dark:text-gray-400">{t('type')}:</span>
                <div className="flex items-center space-x-1 text-gray-700 dark:text-gray-300">
                  {VARIABLE_TYPES.find(t => t.value === variable.type)?.icon}
                  <span className="text-sm font-medium capitalize">{variable.type}</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500 dark:text-gray-400">{t('category')}:</span>
                <div className="flex items-center space-x-1 text-gray-700 dark:text-gray-300">
                  {VARIABLE_CATEGORIES.find(c => c.value === variable.category)?.icon}
                  <span className="text-sm font-medium">{variable.category}</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500 dark:text-gray-400">{t('value')}:</span>
                {renderVariableValue(variable)}
              </div>
            </div>

            <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {t('updated')} {new Date(variable.updatedAt).toLocaleDateString()}
              </span>
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => handleEditVariable(variable)}
                  className="p-2 text-gray-400 hover:text-blue-600 dark:text-gray-500 dark:hover:text-blue-400 transition-colors"
                  title={t('editVariableTooltip')}
                >
                  <Edit3 size={16} />
                </button>
                <button
                  onClick={() => setDeleteConfirmId(variable.id)}
                  className="p-2 text-gray-400 hover:text-red-600 dark:text-gray-500 dark:hover:text-red-400 transition-colors"
                  title={t('deleteVariableTooltip')}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredVariables.length === 0 && (
        <div className="text-center py-12">
          <Database size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{t('noVariablesFound')}</h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            {searchTerm || filterCategory !== 'all' || filterType !== 'all' 
              ? t('tryAdjustingFilters')
              : t('createFirstVariable')}
          </p>
          {!searchTerm && filterCategory === 'all' && filterType === 'all' && (
            <button
              onClick={() => {
                resetForm();
                setShowForm(true);
              }}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-md transition-colors"
            >
              <Plus size={16} />
              <span>{t('createVariable')}</span>
            </button>
          )}
        </div>
      )}

      {/* Variable Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {editingVariable ? t('editVariable') : t('createNewVariable')}
                </h2>
                <button
                  onClick={() => {
                    setShowForm(false);
                    resetForm();
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 transition-colors"
                >
                  <X size={24} />
                </button>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); handleSaveVariable(); }} className="space-y-6">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('variableName')} *
                    </label>
                    <input
                      type="text"
                      value={formData.name || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                      placeholder={t('variableNamePlaceholder')}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                    />
                    {formErrors.name && (
                      <p className="text-red-500 dark:text-red-400 text-xs mt-1">{formErrors.name}</p>
                    )}
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {t('useSnakeCaseFormat')}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('displayLabel')} *
                    </label>
                    <input
                      type="text"
                      value={formData.label || ''}
                      onChange={(e) => setFormData(prev => ({ ...prev, label: e.target.value }))}
                      placeholder={t('displayLabelPlaceholder')}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                    />
                    {formErrors.label && (
                      <p className="text-red-500 dark:text-red-400 text-xs mt-1">{formErrors.label}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('description')}
                  </label>
                  <textarea
                    value={formData.description || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder={t('descriptionPlaceholder')}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                  />
                </div>

                {/* Type and Category */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('type')} *
                    </label>
                    <select
                      value={formData.type || 'string'}
                      onChange={(e) => setFormData(prev => ({ 
                        ...prev, 
                        type: e.target.value as VariableType,
                        defaultValue: e.target.value === 'boolean' ? false : '',
                        options: e.target.value === 'select' ? [''] : undefined
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      {VARIABLE_TYPES.map(type => (
                        <option key={type.value} value={type.value}>{type.label}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('category')} *
                    </label>
                    <select
                      value={formData.category || 'Custom'}
                      onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as VariableCategory }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    >
                      {VARIABLE_CATEGORIES.map(cat => (
                        <option key={cat.value} value={cat.value}>{cat.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Default Value */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('defaultValue')}
                  </label>
                  {renderFormInput()}
                  {formErrors.defaultValue && (
                    <p className="text-red-500 dark:text-red-400 text-xs mt-1">{formErrors.defaultValue}</p>
                  )}
                </div>

                {/* Required Checkbox */}
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="required"
                    checked={formData.required || false}
                    onChange={(e) => setFormData(prev => ({ ...prev, required: e.target.checked }))}
                    className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-400 bg-white dark:bg-gray-700"
                  />
                  <label htmlFor="required" className="text-sm text-gray-700 dark:text-gray-300">
                    {t('thisVariableIsRequired')}
                  </label>
                </div>

                {/* Preview */}
                {formData.name && (
                  <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-md">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t('preview')}</h4>
                    <div className="font-mono text-sm text-blue-600 dark:text-blue-400">
                      {`{{${formData.name}}}`}
                    </div>
                  </div>
                )}

                {/* Form Actions */}
                <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      resetForm();
                    }}
                    className="px-4 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    {t('cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>{t('saving')}</span>
                      </>
                    ) : (
                      <>
                        <Save size={16} />
                        <span>{editingVariable ? t('update') : t('create')} Variable</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center space-x-3 mb-4">
                <div className="flex-shrink-0">
                  <AlertCircle className="text-red-600 dark:text-red-400" size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">{t('deleteConfirmationTitle')}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t('deleteConfirmationMessage')}
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => setDeleteConfirmId(null)}
                  className="px-4 py-2 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  {t('cancel')}
                </button>
                <button
                  onClick={() => handleDeleteVariable(deleteConfirmId)}
                  className="px-4 py-2 bg-red-600 dark:bg-red-500 text-white rounded-md hover:bg-red-700 dark:hover:bg-red-600 transition-colors"
                >
                  {t('delete')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notification Toast */}
      {notification && (
        <div className="fixed bottom-4 right-4 z-50 animate-fade-in">
          <div className={`px-4 py-3 rounded-md shadow-lg flex items-center space-x-2 ${
            notification.type === 'success' 
              ? 'bg-green-600 dark:bg-green-500 text-white' 
              : 'bg-red-600 dark:bg-red-500 text-white'
          }`}>
            {notification.type === 'success' ? (
              <Check size={16} />
            ) : (
              <AlertCircle size={16} />
            )}
            <span>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              className="ml-2 text-white hover:text-gray-200"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleImportVariables}
        className="hidden"
      />

      {/* Custom Styles */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default VariablesManager;