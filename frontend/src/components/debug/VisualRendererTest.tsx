import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Eye, EyeOff } from 'lucide-react'
import VisualRenderer from '../Chat/VisualRenderer'
import { VisualPayload, VisualCard } from '../../types'

interface VisualTestCase {
  name: string
  description: string
  payload: VisualPayload
}

const generateSampleData = () => ({
  // Sample time series data for security events
  timeSeriesData: Array.from({ length: 24 }, (_, i) => ({
    timestamp: `${String(i).padStart(2, '0')}:00`,
    failed_logins: Math.floor(Math.random() * 50) + 10,
    successful_logins: Math.floor(Math.random() * 200) + 50,
    x: `${String(i).padStart(2, '0')}:00`,
    y: Math.floor(Math.random() * 50) + 10
  })),

  // Sample threat distribution data
  threatData: [
    { name: 'Malware', value: 45, count: 145 },
    { name: 'Phishing', value: 32, count: 98 },
    { name: 'DDoS', value: 18, count: 67 },
    { name: 'Brute Force', value: 25, count: 89 },
    { name: 'SQL Injection', value: 12, count: 23 }
  ],

  // Sample geographic data
  locationData: [
    { name: 'United States', ip: '192.168.1.1', count: 245, events: 245, coordinates: { lat: 39.8283, lng: -98.5795 } },
    { name: 'China', ip: '10.0.0.1', count: 189, events: 189, coordinates: { lat: 35.8617, lng: 104.1954 } },
    { name: 'Russia', ip: '172.16.0.1', count: 156, events: 156, coordinates: { lat: 61.5240, lng: 105.3188 } },
    { name: 'Germany', ip: '192.168.10.1', count: 134, events: 134, coordinates: { lat: 51.1657, lng: 10.4515 } },
    { name: 'Brazil', ip: '10.1.1.1', count: 98, events: 98, coordinates: { lat: -14.2350, lng: -51.9253 } }
  ],

  // Sample network topology data
  networkData: {
    nodes: [
      { id: '192.168.1.1', name: 'Web Server', type: 'source' },
      { id: '192.168.1.100', name: 'Database', type: 'target' },
      { id: '10.0.0.1', name: 'External Host', type: 'source' },
      { id: '172.16.0.1', name: 'DMZ Server', type: 'target' },
      { id: '192.168.1.50', name: 'Admin Workstation', type: 'source' }
    ],
    edges: [
      { source: '10.0.0.1', target: '192.168.1.1', weight: 145 },
      { source: '192.168.1.1', target: '192.168.1.100', weight: 89 },
      { source: '172.16.0.1', target: '192.168.1.100', weight: 67 },
      { source: '192.168.1.50', target: '192.168.1.1', weight: 23 }
    ]
  },

  // Sample tabular data
  incidentData: [
    ['2024-01-15 14:30', 'High', 'Failed Login Attempt', '192.168.1.100', 'admin'],
    ['2024-01-15 14:32', 'Medium', 'Port Scan Detected', '10.0.0.1', 'system'],
    ['2024-01-15 14:35', 'Low', 'File Access', '192.168.1.50', 'user1'],
    ['2024-01-15 14:37', 'High', 'Malware Signature', '172.16.0.1', 'system'],
    ['2024-01-15 14:40', 'Critical', 'Data Exfiltration', '192.168.1.100', 'admin']
  ]
})

