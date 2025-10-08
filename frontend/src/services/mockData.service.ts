/**
 * KARTAVYA SIEM - Dynamic Mock Data Service
 * Generates realistic, dynamic SIEM data for demo purposes
 */

import { 
  SecurityAlert, 
  DashboardMetrics, 
  ChatMessage, 
  NetworkTraffic, 
  UserActivity, 
  SystemStatus 
} from './api.service';

// ============= REALISTIC DATA GENERATORS =============

class MockDataService {
  private static instance: MockDataService;
  private startTime: number;
  private alertCount: number = 0;
  private incidentCount: number = 0;

  constructor() {
    this.startTime = Date.now();
  }

  static getInstance(): MockDataService {
    if (!MockDataService.instance) {
      MockDataService.instance = new MockDataService();
    }
    return MockDataService.instance;
  }

  // ============= SECURITY ALERTS =============

  private threatTypes = [
    'Malware Detection', 'Phishing Attempt', 'DDoS Attack', 'SQL Injection',
    'Cross-Site Scripting', 'Brute Force Attack', 'Data Exfiltration',
    'Privilege Escalation', 'Suspicious Network Activity', 'Unauthorized Access',
    'Ransomware Activity', 'Command & Control Communication', 'Port Scanning',
    'Vulnerability Exploitation', 'Account Compromise'
  ];

  private ipAddresses = [
    '192.168.1.100', '10.0.0.45', '172.16.0.23', '203.45.67.89',
    '45.32.11.78', '185.220.101.42', '91.198.174.192', '104.248.155.73'
  ];

  private sources = [
    'Firewall', 'IDS/IPS', 'Antivirus', 'EDR', 'Network Monitor',
    'Web Proxy', 'Email Security', 'DNS Monitor', 'SIEM Correlation Engine'
  ];

  generateSecurityAlerts(count: number = 20): SecurityAlert[] {
    const alerts: SecurityAlert[] = [];
    const severities: Array<'critical' | 'high' | 'medium' | 'low'> = ['critical', 'high', 'medium', 'low'];
    const statuses: Array<'active' | 'investigating' | 'resolved'> = ['active', 'investigating', 'resolved'];

    for (let i = 0; i < count; i++) {
      const severity = severities[Math.floor(Math.random() * severities.length)];
      const threat = this.threatTypes[Math.floor(Math.random() * this.threatTypes.length)];
      const ip = this.ipAddresses[Math.floor(Math.random() * this.ipAddresses.length)];
      const source = this.sources[Math.floor(Math.random() * this.sources.length)];
      
      alerts.push({
        id: `alert-${Date.now()}-${i}`,
        title: `${threat} Detected`,
        description: `Suspicious activity detected from ${ip}. ${this.generateThreatDescription(threat)}`,
        severity,
        timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(), // Last 24 hours
        source,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        assignee: Math.random() > 0.5 ? 'security.analyst@kartavya.com' : undefined
      });
    }

    return alerts.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  private generateThreatDescription(threat: string): string {
    const descriptions: Record<string, string[]> = {
      'Malware Detection': [
        'Trojan.Win32.Agent variant identified in system memory',
        'Suspicious executable with known malware signature detected',
        'Potential ransomware encryption behavior observed'
      ],
      'Phishing Attempt': [
        'Email contains suspicious links redirecting to credential harvesting site',
        'Domain reputation indicates known phishing infrastructure',
        'Attachment contains macro with suspicious PowerShell commands'
      ],
      'DDoS Attack': [
        'Abnormal traffic volume detected from multiple source IPs',
        'SYN flood attack pattern identified on web services',
        'Network bandwidth saturation detected'
      ],
      'SQL Injection': [
        'Union-based SQL injection attempt in web application login form',
        'Database query manipulation detected in user input',
        'Error-based SQL injection payload identified'
      ]
    };

    const threatDescriptions = descriptions[threat] || ['Suspicious security event detected'];
    return threatDescriptions[Math.floor(Math.random() * threatDescriptions.length)];
  }

  // ============= DASHBOARD METRICS =============

  generateDashboardMetrics(): DashboardMetrics {
    const now = Date.now();
    const hoursRunning = Math.floor((now - this.startTime) / (1000 * 60 * 60));
    
    // Dynamic values that change over time
    const baseThreats = 1247 + Math.floor(Math.sin(now / 100000) * 50);
    const activeAlerts = 23 + Math.floor(Math.cos(now / 80000) * 15);
    const systemsOnline = 98.5 + Math.sin(now / 200000) * 1.5;
    const incidentsToday = 5 + Math.floor(hoursRunning / 2) + Math.floor(Math.random() * 3);

    return {
      totalThreats: Math.max(0, baseThreats),
      activeAlerts: Math.max(0, activeAlerts),
      systemsOnline: Math.min(100, Math.max(95, systemsOnline)),
      incidentsToday: incidentsToday,
      threatTrends: this.generateThreatTrends(),
      topThreats: this.generateTopThreats()
    };
  }

  private generateThreatTrends(): Array<{ date: string; count: number }> {
    const trends = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const baseCount = 150;
      const variation = Math.sin(i * 0.5) * 30 + Math.random() * 40;
      trends.push({
        date: date.toISOString().split('T')[0],
        count: Math.floor(baseCount + variation)
      });
    }
    return trends;
  }

