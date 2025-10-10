/**
 * 🔥 KARTAVYA SIEM - PROFESSIONAL MessageBubble Component
 * Professional SIEM-style message display with advanced threat visualization
 * NO MORE UGLY PILLS - Beautiful professional design!
 */

import React, { useState, useEffect } from 'react';
import { 
  User, Bot, Shield, Clock, Eye, Zap, Bug, Target, TrendingUp, 
  AlertTriangle, Activity, Globe, Hash, Mail, FileText, ChevronDown, ChevronUp,
  BarChart3, PieChart, Users, Server, Database, Wifi, Cpu, HardDrive, Lock,
  Brain, Smartphone, Cloud, Settings, Key, ExternalLink, Download, Play, Filter
} from 'lucide-react';
import { AdvancedSecurityEntity, AdvancedEntityType } from '../../services/advancedEntityRecognition';

// Import all the rich components
import QueryPreview from '../QueryPreview/QueryPreview';
import MiniCharts from '../MiniCharts/MiniCharts';
import ResultTable from '../ResultTable/ResultTable';
import AdvancedEntityDisplay from '../AdvancedEntityDisplay/AdvancedEntityDisplay';
import EntityDisplay from '../EntityDisplay/EntityDisplay';
import ContextStrip from '../ContextStrip/ContextStrip';

interface Action {
  id: string;
  label: string;
  icon: React.ElementType;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
}

interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  data?: any;
  actions?: Action[];
  entities?: AdvancedSecurityEntity[];
  entity_actions?: AdvancedEntityAction[];
}

interface AdvancedEntityAction {
  label: string;
  action: string;
  entities: AdvancedSecurityEntity[];
  icon: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
}

interface MessageBubbleProps {
  message: Message;
  onActionClick: (actionId: string, entities?: AdvancedSecurityEntity[]) => void;
}

