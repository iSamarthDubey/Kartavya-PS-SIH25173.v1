import React, { useState } from 'react';
import { FileText, Download, Calendar, Filter, BarChart3 } from 'lucide-react';

interface ReportsProps {
  isConnected: boolean;
}

const Reports: React.FC<ReportsProps> = ({ isConnected }) => {
  const [selectedReport, setSelectedReport] = useState('');

  const reportTemplates = [
    { id: 'security-summary', name: 'Security Summary Report', desc: 'Daily/Weekly/Monthly security overview' },
    { id: 'incident-details', name: 'Incident Investigation Report', desc: 'Detailed analysis of security incidents' },
    { id: 'threat-intelligence', name: 'Threat Intelligence Report', desc: 'Latest threats and indicators' },
    { id: 'compliance-audit', name: 'Compliance Audit Report', desc: 'Regulatory compliance status' },
    { id: 'user-activity', name: 'User Activity Report', desc: 'User behavior and access patterns' },
    { id: 'network-analysis', name: 'Network Security Analysis', desc: 'Network traffic and anomalies' },
  ];

  const recentReports = [
    { id: 1, name: 'Weekly Security Summary - Jan 2025', type: 'Security Summary', date: '2025-01-08', status: 'completed' },
    { id: 2, name: 'Malware Incident Investigation', type: 'Incident Details', date: '2025-01-07', status: 'completed' },
    { id: 3, name: 'Monthly Compliance Report', type: 'Compliance Audit', date: '2025-01-05', status: 'processing' },
    { id: 4, name: 'Network Analysis - December', type: 'Network Analysis', date: '2025-01-01', status: 'completed' },
  ];

  const generateReport = () => {
    if (!selectedReport) return;
    
    // This would call your backend's report generation API
    console.log('Generating report:', selectedReport);
    alert(`Report "${selectedReport}" generation started. You'll receive an email when it's ready.`);
  };

  return (
    <div className="space-y-6">
      {/* Generate New Report */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-blue-400" />
          Generate New Report
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {reportTemplates.map((template) => (
            <div
              key={template.id}
              onClick={() => setSelectedReport(template.id)}
              className={`p-4 border-2 rounded-xl cursor-pointer transition-all ${
                selectedReport === template.id
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
              }`}
            >
              <h4 className="text-white font-medium mb-2">{template.name}</h4>
              <p className="text-sm text-gray-400">{template.desc}</p>
            </div>
          ))}
        </div>

        <div className="flex items-center space-x-4 mb-4">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <select className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white">
              <option>Last 24 hours</option>
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Custom range</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white">
              <option>All severity levels</option>
              <option>Critical only</option>
              <option>High & Critical</option>
              <option>Medium & above</option>
            </select>
          </div>
        </div>

        <button
          onClick={generateReport}
          disabled={!selectedReport}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
        >
          Generate Report
        </button>
      </div>

      {/* Recent Reports */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <FileText className="w-5 h-5 mr-2 text-green-400" />
          Recent Reports
        </h3>
        
        <div className="space-y-3">
          {recentReports.map((report) => (
            <div key={report.id} className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg border border-gray-600">
              <div className="flex items-center space-x-4">
                <div className={`w-3 h-3 rounded-full ${
                  report.status === 'completed' ? 'bg-green-500' :
                  report.status === 'processing' ? 'bg-yellow-500 animate-pulse' : 'bg-gray-500'
                }`}></div>
                
                <div>
                  <h4 className="text-white font-medium">{report.name}</h4>
                  <p className="text-sm text-gray-400">{report.type} • {report.date}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  report.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                  report.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-gray-500/20 text-gray-400'
                }`}>
                  {report.status}
                </span>
                
                {report.status === 'completed' && (
                  <button className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors">
                    <Download className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Reports Generated</p>
              <p className="text-2xl font-bold text-white">47</p>
            </div>
            <FileText className="w-6 h-6 text-blue-400" />
          </div>
        </div>
        
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">This Month</p>
              <p className="text-2xl font-bold text-white">12</p>
            </div>
            <Calendar className="w-6 h-6 text-green-400" />
          </div>
        </div>
        
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">Avg. Generation Time</p>
              <p className="text-2xl font-bold text-white">2.3m</p>
            </div>
            <BarChart3 className="w-6 h-6 text-yellow-400" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
