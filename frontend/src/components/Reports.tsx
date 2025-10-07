import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  Download,
  Calendar,
  Filter,
  Search,
  Plus,
  Eye,
  Share2,
  Clock,
  AlertTriangle,
  Shield,
  TrendingUp,
  BarChart3,
  PieChart,
  Users,
  Database,
  Zap,
  CheckCircle,
  XCircle,
  RefreshCw,
  Settings,
  Archive,
  Trash2,
  Edit3
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart as RechartsPieChart, Cell, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface Report {
  id: string;
  title: string;
  description: string;
  type: 'security_summary' | 'incident_analysis' | 'compliance_audit' | 'threat_intelligence' | 'performance_metrics';
  status: 'generated' | 'generating' | 'failed' | 'scheduled';
  created_at: string;
  generated_by: string;
  file_size: string;
  format: 'pdf' | 'json' | 'csv' | 'html';
  tags: string[];
  data_range: {
    start: string;
    end: string;
  };
  metrics: {
    total_events: number;
    critical_alerts: number;
    threats_blocked: number;
    compliance_score: number;
  };
}

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: string;
  estimated_time: string;
  data_sources: string[];
  parameters: string[];
}

export const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([
    {
      id: '1',
      title: 'Weekly Security Summary',
      description: 'Comprehensive overview of security events, threats, and system performance',
      type: 'security_summary',
      status: 'generated',
      created_at: '2024-01-15T10:30:00Z',
      generated_by: 'Auto-Scheduler',
      file_size: '2.4 MB',
      format: 'pdf',
      tags: ['weekly', 'automated', 'summary'],
      data_range: {
        start: '2024-01-08T00:00:00Z',
        end: '2024-01-14T23:59:59Z'
      },
      metrics: {
        total_events: 15847,
        critical_alerts: 23,
        threats_blocked: 156,
        compliance_score: 94.2
      }
    },
    {
      id: '2',
      title: 'Phishing Campaign Analysis',
      description: 'Detailed analysis of recent phishing attempts and mitigation effectiveness',
      type: 'incident_analysis',
      status: 'generating',
      created_at: '2024-01-15T14:22:00Z',
      generated_by: 'John Doe',
      file_size: 'Estimating...',
      format: 'pdf',
      tags: ['phishing', 'analysis', 'manual'],
      data_range: {
        start: '2024-01-10T00:00:00Z',
        end: '2024-01-15T14:00:00Z'
      },
      metrics: {
        total_events: 234,
        critical_alerts: 12,
        threats_blocked: 89,
        compliance_score: 87.5
      }
    },
    {
      id: '3',
      title: 'Monthly Compliance Audit',
      description: 'Compliance assessment against industry standards and regulatory requirements',
      type: 'compliance_audit',
      status: 'generated',
      created_at: '2024-01-01T09:00:00Z',
      generated_by: 'Compliance Bot',
      file_size: '1.8 MB',
      format: 'pdf',
      tags: ['monthly', 'compliance', 'audit'],
      data_range: {
        start: '2023-12-01T00:00:00Z',
        end: '2023-12-31T23:59:59Z'
      },
      metrics: {
        total_events: 45623,
        critical_alerts: 8,
        threats_blocked: 234,
        compliance_score: 96.8
      }
    }
  ]);

  const [reportTemplates] = useState<ReportTemplate[]>([
    {
      id: 't1',
      name: 'Security Summary',
      description: 'General security overview with key metrics and trends',
      type: 'security_summary',
      estimated_time: '2-3 minutes',
      data_sources: ['Elasticsearch', 'Wazuh', 'System Logs'],
      parameters: ['Date Range', 'Alert Severity', 'Data Sources']
    },
    {
      id: 't2',
      name: 'Incident Investigation',
      description: 'Deep dive analysis of specific security incidents',
      type: 'incident_analysis',
      estimated_time: '5-8 minutes',
      data_sources: ['SIEM Logs', 'Network Traffic', 'System Events'],
      parameters: ['Incident ID', 'Time Window', 'Affected Systems']
    },
    {
      id: 't3',
      name: 'Compliance Report',
      description: 'Regulatory compliance assessment and recommendations',
      type: 'compliance_audit',
      estimated_time: '10-15 minutes',
      data_sources: ['All Security Systems', 'Audit Logs', 'Policy Engine'],
      parameters: ['Compliance Framework', 'Audit Period', 'Scope']
    }
  ]);

  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [isGenerating, setIsGenerating] = useState(false);

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = filterStatus === 'all' || report.status === filterStatus;
    const matchesType = filterType === 'all' || report.type === filterType;
    return matchesSearch && matchesStatus && matchesType;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'generated': return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'generating': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
      case 'failed': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'scheduled': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      default: return 'text-space-400 bg-space-500/10 border-space-500/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'generated': return <CheckCircle className="w-4 h-4" />;
      case 'generating': return <RefreshCw className="w-4 h-4 animate-spin" />;
      case 'failed': return <XCircle className="w-4 h-4" />;
      case 'scheduled': return <Clock className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'security_summary': return <Shield className="w-4 h-4" />;
      case 'incident_analysis': return <AlertTriangle className="w-4 h-4" />;
      case 'compliance_audit': return <CheckCircle className="w-4 h-4" />;
      case 'threat_intelligence': return <TrendingUp className="w-4 h-4" />;
      case 'performance_metrics': return <BarChart3 className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const formatFileSize = (size: string) => {
    return size;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDownloadReport = (report: Report) => {
    // Simulate download
    const blob = new Blob(['Report content'], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.title.replace(/\s+/g, '_')}.${report.format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleGenerateReport = async (template: ReportTemplate) => {
    setIsGenerating(true);
    setShowCreateModal(false);
    
    // Simulate report generation
    const newReport: Report = {
      id: Date.now().toString(),
      title: `${template.name} - ${new Date().toISOString().split('T')[0]}`,
      description: template.description,
      type: template.type as any,
      status: 'generating',
      created_at: new Date().toISOString(),
      generated_by: 'Current User',
      file_size: 'Generating...',
      format: 'pdf',
      tags: ['manual', template.type],
      data_range: {
        start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        end: new Date().toISOString()
      },
      metrics: {
        total_events: 0,
        critical_alerts: 0,
        threats_blocked: 0,
        compliance_score: 0
      }
    };

    setReports(prev => [newReport, ...prev]);

    // Simulate completion
    setTimeout(() => {
      setReports(prev => prev.map(r => 
        r.id === newReport.id 
          ? { 
              ...r, 
              status: 'generated',
              file_size: '1.2 MB',
              metrics: {
                total_events: Math.floor(Math.random() * 10000) + 5000,
                critical_alerts: Math.floor(Math.random() * 50) + 10,
                threats_blocked: Math.floor(Math.random() * 200) + 50,
                compliance_score: Math.floor(Math.random() * 20) + 80
              }
            }
          : r
      ));
      setIsGenerating(false);
    }, 3000);
  };

  const chartData = [
    { month: 'Jan', reports: 12, automated: 8, manual: 4 },
    { month: 'Feb', reports: 15, automated: 10, manual: 5 },
    { month: 'Mar', reports: 18, automated: 12, manual: 6 },
    { month: 'Apr', reports: 14, automated: 9, manual: 5 },
    { month: 'May', reports: 20, automated: 13, manual: 7 },
    { month: 'Jun', reports: 16, automated: 11, manual: 5 }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyber-darker via-space-950 to-cyber-dark p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Security Reports</h1>
            <p className="text-space-400">
              Generate, manage, and export comprehensive security reports and analytics
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-cyber-accent/20 hover:bg-cyber-accent/30 border border-cyber-accent/50 rounded-lg text-cyber-accent transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>New Report</span>
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-space-700/50 hover:bg-space-600/50 border border-space-600/50 rounded-lg text-space-300 transition-colors">
              <Settings className="w-4 h-4" />
              <span>Templates</span>
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              title: 'Total Reports',
              value: reports.length.toString(),
              change: '+3 this week',
              icon: <FileText className="w-6 h-6" />,
              color: 'from-blue-500 to-blue-600'
            },
            {
              title: 'Generated Today',
              value: reports.filter(r => 
                new Date(r.created_at).toDateString() === new Date().toDateString()
              ).length.toString(),
              change: '+2 from yesterday',
              icon: <CheckCircle className="w-6 h-6" />,
              color: 'from-green-500 to-green-600'
            },
            {
              title: 'In Progress',
              value: reports.filter(r => r.status === 'generating').length.toString(),
              change: 'Avg: 3min',
              icon: <RefreshCw className="w-6 h-6" />,
              color: 'from-yellow-500 to-yellow-600'
            },
            {
              title: 'Automated',
              value: reports.filter(r => r.tags.includes('automated')).length.toString(),
              change: '67% of total',
              icon: <Zap className="w-6 h-6" />,
              color: 'from-cyber-accent to-space-500'
            }
          ].map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6 hover:border-space-600/50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-space-400 text-sm font-medium">{stat.title}</p>
                  <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                  <p className="text-xs text-space-500 mt-1">{stat.change}</p>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg`}>
                  <div className="text-white">{stat.icon}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Report Generation Trends */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-6">Report Generation Trends</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="month" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1f2937', 
                      border: '1px solid #374151', 
                      borderRadius: '8px',
                      color: '#f3f4f6'
                    }} 
                  />
                  <Legend />
                  <Bar dataKey="automated" stackId="a" fill="#3b82f6" name="Automated" />
                  <Bar dataKey="manual" stackId="a" fill="#06b6d4" name="Manual" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Report Types Distribution */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6"
          >
            <h3 className="text-xl font-semibold text-white mb-6">Report Types</h3>
            <div className="space-y-4">
              {[
                { type: 'Security Summary', count: 45, percentage: 40 },
                { type: 'Incident Analysis', count: 28, percentage: 25 },
                { type: 'Compliance Audit', count: 23, percentage: 20 },
                { type: 'Threat Intelligence', count: 17, percentage: 15 }
              ].map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-space-300">{item.type}</span>
                    <span className="text-white font-medium">{item.count} reports</span>
                  </div>
                  <div className="w-full bg-space-800/50 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-cyber-accent to-space-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Filters */}
        <div className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-space-400" />
              <input
                type="text"
                placeholder="Search reports..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-space-800/50 border border-space-600/50 rounded-lg text-white placeholder-space-400 focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none transition-colors"
              />
            </div>
            
            <div className="flex items-center space-x-4">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 bg-space-800/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none transition-colors"
              >
                <option value="all">All Status</option>
                <option value="generated">Generated</option>
                <option value="generating">Generating</option>
                <option value="failed">Failed</option>
                <option value="scheduled">Scheduled</option>
              </select>
              
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-2 bg-space-800/50 border border-space-600/50 rounded-lg text-white focus:border-cyber-accent focus:ring-1 focus:ring-cyber-accent focus:outline-none transition-colors"
              >
                <option value="all">All Types</option>
                <option value="security_summary">Security Summary</option>
                <option value="incident_analysis">Incident Analysis</option>
                <option value="compliance_audit">Compliance Audit</option>
                <option value="threat_intelligence">Threat Intelligence</option>
                <option value="performance_metrics">Performance Metrics</option>
              </select>
            </div>
          </div>
        </div>

        {/* Reports List */}
        <div className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-xl overflow-hidden">
          <div className="divide-y divide-space-700/30">
            {filteredReports.map((report) => (
              <motion.div
                key={report.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-6 hover:bg-space-800/30 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="p-2 bg-space-700/50 rounded-lg">
                      {getTypeIcon(report.type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-white truncate">
                          {report.title}
                        </h3>
                        <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(report.status)}`}>
                          {getStatusIcon(report.status)}
                          <span className="capitalize">{report.status}</span>
                        </div>
                      </div>
                      
                      <p className="text-space-400 text-sm mb-3">{report.description}</p>
                      
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                        <div>
                          <span className="text-space-500">Created:</span>
                          <p className="text-space-300 font-medium">{formatDate(report.created_at)}</p>
                        </div>
                        <div>
                          <span className="text-space-500">Size:</span>
                          <p className="text-space-300 font-medium">{report.file_size}</p>
                        </div>
                        <div>
                          <span className="text-space-500">Events:</span>
                          <p className="text-space-300 font-medium">{report.metrics.total_events.toLocaleString()}</p>
                        </div>
                        <div>
                          <span className="text-space-500">Critical:</span>
                          <p className="text-space-300 font-medium">{report.metrics.critical_alerts}</p>
                        </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-1 mt-3">
                        {report.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-space-800/50 text-cyber-accent text-xs rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => setSelectedReport(report)}
                      className="p-2 hover:bg-space-700/50 text-space-400 hover:text-space-300 rounded-lg transition-colors"
                      title="View Report"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    
                    {report.status === 'generated' && (
                      <>
                        <button
                          onClick={() => handleDownloadReport(report)}
                          className="p-2 hover:bg-space-700/50 text-space-400 hover:text-cyber-accent rounded-lg transition-colors"
                          title="Download Report"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        
                        <button className="p-2 hover:bg-space-700/50 text-space-400 hover:text-space-300 rounded-lg transition-colors" title="Share Report">
                          <Share2 className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    
                    <button className="p-2 hover:bg-space-700/50 text-space-400 hover:text-red-400 rounded-lg transition-colors" title="Archive Report">
                      <Archive className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Create Report Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gradient-to-br from-space-900 to-cyber-dark border border-space-700 rounded-xl p-6 w-full max-w-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Generate New Report</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-space-700/50 text-space-400 hover:text-space-300 rounded-lg transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                {reportTemplates.map((template) => (
                  <div
                    key={template.id}
                    className="p-4 bg-space-800/30 border border-space-700/50 rounded-lg hover:border-space-600/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white mb-2">{template.name}</h3>
                        <p className="text-space-400 text-sm mb-3">{template.description}</p>
                        
                        <div className="grid grid-cols-2 gap-4 text-xs">
                          <div>
                            <span className="text-space-500">Est. Time:</span>
                            <p className="text-space-300">{template.estimated_time}</p>
                          </div>
                          <div>
                            <span className="text-space-500">Data Sources:</span>
                            <p className="text-space-300">{template.data_sources.join(', ')}</p>
                          </div>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => handleGenerateReport(template)}
                        disabled={isGenerating}
                        className="ml-4 px-4 py-2 bg-cyber-accent/20 hover:bg-cyber-accent/30 border border-cyber-accent/50 rounded-lg text-cyber-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Generate
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};
