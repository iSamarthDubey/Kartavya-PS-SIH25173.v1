/**
 * KARTAVYA SIEM - MessageBubble Component
 * Renders individual chat messages with rich content and actions
 */

import React from 'react';
import { User, Bot, Shield, Clock, Eye, Zap, Bug, Target } from 'lucide-react';
import { AdvancedSecurityEntity, AdvancedEntityType } from '../../services/advancedEntityRecognition';

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
  entities?: AdvancedSecurityEntity[]; // V2.5 Enhancement: Advanced security entities with enrichment
  entity_actions?: AdvancedEntityAction[]; // V2.5 Enhancement: Advanced entity-based actions
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

// 🚀 V2.5 ADVANCED ENHANCEMENT: Entity highlighting with threat intelligence
const highlightEntities = (text: string, entities: AdvancedSecurityEntity[] = []): React.ReactNode => {
  if (!entities || entities.length === 0) {
    return text;
  }

  // Sort entities by start position (descending) to replace from end to beginning
  const sortedEntities = [...entities].sort((a, b) => b.start_position - a.start_position);
  
  let highlightedText = text;
  
  sortedEntities.forEach((entity) => {
    const entityText = highlightedText.substring(entity.start_position, entity.end_position);
    const entityColor = getAdvancedEntityColor(entity.type, entity.risk_score);
    const entityIcon = getAdvancedEntityIcon(entity.type);
    const riskIndicator = getRiskIndicator(entity.risk_score || 0);
    
    const tooltipText = `${entity.type.replace('_', ' ').toUpperCase()}: ${entity.text}\nConfidence: ${(entity.confidence * 100).toFixed(1)}%\nRisk Score: ${entity.risk_score || 'N/A'}${entity.enrichment ? `\nReputation: ${entity.enrichment.reputation}` : ''}`;
    
    const replacement = `<span class="inline-flex items-center px-2 py-1 mx-1 text-xs font-medium rounded-full ${entityColor} cursor-pointer" title="${tooltipText}">
      <span class="mr-1">${entityIcon}</span>
      ${entityText}
      ${riskIndicator}
    </span>`;
    
    highlightedText = highlightedText.substring(0, entity.start_position) + replacement + highlightedText.substring(entity.end_position);
  });
  
  return <span dangerouslySetInnerHTML={{ __html: highlightedText }} />;
};

const getEntityColor = (entityType: string): string => {
  const colorMap: Record<string, string> = {
    'IP_ADDRESS': 'bg-blue-100 text-blue-800 border border-blue-200',
    'DOMAIN': 'bg-green-100 text-green-800 border border-green-200',
    'EMAIL': 'bg-purple-100 text-purple-800 border border-purple-200',
    'HASH': 'bg-red-100 text-red-800 border border-red-200',
    'CVE': 'bg-orange-100 text-orange-800 border border-orange-200',
    'MITRE_TECHNIQUE': 'bg-indigo-100 text-indigo-800 border border-indigo-200',
    'USER_AGENT': 'bg-gray-100 text-gray-800 border border-gray-200',
    'FILE_PATH': 'bg-yellow-100 text-yellow-800 border border-yellow-200'
  };
  return colorMap[entityType] || 'bg-gray-100 text-gray-800 border border-gray-200';
};

const getEntityIcon = (entityType: string): string => {
  const iconMap: Record<string, string> = {
    'IP_ADDRESS': '🌐',
    'DOMAIN': '🔗',
    'EMAIL': '📧',
    'HASH': '🔒',
    'CVE': '🚨',
    'MITRE_TECHNIQUE': '🎯',
    'USER_AGENT': '🖥️',
    'FILE_PATH': '📁'
  };
  return iconMap[entityType] || '🔍';
};

