import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, Calendar, Filter } from 'lucide-react';

export const Reports: React.FC = () => {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [reports, setReports] = useState<any[]>([]);

  const handleGenerateReport = async () => {
    setIsGenerating(true);
    
    // Simulate API call
    setTimeout(() => {
      const newReport = {
        id: Date.now(),
        title: `Security Report - ${new Date().toLocaleDateString()}`,
        generatedAt: new Date(),
        summary: 'Generated security report with threat analysis and recommendations.',
        findings: [
          { category: 'Authentication', description: 'Multiple failed login attempts detected', severity: 'high' },
          { category: 'Network', description: 'Suspicious network traffic patterns', severity: 'medium' }
        ]
      };
      setReports(prev => [...prev, newReport]);
      setIsGenerating(false);
    }, 2000);
  };

  const handleDownload = (reportId: number, format: 'pdf' | 'csv') => {
    console.log(`Downloading report ${reportId} as ${format}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="h-full flex flex-col"
    >
      {/* Header */}
      <div className="glass-card p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold neon-text mb-2">Security Reports</h1>
            <p className="text-gray-400">Generate and manage automated security reports</p>
          </div>
          <motion.button
            onClick={handleGenerateReport}
            disabled={isGenerating}
            className="cyber-button flex items-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <FileText className="w-4 h-4" />
            {isGenerating ? 'Generating...' : 'Generate Report'}
          </motion.button>
        </div>
      </div>

      {/* Report Generator */}
      <div className="glass-card p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Filter className="w-5 h-5" />
          Report Configuration
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Date Range</label>
            <div className="space-y-2">
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                className="cyber-input w-full"
                title="Start date"
                placeholder="Start date"
              />
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                className="cyber-input w-full"
                title="End date"
                placeholder="End date"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Quick Actions</label>
            <div className="space-y-2">
              <button
                onClick={() => {
                  setDateRange({
                    start: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                    end: new Date().toISOString().split('T')[0]
                  });
                }}
                className="w-full p-2 bg-glass-light border border-glass-medium rounded-lg text-sm hover:bg-glass-medium transition-colors"
              >
                Last 24 Hours
              </button>
              <button
                onClick={() => {
                  setDateRange({
                    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                    end: new Date().toISOString().split('T')[0]
                  });
                }}
                className="w-full p-2 bg-glass-light border border-glass-medium rounded-lg text-sm hover:bg-glass-medium transition-colors"
              >
                Last 7 Days
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="flex-1 overflow-y-auto scrollbar-cyber">
        {reports.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="glass-card p-8 max-w-md mx-auto">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Reports Generated</h3>
              <p className="text-gray-400 text-sm">
                Generate your first security report using the configuration above
              </p>
            </div>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {reports.map((report, index) => (
              <motion.div
                key={report.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-2">{report.title}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {report.generatedAt.toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <motion.button
                      onClick={() => handleDownload(report.id, 'pdf')}
                      className="p-2 bg-glass-light border border-glass-medium rounded-lg hover:bg-glass-medium transition-colors"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Download className="w-4 h-4" />
                    </motion.button>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-gray-300">{report.summary}</p>
                </div>

                {report.findings.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">Key Findings:</h4>
                    <div className="space-y-2">
                      {report.findings.map((finding: any, idx: number) => (
                        <div
                          key={idx}
                          className="p-3 rounded-lg border border-glass-medium bg-glass-light"
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium">{finding.category}</span>
                            <span className="text-xs px-2 py-1 rounded-full bg-orange-500/20 text-orange-400">
                              {finding.severity.toUpperCase()}
                            </span>
                          </div>
                          <p className="text-gray-300 text-sm">{finding.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};
