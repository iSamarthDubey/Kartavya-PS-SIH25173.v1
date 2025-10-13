#!/usr/bin/env python3
"""
💬 Chat Conversation Memory System
==================================
Advanced conversation context and memory features for security investigations:
- Session-based conversation tracking
- Context-aware query processing
- Investigation timeline building
- Entity relationship mapping
- Adaptive query suggestions
- Multi-turn dialogue management
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp.security_entities import SecurityNLPRecognizer, SecurityEntity


class ConversationState(Enum):
    """States of a security investigation conversation"""
    INITIATED = "initiated"
    EXPLORING = "exploring"
    INVESTIGATING = "investigating"
    CORRELATING = "correlating"
    ANALYZING = "analyzing"
    CONCLUDING = "concluding"
    COMPLETED = "completed"


class QueryIntent(Enum):
    """Types of security query intents"""
    SEARCH = "search"
    INVESTIGATE = "investigate"
    CORRELATE = "correlate"
    ANALYZE = "analyze"
    HUNT = "hunt"
    MONITOR = "monitor"
    REPORT = "report"
    EXPLAIN = "explain"


@dataclass
class ConversationTurn:
    """A single turn in the conversation"""
    turn_id: str
    timestamp: datetime
    user_query: str
    intent: QueryIntent
    entities: List[SecurityEntity]
    context_used: List[str]
    response: str
    confidence: float
    execution_time_ms: float
    related_turns: List[str] = field(default_factory=list)


@dataclass 
class InvestigationContext:
    """Investigation context tracking"""
    primary_entities: Dict[str, Set[str]] = field(default_factory=dict)  # entity_type -> values
    timeline: List[Tuple[datetime, str]] = field(default_factory=list)
    relationships: Dict[str, Set[str]] = field(default_factory=dict)  # entity -> related entities
    hypotheses: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    mitre_techniques: Set[str] = field(default_factory=set)
    threat_actors: Set[str] = field(default_factory=set)
    affected_systems: Set[str] = field(default_factory=set)
    investigation_focus: Optional[str] = None


@dataclass
class ConversationSession:
    """Complete conversation session for security investigation"""
    session_id: str
    created_at: datetime
    last_active: datetime
    state: ConversationState
    turns: List[ConversationTurn]
    context: InvestigationContext
    user_id: str = "analyst"
    investigation_type: str = "general"
    priority: str = "medium"


class SecurityContextBuilder:
    """Builds and maintains security investigation context"""
    
    def __init__(self):
        self.nlp_recognizer = SecurityNLPRecognizer()
        
        # Context patterns for different investigation types
        self.investigation_patterns = {
            "malware_analysis": {
                "key_entities": ["malware_family", "file_hash", "ip_address", "domain"],
                "focus_questions": [
                    "What files were affected?",
                    "Which systems were compromised?",
                    "What network communications occurred?",
                    "Are there indicators of persistence?"
                ]
            },
            "incident_response": {
                "key_entities": ["threat_actor", "mitre_technique", "ip_address", "hostname"],
                "focus_questions": [
                    "What was the initial attack vector?",
                    "How did the attacker move laterally?",
                    "What data was accessed or exfiltrated?",
                    "What is the current threat status?"
                ]
            },
            "threat_hunting": {
                "key_entities": ["attack_pattern", "mitre_technique", "process_name", "file_path"],
                "focus_questions": [
                    "Are there similar patterns in other systems?",
                    "What behavioral indicators suggest compromise?",
                    "Which hunt hypotheses should we test?",
                    "What additional data sources should we query?"
                ]
            }
        }
    
    def analyze_query_context(self, query: str, session: ConversationSession) -> Dict[str, Any]:
        """Analyze query in the context of ongoing conversation"""
        analysis = self.nlp_recognizer.analyze_text(query)
        
        # Determine intent based on query patterns
        intent = self._classify_intent(query, analysis)
        
        # Identify context dependencies
        context_deps = self._identify_context_dependencies(query, session)
        
        # Generate contextual suggestions
        suggestions = self._generate_contextual_suggestions(session, analysis)
        
        return {
            "intent": intent,
            "analysis": analysis,
            "context_dependencies": context_deps,
            "suggestions": suggestions,
            "recommended_next_steps": self._recommend_next_steps(session, intent)
        }
    
    def _classify_intent(self, query: str, analysis: Dict[str, Any]) -> QueryIntent:
        """Classify the intent of a security query"""
        query_lower = query.lower()
        
        # Intent classification based on keywords and patterns
        if any(word in query_lower for word in ["search", "find", "show", "list"]):
            return QueryIntent.SEARCH
        elif any(word in query_lower for word in ["investigate", "analyze", "examine", "detail"]):
            return QueryIntent.INVESTIGATE
        elif any(word in query_lower for word in ["correlate", "relate", "connect", "link"]):
            return QueryIntent.CORRELATE
        elif any(word in query_lower for word in ["hunt", "hunting", "detect", "discover"]):
            return QueryIntent.HUNT
        elif any(word in query_lower for word in ["monitor", "watch", "track", "observe"]):
            return QueryIntent.MONITOR
        elif any(word in query_lower for word in ["report", "summary", "summarize"]):
            return QueryIntent.REPORT
        elif any(word in query_lower for word in ["explain", "why", "how", "what"]):
            return QueryIntent.EXPLAIN
        else:
            # Default based on entities found
            if analysis.get("threat_indicators", {}).get("severity_score", 0) > 50:
                return QueryIntent.INVESTIGATE
            else:
                return QueryIntent.SEARCH
    
    def _identify_context_dependencies(self, query: str, session: ConversationSession) -> List[str]:
        """Identify what context from previous turns is relevant"""
        dependencies = []
        
        # Check for pronouns and references
        pronouns = ["this", "that", "these", "those", "it", "them", "they"]
        if any(pronoun in query.lower() for pronoun in pronouns):
            dependencies.append("entity_reference")
        
        # Check for temporal references
        temporal = ["earlier", "before", "previous", "last", "recent"]
        if any(temp in query.lower() for temp in temporal):
            dependencies.append("temporal_reference")
        
        # Check for implicit entity continuation
        current_entities = self.nlp_recognizer.extract_entities(query)
        if len(current_entities) == 0 and len(session.turns) > 0:
            dependencies.append("implicit_entity_continuation")
        
        return dependencies
    
    def _generate_contextual_suggestions(self, session: ConversationSession, analysis: Dict[str, Any]) -> List[str]:
        """Generate contextual query suggestions based on conversation state"""
        suggestions = []
        
        # Base suggestions on conversation state
        if session.state == ConversationState.INITIATED:
            suggestions.extend([
                "Show me recent security alerts",
                "Hunt for suspicious PowerShell activity",
                "Investigate failed authentication attempts"
            ])
        
        elif session.state == ConversationState.EXPLORING:
            # Get primary entities from context
            primary_entities = session.context.primary_entities
            if "ip_address" in primary_entities:
                suggestions.append("Show all activities from these IP addresses")
            if "hostname" in primary_entities:
                suggestions.append("Analyze all events from these hosts")
            if "username" in primary_entities:
                suggestions.append("Investigate user behavior patterns")
        
        elif session.state == ConversationState.INVESTIGATING:
            suggestions.extend([
                "Correlate these events with network traffic",
                "Find lateral movement indicators",
                "Check for data exfiltration attempts",
                "Look for persistence mechanisms"
            ])
        
        elif session.state == ConversationState.CORRELATING:
            suggestions.extend([
                "Timeline these events chronologically",
                "Map attack techniques to MITRE framework",
                "Identify the attack chain progression",
                "Find similar patterns in historical data"
            ])
        
        # Add entity-specific suggestions
        entities = analysis.get("entities", [])
        for entity in entities:
            entity_type = entity.get("type")
            entity_value = entity.get("value")
            
            if entity_type == "threat_actor":
                suggestions.append(f"Show all activities attributed to {entity_value}")
            elif entity_type == "malware_family":
                suggestions.append(f"Hunt for {entity_value} variants and related IOCs")
            elif entity_type == "mitre_technique":
                suggestions.append(f"Find other instances of {entity_value} technique")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _recommend_next_steps(self, session: ConversationSession, intent: QueryIntent) -> List[str]:
        """Recommend next investigation steps"""
        recommendations = []
        
        # Base recommendations on intent and context
        if intent == QueryIntent.SEARCH and session.state == ConversationState.INITIATED:
            recommendations.extend([
                "Narrow down the time range for more specific results",
                "Add filters to focus on high-priority events",
                "Consider investigating specific entities found"
            ])
        
        elif intent == QueryIntent.INVESTIGATE:
            recommendations.extend([
                "Correlate findings with network traffic data",
                "Check for related events on other systems",
                "Review user activity patterns around this time"
            ])
        
        elif intent == QueryIntent.HUNT:
            recommendations.extend([
                "Expand hunt to include related indicators",
                "Check for similar patterns in other environments", 
                "Validate findings with additional data sources"
            ])
        
        # Add context-specific recommendations
        if session.context.mitre_techniques:
            recommendations.append("Map discovered techniques to attack progression")
        
        if session.context.threat_actors:
            recommendations.append("Research threat actor TTPs and recent campaigns")
        
        return recommendations[:3]


class ConversationMemoryManager:
    """Manages conversation sessions and memory"""
    
    def __init__(self, max_sessions: int = 100):
        self.sessions: Dict[str, ConversationSession] = {}
        self.max_sessions = max_sessions
        self.context_builder = SecurityContextBuilder()
        self._lock = threading.Lock()
    
    def create_session(self, user_id: str = "analyst", investigation_type: str = "general") -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        
        with self._lock:
            # Clean up old sessions if needed
            if len(self.sessions) >= self.max_sessions:
                self._cleanup_old_sessions()
            
            session = ConversationSession(
                session_id=session_id,
                created_at=datetime.now(),
                last_active=datetime.now(),
                state=ConversationState.INITIATED,
                turns=[],
                context=InvestigationContext(),
                user_id=user_id,
                investigation_type=investigation_type
            )
            
            self.sessions[session_id] = session
        
        return session_id
    
    def process_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """Process a query within a conversation session"""
        with self._lock:
            if session_id not in self.sessions:
                # Create new session if doesn't exist
                session_id = self.create_session()
            
            session = self.sessions[session_id]
            session.last_active = datetime.now()
            
            # Analyze query with context
            start_time = time.time()
            context_analysis = self.context_builder.analyze_query_context(query, session)
            processing_time = (time.time() - start_time) * 1000
            
            # Create conversation turn
            turn = ConversationTurn(
                turn_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                user_query=query,
                intent=context_analysis["intent"],
                entities=context_analysis["analysis"]["entities"],
                context_used=context_analysis["context_dependencies"],
                response=self._generate_response(context_analysis, session),
                confidence=0.85,  # Base confidence
                execution_time_ms=processing_time
            )
            
            # Update session context
            self._update_session_context(session, turn, context_analysis)
            
            # Add turn to session
            session.turns.append(turn)
            
            # Update conversation state
            session.state = self._determine_next_state(session, turn)
            
            return {
                "session_id": session_id,
                "turn_id": turn.turn_id,
                "response": turn.response,
                "intent": turn.intent.value,
                "suggestions": context_analysis["suggestions"],
                "next_steps": context_analysis["recommended_next_steps"],
                "context_summary": self._generate_context_summary(session),
                "conversation_state": session.state.value,
                "processing_time_ms": processing_time
            }
    
    def _generate_response(self, analysis: Dict[str, Any], session: ConversationSession) -> str:
        """Generate contextual response based on analysis"""
        intent = analysis["intent"]
        entities = analysis["analysis"]["entities"]
        
        # Base response on intent and context
        if intent == QueryIntent.SEARCH:
            if entities:
                entity_count = len(entities)
                entity_types = list(set(e["type"] for e in entities))
                return f"Found {entity_count} security entities in your query, including {', '.join(entity_types)}. Searching relevant security data..."
            else:
                return "Searching security data based on your criteria..."
        
        elif intent == QueryIntent.INVESTIGATE:
            primary_entities = [e for e in entities if e["confidence"] > 0.8]
            if primary_entities:
                entity_names = [e["value"] for e in primary_entities[:3]]
                return f"Investigating {', '.join(entity_names)}. Analyzing related security events and building investigation timeline..."
            else:
                return "Starting investigation based on your query. Gathering relevant security data..."
        
        elif intent == QueryIntent.HUNT:
            techniques = [e["value"] for e in entities if e["type"] == "mitre_technique"]
            if techniques:
                return f"Initiating threat hunt for {', '.join(techniques)}. Searching for behavioral indicators and related activity patterns..."
            else:
                return "Starting threat hunting based on your criteria. Looking for suspicious patterns and indicators..."
        
        elif intent == QueryIntent.CORRELATE:
            return "Correlating events and building relationships between security entities. Analyzing temporal patterns and connections..."
        
        elif intent == QueryIntent.ANALYZE:
            return "Performing deep analysis of security data. Examining patterns, anomalies, and potential threat indicators..."
        
        else:
            return f"Processing your {intent.value} request. Analyzing security data and preparing response..."
    
    def _update_session_context(self, session: ConversationSession, turn: ConversationTurn, analysis: Dict[str, Any]):
        """Update session context based on new turn"""
        # Add entities to primary context
        for entity in turn.entities:
            entity_type = entity["type"]
            entity_value = entity["value"]
            
            if entity_type not in session.context.primary_entities:
                session.context.primary_entities[entity_type] = set()
            session.context.primary_entities[entity_type].add(entity_value)
        
        # Track MITRE techniques
        mitre_entities = [e for e in turn.entities if e["type"] == "mitre_technique"]
        for entity in mitre_entities:
            session.context.mitre_techniques.add(entity["value"])
        
        # Track threat actors
        actor_entities = [e for e in turn.entities if e["type"] == "threat_actor"]
        for entity in actor_entities:
            session.context.threat_actors.add(entity["value"])
        
        # Track affected systems
        host_entities = [e for e in turn.entities if e["type"] in ["hostname", "ip_address"]]
        for entity in host_entities:
            session.context.affected_systems.add(entity["value"])
        
        # Add to timeline
        session.context.timeline.append((turn.timestamp, turn.user_query))
        
        # Update investigation focus based on intent
        if turn.intent in [QueryIntent.INVESTIGATE, QueryIntent.HUNT] and turn.entities:
            primary_entity = max(turn.entities, key=lambda x: x["confidence"])
            session.context.investigation_focus = f"{primary_entity['type']}: {primary_entity['value']}"
    
    def _determine_next_state(self, session: ConversationSession, turn: ConversationTurn) -> ConversationState:
        """Determine next conversation state based on current turn"""
        current_state = session.state
        intent = turn.intent
        
        # State transition logic
        if current_state == ConversationState.INITIATED:
            if intent in [QueryIntent.INVESTIGATE, QueryIntent.HUNT]:
                return ConversationState.INVESTIGATING
            else:
                return ConversationState.EXPLORING
        
        elif current_state == ConversationState.EXPLORING:
            if intent == QueryIntent.INVESTIGATE:
                return ConversationState.INVESTIGATING
            elif intent == QueryIntent.CORRELATE:
                return ConversationState.CORRELATING
            else:
                return ConversationState.EXPLORING
        
        elif current_state == ConversationState.INVESTIGATING:
            if intent == QueryIntent.CORRELATE:
                return ConversationState.CORRELATING
            elif intent == QueryIntent.ANALYZE:
                return ConversationState.ANALYZING
            else:
                return ConversationState.INVESTIGATING
        
        elif current_state == ConversationState.CORRELATING:
            if intent == QueryIntent.ANALYZE:
                return ConversationState.ANALYZING
            elif intent == QueryIntent.REPORT:
                return ConversationState.CONCLUDING
            else:
                return ConversationState.CORRELATING
        
        elif current_state == ConversationState.ANALYZING:
            if intent == QueryIntent.REPORT:
                return ConversationState.CONCLUDING
            else:
                return ConversationState.ANALYZING
        
        elif current_state == ConversationState.CONCLUDING:
            return ConversationState.COMPLETED
        
        return current_state
    
    def _generate_context_summary(self, session: ConversationSession) -> Dict[str, Any]:
        """Generate summary of current conversation context"""
        context = session.context
        
        return {
            "investigation_focus": context.investigation_focus,
            "total_entities": sum(len(entities) for entities in context.primary_entities.values()),
            "entity_types": list(context.primary_entities.keys()),
            "mitre_techniques_found": list(context.mitre_techniques),
            "threat_actors_identified": list(context.threat_actors),
            "systems_affected": list(context.affected_systems),
            "conversation_turns": len(session.turns),
            "investigation_duration": str(datetime.now() - session.created_at),
            "current_state": session.state.value
        }
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get complete session history"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        return {
            "session_info": {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_active": session.last_active.isoformat(),
                "state": session.state.value,
                "investigation_type": session.investigation_type,
                "user_id": session.user_id
            },
            "conversation_turns": [
                {
                    "turn_id": turn.turn_id,
                    "timestamp": turn.timestamp.isoformat(),
                    "query": turn.user_query,
                    "intent": turn.intent.value,
                    "response": turn.response,
                    "entities_found": len(turn.entities),
                    "confidence": turn.confidence,
                    "processing_time_ms": turn.execution_time_ms
                }
                for turn in session.turns
            ],
            "context_summary": self._generate_context_summary(session)
        }
    
    def _cleanup_old_sessions(self):
        """Remove old inactive sessions"""
        cutoff_time = datetime.now() - timedelta(hours=24)  # Remove sessions older than 24 hours
        
        to_remove = [
            session_id for session_id, session in self.sessions.items()
            if session.last_active < cutoff_time
        ]
        
        for session_id in to_remove:
            del self.sessions[session_id]


def test_conversation_memory():
    """Test the conversation memory system"""
    print("💬 CHAT CONVERSATION MEMORY SYSTEM")
    print("=" * 60)
    
    # Create memory manager
    memory_manager = ConversationMemoryManager()
    
    # Start a new conversation session
    session_id = memory_manager.create_session(user_id="test_analyst", investigation_type="incident_response")
    print(f"🆔 Created session: {session_id}")
    
    # Simulate conversation flow
    conversation_flow = [
        "Show me recent security alerts",
        "Investigate failed login attempts for user john.doe",
        "What IP addresses attempted these logins?",
        "Correlate these IPs with malware detections",
        "Hunt for lateral movement from these compromised systems",
        "Are there any APT29 indicators in this activity?",
        "Generate a summary of this investigation"
    ]
    
    print("\n📝 SIMULATING INVESTIGATION CONVERSATION")
    print("=" * 60)
    
    for i, query in enumerate(conversation_flow, 1):
        print(f"\n🔍 Turn {i}: {query}")
        print("-" * 40)
        
        result = memory_manager.process_query(session_id, query)
        
        print(f"🎯 Intent: {result['intent']}")
        print(f"💬 Response: {result['response']}")
        print(f"📊 State: {result['conversation_state']}")
        print(f"⏱️  Processing: {result['processing_time_ms']:.2f}ms")
        
        if result['suggestions']:
            print("💡 Suggestions:")
            for suggestion in result['suggestions'][:3]:
                print(f"   • {suggestion}")
        
        if result['next_steps']:
            print("📋 Next Steps:")
            for step in result['next_steps']:
                print(f"   • {step}")
        
        # Show context evolution
        context = result['context_summary']
        if context['total_entities'] > 0:
            print(f"🧠 Context: {context['total_entities']} entities, "
                  f"{len(context['entity_types'])} types")
    
    # Show complete session history
    print(f"\n📋 COMPLETE SESSION HISTORY")
    print("=" * 60)
    
    history = memory_manager.get_session_history(session_id)
    if history:
        session_info = history['session_info']
        print(f"Session ID: {session_info['session_id']}")
        print(f"Investigation Type: {session_info['investigation_type']}")
        print(f"Duration: {history['context_summary']['investigation_duration']}")
        print(f"Total Turns: {len(history['conversation_turns'])}")
        print(f"Final State: {session_info['state']}")
        
        print("\n🧠 Final Context Summary:")
        context = history['context_summary']
        print(f"• Investigation Focus: {context['investigation_focus'] or 'General exploration'}")
        print(f"• Total Entities: {context['total_entities']}")
        print(f"• Entity Types: {', '.join(context['entity_types'])}")
        if context['mitre_techniques_found']:
            print(f"• MITRE Techniques: {', '.join(context['mitre_techniques_found'])}")
        if context['threat_actors_identified']:
            print(f"• Threat Actors: {', '.join(context['threat_actors_identified'])}")
        if context['systems_affected']:
            print(f"• Systems Affected: {', '.join(list(context['systems_affected'])[:3])}")
    
    # Save session data
    session_data = {
        "test_run": {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "conversation_queries": conversation_flow
        },
        "session_history": history
    }
    
    with open("conversation_memory_test_results.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 Session data saved to: conversation_memory_test_results.json")
    print("🟢 Conversation memory system testing complete!")


if __name__ == "__main__":
    test_conversation_memory()
