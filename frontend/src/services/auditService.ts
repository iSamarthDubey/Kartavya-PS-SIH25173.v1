import { api } from './api';
import { User } from '../contexts/AuthContext';

// Audit event types
export type AuditEventType =
  | 'auth.login'
  | 'auth.logout'
  | 'auth.failed_login'
  | 'auth.password_change'
  | 'auth.mfa_enabled'
  | 'query.execute'
  | 'query.export'
  | 'investigation.create'
  | 'investigation.update'
  | 'investigation.close'
  | 'incident.create'
  | 'incident.escalate'
  | 'incident.resolve'
  | 'report.generate'
  | 'report.download'
  | 'alert.acknowledge'
  | 'alert.resolve'
  | 'settings.change'
  | 'data.access'
  | 'data.export'
  | 'admin.user_create'
  | 'admin.user_modify'
  | 'admin.role_change'
  | 'compliance.policy_update';

// Risk levels for audit events
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

// Audit event interface
export interface AuditEvent {
  id: string;
  timestamp: string;
  eventType: AuditEventType;
  userId: string;
  username: string;
  userRole: string;
  sessionId: string;
  ipAddress: string;
  userAgent: string;
  riskLevel: RiskLevel;
  success: boolean;
  details: {
    description: string;
    resource?: string;
    action?: string;
    oldValue?: any;
    newValue?: any;
    affectedUsers?: string[];
    dataAccessed?: string[];
    queryExecuted?: string;
    exportedData?: {
      type: string;
      recordCount: number;
      fileSize: string;
    };
    complianceImpact?: string;
    [key: string]: any;
  };
  metadata: {
    source: string;
    correlationId?: string;
    parentEventId?: string;
    tags?: string[];
  };
}

// Audit query filters
export interface AuditQueryFilters {
  startDate?: string;
  endDate?: string;
  eventTypes?: AuditEventType[];
  userIds?: string[];
  riskLevels?: RiskLevel[];
  success?: boolean;
  ipAddress?: string;
  resource?: string;
  limit?: number;
  offset?: number;
  sortBy?: 'timestamp' | 'riskLevel' | 'eventType';
  sortOrder?: 'asc' | 'desc';
}

// Compliance report types
export interface ComplianceReport {
  id: string;
  reportType: 'gdpr' | 'sox' | 'hipaa' | 'pci_dss' | 'iso_27001';
  generatedAt: string;
  period: {
    startDate: string;
    endDate: string;
  };
  summary: {
    totalEvents: number;
    highRiskEvents: number;
    failedAuthentications: number;
    dataAccessEvents: number;
    complianceScore: number;
    violations: number;
  };
  findings: ComplianceFinding[];
  recommendations: string[];
}

export interface ComplianceFinding {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  affectedUsers: string[];
  events: string[];
  remediation: string;
  dueDate?: string;
}

class AuditService {
  private static instance: AuditService;
  private eventQueue: AuditEvent[] = [];
  private batchSize = 10;
  private flushInterval = 5000; // 5 seconds
  private currentUser: User | null = null;
  private sessionId: string = '';

  private constructor() {
    // Start batch processing
    setInterval(() => this.flushEvents(), this.flushInterval);
  }

  public static getInstance(): AuditService {
    if (!AuditService.instance) {
      AuditService.instance = new AuditService();
    }
    return AuditService.instance;
  }

  // Set current user context
  public setUserContext(user: User | null, sessionId: string = '') {
    this.currentUser = user;
    this.sessionId = sessionId;
  }

