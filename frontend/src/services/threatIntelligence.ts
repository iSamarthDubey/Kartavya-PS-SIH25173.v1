/**
 * KARTAVYA SIEM - Threat Intelligence Service
 * Real-time threat intelligence integration for security entities
 */

export interface ThreatIntelResponse {
  entity: string;
  entity_type: string;
  reputation: 'malicious' | 'suspicious' | 'clean' | 'unknown';
  confidence: number;
  sources: string[];
  first_seen?: string;
  last_seen?: string;
  geo_location?: {
    country: string;
    city?: string;
    latitude?: number;
    longitude?: number;
  };
  threat_types: string[];
  malware_families?: string[];
  campaigns?: string[];
  details: {
    [key: string]: any;
  };
}

export interface IOCEnrichment {
  hash_analysis?: {
    hash_type: string;
    file_size?: number;
    file_type?: string;
    malware_family?: string;
    detection_ratio?: string;
    first_submission?: string;
  };
  ip_analysis?: {
    asn?: string;
    isp?: string;
    country?: string;
    threat_types?: string[];
    blacklisted?: boolean;
  };
  domain_analysis?: {
    registrar?: string;
    creation_date?: string;
    expiration_date?: string;
    dns_records?: any[];
    subdomains?: string[];
  };
}

class ThreatIntelligenceService {
  private backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
  private cache = new Map<string, ThreatIntelResponse>();
  private cacheExpiry = 15 * 60 * 1000; // 15 minutes

  /**
   * Get threat intelligence for an entity from backend
   */
  async getThreatIntel(entity: string, entityType: string): Promise<ThreatIntelResponse> {
    const cacheKey = `${entityType}:${entity}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey)!;
      const age = Date.now() - new Date(cached.details.cached_at || 0).getTime();
      if (age < this.cacheExpiry) {
        return cached;
      }
    }

    try {
      const response = await fetch(`${this.backendUrl}/api/threat-intel/${entityType}/${encodeURIComponent(entity)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Cache the response
      data.details = data.details || {};
      data.details.cached_at = new Date().toISOString();
      this.cache.set(cacheKey, data);
      
      return data;
    } catch (error) {
      // Return minimal response when backend is unavailable
      return {
        entity,
        entity_type: entityType,
        reputation: 'unknown',
        confidence: 0,
        sources: [],
        threat_types: [],
        details: {
          error: 'Backend unavailable',
          cached_at: new Date().toISOString()
        }
      };
    }
  }

  /**
   * Bulk threat intelligence lookup
   */
  async getBulkThreatIntel(entities: Array<{text: string, type: string}>): Promise<ThreatIntelResponse[]> {
    try {
      const response = await fetch(`${this.backendUrl}/api/threat-intel/bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ entities })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      // Return empty responses when backend is unavailable
      return entities.map(entity => ({
        entity: entity.text,
        entity_type: entity.type,
        reputation: 'unknown' as const,
        confidence: 0,
        sources: [],
        threat_types: [],
        details: { error: 'Backend unavailable' }
      }));
    }
  }

  /**
   * Get enriched IOC data from backend
   */
  async enrichIOC(ioc: string, type: string): Promise<IOCEnrichment> {
    try {
      const response = await fetch(`${this.backendUrl}/api/enrich-ioc/${type}/${encodeURIComponent(ioc)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      // Return empty enrichment when backend is unavailable
      return {};
    }
  }


  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; entries: string[] } {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys())
    };
  }
}

export const threatIntelService = new ThreatIntelligenceService();
export default threatIntelService;
