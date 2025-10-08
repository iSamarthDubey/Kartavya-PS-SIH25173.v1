import React, { useState, useRef } from 'react';
import {
  FileText,
  Download,
  Calendar,
  Clock,
  BarChart3,
  PieChart as PieChartIcon,
  TrendingUp,
  Filter,
  Settings,
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  Users,
  Shield,
  Eye,
  Zap,
  Database,
  FileDown,
  Share2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: 'security' | 'compliance' | 'executive' | 'technical';
  estimatedTime: string;
  includesCharts: boolean;
}

interface ReportConfig {
  templateId: string;
  timeRange: {
    start: Date;
    end: Date;
    preset?: string;
  };
  filters: {
    severity?: string[];
    eventTypes?: string[];
    sources?: string[];
  };
  format: 'pdf' | 'html' | 'csv' | 'json';
  includeCharts: boolean;
  includeRawData: boolean;
  autoSchedule?: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    recipients: string[];
  };
}

interface GeneratedReport {
  id: string;
  name: string;
  templateName: string;
  status: 'generating' | 'completed' | 'failed';
  createdAt: Date;
  completedAt?: Date;
  progress: number;
  fileSize?: string;
  downloadUrl?: string;
}

interface ReportGeneratorProps {
  isConnected: boolean;
  onGenerateReport: (config: ReportConfig) => Promise<void>;
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  isConnected,
  onGenerateReport
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [config, setConfig] = useState<ReportConfig>({
    templateId: '',
    timeRange: {
      start: new Date(Date.now() - 24 * 60 * 60 * 1000),
      end: new Date(),
      preset: '24h'
    },
    filters: {},
    format: 'pdf',
    includeCharts: true,
    includeRawData: false
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const templates: ReportTemplate[] = [
    {
      id: 'security-summary',
      name: 'Security Summary Report',
      description: 'Comprehensive overview of security events and threats',
      icon: <Shield className="w-5 h-5 text-blue-400" />,
      category: 'security',
      estimatedTime: '2-3 min',
      includesCharts: true
    },
    {
      id: 'threat-analysis',
      name: 'Threat Analysis Report',
      description: 'Detailed analysis of detected threats and attack patterns',
      icon: <AlertCircle className="w-5 h-5 text-red-400" />,
      category: 'security',
      estimatedTime: '3-5 min',
      includesCharts: true
    },
    {
      id: 'compliance-audit',
      name: 'Compliance Audit Report',
      description: 'Compliance status and regulatory requirements check',
      icon: <CheckCircle className="w-5 h-5 text-green-400" />,
      category: 'compliance',
      estimatedTime: '5-7 min',
      includesCharts: false
    },
    {
      id: 'executive-summary',
      name: 'Executive Summary',
      description: 'High-level security posture for leadership team',
      icon: <TrendingUp className="w-5 h-5 text-purple-400" />,
      category: 'executive',
      estimatedTime: '1-2 min',
      includesCharts: true
    },
    {
      id: 'incident-response',
      name: 'Incident Response Report',
      description: 'Detailed incident analysis and response timeline',
      icon: <Zap className="w-5 h-5 text-orange-400" />,
      category: 'technical',
      estimatedTime: '4-6 min',
      includesCharts: true
    },
    {
      id: 'user-activity',
      name: 'User Activity Report',
      description: 'User behavior analysis and access patterns',
      icon: <Users className="w-5 h-5 text-cyan-400" />,
      category: 'security',
      estimatedTime: '3-4 min',
      includesCharts: true
    }
  ];

  const timeRangePresets = [
    { id: '1h', label: 'Last Hour', start: new Date(Date.now() - 60 * 60 * 1000) },
    { id: '24h', label: 'Last 24 Hours', start: new Date(Date.now() - 24 * 60 * 60 * 1000) },
    { id: '7d', label: 'Last 7 Days', start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
    { id: '30d', label: 'Last 30 Days', start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) },
    { id: 'custom', label: 'Custom Range', start: null }
  ];

  // Mock generated reports
  const mockReports: GeneratedReport[] = [
    {
      id: '1',
      name: 'Security Summary - Daily',
      templateName: 'Security Summary Report',
      status: 'completed',
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      completedAt: new Date(Date.now() - 2 * 60 * 60 * 1000 + 3 * 60 * 1000),
      progress: 100,
      fileSize: '2.4 MB',
      downloadUrl: '#'
    },
    {
      id: '2',
      name: 'Threat Analysis - Weekly',
      templateName: 'Threat Analysis Report',
      status: 'generating',
      createdAt: new Date(Date.now() - 5 * 60 * 1000),
      progress: 65,
    },
    {
      id: '3',
      name: 'Executive Summary - Monthly',
      templateName: 'Executive Summary',
      status: 'failed',
      createdAt: new Date(Date.now() - 60 * 60 * 1000),
      progress: 0,
    }
  ];

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId);
    setConfig(prev => ({ ...prev, templateId }));
  };

