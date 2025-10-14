/**
 * SYNRGY Reports & Export System
 * Comprehensive report generation, templates, scheduling, and export functionality
 */

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  Plus,
  Search,
  Filter,
  Download,
  Calendar,
  Clock,
  User,
  TrendingUp,
  BarChart3,
  PieChart,
  Shield,
  AlertTriangle,
  CheckCircle,
  Eye,
  Edit3,
  Trash2,
  Play,
  Pause,
  RefreshCw,
  Settings,
  Send,
  Mail,
  FileOutput,
  Database,
  ChevronDown,
  Layout,
  Zap,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { api } from '@/services/api'
import { useAuth } from '@/providers/AuthProvider'

interface ReportTemplate {
  id: string
  name: string
  description: string
  category: 'security' | 'compliance' | 'operations' | 'threat_intel' | 'custom'
  type: 'dashboard' | 'table' | 'chart' | 'executive' | 'detailed'
  data_sources: string[]
  parameters: ReportParameter[]
  schedule?: ScheduleConfig
  created_by: {
    id: string
    name: string
  }
  created_at: string
  last_generated?: string
  is_active: boolean
}

interface ReportParameter {
  name: string
  type: 'text' | 'number' | 'date' | 'select' | 'multiselect'
  label: string
  required: boolean
  default_value?: any
  options?: string[]
}

interface ScheduleConfig {
  enabled: boolean
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'
  time: string
  timezone: string
  recipients: string[]
  format: 'pdf' | 'excel' | 'csv' | 'html'
}

interface GeneratedReport {
  id: string
  template_id: string
  template_name: string
  status: 'pending' | 'generating' | 'completed' | 'failed'
  generated_by: {
    id: string
    name: string
  }
  generated_at: string
  file_size?: number
  download_url?: string
  error_message?: string
  parameters_used: Record<string, any>
}