export default function VisualRendererTest() {
  const [selectedTest, setSelectedTest] = useState<string>('composite')
  const [showPayload, setShowPayload] = useState<boolean>(false)
  
  const sampleData = generateSampleData()

  const testCases: VisualTestCase[] = [
    {
      name: 'composite',
      description: 'Complete security dashboard with multiple card types',
      payload: {
        type: 'composite',
        cards: [
          {
            type: 'summary_card',
            title: 'Total Threats Detected',
            value: 1247
          },
          {
            type: 'summary_card', 
            title: 'Critical Incidents',
            value: 23
          },
          {
            type: 'summary_card',
            title: 'Active Connections',
            value: 456
          },
          {
            type: 'summary_card',
            title: 'Blocked IPs',
            value: 89
          },
          {
            type: 'chart',
            title: 'Failed Login Attempts (Last 24h)',
            chart_type: 'timeseries',
            data: sampleData.timeSeriesData,
            config: {
              x_field: 'timestamp',
              y_field: 'failed_logins',
              color: '#FF7A00'
            }
          },
          {
            type: 'chart',
            title: 'Threat Distribution',
            chart_type: 'pie',
            data: sampleData.threatData,
            config: {
              color_field: 'name',
              size_field: 'value'
            }
          },
          {
            type: 'table',
            title: 'Recent Security Incidents',
            columns: [
              { key: 'timestamp', label: 'Timestamp', type: 'date' },
              { key: 'severity', label: 'Severity', type: 'string' },
              { key: 'event', label: 'Event Type', type: 'string' },
              { key: 'source_ip', label: 'Source IP', type: 'string' },
              { key: 'user', label: 'User', type: 'string' }
            ],
            rows: sampleData.incidentData
          }
        ]
      }
    },
    {
      name: 'charts',
      description: 'Various chart types with dynamic field mapping',
      payload: {
        type: 'composite',
        cards: [
          {
            type: 'chart',
            title: 'Login Events Timeline',
            chart_type: 'line',
            data: sampleData.timeSeriesData,
            config: {
              x_field: 'timestamp',
              y_field: 'successful_logins',
              color: '#00EFFF',
              strokeWidth: 2
            }
          },
          {
            type: 'chart',
            title: 'Threat Severity Levels',
            chart_type: 'bar',
            data: [
              { severity: 'Critical', events: 23 },
              { severity: 'High', events: 67 },
              { severity: 'Medium', events: 145 },
              { severity: 'Low', events: 298 }
            ],
            config: {
              x_field: 'severity',
              y_field: 'events',
              color: '#FF7A00'
            }
          },
          {
            type: 'chart',
            title: 'Network Traffic Volume',
            chart_type: 'area',
            data: sampleData.timeSeriesData.map(item => ({
              time: item.timestamp,
              volume: item.failed_logins + item.successful_logins
            })),
            config: {
              x_field: 'time',
              y_field: 'volume',
              color: '#22D3EE'
            }
          }
        ]
      }
    },
    {
      name: 'geospatial',
      description: 'Geographic threat analysis',
      payload: {
        type: 'composite',
        cards: [
          {
            type: 'map',
            title: 'Threat Origins by Geographic Location',
            data: sampleData.locationData
          },
          {
            type: 'chart',
            title: 'Top Attack Sources',
            chart_type: 'bar',
            data: sampleData.locationData.map(loc => ({
              country: loc.name,
              attacks: loc.count
            })),
            config: {
              x_field: 'country',
              y_field: 'attacks'
            }
          }
        ]
      }
    },
    {
      name: 'network',
      description: 'Network topology and connection analysis',
      payload: {
        type: 'composite',
        cards: [
          {
            type: 'network_graph',
            title: 'Network Attack Patterns',
            data: sampleData.networkData
          },
          {
            type: 'summary_card',
            title: 'Network Nodes',
            value: sampleData.networkData.nodes.length
          },
          {
            type: 'summary_card',
            title: 'Active Connections',
            value: sampleData.networkData.edges.length
          }
        ]
      }
    },
    {
      name: 'narrative',
      description: 'AI-generated security analysis report',
      payload: {
        type: 'narrative',
        value: `Based on the security analysis of the last 24 hours, we have identified several concerning patterns:

**Key Findings:**
- **1,247 total threats** were detected across all monitored systems
- **23 critical incidents** require immediate attention
- **Geographic concentration**: 67% of attacks originated from China, Russia, and Eastern Europe
- **Attack vectors**: Failed login attempts increased by 145% compared to yesterday

**Recommendations:**
1. **Immediate**: Implement IP-based blocking for the top 10 attacking sources
2. **Short-term**: Enhance monitoring on database servers (192.168.1.100)
3. **Long-term**: Deploy additional intrusion detection systems in the DMZ

**Risk Assessment:** Current threat level is **HIGH**. The attack pattern suggests a coordinated effort targeting our authentication systems.`
      }
    }
  ]

  const currentTest = testCases.find(test => test.name === selectedTest)

  const refreshData = () => {
    // In a real application, this would fetch new data
    window.location.reload()
  }

  return (
    <div className="space-y-8">
      {/* Test Controls */}
      <div className="bg-synrgy-surface border border-synrgy-primary/20 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-synrgy-text">Visual Renderer Test Suite</h2>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowPayload(!showPayload)}
              className={`px-4 py-2 rounded-lg border transition-all ${
                showPayload 
                  ? 'bg-synrgy-accent/20 border-synrgy-accent text-synrgy-accent' 
                  : 'border-synrgy-primary/20 text-synrgy-muted hover:border-synrgy-primary/40'
              } flex items-center gap-2`}
            >
              {showPayload ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              {showPayload ? 'Hide Payload' : 'Show Payload'}
            </button>
            <button
              onClick={refreshData}
              className="px-4 py-2 bg-synrgy-primary text-synrgy-bg-900 rounded-lg hover:bg-synrgy-primary/90 flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh Data
            </button>
          </div>
        </div>

        {/* Test Case Selector */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          {testCases.map((testCase) => (
            <button
              key={testCase.name}
              onClick={() => setSelectedTest(testCase.name)}
              className={`p-4 rounded-lg border text-left transition-all ${
                selectedTest === testCase.name
                  ? 'bg-synrgy-primary/10 border-synrgy-primary text-synrgy-primary'
                  : 'border-synrgy-primary/20 text-synrgy-muted hover:border-synrgy-primary/40'
              }`}
            >
              <div className="font-medium mb-1 capitalize">{testCase.name}</div>
              <div className="text-xs opacity-75">{testCase.description}</div>
            </button>
          ))}
        </div>

        {/* Payload Display */}
        {showPayload && currentTest && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-6 bg-synrgy-bg-900 border border-synrgy-primary/20 rounded-lg p-4"
          >
            <div className="text-sm font-medium text-synrgy-text mb-2">Current Payload JSON:</div>
            <pre className="text-xs text-synrgy-muted overflow-auto max-h-64">
              {JSON.stringify(currentTest.payload, null, 2)}
            </pre>
          </motion.div>
        )}
      </div>

      {/* Visual Renderer Output */}
      {currentTest && (
        <motion.div
          key={selectedTest}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <VisualRenderer 
            payload={currentTest.payload}
            className="space-y-6"
          />
        </motion.div>
      )}
    </div>
  )
}
