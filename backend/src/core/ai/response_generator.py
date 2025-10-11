"""
AI-Powered Response Generator
Uses Google Gemini AI for intelligent SIEM analysis and response generation
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import re

# Import Google AI library
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AnalysisContext:
    """Context for AI analysis"""
    query_intent: str
    entities: List[Dict[str, Any]]
    results_count: int
    time_range: Optional[str] = None
    severity_levels: Optional[List[str]] = None
    affected_systems: Optional[List[str]] = None
    user_context: Optional[Dict[str, Any]] = None


class ResponseGenerator:
    """AI-powered response generator for SIEM analysis"""
    
    def __init__(self):
        """Initialize the response generator"""
        self.gemini_model = None
        self.initialized = False
        self.fallback_templates = self._load_fallback_templates()
        self.analysis_prompts = self._load_analysis_prompts()
        
        # Initialize Gemini if available
        if GEMINI_AVAILABLE:
            self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Google Gemini AI"""
        try:
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.initialized = True
                logger.info("Gemini AI initialized successfully")
            else:
                logger.warning("Gemini API key not found, using fallback templates")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.initialized = False
    
    async def generate_summary(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str,
        context: Optional[AnalysisContext] = None
    ) -> str:
        """
        Generate an intelligent summary of SIEM query results
        
        Args:
            results: SIEM query results
            query: Original natural language query
            intent: Classified intent
            context: Additional analysis context
            
        Returns:
            AI-generated summary string
        """
        try:
            if not results:
                return self._generate_empty_results_response(query, intent)
            
            # Use Gemini AI if available and initialized
            if self.initialized and GEMINI_AVAILABLE:
                return await self._generate_ai_summary(results, query, intent, context)
            else:
                return self._generate_template_summary(results, query, intent, context)
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._generate_fallback_summary(results, query, intent)
    
    async def generate_recommendations(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str,
        context: Optional[AnalysisContext] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable security recommendations
        
        Args:
            results: SIEM query results
            query: Original query
            intent: Query intent
            context: Analysis context
            
        Returns:
            List of recommendation dictionaries
        """
        try:
            if self.initialized and GEMINI_AVAILABLE:
                return await self._generate_ai_recommendations(results, query, intent, context)
            else:
                return self._generate_template_recommendations(results, query, intent, context)
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._generate_fallback_recommendations(intent)
    
    async def analyze_threat_patterns(
        self,
        results: List[Dict[str, Any]],
        context: Optional[AnalysisContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze threat patterns in the results
        
        Args:
            results: SIEM results to analyze
            context: Analysis context
            
        Returns:
            Threat pattern analysis
        """
        try:
            patterns = {
                "high_frequency_sources": self._identify_high_frequency_sources(results),
                "time_patterns": self._analyze_time_patterns(results),
                "severity_distribution": self._analyze_severity_distribution(results),
                "correlation_indicators": self._identify_correlation_indicators(results),
                "anomalies": self._detect_anomalies(results)
            }
            
            # Enhance with AI analysis if available
            if self.initialized and GEMINI_AVAILABLE and results:
                ai_insights = await self._get_ai_threat_insights(results, patterns)
                patterns["ai_insights"] = ai_insights
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing threat patterns: {e}")
            return {"error": str(e)}
    
    async def generate_follow_up_questions(
        self,
        query: str,
        results: List[Dict[str, Any]],
        intent: str
    ) -> List[str]:
        """
        Generate intelligent follow-up questions
        
        Args:
            query: Original query
            results: Query results
            intent: Query intent
            
        Returns:
            List of follow-up questions
        """
        try:
            if self.initialized and GEMINI_AVAILABLE:
                return await self._generate_ai_follow_ups(query, results, intent)
            else:
                return self._generate_template_follow_ups(query, results, intent)
                
        except Exception as e:
            logger.error(f"Error generating follow-ups: {e}")
            return self._get_default_follow_ups(intent)
    
    async def _generate_ai_summary(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str,
        context: Optional[AnalysisContext] = None
    ) -> str:
        """Generate AI-powered summary using Gemini"""
        
        # Prepare analysis data
        analysis_data = self._prepare_analysis_data(results, context)
        
        # Build prompt
        prompt = self._build_summary_prompt(query, intent, analysis_data, results[:5])  # Limit for token efficiency
        
        try:
            response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
            
            if response and response.text:
                # Clean and validate response
                summary = self._clean_ai_response(response.text)
                return summary
            else:
                logger.warning("Empty response from Gemini, using template fallback")
                return self._generate_template_summary(results, query, intent, context)
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._generate_template_summary(results, query, intent, context)
    
    async def _generate_ai_recommendations(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str,
        context: Optional[AnalysisContext] = None
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""
        
        analysis_data = self._prepare_analysis_data(results, context)
        prompt = self._build_recommendations_prompt(query, intent, analysis_data, results[:3])
        
        try:
            response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
            
            if response and response.text:
                recommendations = self._parse_ai_recommendations(response.text)
                return recommendations
            else:
                return self._generate_template_recommendations(results, query, intent, context)
                
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return self._generate_template_recommendations(results, query, intent, context)
    
    async def _get_ai_threat_insights(
        self,
        results: List[Dict[str, Any]],
        patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get AI insights on threat patterns"""
        
        prompt = f"""
        Analyze these cybersecurity patterns and provide expert insights:
        
        HIGH FREQUENCY SOURCES: {json.dumps(patterns.get('high_frequency_sources', {}), indent=2)}
        TIME PATTERNS: {json.dumps(patterns.get('time_patterns', {}), indent=2)}
        SEVERITY DISTRIBUTION: {json.dumps(patterns.get('severity_distribution', {}), indent=2)}
        
        SAMPLE EVENTS:
        {json.dumps(results[:3], indent=2)}
        
        Provide cybersecurity expert analysis in JSON format:
        {{
            "threat_assessment": "overall threat level and reasoning",
            "attack_indicators": ["list of potential attack indicators"],
            "recommended_actions": ["immediate actions to take"],
            "investigation_priorities": ["areas requiring further investigation"]
        }}
        """
        
        try:
            response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
            if response and response.text:
                # Try to parse JSON response
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return {"ai_insights": "Analysis unavailable"}
            
        except Exception as e:
            logger.error(f"Error getting AI threat insights: {e}")
            return {"error": str(e)}
    
    async def _generate_ai_follow_ups(
        self,
        query: str,
        results: List[Dict[str, Any]],
        intent: str
    ) -> List[str]:
        """Generate AI-powered follow-up questions"""
        
        prompt = f"""
        Based on this cybersecurity query and results, suggest 3-5 intelligent follow-up questions:
        
        ORIGINAL QUERY: {query}
        INTENT: {intent}
        RESULTS COUNT: {len(results)}
        
        SAMPLE RESULTS:
        {json.dumps(results[:2], indent=2) if results else "No results"}
        
        Generate follow-up questions that would help a security analyst investigate further.
        Return as a JSON array of strings.
        """
        
        try:
            response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
            if response and response.text:
                # Try to parse JSON array
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return self._get_default_follow_ups(intent)
            
        except Exception as e:
            logger.error(f"Error generating AI follow-ups: {e}")
            return self._get_default_follow_ups(intent)
    
    def _build_summary_prompt(
        self,
        query: str,
        intent: str,
        analysis_data: Dict[str, Any],
        sample_results: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for summary generation"""
        
        return f"""
        You are a cybersecurity expert analyzing SIEM data. Provide a concise, professional summary.
        
        USER QUERY: {query}
        INTENT: {intent}
        
        ANALYSIS DATA:
        - Total Events: {analysis_data.get('total_count', 0)}
        - Unique Sources: {analysis_data.get('unique_sources', 0)}
        - Unique Users: {analysis_data.get('unique_users', 0)}
        - Time Range: {analysis_data.get('time_span', 'Unknown')}
        - Severity Levels: {analysis_data.get('severity_levels', [])}
        
        SAMPLE EVENTS:
        {json.dumps(sample_results, indent=2)}
        
        Provide a professional summary focusing on:
        1. Key findings
        2. Security implications
        3. Notable patterns or anomalies
        
        Keep response under 200 words and use cybersecurity terminology appropriately.
        """
    
    def _build_recommendations_prompt(
        self,
        query: str,
        intent: str,
        analysis_data: Dict[str, Any],
        sample_results: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for recommendations generation"""
        
        return f"""
        As a cybersecurity expert, provide actionable recommendations based on this SIEM analysis:
        
        QUERY: {query}
        INTENT: {intent}
        ANALYSIS: {json.dumps(analysis_data, indent=2)}
        SAMPLE EVENTS: {json.dumps(sample_results, indent=2)}
        
        Provide recommendations in JSON format:
        [
            {{
                "priority": "high|medium|low",
                "title": "Action Title",
                "description": "Detailed description",
                "category": "investigation|response|prevention|monitoring"
            }}
        ]
        
        Focus on practical, actionable items a security team can implement.
        """
    
    def _prepare_analysis_data(
        self,
        results: List[Dict[str, Any]],
        context: Optional[AnalysisContext] = None
    ) -> Dict[str, Any]:
        """Prepare data for AI analysis"""
        
        if not results:
            return {"total_count": 0}
        
        # Extract unique values
        sources = set()
        users = set()
        hosts = set()
        severities = set()
        
        for result in results:
            if result.get("source_ip"):
                sources.add(result["source_ip"])
            if result.get("user"):
                users.add(result["user"])
            if result.get("host"):
                hosts.add(result["host"])
            if result.get("severity"):
                severities.add(result["severity"])
        
        # Calculate time span
        timestamps = [r.get("timestamp") for r in results if r.get("timestamp")]
        time_span = "Unknown"
        if timestamps and len(timestamps) > 1:
            try:
                sorted_times = sorted(timestamps)
                time_span = f"{sorted_times[0]} to {sorted_times[-1]}"
            except:
                time_span = "Multiple timeframes"
        
        return {
            "total_count": len(results),
            "unique_sources": len(sources),
            "unique_users": len(users),
            "unique_hosts": len(hosts),
            "severity_levels": list(severities),
            "time_span": time_span
        }
    
    def _generate_template_summary(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str,
        context: Optional[AnalysisContext] = None
    ) -> str:
        """Generate summary using templates"""
        
        count = len(results)
        
        if intent == "show_failed_logins":
            unique_users = len(set(r.get("user", "") for r in results if r.get("user")))
            unique_ips = len(set(r.get("source_ip", "") for r in results if r.get("source_ip")))
            return f"Found {count} failed login attempts from {unique_users} users and {unique_ips} IP addresses. This may indicate potential brute force attacks or compromised credentials requiring investigation."
        
        elif intent == "malware_detection":
            unique_threats = len(set(r.get("threat_name", "") for r in results if r.get("threat_name")))
            affected_hosts = len(set(r.get("host", "") for r in results if r.get("host")))
            return f"Detected {count} malware events involving {unique_threats} threat signatures on {affected_hosts} hosts. Immediate containment and forensic analysis recommended."
        
        elif intent == "security_alerts":
            high_severity = len([r for r in results if r.get("severity", "").lower() == "high"])
            return f"Found {count} security alerts with {high_severity} high-severity events. Review critical alerts immediately and assess potential impact on infrastructure."
        
        elif intent == "network_traffic":
            unique_sources = len(set(r.get("source_ip", "") for r in results if r.get("source_ip")))
            total_bytes = sum(r.get("bytes", 0) for r in results)
            return f"Analyzed {count} network events from {unique_sources} sources totaling {total_bytes:,} bytes. Monitor for unusual traffic patterns and potential data exfiltration."
        
        else:
            return f"Analysis complete: Found {count} events matching your query. Review results for security implications and consider follow-up investigations as needed."
    
    def _generate_template_recommendations(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str,
        context: Optional[AnalysisContext] = None
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using templates"""
        
        recommendations = []
        
        if intent == "show_failed_logins":
            recommendations = [
                {
                    "priority": "high",
                    "title": "Review Failed Login Patterns",
                    "description": "Analyze failed login attempts for brute force patterns and suspicious source IPs",
                    "category": "investigation"
                },
                {
                    "priority": "medium",
                    "title": "Implement Account Lockout Policies",
                    "description": "Ensure robust account lockout policies are in place for repeated failed attempts",
                    "category": "prevention"
                },
                {
                    "priority": "medium",
                    "title": "Monitor Affected Accounts",
                    "description": "Set up enhanced monitoring for accounts with multiple failed login attempts",
                    "category": "monitoring"
                }
            ]
        
        elif intent == "malware_detection":
            recommendations = [
                {
                    "priority": "high",
                    "title": "Isolate Affected Systems",
                    "description": "Immediately isolate infected systems to prevent lateral movement",
                    "category": "response"
                },
                {
                    "priority": "high",
                    "title": "Update Antivirus Signatures",
                    "description": "Ensure all security tools have latest threat signatures and definitions",
                    "category": "prevention"
                },
                {
                    "priority": "medium",
                    "title": "Conduct Forensic Analysis",
                    "description": "Perform detailed forensic analysis to understand attack vector and scope",
                    "category": "investigation"
                }
            ]
        
        else:
            recommendations = [
                {
                    "priority": "medium",
                    "title": "Review Security Events",
                    "description": "Conduct thorough review of identified security events and their implications",
                    "category": "investigation"
                },
                {
                    "priority": "low",
                    "title": "Update Monitoring Rules",
                    "description": "Consider updating monitoring rules based on observed patterns",
                    "category": "prevention"
                }
            ]
        
        return recommendations
    
    def _generate_fallback_recommendations(self, intent: str) -> List[Dict[str, Any]]:
        """Generate basic fallback recommendations"""
        return [
            {
                "priority": "medium",
                "title": "Review Query Results",
                "description": "Manually review the query results for potential security implications",
                "category": "investigation"
            }
        ]
    
    def _get_default_follow_ups(self, intent: str) -> List[str]:
        """Get default follow-up questions based on intent"""
        
        follow_ups = {
            "show_failed_logins": [
                "Show me successful logins from these same IP addresses",
                "What are the most frequent failed login usernames?",
                "Are there any failed logins outside business hours?",
                "Show me geographic distribution of these failed logins"
            ],
            "malware_detection": [
                "Which systems are most affected by malware?",
                "Show me the timeline of malware detections",
                "Are there any malware families we haven't seen before?",
                "What network traffic is associated with these infections?"
            ],
            "security_alerts": [
                "Show me only critical severity alerts",
                "Which alert types are most frequent?",
                "Are there any alerts from internal IP ranges?",
                "Show me alerts that haven't been acknowledged"
            ]
        }
        
        return follow_ups.get(intent, [
            "Show me more details about these events",
            "Filter results by severity level",
            "Show me events from the last hour only",
            "Are there any related events I should investigate?"
        ])
    
    def _clean_ai_response(self, text: str) -> str:
        """Clean and validate AI response text"""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        # Ensure reasonable length
        if len(text) > 1000:
            sentences = text.split('.')
            text = '. '.join(sentences[:5]) + '.'
        
        return text
    
    def _parse_ai_recommendations(self, text: str) -> List[Dict[str, Any]]:
        """Parse AI-generated recommendations"""
        try:
            # Try to extract JSON
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                # Validate structure
                valid_recommendations = []
                for rec in recommendations:
                    if isinstance(rec, dict) and "title" in rec and "description" in rec:
                        valid_recommendations.append({
                            "priority": rec.get("priority", "medium"),
                            "title": rec.get("title", "Security Recommendation"),
                            "description": rec.get("description", "Review security findings"),
                            "category": rec.get("category", "investigation")
                        })
                return valid_recommendations
        except:
            pass
        
        # Fallback: parse as text
        return [
            {
                "priority": "medium",
                "title": "AI Analysis Results",
                "description": self._clean_ai_response(text),
                "category": "investigation"
            }
        ]
    
    def _generate_empty_results_response(self, query: str, intent: str) -> str:
        """Generate response for empty results"""
        return f"No events found matching your query. This could indicate either no security issues in the specified timeframe, or the query criteria may need adjustment. Consider broadening the search parameters or checking different time ranges."
    
    def _generate_fallback_summary(
        self,
        results: List[Dict[str, Any]],
        query: str,
        intent: str
    ) -> str:
        """Generate basic fallback summary"""
        count = len(results)
        if count == 0:
            return "No matching events found for your query."
        else:
            return f"Found {count} events matching your security query. Please review the results for potential security implications."
    
    # Threat pattern analysis methods
    def _identify_high_frequency_sources(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Identify high frequency source IPs"""
        sources = {}
        for result in results:
            source_ip = result.get("source_ip")
            if source_ip:
                sources[source_ip] = sources.get(source_ip, 0) + 1
        
        # Return top 10 sources
        return dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _analyze_time_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in events"""
        if not results:
            return {}
        
        timestamps = []
        for result in results:
            if result.get("timestamp"):
                try:
                    # Simple hour extraction (assumes ISO format)
                    timestamp = result["timestamp"]
                    if "T" in timestamp:
                        time_part = timestamp.split("T")[1]
                        hour = int(time_part.split(":")[0])
                        timestamps.append(hour)
                except:
                    continue
        
        if timestamps:
            hour_counts = {}
            for hour in timestamps:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Identify peak hours
            peak_hour = max(hour_counts, key=hour_counts.get)
            
            return {
                "hourly_distribution": hour_counts,
                "peak_hour": peak_hour,
                "peak_hour_count": hour_counts[peak_hour],
                "off_hours_activity": sum(count for hour, count in hour_counts.items() if hour < 6 or hour > 22)
            }
        
        return {}
    
    def _analyze_severity_distribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze severity distribution"""
        severities = {}
        for result in results:
            severity = result.get("severity", "unknown").lower()
            severities[severity] = severities.get(severity, 0) + 1
        
        return severities
    
    def _identify_correlation_indicators(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify potential correlation indicators"""
        if len(results) < 2:
            return {}
        
        # Look for common patterns
        common_users = {}
        common_sources = {}
        common_processes = {}
        
        for result in results:
            user = result.get("user")
            source = result.get("source_ip")
            process = result.get("process_name")
            
            if user:
                common_users[user] = common_users.get(user, 0) + 1
            if source:
                common_sources[source] = common_sources.get(source, 0) + 1
            if process:
                common_processes[process] = common_processes.get(process, 0) + 1
        
        return {
            "repeated_users": {k: v for k, v in common_users.items() if v > 1},
            "repeated_sources": {k: v for k, v in common_sources.items() if v > 1},
            "repeated_processes": {k: v for k, v in common_processes.items() if v > 1}
        }
    
    def _detect_anomalies(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect basic anomalies in the data"""
        if not results:
            return {}
        
        anomalies = {
            "unusual_timing": False,
            "high_frequency_events": False,
            "suspicious_sources": []
        }
        
        # Check for high frequency from single source
        sources = {}
        for result in results:
            source = result.get("source_ip")
            if source:
                sources[source] = sources.get(source, 0) + 1
        
        # Flag sources with >10 events as potentially suspicious
        for source, count in sources.items():
            if count > 10:
                anomalies["suspicious_sources"].append({"source": source, "count": count})
                anomalies["high_frequency_events"] = True
        
        return anomalies
    
    def _load_fallback_templates(self) -> Dict[str, str]:
        """Load fallback response templates"""
        return {
            "failed_login": "Found {count} failed login attempts. Consider investigating potential brute force attacks.",
            "malware": "Detected {count} malware events. Immediate containment and analysis recommended.",
            "network": "Analyzed {count} network events. Monitor for suspicious traffic patterns.",
            "default": "Found {count} security events requiring review."
        }
    
    def _load_analysis_prompts(self) -> Dict[str, str]:
        """Load AI analysis prompts"""
        return {
            "summary": "Analyze these cybersecurity events and provide a professional summary",
            "recommendations": "Provide actionable security recommendations based on this analysis",
            "threat_analysis": "Analyze these events for threat patterns and security implications"
        }
