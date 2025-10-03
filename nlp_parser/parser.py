"""
Enhanced Natural Language Parser for SIEM queries.
Extracts intents and entities from user queries using ML and NLP.
"""

import re
import spacy
import joblib
import dateparser
from typing import Dict, List, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np
import logging

logger = logging.getLogger(__name__)


class NLPParser:
    """Enhanced natural language parser for security queries with ML capabilities."""
    
    def __init__(self, use_ml=True):
        """Initialize the enhanced NLP parser."""
        self.use_ml = use_ml
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Using basic parsing.")
            self.nlp = None
        
        # Initialize ML components
        self.intent_classifier = None
        self.is_trained = False
        
        if self.use_ml:
            self._initialize_ml_components()
        
        # Load patterns for fallback
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
    
    def _initialize_ml_components(self):
        """Initialize machine learning components."""
        try:
            # Create ML pipeline for intent classification
            self.intent_classifier = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
                ('classifier', LogisticRegression(random_state=42))
            ])
            
            # Train with sample data if no model exists
            self._train_default_model()
            
        except ImportError:
            logger.warning("ML libraries not available. Using pattern-based parsing.")
            self.use_ml = False
    
    def _train_default_model(self):
        """Train the model with default security-focused training data."""
        training_data = [
            # Search and retrieval queries
            ("show me all failed login attempts", "search_logs"),
            ("find authentication errors", "search_logs"),
            ("get security events from last hour", "search_logs"),
            ("display firewall blocks", "search_logs"),
            ("search for malware detection", "search_logs"),
            
            # Counting and statistics
            ("how many failed logins today", "count_events"),
            ("count suspicious activities", "count_events"),
            ("number of blocked connections", "count_events"),
            
            # Threat analysis
            ("analyze this security incident", "analyze_threat"),
            ("investigate suspicious behavior", "analyze_threat"),
            ("threat assessment for this IP", "analyze_threat"),
            
            # Statistics and summaries
            ("show security overview", "get_stats"),
            ("generate security summary", "get_stats"),
            ("dashboard statistics", "get_stats"),
            
            # Alerts and notifications
            ("show me critical alerts", "alert_info"),
            ("high priority notifications", "alert_info"),
            ("security warnings", "alert_info")
        ]
        
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        try:
            self.intent_classifier.fit(texts, labels)
            self.is_trained = True
            logger.info("ML model trained successfully with default data")
        except Exception as e:
            logger.error(f"Failed to train ML model: {e}")
            self.use_ml = False
    
    def train_with_data(self, training_examples: List[Tuple[str, str]]):
        """Train the model with custom training data."""
        if not self.use_ml or not self.intent_classifier:
            return False
        
        texts = [item[0] for item in training_examples]
        labels = [item[1] for item in training_examples]
        
        try:
            self.intent_classifier.fit(texts, labels)
            self.is_trained = True
            logger.info(f"Model retrained with {len(training_examples)} examples")
            return True
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            return False
    
    def save_model(self, filepath: str):
        """Save the trained model to disk."""
        if self.intent_classifier and self.is_trained:
            try:
                joblib.dump(self.intent_classifier, filepath)
                logger.info(f"Model saved to {filepath}")
                return True
            except Exception as e:
                logger.error(f"Failed to save model: {e}")
                return False
        return False
    
    def load_model(self, filepath: str):
        """Load a trained model from disk."""
        try:
            self.intent_classifier = joblib.load(filepath)
            self.is_trained = True
            self.use_ml = True
            logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
        """Load intent detection patterns."""
        return {
            'search_logs': [
                r'show.*logs?',
                r'find.*events?',
                r'search.*for',
                r'get.*logs?',
                r'display.*events?'
            ],
            'count_events': [
                r'how many.*',
                r'count.*',
                r'number of.*'
            ],
            'analyze_threat': [
                r'analyze.*threat',
                r'threat.*analysis',
                r'security.*analysis',
                r'investigate.*'
            ],
            'get_stats': [
                r'statistics.*',
                r'stats.*',
                r'summary.*',
                r'overview.*'
            ],
            'alert_info': [
                r'alert.*',
                r'alerts?.*',
                r'warning.*',
                r'notification.*'
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load entity extraction patterns."""
        return {
            'ip_address': [r'\b(?:\d{1,3}\.){3}\d{1,3}\b'],
            'domain': [r'\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\b'],
            'email': [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            'time_range': [
                r'last\s+\d+\s+(?:minute|hour|day|week|month)s?',
                r'past\s+\d+\s+(?:minute|hour|day|week|month)s?',
                r'today|yesterday|last\s+week|last\s+month'
            ],
            'severity': [r'\b(?:low|medium|high|critical)\b'],
            'user': [r'user\s+([a-zA-Z0-9_.-]+)', r'username\s+([a-zA-Z0-9_.-]+)'],
            'port': [r'port\s+(\d+)', r':(\d+)\b'],
            'process': [r'process\s+([a-zA-Z0-9_.-]+)', r'executable\s+([a-zA-Z0-9_.-]+)']
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse a natural language query using enhanced ML capabilities."""
        query_clean = query.lower().strip()
        
        # Extract intent using ML or fallback to patterns
        intent_result = self._extract_intent_ml(query_clean) if self.use_ml else self._extract_intent_pattern(query_clean)
        
        result = {
            'original_query': query,
            'intent': intent_result['intent'],
            'confidence': intent_result.get('confidence', 0.0),
            'entities': self._extract_entities_enhanced(query_clean),
            'temporal': self._extract_temporal_enhanced(query_clean),
            'filters': self._extract_filters(query_clean),
            'parser_type': 'ml' if self.use_ml and self.is_trained else 'pattern'
        }
        
        return result
    
    def _extract_intent_ml(self, query: str) -> Dict[str, Any]:
        """Extract intent using ML classifier."""
        if not self.is_trained or not self.intent_classifier:
            return self._extract_intent_pattern(query)
        
        try:
            # Get prediction and confidence
            prediction = self.intent_classifier.predict([query])[0]
            probabilities = self.intent_classifier.predict_proba([query])[0]
            confidence = max(probabilities)
            
            return {
                'intent': prediction,
                'confidence': confidence,
                'all_probabilities': dict(zip(self.intent_classifier.classes_, probabilities))
            }
        except Exception as e:
            logger.error(f"ML intent extraction failed: {e}")
            return self._extract_intent_pattern(query)
    
    def _extract_intent_pattern(self, query: str) -> Dict[str, Any]:
        """Extract intent using pattern matching (fallback method)."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return {'intent': intent, 'confidence': 0.8}
        
        return {'intent': 'search_logs', 'confidence': 0.5}  # Default
    
    def _extract_entities_enhanced(self, query: str) -> Dict[str, List[str]]:
        """Enhanced entity extraction using spaCy and custom patterns."""
        entities = {}
        
        # Use spaCy for advanced entity recognition
        if self.nlp:
            doc = self.nlp(query)
            for ent in doc.ents:
                entity_type = self._map_spacy_entity(ent.label_)
                if entity_type:
                    if entity_type not in entities:
                        entities[entity_type] = []
                    entities[entity_type].append(ent.text)
        
        # Enhanced pattern-based extraction
        enhanced_patterns = {
            'ip_address': [r'\b(?:\d{1,3}\.){3}\d{1,3}\b'],
            'domain': [r'\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\b'],
            'email': [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            'port': [r'port\s+(\d+)', r':(\d+)\b'],
            'severity': [r'\b(?:low|medium|high|critical|severe)\b'],
            'user': [r'user\s+([a-zA-Z0-9_.-]+)', r'username\s+([a-zA-Z0-9_.-]+)'],
            'host': [r'host\s+([a-zA-Z0-9_.-]+)', r'hostname\s+([a-zA-Z0-9_.-]+)'],
            'status_code': [r'\b(?:200|201|400|401|403|404|500|502|503)\b'],
            'protocol': [r'\b(?:http|https|tcp|udp|icmp|ftp|ssh|dns)\b'],
            'file_path': [r'[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*', r'/(?:[^/\0]+/)*[^/\0]*'],
            'hash': [r'\b[a-fA-F0-9]{32}\b', r'\b[a-fA-F0-9]{40}\b', r'\b[a-fA-F0-9]{64}\b']
        }
        
        for entity_type, patterns in enhanced_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, query, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                if entity_type not in entities:
                    entities[entity_type] = []
                entities[entity_type].extend(list(set(matches)))
        
        return entities
    
    def _map_spacy_entity(self, spacy_label: str) -> Optional[str]:
        """Map spaCy entity labels to our custom entity types."""
        mapping = {
            'PERSON': 'user',
            'ORG': 'organization',
            'GPE': 'location',
            'TIME': 'time',
            'DATE': 'date',
            'MONEY': 'amount',
            'CARDINAL': 'number'
        }
        return mapping.get(spacy_label)
    
    def _extract_temporal_enhanced(self, query: str) -> Optional[Dict[str, Any]]:
        """Enhanced temporal extraction using dateparser."""
        # First try advanced dateparser
        temporal_phrases = [
            'last hour', 'past hour', 'yesterday', 'today', 'last week',
            'past week', 'last month', 'past month', 'last year',
            'since yesterday', 'since last week', 'in the last 24 hours',
            'over the past 2 hours', 'during the weekend', 'this morning',
            'this afternoon', 'this evening', 'between 9 AM and 5 PM'
        ]
        
        for phrase in temporal_phrases:
            if phrase.lower() in query:
                try:
                    parsed_time = dateparser.parse(phrase)
                    if parsed_time:
                        return {
                            'type': 'parsed',
                            'phrase': phrase,
                            'parsed_datetime': parsed_time.isoformat(),
                            'relative_time': phrase
                        }
                except:
                    pass
        
        # Fallback to pattern matching
        temporal_patterns = [
            (r'last (\d+) (minute|hour|day|week|month)s?', 'relative'),
            (r'past (\d+) (minute|hour|day|week|month)s?', 'relative'),
            (r'(today|yesterday|last week|last month)', 'keyword'),
            (r'since (\d{4}-\d{2}-\d{2})', 'absolute'),
            (r'between (\d{4}-\d{2}-\d{2}) and (\d{4}-\d{2}-\d{2})', 'range'),
            (r'(\d+) (minutes?|hours?|days?) ago', 'relative_ago')
        ]
        
        for pattern, time_type in temporal_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return {
                    'type': time_type,
                    'value': match.group(0),
                    'groups': match.groups()
                }
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent detection patterns for fallback."""
        return {
            'search_logs': [
                r'show.*logs?',
                r'find.*events?',
                r'search.*for',
                r'get.*logs?',
                r'display.*events?'
            ],
            'count_events': [
                r'how many.*',
                r'count.*',
                r'number of.*'
            ],
            'analyze_threat': [
                r'analyze.*threat',
                r'threat.*analysis',
                r'security.*analysis',
                r'investigate.*'
            ],
            'get_stats': [
                r'statistics.*',
                r'stats.*',
                r'summary.*',
                r'overview.*'
            ],
            'alert_info': [
                r'alert.*',
                r'alerts?.*',
                r'warning.*',
                r'notification.*'
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load entity extraction patterns for fallback."""
        return {
            'ip_address': [r'\b(?:\d{1,3}\.){3}\d{1,3}\b'],
            'domain': [r'\b[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\b'],
            'email': [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            'time_range': [
                r'last\s+\d+\s+(?:minute|hour|day|week|month)s?',
                r'past\s+\d+\s+(?:minute|hour|day|week|month)s?',
                r'today|yesterday|last\s+week|last\s+month'
            ],
            'severity': [r'\b(?:low|medium|high|critical)\b'],
            'user': [r'user\s+([a-zA-Z0-9_.-]+)', r'username\s+([a-zA-Z0-9_.-]+)'],
            'port': [r'port\s+(\d+)', r':(\d+)\b'],
            'process': [r'process\s+([a-zA-Z0-9_.-]+)', r'executable\s+([a-zA-Z0-9_.-]+)']
        }
        """Extract filter conditions from the query."""
        filters = {}
        
        # Extract common filter patterns
        filter_patterns = {
            'source_ip': r'(?:source|src|from) ip (?:is |equals? )?([0-9.]+)',
            'dest_ip': r'(?:destination|dest|to) ip (?:is |equals? )?([0-9.]+)',
            'port': r'port (?:is |equals? )?(\d+)',
            'protocol': r'protocol (?:is |equals? )?(tcp|udp|icmp|http|https)',
            'status_code': r'status (?:code )?(?:is |equals? )?(\d{3})',
            'user': r'user (?:is |equals? )?([a-zA-Z0-9_.-]+)',
            'host': r'host (?:is |equals? )?([a-zA-Z0-9_.-]+)'
        }
        
        for filter_name, pattern in filter_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                filters[filter_name] = match.group(1)
        
        return filters
    
    def generate_query_suggestions(self, partial_query: str) -> List[str]:
        """Generate query suggestions based on partial input."""
        suggestions = [
            "Show me failed login attempts from the last hour",
            "Find all alerts with high severity",
            "Count events from IP address 192.168.1.100",
            "Search for malware detection events today",
            "Show network traffic to suspicious domains",
            "Find user authentication failures",
            "Display top attacked ports",
            "Analyze threats from external sources"
        ]
        
        # Filter suggestions based on partial query
        if partial_query:
            partial_lower = partial_query.lower()
            filtered = [s for s in suggestions if partial_lower in s.lower()]
            return filtered[:5]
        
    def generate_query_suggestions(self, partial_query: str = "") -> List[str]:
        """Generate intelligent query suggestions based on ML understanding."""
        base_suggestions = [
            "Show me failed SSH login attempts from external IPs in the last 6 hours",
            "Count 404 errors on web servers since yesterday",
            "Find malware detection events with high severity",
            "Display user admin activities on weekends",
            "Search for DNS queries to suspicious domains containing 'malware'",
            "Show me authentication failures from IP 192.168.1.100",
            "Find all critical alerts from the past 24 hours",
            "Count successful logins by user john.doe",
            "Analyze network traffic anomalies today",
            "Search for file access violations on sensitive directories"
        ]
        
        if not partial_query:
            return base_suggestions[:5]
        
        # Use ML to find semantically similar suggestions
        if self.use_ml and self.is_trained:
            try:
                # Get intent for partial query
                intent_result = self._extract_intent_ml(partial_query.lower())
                current_intent = intent_result['intent']
                
                # Filter suggestions by intent similarity
                filtered_suggestions = []
                for suggestion in base_suggestions:
                    suggestion_intent = self._extract_intent_ml(suggestion.lower())['intent']
                    if suggestion_intent == current_intent:
                        filtered_suggestions.append(suggestion)
                
                if filtered_suggestions:
                    return filtered_suggestions[:5]
            except:
                pass
        
        # Fallback to text matching
        partial_lower = partial_query.lower()
        filtered = [s for s in base_suggestions if any(word in s.lower() for word in partial_lower.split())]
        return filtered[:5] if filtered else base_suggestions[:5]
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about the parser's current state."""
        return {
            'ml_enabled': self.use_ml,
            'ml_trained': self.is_trained,
            'spacy_available': self.nlp is not None,
            'supported_intents': list(self.intent_patterns.keys()),
            'parser_version': 'enhanced_ml' if self.use_ml else 'basic_pattern'
        }