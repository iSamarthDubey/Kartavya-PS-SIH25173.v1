/**
 * KARTAVYA SIEM - Advanced Entity Recognition Service
 * Blueprint V2 Phase 1: Enhanced Intelligence
 * Detects security entities like IPs, CVEs, MITRE techniques, domains, etc.
 */

export interface SecurityEntity {
  text: string;
  type: EntityType;
  confidence: number;
  metadata?: any;
  start_position: number;
  end_position: number;
  // Alternative names for compatibility with MessageBubble
  start: number; 
  end: number;
  description?: string;
}

export type EntityType = 
  | 'ip_address' 
  | 'domain' 
  | 'email' 
  | 'hash' 
  | 'cve' 
  | 'mitre_technique' 
  | 'username' 
  | 'filename' 
  | 'port' 
  | 'url'
  | 'registry_key'
  | 'process_name'
  | 'service_name';

export interface EntityPattern {
  type: EntityType;
  regex: RegExp;
  validator?: (match: string) => boolean;
  enricher?: (match: string) => Promise<any>;
}

class AdvancedEntityRecognizer {
  private patterns: EntityPattern[] = [
    // IP Addresses (IPv4 & IPv6)
    {
      type: 'ip_address',
      regex: /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g,
      validator: (ip) => this.isValidIPv4(ip),
      enricher: async (ip) => this.enrichIP(ip)
    },
    
    // IPv6 addresses
    {
      type: 'ip_address',
      regex: /(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::1|::ffff:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/g,
      validator: (ip) => this.isValidIPv6(ip),
      enricher: async (ip) => this.enrichIP(ip)
    },

    // Domain names
    {
      type: 'domain',
      regex: /\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}\b/g,
      validator: (domain) => this.isValidDomain(domain),
      enricher: async (domain) => this.enrichDomain(domain)
    },

    // Email addresses
    {
      type: 'email',
      regex: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
      validator: (email) => this.isValidEmail(email)
    },

    // File hashes (MD5, SHA1, SHA256)
    {
      type: 'hash',
      regex: /\b[a-fA-F0-9]{32}\b|\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{64}\b/g,
      validator: (hash) => this.isValidHash(hash),
      enricher: async (hash) => this.enrichHash(hash)
    },

    // CVE identifiers
    {
      type: 'cve',
      regex: /CVE-\d{4}-\d{4,}/gi,
      enricher: async (cve) => this.enrichCVE(cve)
    },

    // MITRE ATT&CK techniques
    {
      type: 'mitre_technique',
      regex: /T\d{4}(?:\.\d{3})?/g,
      enricher: async (technique) => this.enrichMITRE(technique)
    },

    // URLs
    {
      type: 'url',
      regex: /https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?/gi,
      validator: (url) => this.isValidURL(url)
    },

    // Ports
    {
      type: 'port',
      regex: /\b(?:port\s+)?(\d{1,5})\b/gi,
      validator: (port) => this.isValidPort(port)
    },

    // Windows Registry Keys
    {
      type: 'registry_key',
      regex: /HK(?:EY_)?(?:LOCAL_MACHINE|CURRENT_USER|USERS|CLASSES_ROOT|CURRENT_CONFIG)\\[^\s]+/gi
    },

    // Process names
    {
      type: 'process_name',
      regex: /\b[a-zA-Z0-9_-]+\.exe\b/gi
    },

    // Service names (Windows)
    {
      type: 'service_name',
      regex: /\b(?:svchost|winlogon|csrss|lsass|services|spoolsv|explorer|iexplore|chrome|firefox|powershell|cmd)\b/gi
    }
  ];

