/**
 * KARTAVYA SIEM - Entity Recognition Demo Component
 * Easy way to test and demonstrate all entity recognition features
 */

import React, { useState } from 'react';
import { 
  Play, Copy, Eye, Shield, AlertTriangle, Zap, 
  Globe, Hash, Mail, FileText, Target 
} from 'lucide-react';
import { advancedEntityRecognizer, AdvancedSecurityEntity } from '../../services/advancedEntityRecognition';
import AdvancedEntityDisplay from '../AdvancedEntityDisplay/AdvancedEntityDisplay';

interface DemoQuery {
  title: string;
  query: string;
  description: string;
  expectedEntities: string[];
  category: 'network' | 'malware' | 'vulnerability' | 'mixed';
}

const EntityRecognitionDemo: React.FC = () => {
  const [selectedEntity, setSelectedEntity] = useState<AdvancedSecurityEntity | null>(null);
  const [processingQuery, setProcessingQuery] = useState<string | null>(null);
  const [detectedEntities, setDetectedEntities] = useState<AdvancedSecurityEntity[]>([]);
  const [entityActions, setEntityActions] = useState<any[]>([]);

  const demoQueries: DemoQuery[] = [
    {
      title: "🚨 Advanced Threat Campaign",
      query: "Critical APT29 campaign detected: Credential stuffing from 54.159.34.148 targeting IoT device iot-efc70493 using MITRE technique T1190. AI model model-e8e7d12e compromised with training data poisoning. REvil group suspected.",
      description: "Sophisticated threat detection with APT groups, IoT devices, AI models, and advanced attack techniques",
      expectedEntities: ["Threat Actor", "IP Address", "IoT Device", "MITRE Technique", "AI Model", "Attack Technique"],
      category: "mixed"
    },
    {
      title: "🏭 IoT Security Incident",
      query: "HVAC device iot-efc70493 exhibiting CPU microcode changes and sensor spoofing. Possible REvil group lateral movement attempt via container escape.",
      description: "IoT-focused threat detection with unconventional IOCs and behavioral indicators",
      expectedEntities: ["IoT Device", "Unconventional IOC", "Threat Actor", "Attack Technique"],
      category: "network"
    },
    {
      title: "🤖 AI Security Attack",
      query: "User jennifer11 attempting model inversion on AI system model-e8e7d12e. Training data poisoning detected with membership inference attacks.",
      description: "AI/ML security with model identifiers and advanced AI attack techniques",
      expectedEntities: ["Username", "AI Model", "Attack Technique"],
      category: "mixed"
    },
    {
      title: "🌐 Network Infrastructure Attack", 
      query: "Malicious traffic from IP 185.220.101.42 using DNS tunneling to AWS cloud service. Container pod-abc123 compromised with blockchain address manipulation.",
      description: "Modern infrastructure attack with cloud services and containers",
      expectedEntities: ["IP Address", "Attack Technique", "Cloud Service", "Container ID", "Blockchain Address"],
      category: "network"
    },
    {
      title: "🎯 MITRE Kill Chain Analysis",
      query: "Multi-stage attack: T1190 initial access, T1566.001 spear phishing, T1059.001 PowerShell execution, and T1078.004 cloud account compromise by FIN7 group.",
      description: "Complex kill chain analysis with multiple MITRE techniques and threat actor attribution",
      expectedEntities: ["MITRE Technique", "Threat Actor", "Attack Technique"],
      category: "vulnerability"
    },
    {
      title: "🦠 Advanced Malware Campaign",
      query: "Agent.Win32 malware family deployed via Operation SteelCorgi campaign. TrojanDropper variant targeting certificate hash manipulation and registry key persistence.",
      description: "Sophisticated malware analysis with campaign attribution and persistence mechanisms",
      expectedEntities: ["Malware Family", "Campaign Name", "Certificate Hash", "Registry Key"],
      category: "malware"
    }
  ];

  const processQuery = async (query: string) => {
    setProcessingQuery(query);
    setDetectedEntities([]);
    setEntityActions([]);
    
    try {
      // Extract advanced entities using the built-in recognizer
      const entities = await advancedEntityRecognizer.extractAdvancedEntities(query);
      
      setDetectedEntities(entities);
      setEntityActions([]); // No actions without backend
      
      // Auto-select the first high-risk entity for demonstration
      const highRiskEntity = entities.find(e => (e.risk_score || 0) > 0.7) || entities[0];
      if (highRiskEntity) {
        setSelectedEntity(highRiskEntity);
      }
    } catch (error) {
      console.error('Error processing query:', error);
    } finally {
      setProcessingQuery(null);
    }
  };

  const getEntityIcon = (type: string) => {
    const iconMap: Record<string, React.ComponentType<any>> = {
      'ip_address': Globe,
      'domain': Globe, 
      'email': Mail,
      'hash': Hash,
      'cve': AlertTriangle,
      'mitre_technique': Target,
      'url': Globe,
      'process_name': FileText,
      'registry_key': FileText
    };
    return iconMap[type] || Eye;
  };

  const getCategoryColor = (category: string) => {
    const colorMap: Record<string, string> = {
      'network': 'bg-blue-600',
      'malware': 'bg-red-600', 
      'vulnerability': 'bg-orange-600',
      'mixed': 'bg-purple-600'
    };
    return colorMap[category] || 'bg-gray-600';
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            🚀 Entity Recognition Demo
          </h1>
          <p className="text-gray-400 text-lg">
            Test the advanced entity detection and threat intelligence features
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Demo Queries */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white mb-4">
              🧪 Test Queries
            </h2>
            
            {demoQueries.map((demo, index) => (
              <div key={index} className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={`px-2 py-1 text-xs font-medium text-white rounded ${getCategoryColor(demo.category)}`}>
                      {demo.category.toUpperCase()}
                    </div>
                    <h3 className="font-semibold text-white">{demo.title}</h3>
                  </div>
                </div>
                
                <p className="text-sm text-gray-400 mb-3">{demo.description}</p>
                
                <div className="bg-gray-900 rounded p-3 mb-3">
                  <div className="text-xs text-gray-500 mb-1">Query:</div>
                  <div className="text-sm text-gray-300 font-mono">{demo.query}</div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {demo.expectedEntities.map((entity, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-700 text-xs text-gray-300 rounded">
                        {entity}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => navigator.clipboard.writeText(demo.query)}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded flex items-center space-x-1"
                    >
                      <Copy className="w-3 h-3" />
                      <span>Copy</span>
                    </button>
                    <button
                      onClick={() => processQuery(demo.query)}
                      disabled={processingQuery === demo.query}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white text-xs rounded flex items-center space-x-1"
                    >
                      <Play className="w-3 h-3" />
                      <span>{processingQuery === demo.query ? 'Processing...' : 'Test'}</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Right Panel - Results */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-white mb-4">
              🎯 Detection Results
            </h2>
            
            {detectedEntities.length === 0 ? (
              <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
                <Zap className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-2">No entities detected yet</p>
                <p className="text-sm text-gray-500">Run a test query to see entity recognition in action</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-sm text-gray-400 mb-3">
                  Detected {detectedEntities.length} security entities:
                </div>
                
                {detectedEntities.map((entity, index) => {
                  const IconComponent = getEntityIcon(entity.type);
                  const reputation = entity.enrichment?.reputation || 'unknown';
                  const riskScore = entity.risk_score || 0;
                  const reputationColor = reputation === 'malicious' ? 'text-red-400' :
                                        reputation === 'suspicious' ? 'text-yellow-400' :
                                        reputation === 'clean' ? 'text-green-400' : 'text-gray-400';
                  
                  const riskColor = riskScore >= 0.8 ? 'text-red-400 bg-red-900/20' :
                                   riskScore >= 0.6 ? 'text-orange-400 bg-orange-900/20' :
                                   riskScore >= 0.4 ? 'text-yellow-400 bg-yellow-900/20' :
                                   'text-green-400 bg-green-900/20';
                  
                  return (
                    <div 
                      key={index}
                      onClick={() => setSelectedEntity(entity)}
                      className="bg-gray-800 rounded-lg border border-gray-700 p-4 cursor-pointer hover:border-blue-500 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <IconComponent className="w-5 h-5 text-blue-400" />
                          <div>
                            <div className="flex items-center space-x-2">
                              <div className="font-mono text-sm text-white">{entity.text}</div>
                              {riskScore > 0 && (
                                <span className={`px-2 py-1 rounded text-xs font-medium ${riskColor}`}>
                                  {(riskScore * 100).toFixed(0)}%
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-gray-400 uppercase">{entity.type.replace('_', ' ')}</div>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <div className={`text-xs font-medium uppercase ${reputationColor}`}>
                            {reputation}
                          </div>
                          <div className="text-xs text-gray-500">
                            {Math.round(entity.confidence * 100)}% confidence
                          </div>
                        </div>
                      </div>
                      
                      {/* 🚀 ADVANCED ENRICHMENT DISPLAY */}
                      {entity.enrichment && (
                        <div className="mt-3 flex items-center flex-wrap gap-3 text-xs text-gray-400">
                          {entity.enrichment.geo_location && (
                            <span className="flex items-center space-x-1">
                              <span>📍</span>
                              <span>{entity.enrichment.geo_location.country}</span>
                              {entity.enrichment.geo_location.city && <span>, {entity.enrichment.geo_location.city}</span>}
                            </span>
                          )}
                          {entity.enrichment.campaigns && entity.enrichment.campaigns.length > 0 && (
                            <span className="flex items-center space-x-1">
                              <span>🏴</span>
                              <span>{entity.enrichment.campaigns[0]}</span>
                            </span>
                          )}
                          {entity.enrichment.threat_actors && entity.enrichment.threat_actors.length > 0 && (
                            <span className="flex items-center space-x-1">
                              <span>🦹</span>
                              <span>{entity.enrichment.threat_actors[0]}</span>
                            </span>
                          )}
                          {entity.enrichment.risk_factors && (
                            <span className="flex items-center space-x-1">
                              <span>⚡</span>
                              <span>{entity.enrichment.risk_factors.length} risk factors</span>
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-blue-900/20 border border-blue-700/50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-300 mb-3">
            🎮 How to Use This Demo
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300">
            <div>
              <h4 className="font-medium text-white mb-2">1. Test Entity Detection</h4>
              <p>Click "Test" on any query to see automatic entity extraction and threat intelligence enrichment</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">2. Explore Entity Details</h4>
              <p>Click on any detected entity to see detailed threat intelligence information</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">3. Copy to Main Chat</h4>
              <p>Use "Copy" to paste queries into the main chat interface at /console</p>
            </div>
            <div>
              <h4 className="font-medium text-white mb-2">4. Create Custom Queries</h4>
              <p>Try your own queries with IPs, domains, hashes, CVEs, and MITRE techniques</p>
            </div>
          </div>
        </div>

        {/* Entity Detail Modal */}
        {/* 🚀 ADVANCED ENTITY DETAIL MODAL */}
        {selectedEntity && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="max-w-2xl w-full">
              <AdvancedEntityDisplay 
                entity={selectedEntity}
                onClose={() => setSelectedEntity(null)}
                onActionTaken={(action, entity) => {
                  console.log(`🚀 Advanced Action ${action} taken on`, entity);
                  alert(`🛡️ KARTAVYA SIEM: Executed '${action}' on ${entity.type}: ${entity.text}`);
                  // Don't close modal automatically to allow exploring multiple actions
                }}
              />
            </div>
          </div>
        )}
        
        {/* 🎯 SMART ACTIONS PANEL */}
        {entityActions.length > 0 && (
          <div className="mt-6 bg-gray-800 rounded-lg border border-gray-700 p-4">
            <h3 className="text-lg font-semibold text-white mb-3">
              🎯 Smart Security Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {entityActions.map((action, index) => {
                const riskColors = {
                  'critical': 'bg-red-600 hover:bg-red-700 text-white',
                  'high': 'bg-orange-600 hover:bg-orange-700 text-white',
                  'medium': 'bg-yellow-600 hover:bg-yellow-700 text-white',
                  'low': 'bg-green-600 hover:bg-green-700 text-white'
                };
                const buttonColor = riskColors[action.risk_level] || 'bg-gray-600 hover:bg-gray-700 text-white';
                
                return (
                  <button
                    key={index}
                    onClick={() => {
                      console.log(`🎯 Smart Action: ${action.action}`, action.entities);
                      alert(`🚀 KARTAVYA SIEM: ${action.label}\nAffecting ${action.entities.length} entities`);
                    }}
                    className={`px-4 py-3 rounded-lg transition-colors text-left ${buttonColor}`}
                  >
                    <div className="font-medium text-sm">{action.label}</div>
                    <div className="text-xs opacity-80 mt-1">{action.entities.length} entities affected</div>
                    <div className={`text-xs mt-1 px-2 py-1 rounded ${
                      action.risk_level === 'critical' ? 'bg-red-800' :
                      action.risk_level === 'high' ? 'bg-orange-800' :
                      action.risk_level === 'medium' ? 'bg-yellow-800' :
                      'bg-green-800'
                    }`}>
                      {action.risk_level.toUpperCase()} PRIORITY
                    </div>
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

export default EntityRecognitionDemo;
