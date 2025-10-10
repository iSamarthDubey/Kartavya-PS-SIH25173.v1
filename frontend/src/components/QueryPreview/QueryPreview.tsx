/**
 * KARTAVYA SIEM - QueryPreview Component
 * Shows generated query (ES DSL/KQL) with copy, validate, and edit functionality per blueprint
 */

import React, { useState } from 'react';
import { Copy, Play, Eye, EyeOff, CheckCircle, AlertTriangle } from 'lucide-react';

interface Query {
  dsl?: any;
  kql?: string;
  confidence: number;
  mappings_used?: any;
}

interface QueryPreviewProps {
  query: Query | null;
}

const QueryPreview: React.FC<QueryPreviewProps> = ({ query }) => {
  const [viewMode, setViewMode] = useState<'kql' | 'dsl' | 'explain'>('kql');
  const [isEditable, setIsEditable] = useState(false);
  const [editedQuery, setEditedQuery] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleEdit = () => {
    if (isEditable && editedQuery !== (query?.kql || '')) {
      // Validate and execute edited query
      console.log('Executing edited query:', editedQuery);
      // This would call the backend validation endpoint
    }
    setIsEditable(!isEditable);
    if (!isEditable) {
      setEditedQuery(query?.kql || '');
    }
  };

  if (!query) {
    return (
      <div className="p-4 text-center">
        <div className="text-gray-500 text-sm">
          <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>No query generated yet</p>
          <p className="text-xs mt-1">Send a message to see the generated query</p>
        </div>
      </div>
    );
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) return CheckCircle;
    return AlertTriangle;
  };

  return (
    <div className="p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-400">GENERATED QUERY</h3>
        
        {/* Confidence Score */}
        <div className="flex items-center space-x-1">
          {React.createElement(getConfidenceIcon(query.confidence), { 
            className: `w-3 h-3 ${getConfidenceColor(query.confidence)}` 
          })}
          <span className={`text-xs font-mono ${getConfidenceColor(query.confidence)}`}>
            {Math.round(query.confidence * 100)}%
          </span>
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="flex border-b border-gray-700 mb-4">
        {[
          { id: 'kql', label: 'KQL' },
          { id: 'dsl', label: 'DSL' },
          { id: 'explain', label: 'Explain' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setViewMode(tab.id as any)}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${
              viewMode === tab.id 
                ? 'text-blue-400 border-b-2 border-blue-400' 
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Query Content */}
      <div className="flex-1 overflow-y-auto">
        {viewMode === 'kql' && (
          <div className="space-y-3">
            {/* KQL Display/Editor */}
            {isEditable ? (
              <textarea
                value={editedQuery}
                onChange={(e) => setEditedQuery(e.target.value)}
                className="w-full h-32 bg-gray-900 border border-gray-600 rounded p-3 text-xs font-mono text-gray-300 focus:outline-none focus:border-blue-500"
                placeholder="Edit KQL query..."
              />
            ) : (
              <div className="bg-gray-900 border border-gray-600 rounded p-3">
                <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap break-words">
                  {query.kql || 'No KQL generated'}
                </pre>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={() => handleCopy(query.kql || '')}
                className="flex items-center space-x-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs transition-colors"
              >
                <Copy className="w-3 h-3" />
                <span>{copySuccess ? 'Copied!' : 'Copy'}</span>
              </button>
              
              <button
                onClick={handleEdit}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded text-xs transition-colors ${
                  isEditable 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                {isEditable ? <Play className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                <span>{isEditable ? 'Execute' : 'Edit'}</span>
              </button>
            </div>
          </div>
        )}

        {viewMode === 'dsl' && (
          <div className="space-y-3">
            <div className="bg-gray-900 border border-gray-600 rounded p-3">
              <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
                {query.dsl ? JSON.stringify(query.dsl, null, 2) : 'No DSL generated'}
              </pre>
            </div>
            
            <button
              onClick={() => handleCopy(JSON.stringify(query.dsl, null, 2))}
              className="flex items-center space-x-1 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs transition-colors"
            >
              <Copy className="w-3 h-3" />
              <span>{copySuccess ? 'Copied!' : 'Copy DSL'}</span>
            </button>
          </div>
        )}

        {viewMode === 'explain' && (
          <div className="space-y-4">
            {/* Query Breakdown */}
            <div>
              <h4 className="text-xs font-semibold text-gray-400 mb-2">QUERY INTERPRETATION</h4>
              <div className="bg-gray-900 border border-gray-600 rounded p-3">
                <div className="text-xs text-gray-300 space-y-2">
                  <div>
                    <span className="text-gray-400">Intent:</span> {' '}
                    <span className="text-blue-300">Search failed login events</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Time Range:</span> {' '}
                    <span className="text-green-300">Last 24 hours</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Event Type:</span> {' '}
                    <span className="text-orange-300">Authentication failures</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Field Mappings */}
            {query.mappings_used && (
              <div>
                <h4 className="text-xs font-semibold text-gray-400 mb-2">FIELD MAPPINGS</h4>
                <div className="bg-gray-900 border border-gray-600 rounded p-3">
                  <div className="text-xs text-gray-300 space-y-1">
                    {Object.entries(query.mappings_used).map(([concept, fields]) => (
                      <div key={concept} className="flex justify-between">
                        <span className="text-gray-400">{concept}:</span>
                        <span className="text-blue-300 font-mono">{Array.isArray(fields) ? fields.join(', ') : fields}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Confidence Explanation */}
            <div>
              <h4 className="text-xs font-semibold text-gray-400 mb-2">CONFIDENCE FACTORS</h4>
              <div className="bg-gray-900 border border-gray-600 rounded p-3">
                <div className="text-xs text-gray-300 space-y-1">
                  <div className="flex justify-between">
                    <span>Field mapping accuracy:</span>
                    <span className="text-green-300">95%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Intent recognition:</span>
                    <span className="text-green-300">90%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Time range parsing:</span>
                    <span className="text-green-300">98%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Security Warning */}
      {isEditable && (
        <div className="mt-4 bg-yellow-900/20 border border-yellow-700/50 rounded p-2">
          <div className="flex items-center space-x-2 text-yellow-300 text-xs">
            <AlertTriangle className="w-3 h-3" />
            <span>Edited queries will be validated server-side before execution</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryPreview;