// 🚀 ADVANCED ENTITY STYLING FUNCTIONS
const getAdvancedEntityColor = (entityType: AdvancedEntityType, riskScore?: number): string => {
  const baseColorMap: Record<AdvancedEntityType, string> = {
    // Core entities
    'ip_address': 'bg-blue-100 text-blue-900 border border-blue-300',
    'domain': 'bg-green-100 text-green-900 border border-green-300',
    'email': 'bg-purple-100 text-purple-900 border border-purple-300',
    'hash': 'bg-red-100 text-red-900 border border-red-300',
    'cve': 'bg-orange-100 text-orange-900 border border-orange-300',
    'url': 'bg-cyan-100 text-cyan-900 border border-cyan-300',
    'port': 'bg-gray-100 text-gray-900 border border-gray-300',
    'username': 'bg-indigo-100 text-indigo-900 border border-indigo-300',
    'filename': 'bg-yellow-100 text-yellow-900 border border-yellow-300',
    
    // Advanced entities
    'mitre_technique': 'bg-indigo-100 text-indigo-900 border border-indigo-300',
    'threat_actor': 'bg-red-200 text-red-900 border border-red-400',
    'device_id': 'bg-emerald-100 text-emerald-900 border border-emerald-300',
    'model_id': 'bg-violet-100 text-violet-900 border border-violet-300',
    'attack_technique': 'bg-rose-100 text-rose-900 border border-rose-300',
    'behavioral_indicator': 'bg-amber-100 text-amber-900 border border-amber-300',
    'unconventional_ioc': 'bg-red-300 text-red-950 border border-red-500',
    'campaign_name': 'bg-pink-100 text-pink-900 border border-pink-300',
    'malware_family': 'bg-red-200 text-red-950 border border-red-400',
    'vulnerability_type': 'bg-orange-200 text-orange-900 border border-orange-400',
    'geo_location': 'bg-teal-100 text-teal-900 border border-teal-300',
    'network_protocol': 'bg-slate-100 text-slate-900 border border-slate-300',
    'cloud_service': 'bg-sky-100 text-sky-900 border border-sky-300',
    'container_id': 'bg-lime-100 text-lime-900 border border-lime-300',
    'blockchain_address': 'bg-yellow-200 text-yellow-900 border border-yellow-400',
    'certificate_hash': 'bg-green-200 text-green-900 border border-green-400',
    'registry_key': 'bg-gray-200 text-gray-900 border border-gray-400',
    'process_name': 'bg-blue-200 text-blue-900 border border-blue-400',
    'service_name': 'bg-purple-200 text-purple-900 border border-purple-400'
  };
  
  let baseColor = baseColorMap[entityType] || 'bg-gray-100 text-gray-900 border border-gray-300';
  
  // Modify color based on risk score
  if (riskScore !== undefined) {
    if (riskScore >= 0.8) {
      baseColor = baseColor.replace('100', '200').replace('300', '400'); // More intense for high risk
    } else if (riskScore >= 0.6) {
      baseColor = baseColor.replace('100', '150').replace('300', '350'); // Medium intensity
    }
  }
  
  return baseColor;
};

const getAdvancedEntityIcon = (entityType: AdvancedEntityType): string => {
  const iconMap: Record<AdvancedEntityType, string> = {
    // Core entities
    'ip_address': '🌐',
    'domain': '🔗',
    'email': '📧',
    'hash': '🔒',
    'cve': '🚨',
    'url': '🔗',
    'port': '🚪',
    'username': '👤',
    'filename': '📁',
    
    // Advanced entities
    'mitre_technique': '🎯',
    'threat_actor': '🦹',
    'device_id': '🏭',
    'model_id': '🤖',
    'attack_technique': '⚔️',
    'behavioral_indicator': '📊',
    'unconventional_ioc': '🔬',
    'campaign_name': '🏴',
    'malware_family': '🦠',
    'vulnerability_type': '🛡️',
    'geo_location': '🌍',
    'network_protocol': '🔌',
    'cloud_service': '☁️',
    'container_id': '📦',
    'blockchain_address': '₿',
    'certificate_hash': '🔐',
    'registry_key': '🗝️',
    'process_name': '⚙️',
    'service_name': '🔧'
  };
  return iconMap[entityType] || '🔍';
};

const getRiskIndicator = (riskScore: number): string => {
  if (riskScore >= 0.8) return '<span class="ml-1 text-red-500">🔴</span>';
  if (riskScore >= 0.6) return '<span class="ml-1 text-orange-500">🟡</span>';
  if (riskScore >= 0.4) return '<span class="ml-1 text-yellow-500">🟡</span>';
  return '<span class="ml-1 text-green-500">🟢</span>';
};