  const handleTimeRangeChange = (preset: string) => {
    const presetData = timeRangePresets.find(p => p.id === preset);
    if (presetData && presetData.start) {
      setConfig(prev => ({
        ...prev,
        timeRange: {
          start: presetData.start!,
          end: new Date(),
          preset
        }
      }));
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedTemplate) return;

    setIsGenerating(true);
    
    try {
      await onGenerateReport(config);
      
      // Mock report generation
      const newReport: GeneratedReport = {
        id: Date.now().toString(),
        name: `${templates.find(t => t.id === selectedTemplate)?.name} - ${new Date().toLocaleDateString()}`,
        templateName: templates.find(t => t.id === selectedTemplate)?.name || '',
        status: 'generating',
        createdAt: new Date(),
        progress: 0
      };
      
      setReports(prev => [newReport, ...prev]);
      
      // Simulate progress
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress >= 100) {
          progress = 100;
          clearInterval(progressInterval);
          
          setReports(prev => prev.map(r => 
            r.id === newReport.id 
              ? { ...r, status: 'completed', progress: 100, completedAt: new Date(), fileSize: '1.8 MB' }
              : r
          ));
        } else {
          setReports(prev => prev.map(r => 
            r.id === newReport.id ? { ...r, progress } : r
          ));
        }
      }, 500);
      
    } catch (error) {
      console.error('Report generation failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      security: 'bg-blue-500/10 border-blue-500/20',
      compliance: 'bg-green-500/10 border-green-500/20',
      executive: 'bg-purple-500/10 border-purple-500/20',
      technical: 'bg-orange-500/10 border-orange-500/20'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-500/10 border-gray-500/20';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      generating: 'text-blue-400 bg-blue-900/20',
      completed: 'text-green-400 bg-green-900/20',
      failed: 'text-red-400 bg-red-900/20'
    };
    return colors[status as keyof typeof colors] || 'text-gray-400 bg-gray-900/20';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Report Generator</h1>
          <p className="text-gray-400">Generate comprehensive security reports and analytics</p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'}`} />
          <span className="text-sm text-gray-300">
            {isConnected ? 'Live Data' : 'Demo Mode'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Configuration */}
        <div className="lg:col-span-2 space-y-6">
          {/* Template Selection */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Select Report Template</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map((template) => (
                <motion.button
                  key={template.id}
                  onClick={() => handleTemplateSelect(template.id)}
                  className={`p-4 rounded-lg border text-left transition-all hover:scale-105 ${
                    selectedTemplate === template.id
                      ? 'border-blue-500 bg-blue-500/10'
                      : `${getCategoryColor(template.category)}`
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-start space-x-3">
                    {template.icon}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-200 mb-1">
                        {template.name}
                      </div>
                      <div className="text-xs text-gray-400 mb-2">
                        {template.description}
                      </div>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>{template.estimatedTime}</span>
                        {template.includesCharts && (
                          <>
                            <BarChart3 className="w-3 h-3" />
                            <span>Charts</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Time Range Selection */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Time Range</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-4">
              {timeRangePresets.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => handleTimeRangeChange(preset.id)}
                  className={`p-2 rounded-lg text-sm transition-colors ${
                    config.timeRange.preset === preset.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {preset.label}
                </button>
              ))}
            </div>

            {config.timeRange.preset === 'custom' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Start Date</label>
                  <input
                    type="datetime-local"
                    className="w-full p-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200"
                    value={config.timeRange.start.toISOString().slice(0, 16)}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      timeRange: { ...prev.timeRange, start: new Date(e.target.value) }
                    }))}
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-2">End Date</label>
                  <input
                    type="datetime-local"
                    className="w-full p-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200"
                    value={config.timeRange.end.toISOString().slice(0, 16)}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      timeRange: { ...prev.timeRange, end: new Date(e.target.value) }
                    }))}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Advanced Options */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Options</h3>
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-blue-400 hover:text-blue-300 text-sm"
              >
                {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Format</label>
                <select
                  value={config.format}
                  onChange={(e) => setConfig(prev => ({ ...prev, format: e.target.value as any }))}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200"
                >
                  <option value="pdf">PDF</option>
                  <option value="html">HTML</option>
                  <option value="csv">CSV</option>
                  <option value="json">JSON</option>
                </select>
              </div>

              <div className="flex items-center space-x-2 pt-6">
                <input
                  type="checkbox"
                  id="includeCharts"
                  checked={config.includeCharts}
                  onChange={(e) => setConfig(prev => ({ ...prev, includeCharts: e.target.checked }))}
                  className="rounded border-gray-600 bg-gray-700"
                />
                <label htmlFor="includeCharts" className="text-sm text-gray-300">Include Charts</label>
              </div>

              <div className="flex items-center space-x-2 pt-6">
                <input
                  type="checkbox"
                  id="includeRawData"
                  checked={config.includeRawData}
                  onChange={(e) => setConfig(prev => ({ ...prev, includeRawData: e.target.checked }))}
                  className="rounded border-gray-600 bg-gray-700"
                />
                <label htmlFor="includeRawData" className="text-sm text-gray-300">Include Raw Data</label>
              </div>
            </div>

            <AnimatePresence>
              {showAdvanced && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4 pt-4 border-t border-gray-700"
                >
                  {/* Filters */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Severity Levels</label>
                      <div className="space-y-2">
                        {['Critical', 'High', 'Medium', 'Low'].map(severity => (
                          <label key={severity} className="flex items-center space-x-2">
                            <input type="checkbox" className="rounded border-gray-600 bg-gray-700" />
                            <span className="text-sm text-gray-300">{severity}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Event Types</label>
                      <div className="space-y-2">
                        {['Authentication', 'Network', 'Malware', 'System'].map(type => (
                          <label key={type} className="flex items-center space-x-2">
                            <input type="checkbox" className="rounded border-gray-600 bg-gray-700" />
                            <span className="text-sm text-gray-300">{type}</span>
                          </label>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Sources</label>
                      <textarea
                        placeholder="Enter IP addresses or hostnames..."
                        className="w-full p-2 bg-gray-700 border border-gray-600 rounded-lg text-gray-200 text-sm"
                        rows={4}
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex items-center justify-between pt-4">
              <div className="text-sm text-gray-400">
                Estimated generation time: {templates.find(t => t.id === selectedTemplate)?.estimatedTime || 'Select template'}
              </div>
              
              <button
                onClick={handleGenerateReport}
                disabled={!selectedTemplate || isGenerating}
                className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                {isGenerating ? <Pause className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                <span>{isGenerating ? 'Generating...' : 'Generate Report'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Generated Reports */}
        <div className="space-y-6">
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Generated Reports</h3>
            
            <div className="space-y-3">
              {mockReports.map((report) => (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 bg-gray-900/30 rounded-lg border border-gray-700/50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-200 mb-1">
                        {report.name}
                      </div>
                      <div className="text-xs text-gray-400">
                        {report.templateName}
                      </div>
                    </div>
                    
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                      {report.status}
                    </div>
                  </div>

                  {report.status === 'generating' && (
                    <div className="mb-2">
                      <div className="flex justify-between text-xs text-gray-400 mb-1">
                        <span>Progress</span>
                        <span>{Math.round(report.progress)}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${report.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{report.createdAt.toLocaleString()}</span>
                    {report.status === 'completed' && (
                      <div className="flex items-center space-x-2">
                        <span>{report.fileSize}</span>
                        <button className="text-blue-400 hover:text-blue-300">
                          <Download className="w-3 h-3" />
                        </button>
                        <button className="text-gray-400 hover:text-gray-300">
                          <Share2 className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>

            <button className="w-full mt-4 p-2 text-blue-400 hover:text-blue-300 text-sm border border-gray-700 hover:border-gray-600 rounded-lg transition-colors">
              View All Reports
            </button>
          </div>

          {/* Quick Stats */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Report Statistics</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Reports Generated</span>
                <span className="text-sm font-medium text-white">247</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Total Size</span>
                <span className="text-sm font-medium text-white">1.2 GB</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Avg Generation Time</span>
                <span className="text-sm font-medium text-white">3.2 min</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Success Rate</span>
                <span className="text-sm font-medium text-green-400">98.7%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator;
