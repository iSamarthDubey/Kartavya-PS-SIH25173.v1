import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Download, 
  Calendar, 
  Filter, 
  Search,
  Plus,
  Eye,
  Share,
  Clock,
  AlertTriangle,
  Shield,
  TrendingUp,
  BarChart3,
  PieChart,
  Activity,
  Users,
  Globe,
  Zap
} from 'lucide-react';

interface Report {
  id: string;
  title: string;
  type: 'security' | 'compliance' | 'incident' | 'performance';
  status: 'completed' | 'generating' | 'scheduled';
  createdAt: Date;
  size: string;
  description: string;
  author: string;
  tags: string[];
}

const mockReports: Report[] = [
  {
    id: '1',
    title: 'Weekly Security Assessment',
    type: 'security',
    status: 'completed',
    createdAt: new Date('2024-10-07'),
    size: '2.4 MB',
    description: 'Comprehensive security analysis for the past week including threat detection, blocked attacks, and system vulnerabilities.',
    author: 'Security Analyst',
    tags: ['weekly', 'threats', 'security']
  },
  {
    id: '2',
    title: 'Malware Detection Summary',
    type: 'security',
    status: 'completed',
    createdAt: new Date('2024-10-06'),
    size: '1.8 MB',
    description: 'Detailed analysis of malware detections, including attack vectors, affected systems, and remediation actions taken.',
    author: 'Malware Analyst',
    tags: ['malware', 'detections', 'analysis']
  },
  {
    id: '3',
    title: 'Compliance Audit Report',
    type: 'compliance',
    status: 'generating',
    createdAt: new Date('2024-10-08'),
    size: 'Generating...',
    description: 'Monthly compliance audit covering GDPR, ISO 27001, and internal security policies.',
    author: 'Compliance Officer',
    tags: ['compliance', 'audit', 'monthly']
  },
  {
    id: '4',
    title: 'Incident Response Analysis',
    type: 'incident',
    status: 'completed',
    createdAt: new Date('2024-10-05'),
    size: '3.2 MB',
    description: 'Investigation report for security incident INC-2024-0087 including timeline, impact assessment, and lessons learned.',
    author: 'Incident Manager',
    tags: ['incident', 'response', 'investigation']
  }
];

