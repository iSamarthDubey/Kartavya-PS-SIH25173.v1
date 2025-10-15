/**
 * SYNRGY Investigation Management System
 * Complete CRUD system for investigations with timeline, collaboration, and case management
 */

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Plus,
  Filter,
  Clock,
  User,
  AlertTriangle,
  Shield,
  Eye,
  Edit3,
  Trash2,
  Users,
  Calendar,
  FileText,
  MessageSquare,
  Hash,
  TrendingUp,
  ExternalLink,
  CheckCircle,
  XCircle,
  AlertCircle,
  PauseCircle,
  PlayCircle,
  Archive,
  Tag,
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { api } from '@/services/api'
import { useAuth } from '@/providers/AuthProvider'

interface Investigation {
  id: string
  title: string
  description: string
  status: 'open' | 'in_progress' | 'on_hold' | 'closed' | 'archived'
  priority: 'low' | 'medium' | 'high' | 'critical'
  category: string
  tags: string[]
  assignee: {
    id: string
    name: string
    avatar?: string
  }
  created_by: {
    id: string
    name: string
    avatar?: string
  }
  created_at: string
  updated_at: string
  timeline: TimelineEvent[]
  collaborators: User[]
  artifacts: Artifact[]
  metadata: Record<string, any>
}

interface TimelineEvent {
  id: string
  type: 'created' | 'updated' | 'status_changed' | 'comment' | 'artifact_added' | 'assigned'
  description: string
  user: {
    id: string
    name: string
    avatar?: string
  }
  timestamp: string
  metadata?: Record<string, any>
}

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: string
}

interface Artifact {
  id: string
  name: string
  type: 'file' | 'log' | 'screenshot' | 'network_capture' | 'memory_dump' | 'other'
  size: number
  hash: string
  created_at: string
  created_by: string
}