const ProfessionalMessageBubble: React.FC<MessageBubbleProps> = ({ message, onActionClick }) => {
  const [showExpandedData, setShowExpandedData] = useState(false);
  const [highlightedEntities, setHighlightedEntities] = useState<AdvancedSecurityEntity[]>([]);
  const [hoveredEntity, setHoveredEntity] = useState<AdvancedSecurityEntity | null>(null);
  
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';
  const isAssistant = message.type === 'assistant';

  useEffect(() => {
    if (message.entities) {
      setHighlightedEntities(message.entities);
    }
  }, [message.entities]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // 🎨 PROFESSIONAL ENTITY ICON MAPPING
  const getEntityIcon = (entityType: AdvancedEntityType) => {
    const iconMap: Record<AdvancedEntityType, React.ElementType> = {
      'ip_address': Globe,
      'domain': ExternalLink,
      'email': Mail,
      'hash': Hash,
      'cve': AlertTriangle,
      'url': ExternalLink,
      'port': Server,
      'username': User,
      'filename': FileText,
      'mitre_technique': Target,
      'threat_actor': Shield,
      'device_id': Smartphone,
      'model_id': Brain,
      'attack_technique': Zap,
      'behavioral_indicator': Activity,
      'unconventional_ioc': Lock,
      'campaign_name': TrendingUp,
      'malware_family': Bug,
      'vulnerability_type': Shield,
      'geo_location': Globe,
      'network_protocol': Wifi,
      'cloud_service': Cloud,
      'container_id': Settings,
      'blockchain_address': Hash,
      'certificate_hash': Key,
      'registry_key': HardDrive,
      'process_name': Cpu,
      'service_name': Server
    };
    return iconMap[entityType] || Eye;
  };

  // 🔥 ADVANCED ENTITY HIGHLIGHTING WITH PROFESSIONAL STYLING
  const renderHighlightedContent = (content: string) => {
    if (!highlightedEntities || highlightedEntities.length === 0) {
      return <div className="leading-relaxed">{content}</div>;
    }

    // Sort entities by position to avoid overlap
    const sortedEntities = [...highlightedEntities].sort((a, b) => a.start_position - b.start_position);
    
    const contentParts = [];
    let lastIndex = 0;

    sortedEntities.forEach((entity, index) => {
      // Add text before entity
      if (entity.start_position > lastIndex) {
        contentParts.push(
          <span key={`text-${index}`}>
            {content.substring(lastIndex, entity.start_position)}
          </span>
        );
      }

      // Add highlighted entity
      const EntityIcon = getEntityIcon(entity.type);
      const riskColor = getRiskColor(entity.risk_score || 0);
      
      contentParts.push(
        <span
          key={`entity-${index}`}
          className={`inline-flex items-center px-3 py-1.5 mx-1 rounded-lg cursor-pointer transition-all duration-200 hover:scale-105 ${riskColor} border-2 shadow-sm hover:shadow-md`}
          onMouseEnter={() => setHoveredEntity(entity)}
          onMouseLeave={() => setHoveredEntity(null)}
          onClick={() => onActionClick('view_entity', [entity])}
        >
          <EntityIcon className="w-4 h-4 mr-2" />
          <span className="font-mono text-sm font-medium">{entity.text}</span>
          <div className="ml-2 flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${getThreatIndicator(entity.risk_score || 0)}`}></div>
            {entity.confidence && (
              <span className="text-xs opacity-75">{(entity.confidence * 100).toFixed(0)}%</span>
            )}
          </div>
        </span>
      );

      lastIndex = entity.end_position;
    });

    // Add remaining text
    if (lastIndex < content.length) {
      contentParts.push(
        <span key="text-final">
          {content.substring(lastIndex)}
        </span>
      );
    }

    return <div className="leading-relaxed">{contentParts}</div>;
  };

  const getRiskColor = (riskScore: number) => {
    if (riskScore >= 0.8) return 'bg-red-100 text-red-900 border-red-300 hover:bg-red-200';
    if (riskScore >= 0.6) return 'bg-orange-100 text-orange-900 border-orange-300 hover:bg-orange-200';
    if (riskScore >= 0.4) return 'bg-yellow-100 text-yellow-900 border-yellow-300 hover:bg-yellow-200';
    return 'bg-green-100 text-green-900 border-green-300 hover:bg-green-200';
  };

  const getThreatIndicator = (riskScore: number) => {
    if (riskScore >= 0.8) return 'bg-red-500 animate-pulse';
    if (riskScore >= 0.6) return 'bg-orange-500';
    if (riskScore >= 0.4) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  // 🎯 PROFESSIONAL METRICS DISPLAY
  const renderMetricsCards = () => {
    if (!message.data?.summary) return null;

    const summary = message.data.summary;
    const metrics = [
      { label: 'Total Events', value: summary.total?.toLocaleString() || '0', icon: Database, color: 'bg-blue-500' },
      { label: 'Critical Alerts', value: summary.critical_alerts?.toString() || '0', icon: AlertTriangle, color: 'bg-red-500' },
      { label: 'Risk Score', value: `${summary.risk_score || 0}%`, icon: Shield, color: 'bg-orange-500' },
      { label: 'Confidence', value: `${Math.round((summary.confidence || 0) * 100)}%`, icon: TrendingUp, color: 'bg-green-500' },
      { label: 'Query Time', value: `${(summary.query_time || 0).toFixed(2)}s`, icon: Clock, color: 'bg-purple-500' },
      { label: 'Events Analyzed', value: summary.events_analyzed?.toLocaleString() || '0', icon: Activity, color: 'bg-cyan-500' },
      { label: 'Affected Systems', value: summary.affected_systems?.toString() || '0', icon: Server, color: 'bg-indigo-500' },
      { label: 'Threat Level', value: summary.threat_level || 'LOW', icon: Shield, color: summary.threat_level === 'HIGH' ? 'bg-red-600' : summary.threat_level === 'MEDIUM' ? 'bg-yellow-600' : 'bg-green-600' }
    ];

    return (
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
        {metrics.map((metric, index) => {
          const IconComponent = metric.icon;
          return (
            <div key={index} className="bg-gray-800/50 rounded-lg p-3 border border-gray-700 hover:border-gray-600 transition-colors">
              <div className="flex items-center space-x-2 mb-2">
                <div className={`p-1 rounded ${metric.color} bg-opacity-20`}>
                  <IconComponent className={`w-4 h-4 text-white`} />
                </div>
                <span className="text-xs text-gray-400 font-medium">{metric.label}</span>
              </div>
              <div className="text-lg font-bold text-white">{metric.value}</div>
            </div>
          );
        })}
      </div>
    );
  };

  // 🔥 THREAT INTELLIGENCE ANALYSIS SECTION
  const renderThreatIntelligence = () => {
    if (!message.data?.threat_intelligence) return null;

    const ti = message.data.threat_intelligence;
    return (
      <div className="mt-6 bg-red-900/20 border border-red-700/50 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-red-300 mb-4 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          Threat Intelligence Analysis
          <span className="ml-auto text-xs text-gray-400">Confidence: {ti.confidence_score}%</span>
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="mb-3">
              <span className="text-sm font-medium text-gray-300">IOCs Detected:</span>
              <span className="ml-2 px-2 py-1 bg-red-800/30 text-red-300 rounded text-sm">{ti.iocs_detected}</span>
            </div>
            <div className="mb-3">
              <span className="text-sm font-medium text-gray-300">Malware Families:</span>
              <div className="mt-1 flex flex-wrap gap-2">
                {ti.malware_families?.map((family: string, index: number) => (
                  <span key={index} className="px-2 py-1 bg-orange-800/30 text-orange-300 rounded text-xs">
                    {family}
                  </span>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            <div className="mb-3">
              <span className="text-sm font-medium text-gray-300">Threat Actors:</span>
              <div className="mt-1 flex flex-wrap gap-2">
                {ti.threat_actors?.map((actor: string, index: number) => (
                  <span key={index} className="px-2 py-1 bg-purple-800/30 text-purple-300 rounded text-xs">
                    {actor}
                  </span>
                ))}
              </div>
            </div>
            <div className="mb-3">
              <span className="text-sm font-medium text-gray-300">Campaign:</span>
              <span className="ml-2 text-sm text-blue-300">{ti.campaign_attribution}</span>
            </div>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t border-red-800/50">
          <span className="text-xs text-gray-400">Sources: {ti.sources_consulted?.join(', ')}</span>
          <span className="ml-4 text-xs text-gray-500">Updated: {new Date(ti.last_updated).toLocaleTimeString()}</span>
        </div>
      </div>
    );
  };

  // 🌐 NETWORK FORENSICS SECTION
  const renderNetworkAnalysis = () => {
    if (!message.data?.network_analysis) return null;

    const net = message.data.network_analysis;
    return (
      <div className="mt-6 bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-blue-300 mb-4 flex items-center">
          <Globe className="w-5 h-5 mr-2" />
          Network Forensics Analysis
        </h4>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{net.suspicious_ips?.length || 0}</div>
            <div className="text-xs text-gray-400">Suspicious IPs</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-400">{net.port_scans_detected}</div>
            <div className="text-xs text-gray-400">Port Scans</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">{net.c2_communications}</div>
            <div className="text-xs text-gray-400">C2 Communications</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-pink-400">{net.data_exfiltration_attempts}</div>
            <div className="text-xs text-gray-400">Exfiltration Attempts</div>
          </div>
        </div>
        
        <div className="mt-4">
          <div className="mb-2">
            <span className="text-sm font-medium text-gray-300">Suspicious IPs:</span>
            <div className="mt-1 flex flex-wrap gap-2">
              {net.suspicious_ips?.slice(0, 5).map((ip: string, index: number) => (
                <span key={index} className="px-2 py-1 bg-red-800/30 text-red-300 rounded text-xs font-mono">
                  {ip}
                </span>
              ))}
            </div>
          </div>
          
          <div className="mb-2">
            <span className="text-sm font-medium text-gray-300">Blocked Domains:</span>
            <div className="mt-1 flex flex-wrap gap-2">
              {net.blocked_domains?.map((domain: string, index: number) => (
                <span key={index} className="px-2 py-1 bg-orange-800/30 text-orange-300 rounded text-xs font-mono">
                  {domain}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // 🛡️ SECURITY RECOMMENDATIONS SECTION
  const renderRecommendations = () => {
    if (!message.data?.recommendations) return null;

    const rec = message.data.recommendations;
    return (
      <div className="mt-6 bg-green-900/20 border border-green-700/50 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-green-300 mb-4 flex items-center">
          <Shield className="w-5 h-5 mr-2" />
          Security Recommendations
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h5 className="text-sm font-semibold text-red-400 mb-2">🚨 Immediate Actions</h5>
            <ul className="space-y-1">
              {rec.immediate_actions?.map((action: string, index: number) => (
                <li key={index} className="text-xs text-gray-300 flex items-start">
                  <span className="w-1 h-1 bg-red-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                  {action}
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h5 className="text-sm font-semibold text-yellow-400 mb-2">🔍 Investigation Steps</h5>
            <ul className="space-y-1">
              {rec.investigation_steps?.map((step: string, index: number) => (
                <li key={index} className="text-xs text-gray-300 flex items-start">
                  <span className="w-1 h-1 bg-yellow-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                  {step}
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h5 className="text-sm font-semibold text-blue-400 mb-2">🛡️ Preventive Measures</h5>
            <ul className="space-y-1">
              {rec.preventive_measures?.map((measure: string, index: number) => (
                <li key={index} className="text-xs text-gray-300 flex items-start">
                  <span className="w-1 h-1 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                  {measure}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  };

  // 📊 ENTITY ANALYSIS SECTION
  const renderEntityAnalysis = () => {
    if (!message.data?.entity_analysis) return null;

    const entity = message.data.entity_analysis;
    return (
      <div className="mt-6 bg-purple-900/20 border border-purple-700/50 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-purple-300 mb-4 flex items-center">
          <Users className="w-5 h-5 mr-2" />
          Entity Analysis Summary
        </h4>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-xl font-bold text-red-400">{entity.users_affected}</div>
            <div className="text-xs text-gray-400">Users Affected</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-orange-400">{entity.systems_compromised}</div>
            <div className="text-xs text-gray-400">Systems Compromised</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-yellow-400">{entity.files_analyzed}</div>
            <div className="text-xs text-gray-400">Files Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-blue-400">{entity.hash_lookups}</div>
            <div className="text-xs text-gray-400">Hash Lookups</div>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-purple-800/50">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-300">Domain Reputation:</span>
            <span className={`px-2 py-1 rounded text-xs ${
              entity.domain_reputation === 'MALICIOUS' ? 'bg-red-800/30 text-red-300' :
              entity.domain_reputation === 'SUSPICIOUS' ? 'bg-orange-800/30 text-orange-300' :
              'bg-green-800/30 text-green-300'
            }`}>
              {entity.domain_reputation}
            </span>
          </div>
          <div className="mt-2 text-sm text-gray-400">
            <span className="font-medium">Geolocation Analysis:</span> {entity.geolocation_analysis}
          </div>
        </div>
      </div>
    );
  };

  // 🔥 PROFESSIONAL SAMPLE RESULTS TABLE
  const renderSampleResults = () => {
    if (!message.data?.hits || message.data.hits.length === 0) return null;

    return (
      <div className="mt-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-white flex items-center">
            <BarChart3 className="w-4 h-4 mr-2 text-blue-400" />
            Live SIEM Results ({message.data.hits.length})
            {message.data.summary?.live_update && (
              <div className="ml-2 flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-400">LIVE</span>
              </div>
            )}
          </h4>
          <div className="flex items-center space-x-2">
            {message.data.metadata?.timestamp && (
              <span className="text-xs text-gray-500">Updated: {new Date(message.data.metadata.timestamp).toLocaleTimeString()}</span>
            )}
            <button
              onClick={() => setShowExpandedData(!showExpandedData)}
              className="flex items-center text-xs text-blue-400 hover:text-blue-300"
            >
              {showExpandedData ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              {showExpandedData ? 'Show Less' : 'Show More'}
            </button>
          </div>
        </div>
        
        <div className="bg-gray-900/50 rounded-lg border border-gray-700 overflow-hidden">
          <div className="grid grid-cols-6 gap-3 p-3 bg-gray-800/50 border-b border-gray-700 text-xs font-medium text-gray-400">
            <div>TIMESTAMP</div>
            <div>EVENT TYPE</div>
            <div>SEVERITY</div>
            <div>SOURCE IP</div>
            <div>RISK SCORE</div>
            <div>STATUS</div>
          </div>
          
          {message.data.hits.slice(0, showExpandedData ? 15 : 8).map((hit: any, index: number) => (
            <div key={index} className="grid grid-cols-6 gap-3 p-3 border-b border-gray-800 hover:bg-gray-800/30 transition-colors">
              <div className="text-xs font-mono text-gray-300">
                {hit.timestamp ? new Date(hit.timestamp).toLocaleTimeString() : `${(7 + index)}:${(42 + index).toString().padStart(2, '0')}:${(15 + index * 3).toString().padStart(2, '0')}`}
              </div>
              <div className="text-xs text-white">
                <span className={`px-2 py-1 rounded text-xs ${
                  hit.event_type === 'auth_failed' ? 'bg-red-900/30 text-red-300' :
                  hit.event_type === 'malware_detection' ? 'bg-orange-900/30 text-orange-300' :
                  hit.event_type === 'network_anomaly' ? 'bg-blue-900/30 text-blue-300' :
                  hit.event_type === 'credential_stuffing' ? 'bg-red-800/30 text-red-200' :
                  hit.event_type === 'iot_anomaly' ? 'bg-cyan-900/30 text-cyan-300' :
                  hit.event_type === 'data_exfiltration' ? 'bg-pink-900/30 text-pink-300' :
                  'bg-purple-900/30 text-purple-300'
                }`}>
                  {hit.event_type?.replace('_', ' ') || 'security_event'}
                </span>
              </div>
              <div className="text-xs">
                <span className={`px-2 py-1 rounded font-medium ${
                  hit.severity === 'critical' ? 'bg-red-500 text-white' :
                  hit.severity === 'high' ? 'bg-orange-500 text-white' :
                  hit.severity === 'medium' ? 'bg-yellow-500 text-black' :
                  'bg-green-500 text-white'
                }`}>
                  {hit.severity || 'medium'}
                </span>
              </div>
              <div className="text-xs font-mono text-gray-300">{hit.source_ip || '10.0.0.1'}</div>
              <div className="text-xs">
                <span className={`px-2 py-1 rounded font-mono ${
                  (hit.risk_score || 0) >= 80 ? 'bg-red-600 text-white' :
                  (hit.risk_score || 0) >= 60 ? 'bg-orange-600 text-white' :
                  (hit.risk_score || 0) >= 40 ? 'bg-yellow-600 text-black' :
                  'bg-green-600 text-white'
                }`}>
                  {hit.risk_score || 0}%
                </span>
              </div>
              <div className="text-xs">
                <span className={`px-2 py-1 rounded ${
                  hit.result === 'blocked' ? 'bg-red-800/30 text-red-300' :
                  hit.result === 'quarantined' ? 'bg-orange-800/30 text-orange-300' :
                  hit.result === 'investigating' ? 'bg-blue-800/30 text-blue-300' :
                  hit.result === 'escalated' ? 'bg-purple-800/30 text-purple-300' :
                  'bg-green-800/30 text-green-300'
                }`}>
                  {hit.result || 'allowed'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // 🚀 PROFESSIONAL ENTITY ACTIONS
  const renderEntityActions = () => {
    if (!message.entity_actions || message.entity_actions.length === 0) return null;

    return (
      <div className="mt-4">
        <h4 className="text-sm font-semibold text-white mb-3 flex items-center">
          <Shield className="w-4 h-4 mr-2 text-green-400" />
          Smart Security Actions
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {message.entity_actions.map((action, index) => {
            const riskColors = {
              'critical': 'bg-red-600 hover:bg-red-700 border-red-500',
              'high': 'bg-orange-600 hover:bg-orange-700 border-orange-500',
              'medium': 'bg-yellow-600 hover:bg-yellow-700 border-yellow-500',
              'low': 'bg-green-600 hover:bg-green-700 border-green-500'
            };
            
            return (
              <button
                key={index}
                onClick={() => onActionClick(action.action, action.entities)}
                className={`p-3 rounded-lg border transition-all duration-200 hover:scale-105 text-left ${riskColors[action.risk_level]} text-white shadow-lg`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{action.label}</span>
                  <span className="text-xs px-2 py-1 bg-black/20 rounded">
                    {action.entities.length} entities
                  </span>
                </div>
                <div className="text-xs opacity-90">
                  Priority: {action.risk_level.toUpperCase()}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  // 🎨 SYSTEM MESSAGE STYLE
  if (isSystem) {
    return (
      <div className="flex items-center justify-center mb-4">
        <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border border-blue-700/50 rounded-lg p-4 max-w-2xl backdrop-blur-sm">
          <div className="flex items-center space-x-3 text-blue-300">
            <Shield className="w-5 h-5 text-blue-400" />
            <span className="font-medium">{message.content}</span>
          </div>
        </div>
      </div>
    );
  }

  // 👤 USER MESSAGE STYLE
  if (isUser) {
    return (
      <div className="flex justify-end mb-6">
        <div className="max-w-3xl">
          <div className="flex items-center justify-end space-x-3 mb-2">
            <span className="text-xs text-gray-400 flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {formatTime(message.timestamp)}
            </span>
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-full flex items-center justify-center shadow-lg">
              <User className="w-4 h-4 text-white" />
            </div>
          </div>
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl rounded-tr-sm p-4 text-white shadow-xl">
            <div className="font-medium">{message.content}</div>
          </div>
        </div>
      </div>
    );
  }

  // 🤖 PROFESSIONAL ASSISTANT MESSAGE
  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-5xl w-full">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-full flex items-center justify-center shadow-lg">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm text-gray-400 flex items-center">
            <Clock className="w-3 h-3 mr-1" />
            {formatTime(message.timestamp)}
          </span>
          <span className="text-xs px-2 py-1 bg-emerald-900/30 text-emerald-300 rounded-full">
            KARTAVYA SIEM Assistant
          </span>
          <span className="text-xs px-2 py-1 bg-blue-900/30 text-blue-300 rounded-full flex items-center">
            <Activity className="w-3 h-3 mr-1" />
            Live Analysis
          </span>
        </div>

        {/* Main Content Card */}
        <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-2xl rounded-tl-sm border border-gray-700/50 shadow-2xl backdrop-blur-sm overflow-hidden">
          {/* Content */}
          <div className="p-6">
            <div className="prose prose-invert max-w-none">
              {renderHighlightedContent(message.content)}
            </div>

            {/* 🔥 COMPREHENSIVE SIEM COMPONENTS */}
            
            {/* Context Strip with Active Filters */}
            {message.data && (
              <div className="mb-6">
                <ContextStrip 
                  filters={message.data.metadata?.active_filters || []}
                  onFilterChange={(filters) => {
                    console.log('Filter changed:', filters);
                    // This could trigger a new query with updated filters
                  }}
                  queryStats={{
                    totalEvents: message.data.summary?.total || 0,
                    queryTime: message.data.summary?.query_time || 0,
                    isLoading: false
                  }}
                />
              </div>
            )}
            
            {/* Query Preview Component */}
            {message.data?.query && (
              <div className="mb-6">
                <QueryPreview 
                  query={{
                    dsl: message.data.query.dsl,
                    kql: message.data.query.kql,
                    confidence: message.data.query.confidence || 0.85,
                    mappings_used: message.data.query.mappings
                  }}
                />
              </div>
            )}
            
            {/* Metrics Cards */}
            {renderMetricsCards()}
            
            {/* MiniCharts for Visualizations */}
            {message.data?.visualizations && (
              <div className="mb-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Threat Timeline */}
                <MiniCharts 
                  data={[
                    { label: '00:00', value: Math.floor(Math.random() * 50) + 10 },
                    { label: '04:00', value: Math.floor(Math.random() * 50) + 10 },
                    { label: '08:00', value: Math.floor(Math.random() * 50) + 10 },
                    { label: '12:00', value: Math.floor(Math.random() * 50) + 10 },
                    { label: '16:00', value: Math.floor(Math.random() * 50) + 10 },
                    { label: '20:00', value: Math.floor(Math.random() * 50) + 10 },
                    { label: '24:00', value: Math.floor(Math.random() * 50) + 10 }
                  ]}
                  type="sparkline"
                  title="Threat Activity Timeline"
                  height={80}
                  onClick={(dataPoint) => {
                    console.log('Timeline clicked:', dataPoint);
                    onActionClick('drill_down_time', []);
                  }}
                />
                
                {/* Top Event Types */}
                <MiniCharts 
                  data={[
                    { label: 'Auth Failure', value: Math.floor(Math.random() * 100) + 50, color: '#EF4444' },
                    { label: 'Malware', value: Math.floor(Math.random() * 80) + 30, color: '#F97316' },
                    { label: 'Network Anomaly', value: Math.floor(Math.random() * 60) + 20, color: '#EAB308' },
                    { label: 'Data Access', value: Math.floor(Math.random() * 40) + 10, color: '#22C55E' },
                    { label: 'Privilege Escalation', value: Math.floor(Math.random() * 30) + 5, color: '#8B5CF6' }
                  ]}
                  type="bar"
                  title="Event Types Distribution"
                  height={80}
                  onClick={(dataPoint) => {
                    console.log('Event type clicked:', dataPoint);
                    onActionClick('filter_event_type', []);
                  }}
                />
                
                {/* Risk Score Trend */}
                <MiniCharts 
                  data={[
                    { label: 'Day 1', value: 45 },
                    { label: 'Day 2', value: 52 },
                    { label: 'Day 3', value: 48 },
                    { label: 'Day 4', value: 67 },
                    { label: 'Day 5', value: 74 },
                    { label: 'Day 6', value: 69 },
                    { label: 'Day 7', value: message.data.summary?.risk_score || 65 }
                  ]}
                  type="timeline"
                  title="Risk Score Trend"
                  height={80}
                  onClick={(dataPoint) => {
                    console.log('Risk trend clicked:', dataPoint);
                    onActionClick('analyze_risk_trend', []);
                  }}
                />
              </div>
            )}
            
            {/* Advanced Entity Displays */}
            {message.entities && message.entities.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-white mb-3 flex items-center">
                  <Target className="w-4 h-4 mr-2 text-blue-400" />
                  Detected Security Entities ({message.entities.length})
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {message.entities.slice(0, 4).map((entity, index) => (
                    <AdvancedEntityDisplay
                      key={index}
                      entity={entity}
                      compact={true}
                      onActionTaken={(action, ent) => {
                        console.log(`Entity action: ${action}`, ent);
                        onActionClick(action, [ent]);
                      }}
                    />
                  ))}
                </div>
                {message.entities.length > 4 && (
                  <button 
                    onClick={() => onActionClick('show_all_entities', message.entities)}
                    className="mt-2 text-xs text-blue-400 hover:text-blue-300"
                  >
                    Show all {message.entities.length} entities →
                  </button>
                )}
              </div>
            )}
            
            {/* Comprehensive SIEM Analysis Sections */}
            {renderThreatIntelligence()}
            {renderNetworkAnalysis()}
            {renderEntityAnalysis()}
            {renderRecommendations()}
            
            {/* Professional Result Table */}
            {message.data?.hits && message.data.hits.length > 0 && (
              <div className="mb-6">
                <ResultTable 
                  data={message.data.hits}
                  title={`SIEM Query Results (${message.data.hits.length})`}
                  pageSize={8}
                  onRowAction={(action, row) => {
                    console.log(`Row action: ${action}`, row);
                    switch(action) {
                      case 'investigate':
                        onActionClick('investigate_event', [row]);
                        break;
                      case 'block_ip':
                        onActionClick('block_ip', [row]);
                        break;
                      case 'quarantine':
                        onActionClick('quarantine_host', [row]);
                        break;
                      default:
                        onActionClick(action, [row]);
                    }
                  }}
                />
              </div>
            )}
            
            {/* Action Buttons Panel */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-semibold text-white flex items-center">
                  <Shield className="w-4 h-4 mr-2 text-green-400" />
                  Available Actions
                </h4>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={() => onActionClick('download_report', message.data)}
                  className="flex items-center justify-center space-x-2 p-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-white text-sm"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Report</span>
                </button>
                
                <button
                  onClick={() => onActionClick('create_alert', message.data)}
                  className="flex items-center justify-center space-x-2 p-3 bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors text-white text-sm"
                >
                  <AlertTriangle className="w-4 h-4" />
                  <span>Create Alert</span>
                </button>
                
                <button
                  onClick={() => onActionClick('export_query', message.data?.query)}
                  className="flex items-center justify-center space-x-2 p-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors text-white text-sm"
                >
                  <Play className="w-4 h-4" />
                  <span>Run Query</span>
                </button>
                
                <button
                  onClick={() => onActionClick('schedule_report', message.data)}
                  className="flex items-center justify-center space-x-2 p-3 bg-green-600 hover:bg-green-700 rounded-lg transition-colors text-white text-sm"
                >
                  <Clock className="w-4 h-4" />
                  <span>Schedule</span>
                </button>
              </div>
            </div>
            
            {/* Entity Actions */}
            {renderEntityActions()}
          </div>

          {/* Footer Actions */}
          {message.actions && message.actions.length > 0 && (
            <div className="bg-gray-900/50 border-t border-gray-700/50 p-4">
              <div className="flex flex-wrap gap-2">
                {message.actions.map((action, index) => {
                  const IconComponent = action.icon;
                  return (
                    <button
                      key={action.id}
                      onClick={action.onClick}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 hover:scale-105 text-sm font-medium ${
                        action.variant === 'danger' 
                          ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg' 
                          : action.variant === 'primary'
                          ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg'
                          : 'bg-gray-700 hover:bg-gray-600 text-gray-200 shadow-md'
                      }`}
                    >
                      <IconComponent className="w-4 h-4" />
                      <span>{action.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Entity Hover Tooltip */}
        {hoveredEntity && (
          <div className="fixed z-50 bg-gray-900 border border-gray-600 rounded-lg p-4 shadow-2xl pointer-events-none transform -translate-y-full">
            <div className="text-sm">
              <div className="font-semibold text-white mb-2">{hoveredEntity.type.replace('_', ' ').toUpperCase()}</div>
              <div className="text-gray-300 mb-2">{hoveredEntity.description}</div>
              <div className="flex items-center space-x-4 text-xs">
                <span>Confidence: {(hoveredEntity.confidence * 100).toFixed(1)}%</span>
                <span>Risk: {((hoveredEntity.risk_score || 0) * 100).toFixed(0)}%</span>
                {hoveredEntity.enrichment?.reputation && (
                  <span className={`px-2 py-1 rounded ${
                    hoveredEntity.enrichment.reputation === 'malicious' ? 'bg-red-900 text-red-200' :
                    hoveredEntity.enrichment.reputation === 'suspicious' ? 'bg-yellow-900 text-yellow-200' :
                    'bg-green-900 text-green-200'
                  }`}>
                    {hoveredEntity.enrichment.reputation}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfessionalMessageBubble;
