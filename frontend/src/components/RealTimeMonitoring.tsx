import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, AlertTriangle, Server, Cpu, HardDrive, Wifi, RefreshCw, Filter, Calendar, Download, Bell, Settings } from 'lucide-react';

// Componente de Monitoreo en Tiempo Real
const RealTimeMonitoring = () => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [activeMetric, setActiveMetric] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [notifications, setNotifications] = useState<any[]>([]);
  
  // WebSocket para datos en tiempo real
  const wsRef = useRef(null);

  // Datos simulados para las métricas
  const [metrics, setMetrics] = useState({
    executionsPerMinute: [] as any[],
    successRate: [] as any[],
    averageExecutionTime: [] as any[],
    activeFlows: [] as any[],
    systemResources: {
      cpu: 45,
      memory: 62,
      storage: 38,
      network: 72
    },
    recentErrors: [] as any[],
    flowPerformance: [] as any[]
  });

  // Conectar WebSocket para actualizaciones en tiempo real
  useEffect(() => {
    // Simular WebSocket connection
    const connectWebSocket = () => {
      // En producción, esto sería: wsRef.current = new WebSocket('wss://api.agentiqware.com/monitoring');
      console.log('Connecting to monitoring WebSocket...');
      
      // Simular actualizaciones de datos
      if (autoRefresh) {
        const interval = setInterval(() => {
          updateMetrics();
        }, refreshInterval);
        
        return () => clearInterval(interval);
      }
    };

    connectWebSocket();
  }, [autoRefresh, refreshInterval]);

  // Actualizar métricas (simulado)
  const updateMetrics = () => {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString();
    
    setMetrics((prev: any) => ({
      executionsPerMinute: [
        ...prev.executionsPerMinute.slice(-29),
        {
          time: timeLabel,
          value: Math.floor(Math.random() * 50) + 30,
          timestamp: now.getTime()
        }
      ],
      successRate: [
        ...prev.successRate.slice(-29),
        {
          time: timeLabel,
          rate: Math.random() * 5 + 95,
          timestamp: now.getTime()
        }
      ],
      averageExecutionTime: [
        ...prev.averageExecutionTime.slice(-29),
        {
          time: timeLabel,
          duration: Math.random() * 2000 + 500,
          timestamp: now.getTime()
        }
      ],
      activeFlows: [
        ...prev.activeFlows.slice(-29),
        {
          time: timeLabel,
          count: Math.floor(Math.random() * 10) + 5,
          timestamp: now.getTime()
        }
      ],
      systemResources: {
        cpu: Math.min(100, Math.max(0, prev.systemResources.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.min(100, Math.max(0, prev.systemResources.memory + (Math.random() - 0.5) * 5)),
        storage: Math.min(100, Math.max(0, prev.systemResources.storage + (Math.random() - 0.5) * 2)),
        network: Math.min(100, Math.max(0, prev.systemResources.network + (Math.random() - 0.5) * 15))
      },
      recentErrors: prev.recentErrors,
      flowPerformance: prev.flowPerformance
    }));

    // Simular notificaciones ocasionales
    if (Math.random() > 0.9) {
      addNotification({
        type: Math.random() > 0.5 ? 'warning' : 'error',
        message: Math.random() > 0.5 ? 'High CPU usage detected' : 'Flow execution failed',
        timestamp: now
      });
    }
  };

  // Agregar notificación
  const addNotification = (notification: any) => {
    setNotifications(prev => [
      { ...notification, id: Date.now() },
      ...prev.slice(0, 4)
    ]);
  };

  // Datos para el gráfico de distribución de errores
  const errorDistribution = [
    { name: 'Timeout', value: 30, color: '#EF4444' },
    { name: 'Connection', value: 25, color: '#F59E0B' },
    { name: 'Validation', value: 20, color: '#10B981' },
    { name: 'Permission', value: 15, color: '#3B82F6' },
    { name: 'Other', value: 10, color: '#8B5CF6' }
  ];

  // Datos de rendimiento por flujo
  const flowPerformanceData = [
    { name: 'Invoice Processing', executions: 245, avgTime: 1.2, successRate: 98.5 },
    { name: 'Data Migration', executions: 189, avgTime: 3.5, successRate: 96.2 },
    { name: 'Report Generation', executions: 156, avgTime: 2.1, successRate: 99.1 },
    { name: 'Email Automation', executions: 134, avgTime: 0.8, successRate: 97.8 },
    { name: 'File Sync', executions: 98, avgTime: 1.5, successRate: 95.5 }
  ];

  // Métricas clave
  const keyMetrics = [
    {
      label: 'Total Executions',
      value: '12,847',
      change: '+12.5%',
      trend: 'up',
      icon: Activity,
      color: 'blue'
    },
    {
      label: 'Success Rate',
      value: '97.8%',
      change: '+2.3%',
      trend: 'up',
      icon: CheckCircle,
      color: 'green'
    },
    {
      label: 'Avg. Duration',
      value: '1.8s',
      change: '-0.3s',
      trend: 'down',
      icon: Clock,
      color: 'purple'
    },
    {
      label: 'Active Flows',
      value: '47',
      change: '+5',
      trend: 'up',
      icon: TrendingUp,
      color: 'indigo'
    }
  ];

  // Componente de métrica clave
  const KeyMetricCard = ({ metric }: { metric: any }) => {
    const colorClasses: any = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600',
      indigo: 'bg-indigo-100 text-indigo-600'
    };

    return (
      <div className="bg-white rounded-lg p-6 shadow-sm border hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{metric.label}</p>
            <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
            <div className="flex items-center mt-2">
              {metric.trend === 'up' ? (
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-green-500 mr-1" />
              )}
              <span className="text-sm text-green-600">{metric.change}</span>
            </div>
          </div>
          <div className={`p-3 rounded-lg ${colorClasses[metric.color]}`}>
            <metric.icon className="w-6 h-6" />
          </div>
        </div>
      </div>
    );
  };

  // Componente de recursos del sistema
  const SystemResourceCard = ({ label, value, icon: Icon, color }: { label: any, value: any, icon: any, color: any }) => {
    const getColorClass = (value: number) => {
      if (value < 50) return 'text-green-500';
      if (value < 75) return 'text-yellow-500';
      return 'text-red-500';
    };

    return (
      <div className="bg-white rounded-lg p-4 shadow-sm border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-600">{label}</span>
          <Icon className="w-4 h-4 text-gray-400" />
        </div>
        <div className="flex items-end justify-between">
          <span className={`text-2xl font-bold ${getColorClass(value)}`}>
            {value.toFixed(1)}%
          </span>
          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all ${
                value < 50 ? 'bg-green-500' : value < 75 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${value}%` }}
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Real-Time Monitoring</h1>
            <p className="text-gray-600 mt-1">Monitor your flows and system performance</p>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Time Range Selector */}
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-white focus:ring-2 focus:ring-blue-500"
            >
              <option value="5m">Last 5 minutes</option>
              <option value="15m">Last 15 minutes</option>
              <option value="1h">Last hour</option>
              <option value="6h">Last 6 hours</option>
              <option value="24h">Last 24 hours</option>
            </select>

            {/* Auto Refresh Toggle */}
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                autoRefresh 
                  ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
              {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
            </button>

            {/* Export Button */}
            <button className="flex items-center gap-2 px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 transition">
              <Download className="w-4 h-4" />
              Export
            </button>

            {/* Settings */}
            <button className="p-2 bg-white border rounded-lg hover:bg-gray-50 transition">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="mb-6 space-y-2">
          {notifications.map((notification: any) => (
            <div
              key={notification.id}
              className={`flex items-center gap-3 p-3 rounded-lg border ${
                notification.type === 'error' 
                  ? 'bg-red-50 border-red-200' 
                  : 'bg-yellow-50 border-yellow-200'
              }`}
            >
              {notification.type === 'error' ? (
                <XCircle className="w-5 h-5 text-red-500" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
              )}
              <span className="flex-1 text-sm font-medium">
                {notification.message}
              </span>
              <span className="text-xs text-gray-500">
                {notification.timestamp.toLocaleTimeString()}
              </span>
              <button
                onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {keyMetrics.map((metric, index) => (
          <KeyMetricCard key={index} metric={metric} />
        ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Executions Over Time */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Executions Over Time</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={metrics.executionsPerMinute}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#3B82F6" 
                fill="#93BBFC" 
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Success Rate */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Success Rate</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={metrics.successRate}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                domain={[90, 100]}
              />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="rate" 
                stroke="#10B981" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Error Distribution */}
        <div className="bg-white rounded-lg p-6 shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Error Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={errorDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {errorDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Flow Performance */}
        <div className="bg-white rounded-lg p-6 shadow-sm border col-span-2">
          <h3 className="text-lg font-semibold mb-4">Top Performing Flows</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={flowPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="name" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="executions" fill="#3B82F6" name="Executions" />
              <Bar dataKey="successRate" fill="#10B981" name="Success %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* System Resources */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
        <SystemResourceCard
          label="CPU Usage"
          value={metrics.systemResources.cpu}
          icon={Cpu}
          color="blue"
        />
        <SystemResourceCard
          label="Memory"
          value={metrics.systemResources.memory}
          icon={Server}
          color="green"
        />
        <SystemResourceCard
          label="Storage"
          value={metrics.systemResources.storage}
          icon={HardDrive}
          color="purple"
        />
        <SystemResourceCard
          label="Network I/O"
          value={metrics.systemResources.network}
          icon={Wifi}
          color="indigo"
        />
      </div>

      {/* Flow Performance Table */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Flow Performance Details</h3>
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 rounded-lg hover:bg-gray-200 transition">
              <Filter className="w-4 h-4" />
              Filter
            </button>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Flow Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Executions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg. Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Run
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {flowPerformanceData.map((flow, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{flow.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      Active
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {flow.executions}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {flow.avgTime}s
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-gray-900">{flow.successRate}%</span>
                      <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${flow.successRate}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    2 min ago
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RealTimeMonitoring;