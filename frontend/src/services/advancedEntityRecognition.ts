/**
 * 🚀 KARTAVYA SIEM - ADVANCED Entity Recognition Service 
 * Enhanced for sophisticated threat detection from Advanced SIEM Dataset
 * Detects: APT groups, MITRE techniques, IoT devices, AI models, behavioral indicators, unconventional IOCs
 */

export interface AdvancedSecurityEntity {
  text: string;
  type: AdvancedEntityType;
  confidence: number;
  metadata?: any;
  start_position: number;
  end_position: number;
  start: number; // Compatibility
  end: number;   // Compatibility
  description?: string;
  enrichment?: ThreatEnrichment;
  risk_score?: number;
  context?: string;
}

export type AdvancedEntityType = 
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
  | 'service_name'
  // 🆕 Advanced SIEM Entity Types
  | 'threat_actor'           // APT29, FIN7, REvil, etc.
  | 'device_id'              // IoT devices: iot-efc70493
  | 'model_id'               // AI models: model-e8e7d12e  
  | 'attack_technique'       // Credential stuffing, lateral movement
  | 'behavioral_indicator'   // Baseline deviation, entropy
  | 'unconventional_ioc'     // CPU microcode changes, etc.
  | 'campaign_name'          // Operation names, APT campaigns
  | 'malware_family'         // Agent.Win32, TrojanDropper
  | 'vulnerability_type'     // Zero-day, supply chain
  | 'geo_location'           // Countries, regions in context
  | 'network_protocol'       // SSH, RDP, SMB, DNS in context
  | 'cloud_service'          // AWS, GCP, Azure, OCI
  | 'container_id'           // Docker containers, K8s pods
  | 'blockchain_address'     // Crypto wallet addresses
  | 'certificate_hash';      // TLS/SSL certificate hashes

export interface ThreatEnrichment {
  reputation: 'clean' | 'suspicious' | 'malicious';
  confidence: number;
  geo_location?: { country: string; city?: string };
  campaigns?: string[];
  malware_families?: string[];
  threat_actors?: string[];
  first_seen?: string;
  last_seen?: string;
  asn?: string;
  risk_factors?: string[];
}

export interface AdvancedEntityPattern {
  type: AdvancedEntityType;
  patterns: RegExp[];
  validator?: (match: string) => boolean;
  enricher?: (match: string) => Promise<ThreatEnrichment>;
  risk_calculator?: (match: string) => number;
  context_detector?: (text: string, match: string, position: number) => string;
}