  // Log an audit event
  public async logEvent(
    eventType: AuditEventType,
    details: Partial<AuditEvent['details']> = {},
    riskLevel: RiskLevel = 'low',
    success: boolean = true
  ): Promise<void> {
    const event: AuditEvent = {
      id: this.generateEventId(),
      timestamp: new Date().toISOString(),
      eventType,
      userId: this.currentUser?.id || 'anonymous',
      username: this.currentUser?.username || 'anonymous',
      userRole: this.currentUser?.role || 'unknown',
      sessionId: this.sessionId,
      ipAddress: await this.getClientIP(),
      userAgent: navigator.userAgent,
      riskLevel,
      success,
      details: {
        description: this.getEventDescription(eventType, details),
        ...details,
      },
      metadata: {
        source: 'frontend',
        correlationId: this.generateCorrelationId(),
        tags: this.generateTags(eventType, riskLevel),
      },
    };

    // Add to queue
    this.eventQueue.push(event);

    // Flush immediately for high/critical risk events
    if (riskLevel === 'high' || riskLevel === 'critical') {
      await this.flushEvents();
    }

    // Also log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[AUDIT]', event);
    }
  }

  // Common audit logging methods
  public async logLogin(success: boolean, details: any = {}) {
    await this.logEvent(
      success ? 'auth.login' : 'auth.failed_login',
      { ...details, loginMethod: details.mfaUsed ? 'password+mfa' : 'password' },
      success ? 'low' : 'medium',
      success
    );
  }

  public async logLogout() {
    await this.logEvent('auth.logout', { reason: 'user_initiated' }, 'low');
  }

  public async logQueryExecution(query: string, resultCount: number, executionTime: number) {
    await this.logEvent(
      'query.execute',
      {
        queryExecuted: this.redactSensitiveData(query),
        resultCount,
        executionTime,
        queryType: this.determineQueryType(query),
      },
      this.calculateQueryRisk(query, resultCount),
      true
    );
  }

  public async logDataExport(dataType: string, recordCount: number, format: string) {
    await this.logEvent(
      'data.export',
      {
        exportedData: {
          type: dataType,
          recordCount,
          fileSize: this.estimateFileSize(recordCount, format),
        },
        format,
      },
      recordCount > 10000 ? 'high' : recordCount > 1000 ? 'medium' : 'low'
    );
  }

  public async logIncidentCreation(incidentId: string, severity: string) {
    await this.logEvent(
      'incident.create',
      {
        resource: `incident:${incidentId}`,
        severity,
        action: 'create',
      },
      severity === 'critical' ? 'high' : 'medium'
    );
  }

  public async logSettingsChange(setting: string, oldValue: any, newValue: any) {
    await this.logEvent(
      'settings.change',
      {
        resource: `setting:${setting}`,
        action: 'update',
        oldValue: this.redactSensitiveData(oldValue),
        newValue: this.redactSensitiveData(newValue),
      },
      this.calculateSettingsRisk(setting),
      true
    );
  }

  // Query audit events
  public async getAuditEvents(filters: AuditQueryFilters = {}): Promise<{
    events: AuditEvent[];
    total: number;
    hasMore: boolean;
  }> {
    try {
      const response = await api.get('/audit/events', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch audit events:', error);
      throw error;
    }
  }

  // Generate compliance report
  public async generateComplianceReport(
    reportType: ComplianceReport['reportType'],
    startDate: string,
    endDate: string
  ): Promise<ComplianceReport> {
    try {
      const response = await api.post('/audit/compliance/report', {
        reportType,
        startDate,
        endDate,
      });

      // Log the report generation
      await this.logEvent(
        'report.generate',
        {
          reportType: `compliance:${reportType}`,
          period: { startDate, endDate },
        },
        'medium'
      );

      return response.data;
    } catch (error) {
      console.error('Failed to generate compliance report:', error);
      throw error;
    }
  }

  // Get user activity summary
  public async getUserActivitySummary(
    userId: string,
    days: number = 30
  ): Promise<{
    totalEvents: number;
    eventsByType: Record<AuditEventType, number>;
    riskDistribution: Record<RiskLevel, number>;
    recentEvents: AuditEvent[];
  }> {
    try {
      const endDate = new Date().toISOString();
      const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

      const response = await api.get(`/audit/users/${userId}/activity`, {
        params: { startDate, endDate },
      });

      return response.data;
    } catch (error) {
      console.error('Failed to fetch user activity:', error);
      throw error;
    }
  }

  // Private helper methods
  private async flushEvents(): Promise<void> {
    if (this.eventQueue.length === 0) return;

    const events = this.eventQueue.splice(0, this.batchSize);

    try {
      await api.post('/audit/events/batch', { events });
    } catch (error) {
      console.error('Failed to send audit events:', error);
      // Re-queue events for retry (but limit to prevent memory issues)
      if (this.eventQueue.length < 1000) {
        this.eventQueue.unshift(...events);
      }
    }
  }

  private generateEventId(): string {
    return `audit_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }

  private generateCorrelationId(): string {
    return `corr_${Date.now()}_${Math.random().toString(36).substring(2)}`;
  }

  private async getClientIP(): Promise<string> {
    // In a real implementation, this would be determined by the backend
    return 'client_ip_masked';
  }

  private getEventDescription(eventType: AuditEventType, details: any): string {
    const descriptions: Record<AuditEventType, string> = {
      'auth.login': 'User successfully logged in',
      'auth.logout': 'User logged out',
      'auth.failed_login': 'Failed login attempt',
      'auth.password_change': 'User changed password',
      'auth.mfa_enabled': 'Multi-factor authentication enabled',
      'query.execute': 'SIEM query executed',
      'query.export': 'Query results exported',
      'investigation.create': 'New investigation created',
      'investigation.update': 'Investigation updated',
      'investigation.close': 'Investigation closed',
      'incident.create': 'New incident created',
      'incident.escalate': 'Incident escalated',
      'incident.resolve': 'Incident resolved',
      'report.generate': 'Report generated',
      'report.download': 'Report downloaded',
      'alert.acknowledge': 'Alert acknowledged',
      'alert.resolve': 'Alert resolved',
      'settings.change': 'System settings modified',
      'data.access': 'Sensitive data accessed',
      'data.export': 'Data exported',
      'admin.user_create': 'New user account created',
      'admin.user_modify': 'User account modified',
      'admin.role_change': 'User role changed',
      'compliance.policy_update': 'Compliance policy updated',
    };

    return descriptions[eventType] || 'Unknown event';
  }

  private generateTags(eventType: AuditEventType, riskLevel: RiskLevel): string[] {
    const tags = [eventType.split('.')[0], riskLevel];

    // Add specific tags based on event type
    if (eventType.startsWith('auth.')) tags.push('authentication');
    if (eventType.startsWith('query.') || eventType === 'data.access') tags.push('data_access');
    if (eventType.startsWith('incident.') || eventType.startsWith('investigation.'))
      tags.push('security_ops');
    if (eventType.startsWith('admin.') || eventType === 'compliance.policy_update')
      tags.push('administration');

    return tags;
  }

  private redactSensitiveData(data: any): any {
    if (typeof data === 'string') {
      // Redact common sensitive patterns
      return data
        .replace(/password\s*[:=]\s*["']?[^"'\s]+/gi, 'password: [REDACTED]')
        .replace(/token\s*[:=]\s*["']?[^"'\s]+/gi, 'token: [REDACTED]')
        .replace(/api[_-]?key\s*[:=]\s*["']?[^"'\s]+/gi, 'api_key: [REDACTED]');
    }
    
    if (typeof data === 'object' && data !== null) {
      const redacted = { ...data };
      const sensitiveFields = ['password', 'token', 'apiKey', 'secret', 'key'];
      
      for (const field of sensitiveFields) {
        if (field in redacted) {
          redacted[field] = '[REDACTED]';
        }
      }
      
      return redacted;
    }
    
    return data;
  }

  private determineQueryType(query: string): string {
    const q = query.toLowerCase();
    if (q.includes('select') || q.includes('get')) return 'select';
    if (q.includes('count') || q.includes('agg')) return 'aggregation';
    if (q.includes('search') || q.includes('match')) return 'search';
    return 'unknown';
  }

  private calculateQueryRisk(query: string, resultCount: number): RiskLevel {
    const q = query.toLowerCase();
    
    // High risk patterns
    if (q.includes('*') && q.includes('password')) return 'critical';
    if (q.includes('user') && q.includes('password')) return 'high';
    if (resultCount > 100000) return 'high';
    if (resultCount > 10000) return 'medium';
    
    return 'low';
  }

  private calculateSettingsRisk(setting: string): RiskLevel {
    const highRiskSettings = ['auth', 'permission', 'role', 'security', 'encryption'];
    const mediumRiskSettings = ['notification', 'export', 'timeout'];
    
    const s = setting.toLowerCase();
    
    if (highRiskSettings.some(risk => s.includes(risk))) return 'high';
    if (mediumRiskSettings.some(risk => s.includes(risk))) return 'medium';
    
    return 'low';
  }

  private estimateFileSize(recordCount: number, format: string): string {
    let bytesPerRecord = 1024; // Default 1KB per record
    
    switch (format.toLowerCase()) {
      case 'json':
        bytesPerRecord = 2048;
        break;
      case 'csv':
        bytesPerRecord = 512;
        break;
      case 'xml':
        bytesPerRecord = 3072;
        break;
      case 'pdf':
        bytesPerRecord = 4096;
        break;
    }
    
    const totalBytes = recordCount * bytesPerRecord;
    
    if (totalBytes < 1024) return `${totalBytes} B`;
    if (totalBytes < 1024 * 1024) return `${Math.round(totalBytes / 1024)} KB`;
    if (totalBytes < 1024 * 1024 * 1024) return `${Math.round(totalBytes / (1024 * 1024))} MB`;
    
    return `${Math.round(totalBytes / (1024 * 1024 * 1024))} GB`;
  }
}

// Export singleton instance
export const auditService = AuditService.getInstance();

// React hook for audit logging
export const useAuditLogger = () => {
  const logEvent = auditService.logEvent.bind(auditService);
  const logLogin = auditService.logLogin.bind(auditService);
  const logLogout = auditService.logLogout.bind(auditService);
  const logQueryExecution = auditService.logQueryExecution.bind(auditService);
  const logDataExport = auditService.logDataExport.bind(auditService);
  const logIncidentCreation = auditService.logIncidentCreation.bind(auditService);
  const logSettingsChange = auditService.logSettingsChange.bind(auditService);

  return {
    logEvent,
    logLogin,
    logLogout,
    logQueryExecution,
    logDataExport,
    logIncidentCreation,
    logSettingsChange,
  };
};
