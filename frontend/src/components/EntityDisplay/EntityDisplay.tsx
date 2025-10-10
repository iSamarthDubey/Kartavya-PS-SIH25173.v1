/**
 * KARTAVYA SIEM - Enriched Entity Display Component
 * Shows threat intelligence and contextual information for detected entities
 */

import React, { useState } from 'react';
import { 
  Shield, AlertTriangle, Globe, Clock, Eye, ExternalLink,
  MapPin, Server, Database, Zap, TrendingUp, X 
} from 'lucide-react';
import { AdvancedSecurityEntity, AdvancedEntityType } from '../../services/advancedEntityRecognition';

interface EntityDisplayProps {
  entity: AdvancedSecurityEntity;
  onClose?: () => void;
  onActionTaken?: (action: string, entity: AdvancedSecurityEntity) => void;
}

const EntityDisplay: React.FC<EntityDisplayProps> = ({ entity, onClose, onActionTaken }) => {
  const [showFullDetails, setShowFullDetails] = useState(false);
  
  const enrichment = entity.enrichment;
  const reputation = enrichment?.reputation || 'unknown';
  const confidence = entity.confidence || 0;
  
  const getReputationColor = (rep: string) => {
    switch (rep) {
      case 'malicious': return 'text-red-400 bg-red-900/20 border-red-700';
      case 'suspicious': return 'text-yellow-400 bg-yellow-900/20 border-yellow-700';
      case 'clean': return 'text-green-400 bg-green-900/20 border-green-700';
      default: return 'text-gray-400 bg-gray-900/20 border-gray-700';
    }
  };

  const getReputationIcon = (rep: string) => {
    switch (rep) {
      case 'malicious': return <AlertTriangle className="w-4 h-4" />;
      case 'suspicious': return <Shield className="w-4 h-4" />;  
      case 'clean': return <Shield className="w-4 h-4" />;
      default: return <Eye className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 max-w-md">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`p-1 rounded border ${getReputationColor(reputation)}`}>
            {getReputationIcon(reputation)}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">{entity.text}</h3>
            <p className="text-xs text-gray-400 uppercase">{entity.type.replace('_', ' ')}</p>
            {entity.risk_score && (
              <div className="flex items-center space-x-1 mt-1">
                <span className="text-xs text-gray-500">Risk:</span>
                <span className={`text-xs px-1 rounded ${
                  entity.risk_score >= 0.8 ? 'bg-red-900/30 text-red-300' :
                  entity.risk_score >= 0.6 ? 'bg-orange-900/30 text-orange-300' :
                  entity.risk_score >= 0.4 ? 'bg-yellow-900/30 text-yellow-300' :
                  'bg-green-900/30 text-green-300'
                }`}>
                  {(entity.risk_score * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-gray-400 hover:text-gray-300">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Threat Intelligence Summary */}
      {enrichment && (
        <div className="space-y-3">
          {/* Reputation & Confidence */}
          <div className="grid grid-cols-2 gap-3">
            <div className={`p-2 rounded border text-center ${getReputationColor(reputation)}`}>
              <div className="text-xs font-medium uppercase">Reputation</div>
              <div className="text-sm font-bold mt-1">{reputation}</div>
            </div>
            <div className="p-2 rounded border border-gray-600 text-center">
              <div className="text-xs font-medium text-gray-400 uppercase">Confidence</div>
              <div className="text-sm font-bold text-white mt-1">{Math.round(confidence * 100)}%</div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            {enrichment.geo_location && (
              <div className="flex items-center space-x-1 text-gray-300">
                <MapPin className="w-3 h-3" />
                <span>{enrichment.geo_location.country}</span>
                {enrichment.geo_location.city && (
                  <span className="text-gray-400">, {enrichment.geo_location.city}</span>
                )}
              </div>
            )}
            {enrichment.risk_factors && (
              <div className="flex items-center space-x-1 text-gray-300">
                <Database className="w-3 h-3" />
                <span>{enrichment.risk_factors.length} risk factors</span>
              </div>
            )}
            {enrichment.first_seen && (
              <div className="flex items-center space-x-1 text-gray-300">
                <Clock className="w-3 h-3" />
                <span>First seen {new Date(enrichment.first_seen).toLocaleDateString()}</span>
              </div>
            )}
            {enrichment.campaigns && enrichment.campaigns.length > 0 && (
              <div className="flex items-center space-x-1 text-orange-300">
                <Zap className="w-3 h-3" />
                <span>{enrichment.campaigns[0]}</span>
              </div>
            )}
          </div>

          {/* Risk Factors */}
          {enrichment.risk_factors && enrichment.risk_factors.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-400 mb-1">RISK FACTORS</div>
              <div className="flex flex-wrap gap-1">
                {enrichment.risk_factors.map((factor, index) => (
                  <span key={index} className="px-2 py-1 bg-orange-900/30 text-orange-300 text-xs rounded">
                    {factor}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Campaigns */}
          {enrichment.campaigns && enrichment.campaigns.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-400 mb-1">CAMPAIGNS</div>
              <div className="flex flex-wrap gap-1">
                {enrichment.campaigns.map((campaign, index) => (
                  <span key={index} className="px-2 py-1 bg-red-900/30 text-red-300 text-xs rounded">
                    {campaign}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Malware Families */}
          {enrichment.malware_families && enrichment.malware_families.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-400 mb-1">MALWARE FAMILIES</div>
              <div className="flex flex-wrap gap-1">
                {enrichment.malware_families.map((family, index) => (
                  <span key={index} className="px-2 py-1 bg-red-900/30 text-red-300 text-xs rounded">
                    {family}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Threat Actors */}
          {enrichment.threat_actors && enrichment.threat_actors.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-400 mb-1">THREAT ACTORS</div>
              <div className="flex flex-wrap gap-1">
                {enrichment.threat_actors.map((actor, index) => (
                  <span key={index} className="px-2 py-1 bg-purple-900/30 text-purple-300 text-xs rounded">
                    {actor}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="flex space-x-2 pt-2 border-t border-gray-700">
            <button 
              onClick={() => onActionTaken?.('investigate', entity)}
              className="flex-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors"
            >
              <Eye className="w-3 h-3 inline mr-1" />
              Investigate
            </button>
            <button 
              onClick={() => onActionTaken?.('block', entity)}
              className={`flex-1 px-3 py-1.5 text-xs font-medium rounded transition-colors ${
                reputation === 'malicious' 
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-gray-600 hover:bg-gray-700 text-gray-300'
              }`}
            >
              <Shield className="w-3 h-3 inline mr-1" />
              {reputation === 'malicious' ? 'Block' : 'Monitor'}
            </button>
          </div>

          {/* Detailed View Toggle */}
          <button 
            onClick={() => setShowFullDetails(!showFullDetails)}
            className="w-full text-xs text-blue-400 hover:text-blue-300 transition-colors"
          >
            {showFullDetails ? 'Hide Details' : 'Show Full Details'}
          </button>

          {/* Full Details */}
          {showFullDetails && (
            <div className="mt-3 p-3 bg-gray-900/50 rounded border border-gray-600 text-xs space-y-2">
              <div>
                <span className="text-gray-400">Sources: </span>
                <span className="text-gray-300">{threatIntel.sources.join(', ')}</span>
              </div>
              
              {threatIntel.campaigns && threatIntel.campaigns.length > 0 && (
                <div>
                  <span className="text-gray-400">Campaigns: </span>
                  <span className="text-gray-300">{threatIntel.campaigns.join(', ')}</span>
                </div>
              )}
              
              <div>
                <span className="text-gray-400">Analysis: </span>
                <span className="text-gray-300">{threatIntel.details.additional_info?.recommendation || 'No additional recommendations'}</span>
              </div>

              {/* Entity-specific details */}
              {entity.type === 'ip_address' && threatIntel.details.additional_info && (
                <div className="space-y-1">
                  <div><span className="text-gray-400">Attack Attempts: </span><span className="text-gray-300">{threatIntel.details.additional_info.attack_attempts || 0}</span></div>
                  <div><span className="text-gray-400">Protocols: </span><span className="text-gray-300">{threatIntel.details.additional_info.protocols_used?.join(', ') || 'Unknown'}</span></div>
                </div>
              )}

              {entity.type === 'domain' && threatIntel.details.additional_info && (
                <div className="space-y-1">
                  <div><span className="text-gray-400">Domain Age: </span><span className="text-gray-300">{Math.round(threatIntel.details.additional_info.domain_age_days / 365)} years</span></div>
                  <div><span className="text-gray-400">SSL: </span><span className="text-gray-300">{threatIntel.details.additional_info.ssl_certificate || 'Unknown'}</span></div>
                </div>
              )}

              {entity.type === 'hash' && threatIntel.details.additional_info && (
                <div className="space-y-1">
                  <div><span className="text-gray-400">Packed: </span><span className="text-gray-300">{threatIntel.details.additional_info.packer_detected ? 'Yes' : 'No'}</span></div>
                  <div><span className="text-gray-400">Anti-VM: </span><span className="text-gray-300">{threatIntel.details.additional_info.anti_vm ? 'Yes' : 'No'}</span></div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Basic Entity Info (if no threat intel) */}
      {!threatIntel && (
        <div className="space-y-2">
          <div className="text-xs text-gray-400">
            Confidence: {Math.round(entity.confidence * 100)}%
          </div>
          <div className="flex space-x-2">
            <button 
              onClick={() => onActionTaken?.('lookup', entity)}
              className="flex-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded"
            >
              <ExternalLink className="w-3 h-3 inline mr-1" />
              Lookup
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EntityDisplay;
