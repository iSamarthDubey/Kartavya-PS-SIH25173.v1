#!/usr/bin/env python3
"""
Test Beats detection patterns against actual indices
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_beats_detection():
    """Test if the Beats detection patterns work correctly"""
    
    # Your actual indices
    actual_indices = [
        "metricbeat-2025.10.12",
        ".ds-metricbeat-9.1.4-2025.10.03-000001", 
        "winlogbeat-2025.10.12",
        ".ds-winlogbeat-9.1.4-2025.10.03-000001",
        "security-logs-demo"
    ]
    
    # Beats detection patterns from the code
    beat_patterns = [
        "winlogbeat", "metricbeat", "filebeat", "packetbeat",
        "heartbeat", "auditbeat", "journalbeat", "functionbeat"
    ]
    
    print("🔍 Testing Beats Detection Patterns")
    print("=" * 50)
    
    detected_beats = set()
    
    for index in actual_indices:
        index_lower = index.lower()
        print(f"\n📋 Analyzing index: {index}")
        
        matches = []
        for beat in beat_patterns:
            if beat in index_lower:
                matches.append(beat)
                detected_beats.add(beat)
        
        if matches:
            print(f"  ✅ Detected beats: {matches}")
        else:
            print(f"  ❌ No beats detected")
    
    print(f"\n🎯 SUMMARY:")
    print(f"Total indices analyzed: {len(actual_indices)}")
    print(f"Beats detected: {sorted(list(detected_beats))}")
    print(f"Expected beats based on your indices: ['metricbeat', 'winlogbeat']")
    
    if "metricbeat" in detected_beats and "winlogbeat" in detected_beats:
        print("✅ SUCCESS: Both metricbeat and winlogbeat should be detected!")
    else:
        print("❌ FAILURE: Some beats not detected")
    
    # Test data source detection patterns
    print(f"\n🔧 Testing Data Source Detection:")
    
    data_source_matches = set()
    for index in actual_indices:
        index_lower = index.lower()
        
        # Check if it matches BEATS pattern
        if any(beat in index_lower for beat in ["beat", "winlogbeat", "metricbeat", "filebeat"]):
            data_source_matches.add("BEATS")
            
        # Check if it matches SYSLOG pattern  
        if any(term in index_lower for term in ["syslog", "rsyslog", "log"]):
            data_source_matches.add("SYSLOG")
            
        # Check if it matches ECS pattern
        if any(term in index_lower for term in ["ecs", "elastic"]):
            data_source_matches.add("ECS")
    
    print(f"Data source types detected: {sorted(list(data_source_matches))}")
    
    if "BEATS" in data_source_matches:
        print("✅ SUCCESS: BEATS data source should be detected!")
    else:
        print("❌ FAILURE: BEATS data source not detected")

if __name__ == "__main__":
    test_beats_detection()