const getEntityActionIcon = (iconName: string) => {
  const iconMap: Record<string, React.ComponentType<any>> = {
    'Eye': Eye,
    'Zap': Zap,
    'Bug': Bug,
    'Target': Target,
    'Shield': Shield
  };
  return iconMap[iconName] || Eye;
};

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onActionClick }) => {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getVariantStyles = (variant?: string) => {
    switch (variant) {
      case 'danger':
        return 'bg-red-600 hover:bg-red-700 text-white';
      case 'primary':
        return 'bg-blue-600 hover:bg-blue-700 text-white';
      default:
        return 'bg-gray-700 hover:bg-gray-600 text-gray-200';
    }
  };

  if (isSystem) {
    return (
      <div className="flex items-center justify-center">
        <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3 max-w-md">
          <div className="flex items-center space-x-2 text-blue-300 text-sm">
            <Shield className="w-4 h-4" />
            <span>{message.content}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-4xl ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar and Header */}
        <div className={`flex items-center space-x-2 mb-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
          {!isUser && (
            <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
          )}
          <span className="text-xs text-gray-400 flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>{formatTime(message.timestamp)}</span>
          </span>
          {isUser && (
            <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-lg p-4 ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-800 text-gray-100 border border-gray-700'
        }`}>
          <div className="text-sm leading-relaxed">
            {/* 🚀 V2 ENHANCEMENT: Entity-highlighted content */}
            {message.type === 'assistant' && message.entities ? 
              highlightEntities(message.content, message.entities) : 
              message.content
            }
          </div>

          {/* Data Summary Cards */}
          {message.data?.summary && !isUser && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Summary Stats */}
              <div className="bg-gray-700/50 rounded-lg p-3">
                <h4 className="text-xs font-semibold text-gray-400 mb-2">SUMMARY</h4>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Total Events:</span>
                    <span className="font-mono text-blue-300">{message.data.summary.total}</span>
                  </div>
                  {message.data.summary.topIPs && (
                    <div className="text-xs">
                      <span className="text-gray-400">Top IPs: </span>
                      <span className="text-orange-300">{message.data.summary.topIPs.join(', ')}</span>
                    </div>
                  )}
                  {message.data.summary.severity && (
                    <div className="flex space-x-2 text-xs">
                      <span className="text-red-400">High: {message.data.summary.severity.high}</span>
                      <span className="text-yellow-400">Med: {message.data.summary.severity.medium}</span>
                      <span className="text-green-400">Low: {message.data.summary.severity.low}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Query Info */}
              {message.data.query && (
                <div className="bg-gray-700/50 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-gray-400 mb-2">QUERY DETAILS</h4>
                  <div className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Confidence:</span>
                      <span className="text-green-300">{Math.round(message.data.query.confidence * 100)}%</span>
                    </div>
                    <div className="text-xs text-gray-400 font-mono bg-gray-800 p-2 rounded mt-2 truncate">
                      {message.data.query.kql}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Sample Data Table */}
          {message.data?.hits && message.data.hits.length > 0 && !isUser && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-gray-400 mb-2">SAMPLE RESULTS</h4>
              <div className="bg-gray-900 rounded border border-gray-600 overflow-hidden">
                <table className="w-full text-xs">
                  <thead className="bg-gray-800">
                    <tr>
                      <th className="text-left p-2 text-gray-400">Timestamp</th>
                      <th className="text-left p-2 text-gray-400">Source IP</th>
                      <th className="text-left p-2 text-gray-400">User</th>
                      <th className="text-left p-2 text-gray-400">Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {message.data.hits.slice(0, 3).map((hit: any, index: number) => (
                      <tr key={index} className="border-t border-gray-700 hover:bg-gray-800/50">
                        <td className="p-2 text-gray-300 font-mono">{new Date(hit.timestamp).toLocaleTimeString()}</td>
                        <td className="p-2 text-orange-300 font-mono">{hit.src_ip}</td>
                        <td className="p-2 text-blue-300">{hit.user}</td>
                        <td className="p-2">
                          <span className={`px-1 py-0.5 rounded text-xs ${
                            hit.result === 'failed' ? 'bg-red-900 text-red-300' : 'bg-green-900 text-green-300'
                          }`}>
                            {hit.result}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Standard Action Buttons */}
        {message.actions && message.actions.length > 0 && !isUser && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.actions.map((action) => (
              <button
                key={action.id}
                onClick={() => onActionClick(action.id)}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${getVariantStyles(action.variant)}`}
              >
                <action.icon className="w-3 h-3" />
                <span>{action.label}</span>
              </button>
            ))}
          </div>
        )}
        
        {/* 🚀 V2 ENHANCEMENT: Entity-based Smart Actions */}
        {message.entity_actions && message.entity_actions.length > 0 && !isUser && (
          <div className="mt-3 border-t border-gray-600 pt-3">
            <div className="text-xs font-medium text-gray-400 mb-2 flex items-center">
              <Zap className="w-3 h-3 mr-1" />
              Smart Actions
            </div>
            <div className="flex flex-wrap gap-2">
              {message.entity_actions.map((entityAction, index) => {
                const IconComponent = getEntityActionIcon(entityAction.icon);
                return (
                  <button
                    key={`entity-${index}`}
                    onClick={() => onActionClick(entityAction.action, entityAction.entities)}
                    className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors bg-indigo-600 hover:bg-indigo-700 text-white"
                    title={`${entityAction.label} (${entityAction.entities.length} entities)`}
                  >
                    <IconComponent className="w-3 h-3" />
                    <span>{entityAction.label}</span>
                    <span className="ml-1.5 px-1.5 py-0.5 text-xs bg-indigo-500 text-indigo-100 rounded-full">
                      {entityAction.entities.length}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
