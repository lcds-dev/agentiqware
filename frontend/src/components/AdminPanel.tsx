import React, { useState, useEffect } from 'react';
import { Users, Shield, CreditCard, Activity, Settings, Database, AlertTriangle, Ban, Check, X, Edit, Trash2, Search, Filter, Download, Upload, Mail, Phone, Calendar, Globe, DollarSign, TrendingUp, UserCheck, UserX, Key, Lock, Unlock, RefreshCw, BarChart3, PieChart, Info, ChevronDown, ChevronRight } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart as RePieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Admin Panel Component
const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [users, setUsers] = useState<any[]>([]);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [filters, setFilters] = useState({
    status: 'all',
    subscription: 'all',
    searchQuery: ''
  });
  const [stats, setStats] = useState({
    totalUsers: 1284,
    activeUsers: 892,
    paidUsers: 234,
    revenue: 28450,
    growth: 12.5
  });

  // Simulated user data
  useEffect(() => {
    const mockUsers = [
      {
        id: 'usr_001',
        name: 'John Doe',
        email: 'john.doe@company.com',
        phone: '+1 555-0123',
        company: 'Acme Corp',
        role: 'admin',
        subscription: 'enterprise',
        status: 'active',
        createdAt: '2024-01-15',
        lastLogin: '2024-01-20 14:30',
        flowsCreated: 45,
        executionsTotal: 1250,
        storageUsed: 2.3,
        apiCalls: 15420,
        billing: {
          plan: 'Enterprise',
          amount: 299,
          nextBilling: '2024-02-15',
          paymentMethod: 'Visa ****1234'
        }
      },
      {
        id: 'usr_002',
        name: 'Jane Smith',
        email: 'jane.smith@startup.io',
        phone: '+1 555-0124',
        company: 'StartupCo',
        role: 'user',
        subscription: 'professional',
        status: 'active',
        createdAt: '2024-01-10',
        lastLogin: '2024-01-20 09:15',
        flowsCreated: 12,
        executionsTotal: 450,
        storageUsed: 0.8,
        apiCalls: 5200,
        billing: {
          plan: 'Professional',
          amount: 99,
          nextBilling: '2024-02-10',
          paymentMethod: 'PayPal'
        }
      },
      {
        id: 'usr_003',
        name: 'Carlos García',
        email: 'carlos@empresa.mx',
        phone: '+52 555-0125',
        company: 'Empresa MX',
        role: 'user',
        subscription: 'starter',
        status: 'active',
        createdAt: '2024-01-05',
        lastLogin: '2024-01-19 16:45',
        flowsCreated: 8,
        executionsTotal: 220,
        storageUsed: 0.4,
        apiCalls: 2100,
        billing: {
          plan: 'Starter',
          amount: 29,
          nextBilling: '2024-02-05',
          paymentMethod: 'MasterCard ****5678'
        }
      },
      {
        id: 'usr_004',
        name: 'Maria Rodriguez',
        email: 'maria@freelance.com',
        phone: '+34 555-0126',
        company: 'Freelance',
        role: 'user',
        subscription: 'free',
        status: 'active',
        createdAt: '2023-12-20',
        lastLogin: '2024-01-18 11:20',
        flowsCreated: 3,
        executionsTotal: 45,
        storageUsed: 0.1,
        apiCalls: 450,
        billing: null
      },
      {
        id: 'usr_005',
        name: 'Robert Johnson',
        email: 'robert@blocked.com',
        phone: '+1 555-0127',
        company: 'Unknown',
        role: 'user',
        subscription: 'free',
        status: 'suspended',
        suspendedReason: 'Terms of service violation',
        createdAt: '2023-11-15',
        lastLogin: '2024-01-10 08:00',
        flowsCreated: 0,
        executionsTotal: 0,
        storageUsed: 0,
        apiCalls: 0,
        billing: null
      }
    ];
    setUsers(mockUsers);
  }, []);

  // Filter users based on criteria
  const filteredUsers = users.filter(user => {
    if (filters.status !== 'all' && user.status !== filters.status) return false;
    if (filters.subscription !== 'all' && user.subscription !== filters.subscription) return false;
    if (filters.searchQuery && !user.name.toLowerCase().includes(filters.searchQuery.toLowerCase()) &&
        !user.email.toLowerCase().includes(filters.searchQuery.toLowerCase())) return false;
    return true;
  });

  // User growth data for chart
  const growthData = [
    { month: 'Jan', users: 850, revenue: 22000 },
    { month: 'Feb', users: 920, revenue: 23500 },
    { month: 'Mar', users: 980, revenue: 24200 },
    { month: 'Apr', users: 1050, revenue: 25100 },
    { month: 'May', users: 1120, revenue: 26300 },
    { month: 'Jun', users: 1200, revenue: 27500 },
    { month: 'Jul', users: 1284, revenue: 28450 }
  ];

  // Subscription distribution
  const subscriptionData = [
    { name: 'Free', value: 650, color: '#6B7280' },
    { name: 'Starter', value: 400, color: '#3B82F6' },
    { name: 'Professional', value: 180, color: '#8B5CF6' },
    { name: 'Enterprise', value: 54, color: '#10B981' }
  ];

  // Overview Tab
  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Total Users</span>
            <Users className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold">{stats.totalUsers.toLocaleString()}</div>
          <div className="text-xs text-green-600 mt-1">+{stats.growth}% this month</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Active Users</span>
            <UserCheck className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold">{stats.activeUsers.toLocaleString()}</div>
          <div className="text-xs text-gray-500 mt-1">69.4% of total</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Paid Users</span>
            <CreditCard className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold">{stats.paidUsers}</div>
          <div className="text-xs text-green-600 mt-1">+18 this month</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">MRR</span>
            <DollarSign className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold">${stats.revenue.toLocaleString()}</div>
          <div className="text-xs text-green-600 mt-1">+8.2% growth</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Churn Rate</span>
            <TrendingUp className="w-5 h-5 text-red-500" />
          </div>
          <div className="text-2xl font-bold">2.3%</div>
          <div className="text-xs text-green-600 mt-1">-0.5% improved</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">User Growth & Revenue</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={growthData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="users" stroke="#3B82F6" name="Users" strokeWidth={2} />
              <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#10B981" name="Revenue ($)" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold mb-4">Subscription Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RePieChart>
              <Pie
                data={subscriptionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {subscriptionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RePieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold">Recent Activity</h3>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">New user registration: john.doe@company.com</span>
            <span className="text-xs text-gray-400 ml-auto">2 minutes ago</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Subscription upgraded: jane@startup.io (Pro → Enterprise)</span>
            <span className="text-xs text-gray-400 ml-auto">15 minutes ago</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span className="text-sm text-gray-600">API rate limit warning: user_0234</span>
            <span className="text-xs text-gray-400 ml-auto">1 hour ago</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Account suspended: robert@blocked.com (ToS violation)</span>
            <span className="text-xs text-gray-400 ml-auto">3 hours ago</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Users Management Tab
  const UsersTab = () => (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search users..."
                className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                value={filters.searchQuery}
                onChange={(e) => setFilters({ ...filters, searchQuery: e.target.value })}
              />
            </div>
          </div>
          
          <select
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="suspended">Suspended</option>
          </select>
          
          <select
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            value={filters.subscription}
            onChange={(e) => setFilters({ ...filters, subscription: e.target.value })}
          >
            <option value="all">All Plans</option>
            <option value="free">Free</option>
            <option value="starter">Starter</option>
            <option value="professional">Professional</option>
            <option value="enterprise">Enterprise</option>
          </select>
          
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            <Filter className="w-4 h-4 inline mr-2" />
            Apply Filters
          </button>
          
          <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
            <Download className="w-4 h-4 inline mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Subscription
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{user.name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{user.company}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      user.subscription === 'enterprise' ? 'bg-green-100 text-green-800' :
                      user.subscription === 'professional' ? 'bg-purple-100 text-purple-800' :
                      user.subscription === 'starter' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.subscription}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      user.status === 'active' ? 'bg-green-100 text-green-800' :
                      user.status === 'suspended' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {user.flowsCreated} flows
                      <br />
                      <span className="text-xs text-gray-500">{user.executionsTotal} executions</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.lastLogin}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex gap-2">
                      <button
                        onClick={() => setSelectedUser(user)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Info className="w-4 h-4" />
                      </button>
                      <button className="text-gray-600 hover:text-gray-900">
                        <Edit className="w-4 h-4" />
                      </button>
                      {user.status === 'active' ? (
                        <button className="text-yellow-600 hover:text-yellow-900">
                          <Lock className="w-4 h-4" />
                        </button>
                      ) : (
                        <button className="text-green-600 hover:text-green-900">
                          <Unlock className="w-4 h-4" />
                        </button>
                      )}
                      <button className="text-red-600 hover:text-red-900">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // User Detail Modal
  const UserDetailModal = ({ user, onClose }: { user: any, onClose: () => void }) => {
    if (!user) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold">{user.name}</h2>
              <p className="text-gray-600">{user.email}</p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* User Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">User Information</h3>
              <div className="space-y-2">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">ID</span>
                  <span className="font-medium">{user.id}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Company</span>
                  <span className="font-medium">{user.company}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Phone</span>
                  <span className="font-medium">{user.phone}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Role</span>
                  <span className="font-medium capitalize">{user.role}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Created</span>
                  <span className="font-medium">{user.createdAt}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Status</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    user.status === 'active' ? 'bg-green-100 text-green-800' :
                    user.status === 'suspended' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {user.status}
                  </span>
                </div>
                {user.suspendedReason && (
                  <div className="mt-2 p-3 bg-red-50 rounded-lg">
                    <p className="text-sm text-red-800">
                      <strong>Suspension Reason:</strong> {user.suspendedReason}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Usage Statistics */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Usage Statistics</h3>
              <div className="space-y-2">
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Flows Created</span>
                  <span className="font-medium">{user.flowsCreated}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Total Executions</span>
                  <span className="font-medium">{user.executionsTotal}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Storage Used</span>
                  <span className="font-medium">{user.storageUsed} GB</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">API Calls</span>
                  <span className="font-medium">{user.apiCalls.toLocaleString()}</span>
                </div>
                <div className="flex justify-between py-2 border-b">
                  <span className="text-gray-600">Last Login</span>
                  <span className="font-medium">{user.lastLogin}</span>
                </div>
              </div>
            </div>

            {/* Billing Information */}
            {user.billing && (
              <div className="space-y-4 md:col-span-2">
                <h3 className="text-lg font-semibold">Billing Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Plan</span>
                    <span className="font-medium">{user.billing.plan}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Amount</span>
                    <span className="font-medium">${user.billing.amount}/month</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Next Billing</span>
                    <span className="font-medium">{user.billing.nextBilling}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Payment Method</span>
                    <span className="font-medium">{user.billing.paymentMethod}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-6 pt-6 border-t">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              <Mail className="w-4 h-4 inline mr-2" />
              Send Email
            </button>
            <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
              <Key className="w-4 h-4 inline mr-2" />
              Reset Password
            </button>
            {user.status === 'active' ? (
              <button className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition">
                <Lock className="w-4 h-4 inline mr-2" />
                Suspend Account
              </button>
            ) : (
              <button className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition">
                <Unlock className="w-4 h-4 inline mr-2" />
                Activate Account
              </button>
            )}
            <button className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition ml-auto">
              <Trash2 className="w-4 h-4 inline mr-2" />
              Delete Account
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Billing Tab
  const BillingTab = () => (
    <div className="space-y-6">
      {/* Revenue Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">MRR</span>
            <DollarSign className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold">$28,450</div>
          <div className="text-xs text-green-600 mt-1">+8.2% vs last month</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">ARR</span>
            <TrendingUp className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold">$341,400</div>
          <div className="text-xs text-green-600 mt-1">Projected</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">ARPU</span>
            <BarChart3 className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold">$121.58</div>
          <div className="text-xs text-gray-500 mt-1">Avg per user</div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">LTV</span>
            <Activity className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="text-2xl font-bold">$1,458</div>
          <div className="text-xs text-gray-500 mt-1">Customer lifetime value</div>
        </div>
      </div>

      {/* Subscription Plans Performance */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Subscription Plans Performance</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Users</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MRR</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Churn</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Growth</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 font-medium">Free</td>
                <td className="px-6 py-4">650</td>
                <td className="px-6 py-4">$0</td>
                <td className="px-6 py-4">$0</td>
                <td className="px-6 py-4">5.2%</td>
                <td className="px-6 py-4 text-green-600">+45</td>
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium">Starter</td>
                <td className="px-6 py-4">400</td>
                <td className="px-6 py-4">$29</td>
                <td className="px-6 py-4">$11,600</td>
                <td className="px-6 py-4">2.8%</td>
                <td className="px-6 py-4 text-green-600">+12</td>
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium">Professional</td>
                <td className="px-6 py-4">180</td>
                <td className="px-6 py-4">$99</td>
                <td className="px-6 py-4">$17,820</td>
                <td className="px-6 py-4">1.5%</td>
                <td className="px-6 py-4 text-green-600">+8</td>
              </tr>
              <tr>
                <td className="px-6 py-4 font-medium">Enterprise</td>
                <td className="px-6 py-4">54</td>
                <td className="px-6 py-4">$299</td>
                <td className="px-6 py-4">$16,146</td>
                <td className="px-6 py-4">0.8%</td>
                <td className="px-6 py-4 text-green-600">+3</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Payment Methods */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">Payment Methods</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Credit Card</span>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '65%' }}></div>
                </div>
                <span className="text-sm font-medium">65%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">PayPal</span>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '25%' }}></div>
                </div>
                <span className="text-sm font-medium">25%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Bank Transfer</span>
              <div className="flex items-center gap-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '10%' }}></div>
                </div>
                <span className="text-sm font-medium">10%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">Failed Payments</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <div>
                <p className="font-medium text-sm">john.doe@company.com</p>
                <p className="text-xs text-gray-600">Card declined</p>
              </div>
              <button className="text-red-600 hover:text-red-800">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <div>
                <p className="font-medium text-sm">jane@startup.io</p>
                <p className="text-xs text-gray-600">Insufficient funds</p>
              </div>
              <button className="text-red-600 hover:text-red-800">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
        <p className="text-gray-600 mt-1">Manage users, billing, and system settings</p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm border mb-6">
        <div className="flex overflow-x-auto">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-6 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition ${
              activeTab === 'overview'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Activity className="w-4 h-4 inline mr-2" />
            Overview
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition ${
              activeTab === 'users'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            Users
          </button>
          <button
            onClick={() => setActiveTab('billing')}
            className={`px-6 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition ${
              activeTab === 'billing'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <CreditCard className="w-4 h-4 inline mr-2" />
            Billing
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`px-6 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition ${
              activeTab === 'security'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Shield className="w-4 h-4 inline mr-2" />
            Security
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={`px-6 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition ${
              activeTab === 'system'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Settings className="w-4 h-4 inline mr-2" />
            System
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab />}
      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'billing' && <BillingTab />}

      {/* User Detail Modal */}
      {selectedUser && (
        <UserDetailModal user={selectedUser} onClose={() => setSelectedUser(null)} />
      )}
    </div>
  );
};

export default AdminPanel;