export default function ReportsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'templates' | 'generated' | 'scheduled'>('templates')
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null)

  // Fetch report templates
  const { data: templates = [], isLoading: loadingTemplates } = useQuery({
    queryKey: ['report-templates', { category: categoryFilter, search: searchQuery }],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (categoryFilter !== 'all') params.set('category', categoryFilter)
      if (searchQuery) params.set('search', searchQuery)
      
      const response = await api.get(`/api/reports/templates?${params.toString()}`)
      return response.data.data as ReportTemplate[]
    },
  })

  // Fetch generated reports
  const { data: generatedReports = [], isLoading: loadingReports } = useQuery({
    queryKey: ['generated-reports'],
    queryFn: async () => {
      const response = await api.get('/api/reports/generated')
      return response.data.data as GeneratedReport[]
    },
    refetchInterval: 10000, // Refresh every 10 seconds for status updates
  })

  // Generate report mutation
  const generateReportMutation = useMutation({
    mutationFn: async ({ templateId, parameters }: { templateId: string; parameters: Record<string, any> }) => {
      const response = await api.post(`/api/reports/generate/${templateId}`, { parameters })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['generated-reports'] })
      setShowGenerateModal(false)
      setSelectedTemplate(null)
      toast.success('Report generation started')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to generate report')
    },
  })

  // Create template mutation
  const createTemplateMutation = useMutation({
    mutationFn: async (data: Partial<ReportTemplate>) => {
      const response = await api.post('/api/reports/templates', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['report-templates'] })
      setShowCreateModal(false)
      toast.success('Template created successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create template')
    },
  })

  // Filter templates
  const filteredTemplates = useMemo(() => {
    return templates.filter(template => {
      const matchesSearch = searchQuery === '' || 
        template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        template.description.toLowerCase().includes(searchQuery.toLowerCase())
      
      const matchesCategory = categoryFilter === 'all' || template.category === categoryFilter
      
      return matchesSearch && matchesCategory
    })
  }, [templates, searchQuery, categoryFilter])

  const getCategoryIcon = (category: ReportTemplate['category']) => {
    switch (category) {
      case 'security': return <Shield className="w-4 h-4" />
      case 'compliance': return <CheckCircle className="w-4 h-4" />
      case 'operations': return <Settings className="w-4 h-4" />
      case 'threat_intel': return <AlertTriangle className="w-4 h-4" />
      case 'custom': return <FileText className="w-4 h-4" />
      default: return <FileText className="w-4 h-4" />
    }
  }

  const getTypeIcon = (type: ReportTemplate['type']) => {
    switch (type) {
      case 'dashboard': return <Layout className="w-4 h-4" />
      case 'table': return <Database className="w-4 h-4" />
      case 'chart': return <BarChart3 className="w-4 h-4" />
      case 'executive': return <TrendingUp className="w-4 h-4" />
      case 'detailed': return <FileOutput className="w-4 h-4" />
      default: return <FileText className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: GeneratedReport['status']) => {
    switch (status) {
      case 'pending': return 'text-yellow-400'
      case 'generating': return 'text-blue-400'
      case 'completed': return 'text-green-400'
      case 'failed': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const handleGenerateReport = (template: ReportTemplate) => {
    setSelectedTemplate(template)
    setShowGenerateModal(true)
  }

  const handleDownloadReport = async (report: GeneratedReport) => {
    if (!report.download_url) return
    
    try {
      const response = await api.get(report.download_url, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `${report.template_name}_${report.generated_at}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      toast.error('Failed to download report')
    }
  }

  return (
    <div className="h-full overflow-y-auto bg-synrgy-bg-900">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-synrgy-text mb-2">Reports & Export</h1>
            <p className="text-synrgy-muted">
              Generate security reports, analytics, and scheduled exports
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Template
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-synrgy-primary/10">
          <nav className="flex space-x-8">
            {[
              { key: 'templates', label: 'Templates', icon: FileText },
              { key: 'generated', label: 'Generated Reports', icon: Download },
              { key: 'scheduled', label: 'Scheduled', icon: Calendar },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as any)}
                className={`flex items-center gap-2 px-1 py-3 border-b-2 font-medium text-sm ${
                  activeTab === key
                    ? 'border-synrgy-primary text-synrgy-primary'
                    : 'border-transparent text-synrgy-muted hover:text-synrgy-text'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>

        {/* Filters */}
        <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-synrgy-muted" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search templates and reports..."
                  className="w-full pl-10 pr-4 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text placeholder-synrgy-muted"
                />
              </div>
            </div>

            {/* Category Filter */}
            {activeTab === 'templates' && (
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
              >
                <option value="all">All Categories</option>
                <option value="security">Security</option>
                <option value="compliance">Compliance</option>
                <option value="operations">Operations</option>
                <option value="threat_intel">Threat Intelligence</option>
                <option value="custom">Custom</option>
              </select>
            )}
          </div>
        </div>

        {/* Content */}
        {activeTab === 'templates' && (
          <div className="grid gap-4">
            {loadingTemplates ? (
              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-12 text-center">
                <div className="w-8 h-8 border-2 border-synrgy-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-synrgy-muted">Loading templates...</p>
              </div>
            ) : filteredTemplates.length === 0 ? (
              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-12 text-center">
                <FileText className="w-12 h-12 text-synrgy-muted mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-synrgy-text mb-2">No Templates Found</h3>
                <p className="text-synrgy-muted mb-6">
                  {searchQuery || categoryFilter !== 'all'
                    ? 'No templates match your current filters.'
                    : 'Create your first report template to get started.'}
                </p>
                {!searchQuery && categoryFilter === 'all' && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors mx-auto"
                  >
                    <Plus className="w-4 h-4" />
                    Create Template
                  </button>
                )}
              </div>
            ) : (
              filteredTemplates.map((template) => (
                <motion.div
                  key={template.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6 hover:border-synrgy-primary/20 transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-synrgy-text">{template.name}</h3>
                        <div className="flex items-center gap-1 px-2 py-1 bg-synrgy-primary/10 text-synrgy-primary rounded text-xs">
                          {getCategoryIcon(template.category)}
                          {(template.category || '').replace('_', ' ').toUpperCase()}
                        </div>
                        <div className="flex items-center gap-1 px-2 py-1 bg-synrgy-accent/10 text-synrgy-accent rounded text-xs">
                          {getTypeIcon(template.type)}
                          {(template.type || '').toUpperCase()}
                        </div>
                      </div>
                      <p className="text-synrgy-muted mb-3">{template.description}</p>
                      
                      <div className="flex flex-wrap gap-4 text-sm text-synrgy-muted">
                        <div className="flex items-center gap-1">
                          <Database className="w-4 h-4" />
                          <span>{template.data_sources?.length || 0} data sources</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <User className="w-4 h-4" />
                          <span>{template.created_by?.name || 'Unknown'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>{new Date(template.created_at).toLocaleDateString()}</span>
                        </div>
                        {template.schedule?.enabled && (
                          <div className="flex items-center gap-1 text-green-400">
                            <Calendar className="w-4 h-4" />
                            <span>Scheduled {template.schedule.frequency}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => handleGenerateReport(template)}
                        className="flex items-center gap-1 px-3 py-2 bg-synrgy-primary/20 text-synrgy-primary hover:bg-synrgy-primary/30 rounded transition-colors"
                      >
                        <Play className="w-4 h-4" />
                        Generate
                      </button>
                      <button
                        onClick={() => {
                          // Handle view/edit template
                        }}
                        className="p-2 text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 rounded transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          // Handle edit template
                        }}
                        className="p-2 text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 rounded transition-colors"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          // Handle delete template
                        }}
                        className="p-2 text-synrgy-muted hover:text-red-400 hover:bg-red-400/10 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}

        {activeTab === 'generated' && (
          <div className="grid gap-4">
            {loadingReports ? (
              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-12 text-center">
                <div className="w-8 h-8 border-2 border-synrgy-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-synrgy-muted">Loading reports...</p>
              </div>
            ) : generatedReports.length === 0 ? (
              <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-12 text-center">
                <Download className="w-12 h-12 text-synrgy-muted mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-synrgy-text mb-2">No Generated Reports</h3>
                <p className="text-synrgy-muted">Generate your first report to see it here.</p>
              </div>
            ) : (
              generatedReports.map((report) => (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6 hover:border-synrgy-primary/20 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-synrgy-text">{report.template_name}</h3>
                        <div className={`px-2 py-1 rounded text-xs ${getStatusColor(report.status)}`}>
                          {(report.status || 'unknown').toUpperCase()}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-synrgy-muted">
                        <div className="flex items-center gap-1">
                          <User className="w-4 h-4" />
                          <span>{report.generated_by?.name || 'Unknown'}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>{new Date(report.generated_at).toLocaleString()}</span>
                        </div>
                        {report.file_size && (
                          <div className="flex items-center gap-1">
                            <FileOutput className="w-4 h-4" />
                            <span>{(report.file_size / 1024 / 1024).toFixed(2)} MB</span>
                          </div>
                        )}
                      </div>
                      
                      {report.error_message && (
                        <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-400">
                          {report.error_message}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {report.status === 'completed' && report.download_url && (
                        <button
                          onClick={() => handleDownloadReport(report)}
                          className="flex items-center gap-1 px-3 py-2 bg-synrgy-primary/20 text-synrgy-primary hover:bg-synrgy-primary/30 rounded transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          Download
                        </button>
                      )}
                      {report.status === 'generating' && (
                        <div className="flex items-center gap-1 px-3 py-2 bg-blue-500/20 text-blue-400 rounded">
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Generating...
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}

        {activeTab === 'scheduled' && (
          <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-12 text-center">
            <Calendar className="w-12 h-12 text-synrgy-muted mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-synrgy-text mb-2">Scheduled Reports</h3>
            <p className="text-synrgy-muted">
              Automated report scheduling features will be available here.
            </p>
          </div>
        )}
      </div>

      {/* Generate Report Modal */}
      <AnimatePresence>
        {showGenerateModal && selectedTemplate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => {
              setShowGenerateModal(false)
              setSelectedTemplate(null)
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-synrgy-surface border border-synrgy-primary/20 rounded-xl p-6 max-w-lg w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-lg font-semibold text-synrgy-text mb-4">
                Generate Report: {selectedTemplate.name}
              </h2>
              
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  const formData = new FormData(e.currentTarget)
                  const parameters: Record<string, any> = {}
                  
                  selectedTemplate.parameters.forEach(param => {
                    const value = formData.get(param.name)
                    if (value !== null) {
                      parameters[param.name] = param.type === 'number' ? Number(value) : value
                    }
                  })
                  
                  generateReportMutation.mutate({
                    templateId: selectedTemplate.id,
                    parameters,
                  })
                }}
                className="space-y-4"
              >
                {selectedTemplate.parameters.map((param) => (
                  <div key={param.name}>
                    <label className="block text-sm font-medium text-synrgy-text mb-1">
                      {param.label}
                      {param.required && <span className="text-red-400 ml-1">*</span>}
                    </label>
                    
                    {param.type === 'select' ? (
                      <select
                        name={param.name}
                        required={param.required}
                        defaultValue={param.default_value}
                        className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                      >
                        {param.options?.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    ) : param.type === 'date' ? (
                      <input
                        type="date"
                        name={param.name}
                        required={param.required}
                        defaultValue={param.default_value}
                        className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                      />
                    ) : (
                      <input
                        type={param.type === 'number' ? 'number' : 'text'}
                        name={param.name}
                        required={param.required}
                        defaultValue={param.default_value}
                        className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                      />
                    )}
                  </div>
                ))}
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowGenerateModal(false)
                      setSelectedTemplate(null)
                    }}
                    className="flex-1 px-4 py-2 border border-synrgy-primary/20 text-synrgy-text rounded-lg hover:bg-synrgy-primary/10 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={generateReportMutation.isPending}
                    className="flex-1 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors disabled:opacity-50"
                  >
                    {generateReportMutation.isPending ? 'Generating...' : 'Generate Report'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