  /**
   * Extract all security entities from text
   */
  async extractEntities(text: string): Promise<SecurityEntity[]> {
    const entities: SecurityEntity[] = [];

    for (const pattern of this.patterns) {
      const matches = Array.from(text.matchAll(pattern.regex));
      
      for (const match of matches) {
        const entityText = match[0];
        const startPos = match.index || 0;
        
        // Skip if validator rejects the match
        if (pattern.validator && !pattern.validator(entityText)) {
          continue;
        }

        // Calculate confidence based on pattern specificity
        const confidence = this.calculateConfidence(pattern.type, entityText);

        // Create entity
        const entity: SecurityEntity = {
          text: entityText,
          type: pattern.type,
          confidence,
          start_position: startPos,
          end_position: startPos + entityText.length,
          start: startPos, // Compatibility with MessageBubble
          end: startPos + entityText.length, // Compatibility with MessageBubble
          description: `${pattern.type.toUpperCase()}: ${entityText}`
        };

        // Enrich with additional data if enricher exists
        if (pattern.enricher) {
          try {
            entity.metadata = await pattern.enricher(entityText);
          } catch (error) {
            console.warn(`Failed to enrich ${pattern.type}:`, entityText, error);
          }
        }

        entities.push(entity);
      }
    }

    // Remove duplicates and sort by position
    return this.deduplicateEntities(entities);
  }

  /**
   * Highlight entities in text with HTML spans
   */
  highlightEntities(text: string, entities: SecurityEntity[]): string {
    let highlightedText = text;
    const sortedEntities = entities.sort((a, b) => b.start_position - a.start_position);

    for (const entity of sortedEntities) {
      const before = highlightedText.substring(0, entity.start_position);
      const after = highlightedText.substring(entity.end_position);
      const entityHtml = this.getEntityHTML(entity);
      
      highlightedText = before + entityHtml + after;
    }

    return highlightedText;
  }

  /**
   * Generate contextual actions based on detected entities
   */
  generateEntityActions(entities: SecurityEntity[]): Array<{
    label: string;
    action: string;
    entities: SecurityEntity[];
    icon: string;
  }> {
    const actions = [];
    const entityGroups = this.groupEntitiesByType(entities);

    // IP-based actions
    if (entityGroups.ip_address?.length > 0) {
      actions.push({
        label: `Investigate ${entityGroups.ip_address.length} IP address(es)`,
        action: 'investigate_ips',
        entities: entityGroups.ip_address,
        icon: 'globe'
      });
      
      actions.push({
        label: `Check IP reputation`,
        action: 'check_ip_reputation',
        entities: entityGroups.ip_address,
        icon: 'shield-alert'
      });
    }

    // Hash-based actions
    if (entityGroups.hash?.length > 0) {
      actions.push({
        label: `Scan ${entityGroups.hash.length} hash(es) for malware`,
        action: 'scan_hashes',
        entities: entityGroups.hash,
        icon: 'search'
      });
    }

    // CVE-based actions
    if (entityGroups.cve?.length > 0) {
      actions.push({
        label: `Research ${entityGroups.cve.length} CVE(s)`,
        action: 'research_cves',
        entities: entityGroups.cve,
        icon: 'bug'
      });
    }

    // MITRE-based actions
    if (entityGroups.mitre_technique?.length > 0) {
      actions.push({
        label: `Analyze MITRE techniques`,
        action: 'analyze_mitre',
        entities: entityGroups.mitre_technique,
        icon: 'target'
      });
    }

    return actions;
  }

  // Validation methods
  private isValidIPv4(ip: string): boolean {
    const parts = ip.split('.');
    return parts.length === 4 && parts.every(part => {
      const num = parseInt(part, 10);
      return num >= 0 && num <= 255;
    });
  }

  private isValidIPv6(ip: string): boolean {
    // Simplified IPv6 validation
    return /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/.test(ip) || ip === '::1';
  }

  private isValidDomain(domain: string): boolean {
    return domain.includes('.') && domain.length > 3 && 
           !domain.startsWith('.') && !domain.endsWith('.');
  }

  private isValidEmail(email: string): boolean {
    return email.includes('@') && email.includes('.');
  }

  private isValidHash(hash: string): boolean {
    const len = hash.length;
    return (len === 32 || len === 40 || len === 64) && /^[a-fA-F0-9]+$/.test(hash);
  }