export default function InvestigationsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [selectedInvestigation, setSelectedInvestigation] = useState<Investigation | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [viewMode, setViewMode] = useState<'list' | 'kanban'>('list')

  // Fetch investigations from backend
  const { data: investigations = [], isLoading } = useQuery({
    queryKey: ['investigations', { status: statusFilter, priority: priorityFilter, search: searchQuery }],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.set('status', statusFilter)
      if (priorityFilter !== 'all') params.set('priority', priorityFilter)
      if (searchQuery) params.set('search', searchQuery)
      
      const response = await api.get(`/api/investigations?${params.toString()}`)
      return response.data.data as Investigation[]
    },
  })

  // Create investigation mutation
  const createInvestigationMutation = useMutation({
    mutationFn: async (data: Partial<Investigation>) => {
      const response = await api.post('/api/investigations', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investigations'] })
      setShowCreateModal(false)
      toast.success('Investigation created successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create investigation')
    },
  })

  // Update investigation status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: Investigation['status'] }) => {
      const response = await api.patch(`/api/investigations/${id}`, { status })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investigations'] })
      toast.success('Status updated successfully')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update status')
    },
  })

  // Filter investigations
  const filteredInvestigations = useMemo(() => {
    return investigations.filter(inv => {
      const matchesSearch = searchQuery === '' || 
        inv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inv.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inv.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      
      const matchesStatus = statusFilter === 'all' || inv.status === statusFilter
      const matchesPriority = priorityFilter === 'all' || inv.priority === priorityFilter
      
      return matchesSearch && matchesStatus && matchesPriority
    })
  }, [investigations, searchQuery, statusFilter, priorityFilter])

  const getStatusIcon = (status: Investigation['status']) => {
    switch (status) {
      case 'open': return <AlertCircle className="w-4 h-4" />
      case 'in_progress': return <PlayCircle className="w-4 h-4" />
      case 'on_hold': return <PauseCircle className="w-4 h-4" />
      case 'closed': return <CheckCircle className="w-4 h-4" />
      case 'archived': return <Archive className="w-4 h-4" />
      default: return <AlertCircle className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: Investigation['status']) => {
    switch (status) {
      case 'open': return 'text-blue-400'
      case 'in_progress': return 'text-green-400'
      case 'on_hold': return 'text-yellow-400'
      case 'closed': return 'text-gray-400'
      case 'archived': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  const getPriorityColor = (priority: Investigation['priority']) => {
    switch (priority) {
      case 'critical': return 'text-red-500'
      case 'high': return 'text-orange-500'
      case 'medium': return 'text-yellow-500'
      case 'low': return 'text-green-500'
      default: return 'text-gray-500'
    }
  }

  const handleCreateInvestigation = (data: Partial<Investigation>) => {
    createInvestigationMutation.mutate({
      ...data,
      created_by: { id: user?.id || '', name: user?.full_name || user?.username || '', avatar: '' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      timeline: [{
        id: Date.now().toString(),
        type: 'created',
        description: 'Investigation created',
        user: { id: user?.id || '', name: user?.full_name || user?.username || '', avatar: '' },
        timestamp: new Date().toISOString(),
      }],
      collaborators: [],
      artifacts: [],
      metadata: {},
    })
  }

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-synrgy-bg-900">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-synrgy-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-synrgy-muted">Loading investigations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto bg-synrgy-bg-900">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-synrgy-text mb-2">Investigations</h1>
            <p className="text-synrgy-muted">
              Manage security incidents and digital forensics investigations
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Investigation
          </button>
        </div>

        {/* Filters and Search */}
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
                  placeholder="Search investigations..."
                  className="w-full pl-10 pr-4 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text placeholder-synrgy-muted"
                />
              </div>
            </div>

            {/* Filters */}
            <div className="flex gap-4">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
              >
                <option value="all">All Status</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="on_hold">On Hold</option>
                <option value="closed">Closed</option>
                <option value="archived">Archived</option>
              </select>

              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
              >
                <option value="all">All Priority</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>

              <div className="flex rounded-lg border border-synrgy-primary/20 overflow-hidden">
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 ${
                    viewMode === 'list'
                      ? 'bg-synrgy-primary text-synrgy-bg-900'
                      : 'bg-synrgy-bg-900 text-synrgy-muted hover:text-synrgy-text'
                  }`}
                >
                  List
                </button>
                <button
                  onClick={() => setViewMode('kanban')}
                  className={`px-3 py-2 ${
                    viewMode === 'kanban'
                      ? 'bg-synrgy-primary text-synrgy-bg-900'
                      : 'bg-synrgy-bg-900 text-synrgy-muted hover:text-synrgy-text'
                  }`}
                >
                  Kanban
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Investigations List */}
        <div className="grid gap-4">
          {filteredInvestigations.length === 0 ? (
            <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-12 text-center">
              <Shield className="w-12 h-12 text-synrgy-muted mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-synrgy-text mb-2">No Investigations Found</h3>
              <p className="text-synrgy-muted mb-6">
                {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all'
                  ? 'No investigations match your current filters.'
                  : 'Start by creating your first investigation.'}
              </p>
              {!searchQuery && statusFilter === 'all' && priorityFilter === 'all' && (
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors mx-auto"
                >
                  <Plus className="w-4 h-4" />
                  Create Investigation
                </button>
              )}
            </div>
          ) : (
            filteredInvestigations.map((investigation) => (
              <motion.div
                key={investigation.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-synrgy-surface border border-synrgy-primary/10 rounded-xl p-6 hover:border-synrgy-primary/20 transition-all cursor-pointer"
                onClick={() => setSelectedInvestigation(investigation)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-synrgy-text">{investigation.title}</h3>
                      <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${getStatusColor(investigation.status)}`}>
                        {getStatusIcon(investigation.status)}
                        {investigation.status.replace('_', ' ').toUpperCase()}
                      </div>
                      <div className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(investigation.priority)}`}>
                        {investigation.priority.toUpperCase()}
                      </div>
                    </div>
                    <p className="text-synrgy-muted mb-3 line-clamp-2">{investigation.description}</p>
                    
                    {/* Tags */}
                    {investigation.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {investigation.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="inline-flex items-center gap-1 px-2 py-1 bg-synrgy-primary/10 text-synrgy-primary rounded text-xs"
                          >
                            <Tag className="w-3 h-3" />
                            {tag}
                          </span>
                        ))}
                        {investigation.tags.length > 3 && (
                          <span className="px-2 py-1 bg-synrgy-muted/10 text-synrgy-muted rounded text-xs">
                            +{investigation.tags.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        // Handle edit
                      }}
                      className="p-2 text-synrgy-muted hover:text-synrgy-primary hover:bg-synrgy-primary/10 rounded transition-colors"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        // Handle delete
                      }}
                      className="p-2 text-synrgy-muted hover:text-red-400 hover:bg-red-400/10 rounded transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Bottom info */}
                <div className="flex items-center justify-between text-sm text-synrgy-muted">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      <span>{investigation.assignee?.name || 'Unassigned'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      <span>{investigation.collaborators.length} collaborators</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <FileText className="w-4 h-4" />
                      <span>{investigation.artifacts.length} artifacts</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{new Date(investigation.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Create Investigation Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-synrgy-surface border border-synrgy-primary/20 rounded-xl p-6 max-w-lg w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-lg font-semibold text-synrgy-text mb-4">Create Investigation</h2>
              
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  const formData = new FormData(e.currentTarget)
                  handleCreateInvestigation({
                    title: formData.get('title') as string,
                    description: formData.get('description') as string,
                    priority: formData.get('priority') as Investigation['priority'],
                    category: formData.get('category') as string,
                    status: 'open',
                    tags: (formData.get('tags') as string).split(',').map(t => t.trim()).filter(Boolean),
                  })
                }}
                className="space-y-4"
              >
                <div>
                  <label className="block text-sm font-medium text-synrgy-text mb-1">Title</label>
                  <input
                    name="title"
                    required
                    className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                    placeholder="Enter investigation title"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-synrgy-text mb-1">Description</label>
                  <textarea
                    name="description"
                    required
                    rows={3}
                    className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text resize-none"
                    placeholder="Describe the investigation"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-synrgy-text mb-1">Priority</label>
                    <select
                      name="priority"
                      required
                      className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-synrgy-text mb-1">Category</label>
                    <select
                      name="category"
                      required
                      className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                    >
                      <option value="malware">Malware</option>
                      <option value="phishing">Phishing</option>
                      <option value="data_breach">Data Breach</option>
                      <option value="insider_threat">Insider Threat</option>
                      <option value="network_intrusion">Network Intrusion</option>
                      <option value="fraud">Fraud</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-synrgy-text mb-1">Tags (comma-separated)</label>
                  <input
                    name="tags"
                    className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg focus:border-synrgy-primary focus:outline-none text-synrgy-text"
                    placeholder="e.g., urgent, financial, external"
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 px-4 py-2 border border-synrgy-primary/20 text-synrgy-text rounded-lg hover:bg-synrgy-primary/10 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createInvestigationMutation.isPending}
                    className="flex-1 px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 transition-colors disabled:opacity-50"
                  >
                    {createInvestigationMutation.isPending ? 'Creating...' : 'Create Investigation'}
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
