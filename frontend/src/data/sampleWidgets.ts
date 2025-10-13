/**
 * Sample Dashboard Widgets for SYNRGY Demo
 * These mimic what the backend would provide
 */

import type { DashboardWidget } from '@/types'

export const sampleWidgets: DashboardWidget[] = [
  {
    id: 'security-alerts',
    type: 'summary_card',
    title: 'Active Security Alerts',
    data: {
      type: 'summary_card',
      title: 'Active Security Alerts',
      value: 24,
      trend: 'up',
      status: 'warning',
      comparison: {
        previous: 18,
        change: 6,
        period: 'vs yesterday',
      },
    },
    config: {
      color: 'warning',
      clickable: true,
    },
    position: {
      row: 0,
      col: 0,
      width: 1,
      height: 1,
    },
    last_updated: new Date().toISOString(),
  },
  {
    id: 'failed-logins',
    type: 'summary_card',
    title: 'Failed Login Attempts',
    data: {
      type: 'summary_card',
      title: 'Failed Login Attempts',
      value: 142,
      trend: 'down',
      status: 'success',
      comparison: {
        previous: 189,
        change: -47,
        period: 'vs yesterday',
      },
    },
    config: {
      color: 'success',
      clickable: true,
    },
    position: {
      row: 0,
      col: 1,
      width: 1,
      height: 1,
    },
    last_updated: new Date().toISOString(),
  },
  {
    id: 'threat-score',
    type: 'summary_card',
    title: 'Threat Score',
    data: {
      type: 'summary_card',
      title: 'Current Threat Score',
      value: 'Medium',
      status: 'warning',
      icon: 'shield',
    },
    config: {
      color: 'warning',
      clickable: true,
    },
    position: {
      row: 0,
      col: 2,
      width: 1,
      height: 1,
    },
    last_updated: new Date().toISOString(),
  },
  {
    id: 'response-time',
    type: 'summary_card',
    title: 'Avg Response Time',
    data: {
      type: 'summary_card',
      title: 'Average Response Time',
      value: '2.4m',
      trend: 'stable',
      status: 'success',
      unit: 'minutes',
    },
    config: {
      color: 'primary',
      clickable: true,
    },
    position: {
      row: 0,
      col: 3,
      width: 1,
      height: 1,
    },
    last_updated: new Date().toISOString(),
  },
  {
    id: 'alerts-timeline',
    type: 'chart',
    title: 'Security Events Over Time',
    data: {
      type: 'chart',
      chart_type: 'timeseries',
      title: 'Security Events Timeline',
      data: [
        { x: '00:00', y: 12 },
        { x: '02:00', y: 8 },
        { x: '04:00', y: 15 },
        { x: '06:00', y: 24 },
        { x: '08:00', y: 32 },
        { x: '10:00', y: 28 },
        { x: '12:00', y: 45 },
        { x: '14:00', y: 38 },
        { x: '16:00', y: 52 },
        { x: '18:00', y: 41 },
        { x: '20:00', y: 29 },
        { x: '22:00', y: 18 },
      ],
      config: {
        color: '#00EFFF',
        strokeWidth: 3,
      },
    },
    config: {
      clickable: true,
      interactive: true,
    },
    position: {
      row: 1,
      col: 0,
      width: 2,
      height: 2,
    },
    last_updated: new Date().toISOString(),
  },
  {
    id: 'top-threats',
    type: 'chart',
    title: 'Top Threat Categories',
    data: {
      type: 'chart',
      chart_type: 'bar',
      title: 'Top Threat Categories',
      data: [
        { x: 'Malware', y: 28 },
        { x: 'Phishing', y: 22 },
        { x: 'DDoS', y: 18 },
        { x: 'Intrusion', y: 15 },
        { x: 'Data Breach', y: 12 },
      ],
      config: {
        color: '#FF7A00',
      },
    },
    config: {
      clickable: true,
      interactive: true,
    },
    position: {
      row: 1,
      col: 2,
      width: 2,
      height: 2,
    },
    last_updated: new Date().toISOString(),
  },
  {
    id: 'recent-incidents',
    type: 'table',
    title: 'Recent Security Incidents',
    data: {
      type: 'table',
      title: 'Recent Security Incidents',
      columns: [
        { key: 'timestamp', label: 'Time', type: 'datetime' },
        { key: 'severity', label: 'Severity', type: 'string' },
        { key: 'type', label: 'Type', type: 'string' },
        { key: 'source', label: 'Source IP', type: 'ip' },
        { key: 'status', label: 'Status', type: 'string' },
      ],
      rows: [
        ['2024-01-15 14:23:12', 'High', 'Malware Detection', '192.168.1.45', 'Investigating'],
        ['2024-01-15 14:18:45', 'Critical', 'Data Exfiltration', '10.0.0.23', 'Blocked'],
        ['2024-01-15 14:15:33', 'Medium', 'Failed Login', '172.16.0.12', 'Resolved'],
        ['2024-01-15 14:12:21', 'High', 'Port Scan', '203.0.113.5', 'Monitoring'],
        ['2024-01-15 14:08:19', 'Low', 'File Access', '192.168.1.100', 'Logged'],
      ],
    },
    config: {
      clickable: true,
      sortable: true,
    },
    position: {
      row: 3,
      col: 0,
      width: 4,
      height: 2,
    },
    last_updated: new Date().toISOString(),
  },
]

// Add "Ask CYNRGY" context generators for each widget
export const getWidgetContextQuery = (widget: DashboardWidget, clickData?: any): string => {
  switch (widget.id) {
    case 'security-alerts':
      return clickData
        ? `Investigate the security alert spike. Show me details about the 24 active alerts and their severity breakdown.`
        : `Analyze the current security alerts. What are the main threats and recommended actions?`

    case 'failed-logins':
      return `Investigate the 142 failed login attempts. Show me the top source IPs and any patterns that indicate brute force attacks.`

    case 'threat-score':
      return `Explain the current "Medium" threat score. What factors contribute to this rating and what can we do to improve it?`

    case 'response-time':
      return `Analyze our 2.4 minute average response time. How does this compare to industry standards and where can we improve?`

    case 'alerts-timeline':
      return clickData
        ? `Investigate the security event spike at ${clickData.x || 'this time period'}. What caused the increase and what types of events occurred?`
        : `Analyze the security events timeline. What patterns do you see in the 24-hour period and are there any anomalies?`

    case 'top-threats':
      return clickData
        ? `Deep dive into ${clickData.x || 'this threat category'}. Show me specific incidents, affected systems, and mitigation strategies.`
        : `Analyze the top threat categories. Which threats require immediate attention and what's our current defense posture?`

    case 'recent-incidents':
      return clickData
        ? `Investigate this specific incident from ${clickData.timestamp || 'recent incidents'}. Provide timeline, impact assessment, and next steps.`
        : `Review the recent security incidents. What patterns emerge and what preventive measures should we implement?`

    default:
      return `Analyze the data in the ${widget.title} widget. What insights can you provide?`
  }
}