  private generateTopThreats(): Array<{ name: string; count: number; severity: string }> {
    const threats = [
      { name: 'Malware Detection', severity: 'critical' },
      { name: 'Phishing Attempts', severity: 'high' },
      { name: 'Brute Force Attacks', severity: 'medium' },
      { name: 'DDoS Activity', severity: 'high' },
      { name: 'SQL Injection', severity: 'critical' }
    ];

    return threats.map(threat => ({
      ...threat,
      count: Math.floor(Math.random() * 100) + 20
    })).sort((a, b) => b.count - a.count);
  }

  // ============= NETWORK TRAFFIC =============

  generateNetworkTraffic(count: number = 100): NetworkTraffic[] {
    const traffic: NetworkTraffic[] = [];
    const protocols = ['HTTP', 'HTTPS', 'SSH', 'FTP', 'DNS', 'SMTP', 'TCP', 'UDP'];
    
    for (let i = 0; i < count; i++) {
      const timestamp = new Date(Date.now() - Math.random() * 3600000).toISOString();
      const sourceIp = this.ipAddresses[Math.floor(Math.random() * this.ipAddresses.length)];
      const destIp = this.ipAddresses[Math.floor(Math.random() * this.ipAddresses.length)];
      const protocol = protocols[Math.floor(Math.random() * protocols.length)];
      
      traffic.push({
        timestamp,
        source: sourceIp,
        destination: destIp,
        protocol,
        bytes: Math.floor(Math.random() * 1000000) + 1024,
        packets: Math.floor(Math.random() * 1000) + 10,
        suspicious: Math.random() < 0.1 // 10% suspicious activity
      });
    }

    return traffic.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  // ============= USER ACTIVITY =============

  private userNames = [
    'john.doe', 'jane.smith', 'mike.johnson', 'sarah.wilson', 'david.brown',
    'lisa.davis', 'chris.taylor', 'amy.anderson', 'robert.martinez', 'emily.garcia'
  ];

  private actions = [
    'Login', 'Logout', 'File Access', 'Database Query', 'System Admin',
    'Email Send', 'VPN Connect', 'Password Change', 'Permission Change', 'Download'
  ];

  generateUserActivity(count: number = 50): UserActivity[] {
    const activities: UserActivity[] = [];

    for (let i = 0; i < count; i++) {
      const username = this.userNames[Math.floor(Math.random() * this.userNames.length)];
      const action = this.actions[Math.floor(Math.random() * this.actions.length)];
      const ip = this.ipAddresses[Math.floor(Math.random() * this.ipAddresses.length)];
      
      activities.push({
        id: `activity-${Date.now()}-${i}`,
        userId: `user-${username.replace('.', '')}`,
        username,
        action,
        resource: this.generateResourceName(action),
        timestamp: new Date(Date.now() - Math.random() * 86400000).toISOString(),
        ipAddress: ip,
        riskScore: Math.floor(Math.random() * 100)
      });
    }

    return activities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  private generateResourceName(action: string): string {
    const resources: Record<string, string[]> = {
      'Login': ['/auth/login', '/sso/authenticate', '/portal/access'],
      'File Access': ['/documents/confidential/', '/reports/security/', '/logs/system/'],
      'Database Query': ['users_table', 'security_events', 'audit_logs'],
      'Email Send': ['external@domain.com', 'internal@company.com', 'security@alerts.com']
    };

    const actionResources = resources[action] || ['/system/resource'];
    return actionResources[Math.floor(Math.random() * actionResources.length)];
  }

  // ============= SYSTEM STATUS =============

  generateSystemStatus(): SystemStatus[] {
    const services = [
      'Firewall',
      'IDS/IPS',
      'SIEM Engine',
      'Log Collector',
      'Threat Intelligence',
      'Vulnerability Scanner',
      'Endpoint Detection',
      'Network Monitor'
    ];

    return services.map((service, index) => {
      const uptime = 99.5 + Math.random() * 0.5;
      const status = uptime > 99.8 ? 'online' : uptime > 99.0 ? 'degraded' : 'offline';
      
      return {
        service,
        status: status as 'online' | 'offline' | 'degraded',
        uptime: `${uptime.toFixed(1)}%`,
        lastCheck: new Date(Date.now() - Math.random() * 300000).toISOString(),
        metrics: {
          cpu: Math.floor(Math.random() * 100),
          memory: Math.floor(Math.random() * 100),
          disk: Math.floor(Math.random() * 100)
        }
      };
    });
  }

  // ============= CHAT RESPONSES =============

  private securityResponses = [
    "Based on the current threat landscape analysis, I've identified several indicators of compromise in your network traffic.",
    "The security alert you're investigating shows patterns consistent with a potential Advanced Persistent Threat (APT) group.",
    "I recommend implementing additional network segmentation to contain this suspicious activity.",
    "The log analysis reveals multiple failed authentication attempts from IP addresses in the 185.220.101.x range.",
    "Cross-referencing threat intelligence feeds, this attack vector matches known tactics used by the Lazarus group.",
    "The malware sample exhibits characteristics of a banking Trojan with data exfiltration capabilities.",
    "I suggest escalating this incident to Tier 2 analysts for deeper forensic investigation.",
    "The network traffic anomaly indicates possible DNS tunneling for command and control communication."
  ];

  generateChatResponse(userMessage: string): ChatMessage {
    // Simulate processing time
    const processingDelay = 1000 + Math.random() * 2000;
    
    // Generate contextual response based on message content
    let response = this.securityResponses[Math.floor(Math.random() * this.securityResponses.length)];
    
    if (userMessage.toLowerCase().includes('threat')) {
      response = "I've analyzed the current threat landscape and identified several high-priority indicators. The most concerning pattern involves lateral movement attempts across your network segments.";
    } else if (userMessage.toLowerCase().includes('alert')) {
      response = "The security alert requires immediate attention. Based on MITRE ATT&CK framework mapping, this appears to be Initial Access technique T1566 - Spearphishing Attachment.";
    } else if (userMessage.toLowerCase().includes('network')) {
      response = "Network analysis shows abnormal traffic patterns consistent with data exfiltration. I recommend implementing DLP policies and monitoring egress traffic more closely.";
    }

    return {
      id: `chat-${Date.now()}`,
      content: response,
      role: 'assistant',
      timestamp: new Date().toISOString(),
      metadata: {
        sources: ['MITRE ATT&CK', 'Threat Intelligence', 'Network Analysis'],
        confidence: 0.85 + Math.random() * 0.15,
        actions: ['Escalate Incident', 'Block IP', 'Update Rules']
      }
    };
  }

  // ============= REAL-TIME UPDATES =============

  simulateRealTimeUpdate(): { type: string; data: any } {
    const updateTypes = ['new_alert', 'system_status', 'network_spike', 'user_activity'];
    const type = updateTypes[Math.floor(Math.random() * updateTypes.length)];

    switch (type) {
      case 'new_alert':
        return {
          type: 'new_alert',
          data: this.generateSecurityAlerts(1)[0]
        };
      case 'system_status':
        return {
          type: 'system_status',
          data: { service: 'SIEM Engine', status: 'degraded', message: 'High CPU utilization detected' }
        };
      case 'network_spike':
        return {
          type: 'network_spike',
          data: { bandwidth: '2.3 GB/s', increase: '+45%', duration: '5 minutes' }
        };
      case 'user_activity':
        return {
          type: 'user_activity',
          data: this.generateUserActivity(1)[0]
        };
      default:
        return { type: 'ping', data: { timestamp: new Date().toISOString() } };
    }
  }
}

// ============= MOCK API SIMULATION =============

export class MockApiService {
  private mockData: MockDataService;

  constructor() {
    this.mockData = MockDataService.getInstance();
  }

  // Simulate API delay
  private async delay(ms: number = 300 + Math.random() * 700): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Dashboard APIs
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    await this.delay();
    return this.mockData.generateDashboardMetrics();
  }

  async getSecurityAlerts(limit = 50): Promise<SecurityAlert[]> {
    await this.delay();
    return this.mockData.generateSecurityAlerts(limit);
  }

  async getSystemStatus(): Promise<SystemStatus[]> {
    await this.delay();
    return this.mockData.generateSystemStatus();
  }

  // Chat APIs
  async sendChatMessage(message: string, sessionId?: string): Promise<ChatMessage> {
    await this.delay(1500); // Longer delay for chat responses
    return this.mockData.generateChatResponse(message);
  }

  async getChatHistory(sessionId: string): Promise<ChatMessage[]> {
    await this.delay();
    return []; // Return empty for new sessions
  }

  async createChatSession(): Promise<{ sessionId: string }> {
    await this.delay(200);
    return { sessionId: `session_${Date.now()}` };
  }

  // Network APIs
  async getNetworkTraffic(timeRange = '1h', limit = 100): Promise<NetworkTraffic[]> {
    await this.delay();
    return this.mockData.generateNetworkTraffic(limit);
  }

  // User Activity APIs
  async getUserActivity(limit = 50): Promise<UserActivity[]> {
    await this.delay();
    return this.mockData.generateUserActivity(limit);
  }

  // Health check that always works
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    await this.delay(100);
    return {
      status: 'healthy',
      timestamp: new Date().toISOString()
    };
  }

  // Real-time updates simulation
  startRealTimeUpdates(callback: (update: any) => void): () => void {
    const interval = setInterval(() => {
      const update = this.mockData.simulateRealTimeUpdate();
      callback(update);
    }, 5000 + Math.random() * 10000); // Random updates every 5-15 seconds

    return () => clearInterval(interval);
  }
}

export const mockApiService = new MockApiService();
export default mockApiService;