  private isValidURL(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  private isValidPort(port: string): boolean {
    const num = parseInt(port, 10);
    return num > 0 && num <= 65535;
  }

  // Enrichment methods
  private async enrichIP(ip: string): Promise<any> {
    // In real implementation, call threat intelligence API
    return {
      country: 'Unknown',
      asn: 'Unknown',
      threat_score: Math.random() * 100,
      last_seen: new Date().toISOString()
    };
  }

  private async enrichDomain(domain: string): Promise<any> {
    return {
      registrar: 'Unknown',
      creation_date: 'Unknown',
      threat_score: Math.random() * 100
    };
  }

  private async enrichHash(hash: string): Promise<any> {
    return {
      hash_type: hash.length === 32 ? 'MD5' : hash.length === 40 ? 'SHA1' : 'SHA256',
      malware_family: 'Unknown',
      threat_score: Math.random() * 100
    };
  }

  private async enrichCVE(cve: string): Promise<any> {
    return {
      severity: ['Low', 'Medium', 'High', 'Critical'][Math.floor(Math.random() * 4)],
      cvss_score: (Math.random() * 10).toFixed(1),
      description: `Vulnerability ${cve}`
    };
  }

  private async enrichMITRE(technique: string): Promise<any> {
    const techniques = {
      'T1055': 'Process Injection',
      'T1003': 'OS Credential Dumping',
      'T1059': 'Command and Scripting Interpreter',
      'T1078': 'Valid Accounts'
    };

    return {
      name: techniques[technique as keyof typeof techniques] || 'Unknown Technique',
      tactic: 'Unknown',
      description: `MITRE ATT&CK technique ${technique}`
    };
  }

  // Utility methods
  private calculateConfidence(type: EntityType, text: string): number {
    // More specific patterns get higher confidence
    const baseConfidence: Record<EntityType, number> = {
      cve: 0.95,
      mitre_technique: 0.9,
      hash: 0.85,
      ip_address: 0.8,
      email: 0.8,
      url: 0.75,
      domain: 0.7,
      port: 0.6,
      registry_key: 0.8,
      process_name: 0.7,
      service_name: 0.6,
      username: 0.5,
      filename: 0.5
    };

    return baseConfidence[type] || 0.5;
  }

  private deduplicateEntities(entities: SecurityEntity[]): SecurityEntity[] {
    const seen = new Set<string>();
    return entities
      .filter(entity => {
        const key = `${entity.type}:${entity.text}:${entity.start_position}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      })
      .sort((a, b) => a.start_position - b.start_position);
  }

  private groupEntitiesByType(entities: SecurityEntity[]): Record<string, SecurityEntity[]> {
    return entities.reduce((groups, entity) => {
      const type = entity.type;
      if (!groups[type]) groups[type] = [];
      groups[type].push(entity);
      return groups;
    }, {} as Record<string, SecurityEntity[]>);
  }

  private getEntityHTML(entity: SecurityEntity): string {
    const colorMap: Record<EntityType, string> = {
      ip_address: 'text-orange-400 bg-orange-900/20 border-orange-700',
      domain: 'text-blue-400 bg-blue-900/20 border-blue-700',
      hash: 'text-purple-400 bg-purple-900/20 border-purple-700',
      cve: 'text-red-400 bg-red-900/20 border-red-700',
      mitre_technique: 'text-yellow-400 bg-yellow-900/20 border-yellow-700',
      email: 'text-green-400 bg-green-900/20 border-green-700',
      url: 'text-cyan-400 bg-cyan-900/20 border-cyan-700',
      username: 'text-indigo-400 bg-indigo-900/20 border-indigo-700',
      filename: 'text-pink-400 bg-pink-900/20 border-pink-700',
      port: 'text-teal-400 bg-teal-900/20 border-teal-700',
      registry_key: 'text-rose-400 bg-rose-900/20 border-rose-700',
      process_name: 'text-amber-400 bg-amber-900/20 border-amber-700',
      service_name: 'text-lime-400 bg-lime-900/20 border-lime-700'
    };

    const className = colorMap[entity.type] || 'text-gray-400 bg-gray-900/20 border-gray-700';
    
    return `<span class="px-1 py-0.5 rounded border text-xs font-mono ${className}" title="${entity.type}: ${entity.confidence.toFixed(2)} confidence">${entity.text}</span>`;
  }
}

// Export singleton instance
export const entityRecognizer = new AdvancedEntityRecognizer();
export default entityRecognizer;
