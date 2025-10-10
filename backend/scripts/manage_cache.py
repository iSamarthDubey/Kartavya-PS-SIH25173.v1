#!/usr/bin/env python3
"""
Dataset Cache Management Utility
Manage local dataset cache for lightning-fast startup
"""

import os
import sys
from pathlib import Path
import pickle
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_cache_dir():
    """Get the cache directory path"""
    return Path(__file__).parent.parent / "data" / "datasets" / "Advanced_SIEM_Dataset"

def list_cache():
    """List all cache files with their sizes"""
    cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        logger.info("📁 No cache directory found")
        return
    
    cache_files = list(cache_dir.glob("*.pkl"))
    
    if not cache_files:
        logger.info("📁 Cache directory is empty")
        return
    
    logger.info(f"📊 Found {len(cache_files)} cache files:")
    total_size = 0
    
    for cache_file in cache_files:
        size = cache_file.stat().st_size
        total_size += size
        
        # Try to get record count
        try:
            with open(cache_file, 'rb') as f:
                dataset = pickle.load(f)
            record_count = len(dataset) if isinstance(dataset, list) else "Unknown"
        except:
            record_count = "Corrupted"
        
        logger.info(f"  📄 {cache_file.name}: {size // (1024*1024)}MB, {record_count} records")
    
    logger.info(f"💾 Total cache size: {total_size // (1024*1024)}MB")

def clear_cache():
    """Clear all cache files"""
    cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        logger.info("📁 No cache directory to clear")
        return
    
    cache_files = list(cache_dir.glob("*.pkl"))
    temp_files = list(cache_dir.glob("*.tmp"))
    
    all_files = cache_files + temp_files
    
    if not all_files:
        logger.info("📁 Cache is already empty")
        return
    
    for cache_file in all_files:
        cache_file.unlink()
        logger.info(f"🗑️  Deleted {cache_file.name}")
    
    logger.info(f"✅ Cleared {len(all_files)} cache files")

def validate_cache():
    """Validate all cache files and remove corrupted ones"""
    cache_dir = get_cache_dir()
    
    if not cache_dir.exists():
        logger.info("📁 No cache directory found")
        return
    
    cache_files = list(cache_dir.glob("*.pkl"))
    
    if not cache_files:
        logger.info("📁 No cache files to validate")
        return
    
    logger.info(f"🔍 Validating {len(cache_files)} cache files...")
    
    valid_count = 0
    corrupted_count = 0
    
    for cache_file in cache_files:
        try:
            with open(cache_file, 'rb') as f:
                dataset = pickle.load(f)
            
            if isinstance(dataset, list) and len(dataset) > 0:
                valid_count += 1
                logger.info(f"✅ {cache_file.name}: Valid ({len(dataset)} records)")
            else:
                logger.warning(f"⚠️  {cache_file.name}: Invalid format, removing...")
                cache_file.unlink()
                corrupted_count += 1
                
        except Exception as e:
            logger.error(f"❌ {cache_file.name}: Corrupted ({e}), removing...")
            cache_file.unlink()
            corrupted_count += 1
    
    logger.info(f"📊 Validation complete: {valid_count} valid, {corrupted_count} removed")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("""
🚀 Dataset Cache Management Utility

Commands:
  list     - List all cache files
  clear    - Clear all cache files  
  validate - Validate cache files and remove corrupted ones
  info     - Show cache directory info

Examples:
  python manage_cache.py list
  python manage_cache.py clear
  python manage_cache.py validate
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_cache()
    elif command == "clear":
        clear_cache()
    elif command == "validate":
        validate_cache()
    elif command == "info":
        cache_dir = get_cache_dir()
        logger.info(f"📁 Cache directory: {cache_dir.absolute()}")
        logger.info(f"📁 Exists: {cache_dir.exists()}")
        list_cache()
    else:
        logger.error(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