class SuperAdvancedEntityRecognizer {
  private advancedPatterns: AdvancedEntityPattern[] = [
    
    // 🌐 ENHANCED IP ADDRESS PATTERNS
    {
      type: 'ip_address',
      patterns: [
        /\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/g,
        /(?:from|to|source|destination|src|dst|IP)\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})/gi,
        /\b(54\.159\.34\.148|185\.220\.101\.42|196\.221\.103\.178|10\.0\.0\.45)\b/g // Known IPs from dataset
      ],
      validator: (ip) => this.isValidIPv4(ip),
      enricher: async (ip) => this.enrichIPAdvanced(ip),
      risk_calculator: (ip) => this.calculateIPRisk(ip),
      context_detector: (text, match, pos) => this.detectIPContext(text, match, pos)
    },

    // 🎯 ENHANCED MITRE ATT&CK PATTERNS
    {
      type: 'mitre_technique',
      patterns: [
        /\b(T[0-9]{4}(?:\.[0-9]{3})?)\b/g,
        /(?:MITRE|technique|tactic)\s+(T[0-9]{4}(?:\.[0-9]{3})?)/gi,
        /\b(T1190|T1566\.001|T1059\.001|T1071\.001|T1078\.004|T1486|T1547\.001|T1574\.002|T1218\.011|T1204\.002|T1053\.005|T1110\.003|T1543\.003|T1134\.001)\b/g
      ],
      enricher: async (technique) => this.enrichMITRETechnique(technique),
      risk_calculator: (technique) => this.calculateMITRERisk(technique)
    },

    // 🦹 THREAT ACTOR PATTERNS (APT Groups, Cybercriminal Organizations)
    {
      type: 'threat_actor',
      patterns: [
        /\b(APT[0-9]+|APT-?[0-9]+)\b/gi,
        /\b(APT29|APT28|APT1|APT41|APT38|APT35|APT34|APT33|APT32)\b/gi,
        /\b(Cozy Bear|Fancy Bear|Lazarus Group|Wizard Spider|FIN7|FIN8|FIN11)\b/gi,
        /\b(Carbanak|Equation Group|Shadow Brokers|REvil|Conti|Ryuk)\b/gi,
        /\b(Sandworm Team|Turla|Dragonfly|Leafminer|OilRig)\b/gi,
        /(?:threat actor|apt group|campaign|group)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/gi
      ],
      enricher: async (actor) => this.enrichThreatActor(actor),
      risk_calculator: (actor) => this.calculateThreatActorRisk(actor)
    },

    // 🏭 IOT DEVICE IDENTIFIERS  
    {
      type: 'device_id',
      patterns: [
        /\b(iot-[a-f0-9]{8,})\b/gi,
        /\b(device-[a-f0-9-]+)\b/gi,
        /\b(sensor-[0-9a-f]+|hvac-[0-9a-f]+|camera-[0-9a-f]+)\b/gi,
        /\b(iot-efc70493|iot-13c63915|iot-d1d79ad6|iot-ff3ca055)\b/gi, // Known from dataset
        /(?:device|iot|sensor)\s+([a-z]+-[a-f0-9]{6,})/gi
      ],
      enricher: async (deviceId) => this.enrichIoTDevice(deviceId),
      risk_calculator: (deviceId) => this.calculateDeviceRisk(deviceId),
      context_detector: (text, match, pos) => this.detectDeviceContext(text, match, pos)
    },

    // 🤖 AI/ML MODEL IDENTIFIERS
    {
      type: 'model_id',
      patterns: [
        /\b(model-[a-f0-9]{8,})\b/gi,
        /\b(ai-model-[a-z0-9-]+)\b/gi,
        /\b(model-e8e7d12e|model-cf9d0b65|model-b25bcd75)\b/gi, // Known from dataset
        /(?:model|ai system|ml model)\s+([a-z]+-[a-f0-9]{6,})/gi
      ],
      enricher: async (modelId) => this.enrichAIModel(modelId),
      risk_calculator: (modelId) => this.calculateModelRisk(modelId)
    },

    // ⚔️ ADVANCED ATTACK TECHNIQUES
    {
      type: 'attack_technique',
      patterns: [
        /\b(credential stuffing|brute force|password spray|token replay)\b/gi,
        /\b(lateral movement|privilege escalation|data exfiltration)\b/gi,
        /\b(living off the land|fileless|memory injection|process injection)\b/gi,
        /\b(container escape|sandbox escape|vm escape)\b/gi,
        /\b(supply chain|watering hole|spear phishing|whaling)\b/gi,
        /\b(model inversion|adversarial input|training data poisoning|membership inference)\b/gi,
        /\b(sensor spoofing|protocol violation|command injection|firmware manipulation)\b/gi,
        /\b(side channel|covert channel|dns tunneling|crypto mining)\b/gi
      ],
      enricher: async (technique) => this.enrichAttackTechnique(technique),
      risk_calculator: (technique) => this.calculateAttackTechniqueRisk(technique)
    },

    // 📊 BEHAVIORAL ANALYTICS INDICATORS
    {
      type: 'behavioral_indicator',
      patterns: [
        /\b(baseline deviation|entropy|frequency anomaly|sequence anomaly)\b/gi,
        /\b(risk score|confidence|reputation|threat level)\b/gi,
        /\b(unusual activity|suspicious behavior|anomalous pattern)\b/gi,
        /\b(geo anomaly|impossible travel|time anomaly)\b/gi,
        /\b(behavioral analytics|user behavior|device behavior)\b/gi
      ],
      enricher: async (indicator) => this.enrichBehavioralIndicator(indicator),
      risk_calculator: (indicator) => 0.7
    },

    // 🔬 UNCONVENTIONAL IOCs (Hardware/Firmware Level)
    {
      type: 'unconventional_ioc',
      patterns: [
        /\b(cpu microcode changes|gpu memory artifacts|thermal sensor anomalies)\b/gi,
        /\b(power consumption spikes|bios timestamp anomalies|uefi variable tampering)\b/gi,
        /\b(tpm attestation failures|hardware fingerprint changes)\b/gi,
        /\b(firmware corruption|bootkit|rootkit|hypervisor)\b/gi,
        /\b(cpu speculation|side channel|cache timing|row hammer)\b/gi
      ],
      enricher: async (ioc) => this.enrichUnconventionalIOC(ioc),
      risk_calculator: (ioc) => 0.9 // High risk due to advanced nature
    },

    // 🏴 CAMPAIGN AND OPERATION NAMES
    {
      type: 'campaign_name',
      patterns: [
        /\b(Operation [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b/gi,
        /\b(SolarWinds|Microsoft Exchange|Kaseya|Colonial Pipeline)\b/gi,
        /\b(Credential Stuffing 2024|Operation SteelCorgi)\b/gi, // From dataset
        /(?:campaign|operation)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/gi
      ],
      enricher: async (campaign) => this.enrichCampaign(campaign),
      risk_calculator: (campaign) => 0.85
    },

    // 🦠 MALWARE FAMILY NAMES
    {
      type: 'malware_family',
      patterns: [
        /\b(Agent\.Win32|TrojanDropper|Trojan\.Win32)\b/gi,
        /\b(Emotet|Trickbot|QakBot|IcedID|BazarLoader)\b/gi,
        /\b(Ryuk|Conti|LockBit|BlackMatter|DarkSide)\b/gi,
        /\b(Cobalt Strike|Metasploit|PowerShell Empire)\b/gi,
        /\b([A-Z][a-z]+(?:\.[A-Z][a-z0-9]+)+)\b/g // Generic malware naming
      ],
      enricher: async (malware) => this.enrichMalwareFamily(malware),
      risk_calculator: (malware) => 0.95
    },

    // 🌍 CLOUD SERVICE IDENTIFIERS
    {
      type: 'cloud_service',
      patterns: [
        /\b(AWS|GCP|Azure|OCI|Alibaba)\b/gi,
        /\b(Amazon Web Services|Google Cloud|Microsoft Azure)\b/gi,
        /(?:cloud service|cloud provider)\s+(AWS|GCP|Azure|OCI)/gi
      ],
      enricher: async (service) => this.enrichCloudService(service),
      risk_calculator: (service) => 0.3 // Lower base risk
    },

    // 📦 CONTAINER AND ORCHESTRATION
    {
      type: 'container_id',
      patterns: [
        /\b(container-[a-f0-9-]+)\b/gi,
        /\b(pod-[a-f0-9-]+|k8s-[a-f0-9-]+)\b/gi,
        /\b([a-f0-9]{12,64})\b/g, // Container IDs
        /(?:container|pod|docker)\s+([a-f0-9-]{8,})/gi
      ],
      validator: (id) => /^[a-f0-9-]+$/.test(id),
      enricher: async (containerId) => this.enrichContainer(containerId),
      risk_calculator: (containerId) => 0.4
    }
  ];

  /**
   * 🚀 EXTRACT ALL ADVANCED SECURITY ENTITIES
   */
  async extractAdvancedEntities(text: string): Promise<AdvancedSecurityEntity[]> {
    const entities: AdvancedSecurityEntity[] = [];

    for (const pattern of this.advancedPatterns) {
      for (const regex of pattern.patterns) {
        const matches = Array.from(text.matchAll(regex));
        
        for (const match of matches) {
          const entityText = match[1] || match[0]; // Use capture group if available
          const startPos = match.index || 0;
          
          // Skip if validator rejects the match
          if (pattern.validator && !pattern.validator(entityText)) {
            continue;
          }

          // Calculate confidence based on pattern specificity
          const confidence = this.calculateAdvancedConfidence(pattern.type, entityText);
          
          // Calculate risk score
          const risk_score = pattern.risk_calculator ? 
            pattern.risk_calculator(entityText) : 
            this.calculateDefaultRisk(pattern.type);

          // Detect context
          const context = pattern.context_detector ? 
            pattern.context_detector(text, entityText, startPos) :
            this.extractSurroundingContext(text, startPos, entityText.length);

          // Create advanced entity
          const entity: AdvancedSecurityEntity = {
            text: entityText,
            type: pattern.type,
            confidence,
            start_position: startPos,
            end_position: startPos + entityText.length,
            start: startPos,
            end: startPos + entityText.length,
            description: `${pattern.type.replace('_', ' ').toUpperCase()}: ${entityText}`,
            risk_score,
            context
          };

          // Enrich with threat intelligence if enricher exists
          if (pattern.enricher) {
            try {
              entity.enrichment = await pattern.enricher(entityText);
            } catch (error) {
              console.warn(`Failed to enrich ${pattern.type}:`, entityText, error);
            }
          }

          entities.push(entity);
        }
      }
    }

    return this.deduplicateAdvancedEntities(entities);
  }

  // 🔍 ADVANCED ENRICHMENT METHODS

  private async enrichIPAdvanced(ip: string): Promise<ThreatEnrichment> {
    // Simulate advanced threat intelligence for known IPs from dataset
    const knownThreatIPs: Record<string, ThreatEnrichment> = {
      '54.159.34.148': {
        reputation: 'malicious',
        confidence: 0.87,
        geo_location: { country: 'Mexico', city: 'Unknown' },
        campaigns: ['Credential Stuffing 2024'],
        threat_actors: ['APT29'],
        malware_families: ['Agent.Win32', 'TrojanDropper'],
        first_seen: '2024-11-15T08:30:00Z',
        last_seen: '2024-12-28T15:45:00Z',
        asn: 'AS14061 DigitalOcean LLC',
        risk_factors: ['Botnet C2', 'Credential Stuffing', 'Geographic Anomaly']
      },
      '185.220.101.42': {
        reputation: 'suspicious',
        confidence: 0.72,
        geo_location: { country: 'US', city: 'Chicago' },
        campaigns: ['Operation SteelCorgi'],
        threat_actors: ['FIN7'],
        first_seen: '2024-12-01T12:00:00Z',
        asn: 'AS16509 Amazon.com Inc',
        risk_factors: ['Phishing Infrastructure', 'C2 Communication']
      }
    };

    return knownThreatIPs[ip] || {
      reputation: 'clean',
      confidence: 0.6,
      geo_location: { country: 'Unknown' },
      risk_factors: []
    };
  }

  private async enrichMITRETechnique(technique: string): Promise<ThreatEnrichment> {
    const mitreData: Record<string, any> = {
      'T1190': {
        reputation: 'malicious',
        confidence: 0.95,
        campaigns: ['SolarWinds', 'Credential Stuffing 2024'],
        threat_actors: ['APT29', 'FIN7'],
        risk_factors: ['Initial Access', 'Public-Facing Application']
      },
      'T1566.001': {
        reputation: 'malicious', 
        confidence: 0.92,
        campaigns: ['Spear Phishing Campaign 2024'],
        threat_actors: ['APT29', 'FIN7'],
        risk_factors: ['Phishing', 'Email Attachment']
      }
    };

    return mitreData[technique] || {
      reputation: 'suspicious',
      confidence: 0.8,
      risk_factors: ['Unknown MITRE Technique']
    };
  }

  private async enrichThreatActor(actor: string): Promise<ThreatEnrichment> {
    const actorData: Record<string, ThreatEnrichment> = {
      'APT29': {
        reputation: 'malicious',
        confidence: 0.96,
        geo_location: { country: 'Russia' },
        campaigns: ['SolarWinds', 'Microsoft Exchange'],
        malware_families: ['Cobalt Strike', 'PowerShell Empire'],
        first_seen: '2008-01-01T00:00:00Z',
        risk_factors: ['State-sponsored', 'Advanced Persistent Threat', 'Supply Chain']
      },
      'FIN7': {
        reputation: 'malicious',
        confidence: 0.94,
        campaigns: ['Carbanak', 'FIN7 Spear Phishing'],
        malware_families: ['Carbanak', 'More_eggs'],
        first_seen: '2013-01-01T00:00:00Z',
        risk_factors: ['Financial Motivated', 'Spear Phishing', 'Point of Sale']
      },
      'REvil': {
        reputation: 'malicious',
        confidence: 0.98,
        campaigns: ['Kaseya Supply Chain', 'JBS Attack'],
        malware_families: ['Sodinokibi', 'REvil'],
        first_seen: '2019-01-01T00:00:00Z',
        risk_factors: ['Ransomware as a Service', 'Supply Chain', 'Critical Infrastructure']
      }
    };

    return actorData[actor] || {
      reputation: 'suspicious',
      confidence: 0.7,
      risk_factors: ['Unknown Threat Actor']
    };
  }

  private async enrichIoTDevice(deviceId: string): Promise<ThreatEnrichment> {
    const deviceData: Record<string, ThreatEnrichment> = {
      'iot-efc70493': {
        reputation: 'suspicious',
        confidence: 0.78,
        risk_factors: ['HVAC System', 'Protocol Violation', 'CPU Microcode Changes'],
        campaigns: ['IoT Botnet 2024'],
        threat_actors: ['REvil'],
        first_seen: '2024-06-27T23:01:00Z'
      }
    };

    return deviceData[deviceId] || {
      reputation: 'clean',
      confidence: 0.5,
      risk_factors: ['IoT Device']
    };
  }

  private async enrichAIModel(modelId: string): Promise<ThreatEnrichment> {
    const modelData: Record<string, ThreatEnrichment> = {
      'model-e8e7d12e': {
        reputation: 'suspicious',
        confidence: 0.82,
        risk_factors: ['AI Model Poisoning', 'Training Data Manipulation', 'API Abuse'],
        campaigns: ['AI Attack Campaign 2024'],
        first_seen: '2024-06-10T08:38:16Z'
      }
    };

    return modelData[modelId] || {
      reputation: 'clean',
      confidence: 0.6,
      risk_factors: ['AI/ML Model']
    };
  }

  private async enrichAttackTechnique(technique: string): Promise<ThreatEnrichment> {
    const techniqueRisk: Record<string, ThreatEnrichment> = {
      'credential stuffing': {
        reputation: 'malicious',
        confidence: 0.9,
        risk_factors: ['Authentication Attack', 'Automated Tool', 'Account Takeover'],
        campaigns: ['Credential Stuffing 2024']
      },
      'lateral movement': {
        reputation: 'malicious',
        confidence: 0.95,
        risk_factors: ['Post-Compromise', 'Network Traversal', 'Persistence'],
        threat_actors: ['APT29', 'APT28']
      },
      'container escape': {
        reputation: 'malicious',
        confidence: 0.92,
        risk_factors: ['Container Security', 'Privilege Escalation', 'Host Compromise']
      }
    };

    return techniqueRisk[technique.toLowerCase()] || {
      reputation: 'suspicious',
      confidence: 0.7,
      risk_factors: ['Attack Technique']
    };
  }

  private async enrichBehavioralIndicator(indicator: string): Promise<ThreatEnrichment> {
    return {
      reputation: 'suspicious',
      confidence: 0.65,
      risk_factors: ['Behavioral Anomaly', 'Statistical Deviation']
    };
  }

  private async enrichUnconventionalIOC(ioc: string): Promise<ThreatEnrichment> {
    return {
      reputation: 'malicious',
      confidence: 0.85,
      risk_factors: ['Hardware-level Attack', 'Advanced Persistence', 'Firmware Manipulation']
    };
  }

  private async enrichCampaign(campaign: string): Promise<ThreatEnrichment> {
    return {
      reputation: 'malicious',
      confidence: 0.9,
      risk_factors: ['Coordinated Campaign', 'Multi-stage Attack']
    };
  }

  private async enrichMalwareFamily(malware: string): Promise<ThreatEnrichment> {
    return {
      reputation: 'malicious',
      confidence: 0.95,
      risk_factors: ['Malware', 'Code Execution', 'System Compromise']
    };
  }

  private async enrichCloudService(service: string): Promise<ThreatEnrichment> {
    return {
      reputation: 'clean',
      confidence: 0.8,
      risk_factors: ['Cloud Infrastructure']
    };
  }

  private async enrichContainer(containerId: string): Promise<ThreatEnrichment> {
    return {
      reputation: 'clean',
      confidence: 0.7,
      risk_factors: ['Container Technology']
    };
  }

  // 📊 RISK CALCULATION METHODS

  private calculateIPRisk(ip: string): number {
    const highRiskIPs = ['54.159.34.148', '185.220.101.42', '196.221.103.178'];
    return highRiskIPs.includes(ip) ? 0.9 : 0.4;
  }

  private calculateMITRERisk(technique: string): number {
    const highRiskTechniques = ['T1190', 'T1566.001', 'T1486', 'T1078.004'];
    return highRiskTechniques.includes(technique) ? 0.9 : 0.7;
  }

  private calculateThreatActorRisk(actor: string): number {
    const advancedActors = ['APT29', 'APT28', 'FIN7', 'REvil', 'Lazarus Group'];
    return advancedActors.some(a => actor.includes(a)) ? 0.95 : 0.8;
  }

  private calculateDeviceRisk(deviceId: string): number {
    const compromisedDevices = ['iot-efc70493', 'iot-13c63915'];
    return compromisedDevices.includes(deviceId) ? 0.8 : 0.3;
  }

  private calculateModelRisk(modelId: string): number {
    const compromisedModels = ['model-e8e7d12e', 'model-cf9d0b65'];
    return compromisedModels.includes(modelId) ? 0.85 : 0.4;
  }

  private calculateAttackTechniqueRisk(technique: string): number {
    const highRiskTechniques = ['credential stuffing', 'lateral movement', 'data exfiltration', 'container escape'];
    return highRiskTechniques.includes(technique.toLowerCase()) ? 0.9 : 0.7;
  }

  // 🔧 UTILITY METHODS

  private calculateAdvancedConfidence(type: AdvancedEntityType, text: string): number {
    const confidenceMap: Record<AdvancedEntityType, number> = {
      mitre_technique: 0.95,
      threat_actor: 0.9,
      cve: 0.95,
      attack_technique: 0.85,
      unconventional_ioc: 0.8,
      malware_family: 0.9,
      campaign_name: 0.85,
      device_id: 0.8,
      model_id: 0.8,
      behavioral_indicator: 0.7,
      ip_address: 0.8,
      hash: 0.85,
      email: 0.8,
      url: 0.75,
      domain: 0.7,
      port: 0.6,
      cloud_service: 0.7,
      container_id: 0.75,
      blockchain_address: 0.9,
      certificate_hash: 0.85,
      geo_location: 0.6,
      network_protocol: 0.7,
      vulnerability_type: 0.8,
      registry_key: 0.8,
      process_name: 0.7,
      service_name: 0.6,
      username: 0.5,
      filename: 0.5
    };

    return confidenceMap[type] || 0.5;
  }

  private calculateDefaultRisk(type: AdvancedEntityType): number {
    const riskMap: Record<AdvancedEntityType, number> = {
      threat_actor: 0.95,
      unconventional_ioc: 0.9,
      malware_family: 0.95,
      mitre_technique: 0.85,
      attack_technique: 0.8,
      campaign_name: 0.85,
      cve: 0.8,
      device_id: 0.4,
      model_id: 0.4,
      behavioral_indicator: 0.6,
      ip_address: 0.5,
      hash: 0.7,
      email: 0.3,
      url: 0.4,
      domain: 0.4,
      port: 0.2,
      cloud_service: 0.2,
      container_id: 0.3,
      blockchain_address: 0.6,
      certificate_hash: 0.4,
      geo_location: 0.1,
      network_protocol: 0.2,
      vulnerability_type: 0.8,
      registry_key: 0.4,
      process_name: 0.3,
      service_name: 0.2,
      username: 0.2,
      filename: 0.2
    };

    return riskMap[type] || 0.3;
  }

  private detectIPContext(text: string, ip: string, position: number): string {
    const contextWords = ['from', 'to', 'source', 'destination', 'attack', 'connection', 'traffic'];
    const surrounding = this.extractSurroundingContext(text, position, ip.length);
    
    for (const word of contextWords) {
      if (surrounding.toLowerCase().includes(word)) {
        return `Network ${word} context`;
      }
    }
    return 'Network communication';
  }

  private detectDeviceContext(text: string, deviceId: string, position: number): string {
    const deviceTypes = ['HVAC', 'Sensor', 'Camera', 'Medical', 'Thermostat'];
    const surrounding = this.extractSurroundingContext(text, position, deviceId.length);
    
    for (const type of deviceTypes) {
      if (surrounding.includes(type)) {
        return `${type} device`;
      }
    }
    return 'IoT device';
  }

  private extractSurroundingContext(text: string, position: number, length: number): string {
    const start = Math.max(0, position - 50);
    const end = Math.min(text.length, position + length + 50);
    return text.substring(start, end);
  }

  private isValidIPv4(ip: string): boolean {
    const parts = ip.split('.');
    return parts.length === 4 && parts.every(part => {
      const num = parseInt(part, 10);
      return num >= 0 && num <= 255;
    });
  }

  private deduplicateAdvancedEntities(entities: AdvancedSecurityEntity[]): AdvancedSecurityEntity[] {
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

  /**
   * 🎯 GENERATE ADVANCED ENTITY ACTIONS
   */
  generateAdvancedEntityActions(entities: AdvancedSecurityEntity[]): Array<{
    label: string;
    action: string;
    entities: AdvancedSecurityEntity[];
    icon: string;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
  }> {
    const actions = [];
    const entityGroups = this.groupEntitiesByType(entities);

    // Threat Actor Actions
    if (entityGroups.threat_actor?.length > 0) {
      actions.push({
        label: `🦹 Investigate ${entityGroups.threat_actor.length} threat actor(s)`,
        action: 'investigate_threat_actors',
        entities: entityGroups.threat_actor,
        icon: 'shield-alert',
        risk_level: 'critical' as const
      });
    }

    // IoT Device Actions  
    if (entityGroups.device_id?.length > 0) {
      actions.push({
        label: `🏭 Analyze ${entityGroups.device_id.length} IoT device(s)`,
        action: 'analyze_iot_devices',
        entities: entityGroups.device_id,
        icon: 'cpu',
        risk_level: 'high' as const
      });
    }

    // AI Model Actions
    if (entityGroups.model_id?.length > 0) {
      actions.push({
        label: `🤖 Secure ${entityGroups.model_id.length} AI model(s)`,
        action: 'secure_ai_models',
        entities: entityGroups.model_id,
        icon: 'brain',
        risk_level: 'high' as const
      });
    }

    // Attack Technique Actions
    if (entityGroups.attack_technique?.length > 0) {
      actions.push({
        label: `⚔️ Counter ${entityGroups.attack_technique.length} attack technique(s)`,
        action: 'counter_attack_techniques',
        entities: entityGroups.attack_technique,
        icon: 'sword',
        risk_level: 'high' as const
      });
    }

    // MITRE Technique Actions
    if (entityGroups.mitre_technique?.length > 0) {
      actions.push({
        label: `🎯 Map MITRE kill chain`,
        action: 'map_mitre_killchain',
        entities: entityGroups.mitre_technique,
        icon: 'target',
        risk_level: 'critical' as const
      });
    }

    return actions;
  }

  private groupEntitiesByType(entities: AdvancedSecurityEntity[]): Record<string, AdvancedSecurityEntity[]> {
    return entities.reduce((groups, entity) => {
      const type = entity.type;
      if (!groups[type]) groups[type] = [];
      groups[type].push(entity);
      return groups;
    }, {} as Record<string, AdvancedSecurityEntity[]>);
  }
}

// Export singleton instance
export const advancedEntityRecognizer = new SuperAdvancedEntityRecognizer();
export default advancedEntityRecognizer;
