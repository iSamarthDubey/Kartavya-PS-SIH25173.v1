/**
 * 🚀 KARTAVYA SIEM - Advanced Entity Display Component
 * Displays sophisticated security entities with comprehensive threat intelligence
 * Supports: Threat actors, IoT devices, AI models, behavioral indicators, etc.
 */

import React, { useState } from 'react';
import { 
  Shield, AlertTriangle, Globe, Clock, Eye, ExternalLink, Brain, Cpu, Target, Zap,
  MapPin, Server, Database, TrendingUp, X, Activity, Lock, Wifi, Cloud, Settings,
  HardDrive, Smartphone, Wrench, Code, FileText, Hash, Mail, Key
} from 'lucide-react';
import { AdvancedSecurityEntity, AdvancedEntityType } from '../../services/advancedEntityRecognition';

interface AdvancedEntityDisplayProps {
  entity: AdvancedSecurityEntity;
  onClose?: () => void;
  onActionTaken?: (action: string, entity: AdvancedSecurityEntity) => void;
  compact?: boolean;
}

const AdvancedEntityDisplay: React.FC<AdvancedEntityDisplayProps> = ({ 
  entity, 
  onClose, 
  onActionTaken, 
  compact = false 
}) => {
  const [showFullDetails, setShowFullDetails] = useState(false);
  
  const enrichment = entity.enrichment;
  const reputation = enrichment?.reputation || 'unknown';
  const confidence = entity.confidence || 0;
  const riskScore = entity.risk_score || 0;

  // 🎨 ADVANCED STYLING FUNCTIONS
  const getEntityIcon = (entityType: AdvancedEntityType) => {
    const iconMap: Record<AdvancedEntityType, React.ElementType> = {
      // Core entities
      'ip_address': Globe,
      'domain': ExternalLink,
      'email': Mail,
      'hash': Hash,
      'cve': AlertTriangle,
      'url': ExternalLink,
      'port': Server,
      'username': Eye,
      'filename': FileText,
      
      // Advanced entities
      'mitre_technique': Target,
      'threat_actor': Shield,
      'device_id': Smartphone,
      'model_id': Brain,
      'attack_technique': Zap,
      'behavioral_indicator': Activity,
      'unconventional_ioc': Lock,
      'campaign_name': TrendingUp,
      'malware_family': AlertTriangle,
      'vulnerability_type': Shield,
      'geo_location': MapPin,
      'network_protocol': Wifi,
      'cloud_service': Cloud,
      'container_id': Settings,
      'blockchain_address': Hash,
      'certificate_hash': Key,
      'registry_key': HardDrive,
      'process_name': Cpu,
      'service_name': Wrench
    };
    return iconMap[entityType] || Eye;
  };

  const getReputationColor = (rep: string) => {
    switch (rep) {
      case 'malicious': return 'text-red-400 bg-red-900/20 border-red-700';
      case 'suspicious': return 'text-yellow-400 bg-yellow-900/20 border-yellow-700';
      case 'clean': return 'text-green-400 bg-green-900/20 border-green-700';
      default: return 'text-gray-400 bg-gray-900/20 border-gray-700';
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 0.8) return 'text-red-400 bg-red-900/30';
    if (score >= 0.6) return 'text-orange-400 bg-orange-900/30';
    if (score >= 0.4) return 'text-yellow-400 bg-yellow-900/30';
    return 'text-green-400 bg-green-900/30';
  };

  const getEntityTypeLabel = (entityType: AdvancedEntityType): string => {
    const labelMap: Record<AdvancedEntityType, string> = {
      'ip_address': 'IP Address',
      'domain': 'Domain',
      'email': 'Email',
      'hash': 'File Hash',
      'cve': 'CVE',
      'url': 'URL',
      'port': 'Port',
      'username': 'Username',
      'filename': 'Filename',
      'mitre_technique': 'MITRE Technique',
      'threat_actor': 'Threat Actor',
      'device_id': 'IoT Device',
      'model_id': 'AI Model',
      'attack_technique': 'Attack Technique',
      'behavioral_indicator': 'Behavioral Indicator',
      'unconventional_ioc': 'Advanced IOC',
      'campaign_name': 'Campaign',
      'malware_family': 'Malware Family',
      'vulnerability_type': 'Vulnerability',
      'geo_location': 'Location',
      'network_protocol': 'Protocol',
      'cloud_service': 'Cloud Service',
      'container_id': 'Container',
      'blockchain_address': 'Blockchain Address',
      'certificate_hash': 'Certificate',
      'registry_key': 'Registry Key',
      'process_name': 'Process',
      'service_name': 'Service'
    };
    return labelMap[entityType] || entityType.replace('_', ' ').toUpperCase();
  };

  const getSmartActions = () => {
    const actions = [];
    
    // Entity-specific actions
    switch (entity.type) {
      case 'threat_actor':
        actions.push(
          { label: 'Hunt Campaigns', action: 'hunt_campaigns', variant: 'primary' },
          { label: 'Block TTPs', action: 'block_ttps', variant: 'danger' }
        );
        break;
      case 'device_id':
        actions.push(
          { label: 'Isolate Device', action: 'isolate_device', variant: 'danger' },
          { label: 'Update Firmware', action: 'update_firmware', variant: 'secondary' }
        );
        break;
      case 'model_id':
        actions.push(
          { label: 'Audit Model', action: 'audit_model', variant: 'primary' },
          { label: 'Retrain Model', action: 'retrain_model', variant: 'secondary' }
        );
        break;
      case 'ip_address':
        actions.push(
          { label: 'Block IP', action: 'block_ip', variant: 'danger' },
          { label: 'Check Reputation', action: 'check_reputation', variant: 'secondary' }
        );
        break;
      case 'mitre_technique':
        actions.push(
          { label: 'View Kill Chain', action: 'view_killchain', variant: 'primary' },
          { label: 'Deploy Countermeasures', action: 'deploy_countermeasures', variant: 'secondary' }
        );
        break;
      default:
        actions.push(
          { label: 'Investigate', action: 'investigate', variant: 'primary' },
          { label: 'Monitor', action: 'monitor', variant: 'secondary' }
        );
    }
    
    return actions;
  };

  const getActionColor = (variant: string) => {
    switch (variant) {
      case 'danger': return 'bg-red-600 hover:bg-red-700 text-white';
      case 'primary': return 'bg-blue-600 hover:bg-blue-700 text-white';
      default: return 'bg-gray-600 hover:bg-gray-700 text-gray-300';
    }
  };

  const EntityIcon = getEntityIcon(entity.type);
  const smartActions = getSmartActions();

  if (compact) {
    return (
      <div className="flex items-center space-x-2 p-2 bg-gray-800/50 rounded border border-gray-700">
        <div className={`p-1 rounded border ${getReputationColor(reputation)}`}>
          <EntityIcon className="w-3 h-3" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-mono text-sm text-white truncate">{entity.text}</div>
          <div className="text-xs text-gray-400">{getEntityTypeLabel(entity.type)}</div>
        </div>
        {riskScore > 0 && (
          <div className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(riskScore)}`}>
            {(riskScore * 100).toFixed(0)}%
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 max-w-lg">
      {/* 🔥 ADVANCED HEADER */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3">
          <div className={`p-2 rounded-lg border ${getReputationColor(reputation)}`}>
            <EntityIcon className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <h3 className="text-base font-bold text-white font-mono">{entity.text}</h3>
              {riskScore > 0 && (
                <span className={`px-2 py-1 rounded text-xs font-bold ${getRiskColor(riskScore)}`}>
                  RISK: {(riskScore * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <p className="text-sm text-blue-400 font-medium">{getEntityTypeLabel(entity.type)}</p>
            <p className="text-xs text-gray-400 mt-1">{entity.description}</p>
          </div>
        </div>
        {onClose && (
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-300 p-1"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 🎯 THREAT INTELLIGENCE GRID */}
      {enrichment && (
        <div className="space-y-4">
          {/* Core Metrics */}
          <div className="grid grid-cols-3 gap-3">
            <div className={`p-3 rounded border text-center ${getReputationColor(reputation)}`}>
              <div className="text-xs font-medium uppercase opacity-80">Reputation</div>
              <div className="text-sm font-bold mt-1 capitalize">{reputation}</div>
            </div>
            <div className="p-3 rounded border border-gray-600 text-center">
              <div className="text-xs font-medium text-gray-400 uppercase">Confidence</div>
              <div className="text-sm font-bold text-white mt-1">{(confidence * 100).toFixed(1)}%</div>
            </div>
            <div className={`p-3 rounded border text-center ${getRiskColor(riskScore)} border-current`}>
              <div className="text-xs font-medium uppercase opacity-80">Risk</div>
              <div className="text-sm font-bold mt-1">{(riskScore * 100).toFixed(0)}%</div>
            </div>
          </div>

          {/* 📍 CONTEXTUAL DATA */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            {enrichment.geo_location && (
              <div className="flex items-center space-x-2 text-gray-300">
                <MapPin className="w-4 h-4 text-blue-400" />
                <span>
                  {enrichment.geo_location.country}
                  {enrichment.geo_location.city && `, ${enrichment.geo_location.city}`}
                </span>
              </div>
            )}
            
            {enrichment.first_seen && (
              <div className="flex items-center space-x-2 text-gray-300">
                <Clock className="w-4 h-4 text-green-400" />
                <span>First: {new Date(enrichment.first_seen).toLocaleDateString()}</span>
              </div>
            )}
            
            {enrichment.last_seen && (
              <div className="flex items-center space-x-2 text-gray-300">
                <Activity className="w-4 h-4 text-orange-400" />
                <span>Last: {new Date(enrichment.last_seen).toLocaleDateString()}</span>
              </div>
            )}
            
            {enrichment.asn && (
              <div className="flex items-center space-x-2 text-gray-300">
                <Server className="w-4 h-4 text-purple-400" />
                <span className="truncate">{enrichment.asn}</span>
              </div>
            )}
          </div>

          {/* 🏷️ TAGS SECTION */}
          <div className="space-y-3">
            {/* Risk Factors */}
            {enrichment.risk_factors && enrichment.risk_factors.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-gray-400 mb-2 uppercase">Risk Factors</div>
                <div className="flex flex-wrap gap-1">
                  {enrichment.risk_factors.map((factor, index) => (
                    <span key={index} className="px-2 py-1 bg-red-900/30 text-red-300 text-xs rounded-full border border-red-700/30">
                      {factor}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Campaigns */}
            {enrichment.campaigns && enrichment.campaigns.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-gray-400 mb-2 uppercase">Campaigns</div>
                <div className="flex flex-wrap gap-1">
                  {enrichment.campaigns.map((campaign, index) => (
                    <span key={index} className="px-2 py-1 bg-orange-900/30 text-orange-300 text-xs rounded-full border border-orange-700/30">
                      {campaign}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Threat Actors */}
            {enrichment.threat_actors && enrichment.threat_actors.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-gray-400 mb-2 uppercase">Threat Actors</div>
                <div className="flex flex-wrap gap-1">
                  {enrichment.threat_actors.map((actor, index) => (
                    <span key={index} className="px-2 py-1 bg-purple-900/30 text-purple-300 text-xs rounded-full border border-purple-700/30">
                      {actor}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Malware Families */}
            {enrichment.malware_families && enrichment.malware_families.length > 0 && (
              <div>
                <div className="text-xs font-semibold text-gray-400 mb-2 uppercase">Malware Families</div>
                <div className="flex flex-wrap gap-1">
                  {enrichment.malware_families.map((family, index) => (
                    <span key={index} className="px-2 py-1 bg-red-900/30 text-red-300 text-xs rounded-full border border-red-700/30">
                      {family}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 🚀 SMART ACTIONS */}
          <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-700">
            {smartActions.map((action, index) => (
              <button
                key={index}
                onClick={() => onActionTaken?.(action.action, entity)}
                className={`flex items-center space-x-1 px-3 py-2 text-xs font-medium rounded transition-colors ${getActionColor(action.variant)}`}
              >
                <Eye className="w-3 h-3" />
                <span>{action.label}</span>
              </button>
            ))}
          </div>

          {/* 🔍 DETAILED VIEW TOGGLE */}
          <button 
            onClick={() => setShowFullDetails(!showFullDetails)}
            className="w-full text-xs text-blue-400 hover:text-blue-300 transition-colors py-2 border-t border-gray-700"
          >
            {showFullDetails ? '▲ Hide Advanced Details' : '▼ Show Advanced Details'}
          </button>

          {/* 📋 FULL DETAILS */}
          {showFullDetails && (
            <div className="mt-4 p-3 bg-gray-900/50 rounded border border-gray-600 text-xs space-y-2">
              <div className="font-semibold text-blue-400 mb-3">🔬 Advanced Intelligence</div>
              
              <div className="grid grid-cols-1 gap-2">
                <div>
                  <span className="text-gray-400">Entity Text: </span>
                  <span className="text-gray-300 font-mono">{entity.text}</span>
                </div>
                <div>
                  <span className="text-gray-400">Type: </span>
                  <span className="text-gray-300">{getEntityTypeLabel(entity.type)}</span>
                </div>
                <div>
                  <span className="text-gray-400">Confidence: </span>
                  <span className="text-gray-300">{(confidence * 100).toFixed(2)}%</span>
                </div>
                <div>
                  <span className="text-gray-400">Risk Score: </span>
                  <span className={`font-semibold ${riskScore >= 0.7 ? 'text-red-400' : riskScore >= 0.4 ? 'text-yellow-400' : 'text-green-400'}`}>
                    {(riskScore * 100).toFixed(1)}%
                  </span>
                </div>
                
                {entity.context && (
                  <div>
                    <span className="text-gray-400">Context: </span>
                    <span className="text-gray-300">{entity.context}</span>
                  </div>
                )}
                
                {enrichment.confidence && (
                  <div>
                    <span className="text-gray-400">Intel Confidence: </span>
                    <span className="text-gray-300">{(enrichment.confidence * 100).toFixed(1)}%</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Fallback for entities without enrichment */}
      {!enrichment && (
        <div className="text-center py-4 text-gray-500">
          <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No threat intelligence available</p>
          <p className="text-xs">Confidence: {(confidence * 100).toFixed(1)}%</p>
        </div>
      )}
    </div>
  );
};

export default AdvancedEntityDisplay;