export const Reports: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  const filteredReports = mockReports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || report.type === selectedType;
    const matchesStatus = selectedStatus === 'all' || report.status === selectedStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'security': return <Shield className="w-4 h-4" />;
      case 'compliance': return <FileText className="w-4 h-4" />;
      case 'incident': return <AlertTriangle className="w-4 h-4" />;
      case 'performance': return <TrendingUp className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'security': return 'text-status-success bg-status-success/10 border-status-success/20';
      case 'compliance': return 'text-cyber-blue bg-cyber-blue/10 border-cyber-blue/20';
      case 'incident': return 'text-status-error bg-status-error/10 border-status-error/20';
      case 'performance': return 'text-status-warning bg-status-warning/10 border-status-warning/20';
      default: return 'text-cyber-gray-400 bg-cyber-gray-800/10 border-cyber-gray-700/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-status-success bg-status-success/10';
      case 'generating': return 'text-status-warning bg-status-warning/10';
      case 'scheduled': return 'text-cyber-blue bg-cyber-blue/10';
      default: return 'text-cyber-gray-400 bg-cyber-gray-800/10';
    }
  };

  return (
    <div className="p-6 space-y-6 overflow-y-auto scrollbar-thin scrollbar-thumb-cyber-gray-600 scrollbar-track-transparent">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            Security Reports & Analytics
          </h1>
          <p className="text-cyber-gray-400">
            Generate, view, and manage automated security reports and compliance documentation
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center space-x-2 px-4 py-2 bg-isro-gradient rounded-lg text-white font-medium"
          >
            <Plus className="w-4 h-4" />
            <span>Generate Report</span>
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center space-x-2 px-4 py-2 bg-cyber-navy/50 border border-cyber-gray-700/50 rounded-lg text-white font-medium"
          >
            <Calendar className="w-4 h-4" />
            <span>Schedule</span>
          </motion.button>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <QuickStatCard
          title="Total Reports"
          value="47"
          change="+8"
          icon={<FileText className="w-5 h-5" />}
          color="info"
        />
        <QuickStatCard
          title="This Month"
          value="12"
          change="+3"
          icon={<Calendar className="w-5 h-5" />}
          color="success"
        />
        <QuickStatCard
          title="Generating"
          value="3"
          change="+1"
          icon={<Activity className="w-5 h-5" />}
          color="warning"
        />
        <QuickStatCard
          title="Downloaded"
          value="156"
          change="+24"
          icon={<Download className="w-5 h-5" />}
          color="info"
        />
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex flex-wrap items-center gap-4 p-4 bg-cyber-navy/20 border border-cyber-gray-700/30 rounded-xl"
      >
        {/* Search */}
        <div className="flex-1 min-w-64">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-cyber-gray-400" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-cyber-darker/50 border border-cyber-gray-700/50 rounded-lg text-white placeholder-cyber-gray-400 focus:border-cyber-cyan/50 focus:outline-none"
            />
          </div>
        </div>

        {/* Type Filter */}
        <select
          aria-label="Filter by report type"
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="px-3 py-2 bg-cyber-darker/50 border border-cyber-gray-700/50 rounded-lg text-white focus:border-cyber-cyan/50 focus:outline-none"
        >
          <option value="all">All Types</option>
          <option value="security">Security</option>
          <option value="compliance">Compliance</option>
          <option value="incident">Incident</option>
          <option value="performance">Performance</option>
        </select>

        {/* Status Filter */}
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="px-3 py-2 bg-cyber-darker/50 border border-cyber-gray-700/50 rounded-lg text-white focus:border-cyber-cyan/50 focus:outline-none"
        >
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="generating">Generating</option>
          <option value="scheduled">Scheduled</option>
        </select>
      </motion.div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AnimatePresence>
          {filteredReports.map((report, index) => (
            <ReportCard key={report.id} report={report} index={index} />
          ))}
        </AnimatePresence>
      </div>

      {/* Quick Report Generation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="p-6 bg-cyber-navy/20 border border-cyber-gray-700/30 rounded-xl"
      >
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
          <Zap className="w-5 h-5 text-cyber-cyan" />
          <span>Quick Report Generation</span>
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickReportButton
            title="Threat Summary"
            description="Last 24 hours threat analysis"
            icon={<AlertTriangle className="w-5 h-5" />}
            estimatedTime="2 min"
          />
          <QuickReportButton
            title="System Health"
            description="Current system status report"
            icon={<Activity className="w-5 h-5" />}
            estimatedTime="1 min"
          />
          <QuickReportButton
            title="User Activity"
            description="User access and behavior analysis"
            icon={<Users className="w-5 h-5" />}
            estimatedTime="3 min"
          />
        </div>
      </motion.div>
    </div>
  );
};

interface QuickStatCardProps {
  title: string;
  value: string;
  change: string;
  icon: React.ReactNode;
  color: 'success' | 'warning' | 'error' | 'info';
}

const QuickStatCard: React.FC<QuickStatCardProps> = ({ title, value, change, icon, color }) => {
  const getColorClasses = () => {
    switch (color) {
      case 'success': return 'text-status-success bg-status-success/10 border-status-success/20';
      case 'warning': return 'text-status-warning bg-status-warning/10 border-status-warning/20';
      case 'error': return 'text-status-error bg-status-error/10 border-status-error/20';
      case 'info': return 'text-cyber-cyan bg-cyber-cyan/10 border-cyber-cyan/20';
      default: return 'text-cyber-gray-400 bg-cyber-gray-800/10 border-cyber-gray-700/20';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -1 }}
      className={`p-4 ${getColorClasses()} border rounded-xl backdrop-blur-sm`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="p-2 bg-cyber-darker/50 rounded-lg">
          {icon}
        </div>
        <span className="text-sm font-medium text-status-success">
          {change}
        </span>
      </div>
      <div>
        <p className="text-xl font-bold text-white">{value}</p>
        <p className="text-sm text-cyber-gray-400">{title}</p>
      </div>
    </motion.div>
  );
};

interface ReportCardProps {
  report: Report;
  index: number;
}

const ReportCard: React.FC<ReportCardProps> = ({ report, index }) => {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'security': return <Shield className="w-4 h-4" />;
      case 'compliance': return <FileText className="w-4 h-4" />;
      case 'incident': return <AlertTriangle className="w-4 h-4" />;
      case 'performance': return <TrendingUp className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'security': return 'text-status-success bg-status-success/10 border-status-success/20';
      case 'compliance': return 'text-cyber-blue bg-cyber-blue/10 border-cyber-blue/20';
      case 'incident': return 'text-status-error bg-status-error/10 border-status-error/20';
      case 'performance': return 'text-status-warning bg-status-warning/10 border-status-warning/20';
      default: return 'text-cyber-gray-400 bg-cyber-gray-800/10 border-cyber-gray-700/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-status-success bg-status-success/10';
      case 'generating': return 'text-status-warning bg-status-warning/10';
      case 'scheduled': return 'text-cyber-blue bg-cyber-blue/10';
      default: return 'text-cyber-gray-400 bg-cyber-gray-800/10';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.02, y: -2 }}
      className="p-6 bg-cyber-navy/20 border border-cyber-gray-700/30 rounded-xl backdrop-blur-sm"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg border ${getTypeColor(report.type)}`}>
            {getTypeIcon(report.type)}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{report.title}</h3>
            <p className="text-sm text-cyber-gray-400">by {report.author}</p>
          </div>
        </div>
        
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
          {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-cyber-gray-300 mb-4 line-clamp-2">
        {report.description}
      </p>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {report.tags.map((tag, tagIndex) => (
          <span
            key={tagIndex}
            className="px-2 py-1 bg-cyber-gray-700/30 text-cyber-gray-300 rounded text-xs"
          >
            #{tag}
          </span>
        ))}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-cyber-gray-700/30">
        <div className="flex items-center space-x-4 text-sm text-cyber-gray-400">
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>{report.createdAt.toLocaleDateString()}</span>
          </div>
          <div>
            <span>{report.size}</span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="p-2 text-cyber-gray-400 hover:text-cyber-cyan transition-colors"
          >
            <Eye className="w-4 h-4" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="p-2 text-cyber-gray-400 hover:text-cyber-cyan transition-colors"
          >
            <Share className="w-4 h-4" />
          </motion.button>
          {report.status === 'completed' && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 text-cyber-gray-400 hover:text-status-success transition-colors"
            >
              <Download className="w-4 h-4" />
            </motion.button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

interface QuickReportButtonProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  estimatedTime: string;
}

const QuickReportButton: React.FC<QuickReportButtonProps> = ({ 
  title, 
  description, 
  icon, 
  estimatedTime 
}) => (
  <motion.button
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
    className="p-4 bg-cyber-darker/30 hover:bg-cyber-darker/50 border border-cyber-gray-700/30 rounded-lg transition-all duration-200 text-left group"
  >
    <div className="flex items-center space-x-3 mb-2">
      <div className="p-2 bg-isro-gradient rounded-lg group-hover:scale-110 transition-transform">
        <div className="text-white">
          {icon}
        </div>
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-white">{title}</h4>
        <p className="text-xs text-cyber-gray-400">{description}</p>
      </div>
    </div>
    <div className="flex items-center justify-between">
      <span className="text-xs text-cyber-gray-500">Est. {estimatedTime}</span>
      <div className="w-4 h-4 text-cyber-cyan opacity-0 group-hover:opacity-100 transition-opacity">
        <Plus className="w-4 h-4" />
      </div>
    </div>
  </motion.button>
);