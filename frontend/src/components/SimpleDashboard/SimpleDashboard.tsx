/**
 * KARTAVYA SIEM - Sample Dashboard to Show All Features
 * Comprehensive showcase of all components and visualizations
 */

import React, { useState, useEffect } from 'react';
import { 
  Shield, Activity, BarChart3, TrendingUp, AlertTriangle, Globe, 
  Download, Play, Settings, Clock, Target, Users, Server, Database,
  Eye, Hash, Mail, FileText, Wifi, Brain, Smartphone
} from 'lucide-react';
import MiniCharts from '../MiniCharts/MiniCharts';
import QueryPreview from '../QueryPreview/QueryPreview';
import ContextStrip from '../ContextStrip/ContextStrip';
import EntityDisplay from '../EntityDisplay/EntityDisplay';
import AdvancedEntityDisplay from '../AdvancedEntityDisplay/AdvancedEntityDisplay';
import ResultTable from '../ResultTable/ResultTable';
import { advancedEntityRecognizer, AdvancedSecurityEntity } from '../../services/advancedEntityRecognition';

const SimpleDashboard: React.FC = () => {
  const [activeFilters, setActiveFilters] = useState([
    { type: 'event_type', value: 'authentication_failure', label: 'Auth Failures' },
    { type: 'severity', value: 'high', label: 'High Severity' }
  ]);

  // Sample data for all components
  const sampleQuery = {
    dsl: {
      "query": {
        "bool": {
          "must": [
            { "match": { "event.action": "authentication_failure" } },
            { "range": { "@timestamp": { "gte": "now-24h" } } }
          ]
        }
      }
    },
    kql: 'event.action:"authentication_failure" AND @timestamp >= "now-24h"',
    confidence: 0.92
  };

  const sampleChartData = {
    timeline: [
      { label: '00:00', value: 23, timestamp: '2025-01-10T00:00:00Z' },
      { label: '04:00', value: 45, timestamp: '2025-01-10T04:00:00Z' },
      { label: '08:00', value: 67, timestamp: '2025-01-10T08:00:00Z' },
      { label: '12:00', value: 89, timestamp: '2025-01-10T12:00:00Z' },
      { label: '16:00', value: 34, timestamp: '2025-01-10T16:00:00Z' },
      { label: '20:00', value: 56, timestamp: '2025-01-10T20:00:00Z' },
      { label: '24:00', value: 78, timestamp: '2025-01-10T24:00:00Z' }
    ],
    eventTypes: [
      { label: 'Auth Failures', value: 234, color: '#EF4444' },
      { label: 'Malware Detection', value: 89, color: '#F97316' },
      { label: 'Network Anomaly', value: 156, color: '#EAB308' },
      { label: 'Data Access', value: 67, color: '#22C55E' },
      { label: 'Privilege Escalation', value: 23, color: '#8B5CF6' }
    ],
    riskTrend: [
      { label: 'Mon', value: 45 },
      { label: 'Tue', value: 52 },
      { label: 'Wed', value: 48 },
      { label: 'Thu', value: 67 },
      { label: 'Fri', value: 74 },
      { label: 'Sat', value: 69 },
      { label: 'Sun', value: 82 }
    ]
  };

  const sampleEntities: AdvancedSecurityEntity[] = [
    {
      text: '192.168.1.100',
      type: 'ip_address',
      start_position: 0,
      end_position: 13,
      confidence: 0.95,
      risk_score: 0.8,
      description: 'Suspicious IP with multiple failed login attempts',
      enrichment: {
        reputation: 'suspicious',
        threat_types: ['brute_force', 'reconnaissance'],
        geo_location: { country: 'Unknown', city: 'Unknown' }
      }
    },
    {
      text: 'malicious-domain.com',
      type: 'domain',
      start_position: 0,
      end_position: 19,
      confidence: 0.88,
      risk_score: 0.9,
      description: 'Known malicious domain associated with malware campaigns',
      enrichment: {
        reputation: 'malicious',
        threat_types: ['c2', 'malware_distribution']
      }
    },
    {
      text: 'T1566.001',
      type: 'mitre_technique',
      start_position: 0,
      end_position: 9,
      confidence: 0.92,
      risk_score: 0.75,
      description: 'MITRE ATT&CK Technique: Spearphishing Attachment',
      enrichment: {
        reputation: 'suspicious',
        threat_types: ['initial_access', 'phishing']
      }
    },
    {
      text: 'IoT-Device-001',
      type: 'device_id',
      start_position: 0,
      end_position: 14,
      confidence: 0.90,
      risk_score: 0.6,
      description: 'IoT device showing anomalous network behavior',
      enrichment: {
        reputation: 'suspicious',
        threat_types: ['iot_compromise', 'botnet']
      }
    }
  ];

  const sampleResultData = [
    {
      '@timestamp': '2025-01-10T15:30:45.123Z',
      event_type: 'authentication_failure',
      severity: 'high',
      source_ip: '192.168.1.100',
      user: 'admin',
      result: 'blocked',
      risk_score: 85,
      message: 'Multiple failed login attempts detected'
    },
    {
      '@timestamp': '2025-01-10T15:25:12.456Z',
      event_type: 'malware_detection',
      severity: 'critical',
      source_ip: '10.0.0.15',
      user: 'john.doe',
      result: 'quarantined',
      risk_score: 95,
      message: 'Trojan.Win32.Malware detected and quarantined'
    },
    {
      '@timestamp': '2025-01-10T15:20:33.789Z',
      event_type: 'network_anomaly',
      severity: 'medium',
      source_ip: '172.16.0.50',
      user: 'system',
      result: 'investigating',
      risk_score: 65,
      message: 'Unusual network traffic pattern detected'
    },
    {
      '@timestamp': '2025-01-10T15:15:22.101Z',
      event_type: 'data_exfiltration',
      severity: 'critical',
      source_ip: '203.0.113.45',
      user: 'jane.smith',
      result: 'escalated',
      risk_score: 92,
      message: 'Large data transfer to external IP detected'
    },
    {
      '@timestamp': '2025-01-10T15:10:15.222Z',
      event_type: 'privilege_escalation',
      severity: 'high',
      source_ip: '192.168.2.25',
      user: 'service_account',
      result: 'allowed',
      risk_score: 78,
      message: 'User privilege escalation attempt'
    }
  ];

  const handleActionClick = (actionId: string, data?: any) => {
    console.log(`🚀 Sample Dashboard Action: ${actionId}`, data);
    alert(`🔥 KARTAVYA SIEM Sample: Executing ${actionId} action`);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center">
            <Shield className="w-10 h-10 text-blue-400 mr-4" />
            KARTAVYA SIEM - Component Showcase
          </h1>
          <p className="text-lg text-gray-400">Complete demonstration of all SIEM components and features</p>
        </div>

        {/* 1. Context Strip Component */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Settings className="w-6 h-6 text-blue-400 mr-3" />
            Context Strip - Active Filters
          </h2>
          <ContextStrip 
            filters={activeFilters}
            onFilterChange={setActiveFilters}
            queryStats={{
              totalEvents: 1547,
              queryTime: 0.234,
              isLoading: false
            }}
          />
        </div>

        {/* 2. Query Preview Component */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Play className="w-6 h-6 text-green-400 mr-3" />
            Query Preview - KQL & DSL
          </h2>
          <QueryPreview query={sampleQuery} />
        </div>

        {/* 3. MiniCharts Components */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <BarChart3 className="w-6 h-6 text-purple-400 mr-3" />
            MiniCharts - Interactive Visualizations
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Timeline Chart */}
            <MiniCharts 
              data={sampleChartData.timeline}
              type="sparkline"
              title="24-Hour Threat Activity"
              height={100}
              onClick={(dataPoint) => handleActionClick('drill_timeline', dataPoint)}
            />
            
            {/* Event Types Bar Chart */}
            <MiniCharts 
              data={sampleChartData.eventTypes}
              type="bar"
              title="Event Types Distribution"
              height={100}
              onClick={(dataPoint) => handleActionClick('filter_event_type', dataPoint)}
            />
            
            {/* Risk Trend Timeline */}
            <MiniCharts 
              data={sampleChartData.riskTrend}
              type="timeline"
              title="Weekly Risk Score Trend"
              height={100}
              onClick={(dataPoint) => handleActionClick('analyze_risk', dataPoint)}
            />
          </div>
        </div>

        {/* 4. Advanced Entity Display Components */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Target className="w-6 h-6 text-red-400 mr-3" />
            Advanced Entity Display - Security Entities
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {sampleEntities.map((entity, index) => (
              <div key={index}>
                <h3 className="text-sm font-semibold text-gray-400 mb-2">
                  {entity.type.replace('_', ' ').toUpperCase()} Entity
                </h3>
                <AdvancedEntityDisplay
                  entity={entity}
                  onActionTaken={(action, ent) => handleActionClick(action, ent)}
                />
              </div>
            ))}
          </div>
        </div>

        {/* 5. Result Table Component */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Database className="w-6 h-6 text-cyan-400 mr-3" />
            Result Table - SIEM Data Grid
          </h2>
          
          <ResultTable 
            data={sampleResultData}
            title="Security Events Analysis"
            pageSize={5}
            onRowAction={(action, row) => handleActionClick(`table_${action}`, row)}
          />
        </div>

        {/* 6. Metrics Summary Cards */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Activity className="w-6 h-6 text-yellow-400 mr-3" />
            Live SIEM Metrics
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-2 mb-2">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <span className="text-sm text-gray-400">Critical Alerts</span>
              </div>
              <div className="text-2xl font-bold text-red-400">23</div>
            </div>
            
            <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <span className="text-sm text-gray-400">Risk Score</span>
              </div>
              <div className="text-2xl font-bold text-green-400">78%</div>
            </div>
            
            <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-2 mb-2">
                <Users className="w-5 h-5 text-blue-400" />
                <span className="text-sm text-gray-400">Affected Users</span>
              </div>
              <div className="text-2xl font-bold text-blue-400">156</div>
            </div>
            
            <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center space-x-2 mb-2">
                <Server className="w-5 h-5 text-purple-400" />
                <span className="text-sm text-gray-400">Systems Online</span>
              </div>
              <div className="text-2xl font-bold text-purple-400">847</div>
            </div>
          </div>
        </div>

        {/* 7. Action Buttons Panel */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
            <Shield className="w-6 h-6 text-emerald-400 mr-3" />
            Security Actions
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => handleActionClick('download_report')}
              className="flex items-center justify-center space-x-2 p-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-white"
            >
              <Download className="w-5 h-5" />
              <span>Download Report</span>
            </button>
            
            <button
              onClick={() => handleActionClick('create_alert')}
              className="flex items-center justify-center space-x-2 p-4 bg-red-600 hover:bg-red-700 rounded-lg transition-colors text-white"
            >
              <AlertTriangle className="w-5 h-5" />
              <span>Create Alert</span>
            </button>
            
            <button
              onClick={() => handleActionClick('run_analysis')}
              className="flex items-center justify-center space-x-2 p-4 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors text-white"
            >
              <Play className="w-5 h-5" />
              <span>Run Analysis</span>
            </button>
            
            <button
              onClick={() => handleActionClick('schedule_scan')}
              className="flex items-center justify-center space-x-2 p-4 bg-green-600 hover:bg-green-700 rounded-lg transition-colors text-white"
            >
              <Clock className="w-5 h-5" />
              <span>Schedule Scan</span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center py-8">
          <p className="text-gray-500">
            🔥 KARTAVYA SIEM - All components are interactive and ready for production use
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleDashboard;
