#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kartavya SIEM Assistant - Final Cleanup
Removes old directories after successful migration
"""

import shutil
from pathlib import Path
import json
from datetime import datetime

def cleanup_old_directories():
    """Remove old directories after migration"""
    
    print("\n" + "="*70)
    print("FINAL CLEANUP - REMOVING OLD DIRECTORIES")
    print("="*70 + "\n")
    
    # Directories to remove
    old_dirs = [
        "assistant",
        "siem_connector", 
        "ui_dashboard",
        "rag_pipeline",
        "llm_training",
        "beats-config",
        "src",
        "config",
        "docker",  # Old docker dir, new one is in deployment/
        ".github",  # Can be recreated if needed
        "datasets",  # Empty, replaced by data/
    ]
    
    # Files to remove from root
    old_files = [
        "app.py",  # Old streamlit app
        "install_dependencies.py",
        "setup.py",
        "requirements.txt",  # Moved to backend/
        "requirements-prod.txt",
        "requirements-docker.txt",
        "package-lock.json",  # Root level, not needed
        "repo-structure.txt",  # Old structure doc
        "IN-PROGRESS.md",
        "IN_PROGRESS.md",
        "TO-UPDATE.md",
        "WARP.md",
        "status0.txt",
        "about.txt",
        # Migration scripts (can be archived)
        "migrate_to_clean_structure.py",
        "clean_migrate.py",
        "final_integration.py",
    ]
    
    removed_items = []
    preserved_items = []
    
    print("📁 Removing old directories...")
    for dir_name in old_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Removed: {dir_name}/")
                removed_items.append(f"{dir_name}/")
            except Exception as e:
                print(f"  ⚠️ Could not remove {dir_name}: {e}")
        else:
            print(f"  ⏭️ Skipped: {dir_name}/ (doesn't exist)")
            
    print("\n📄 Removing old files...")
    for file_name in old_files:
        file_path = Path(file_name)
        if file_path.exists() and file_path.is_file():
            try:
                # Archive migration scripts before deletion
                if file_name.endswith(('.py', '.md', '.txt')):
                    archive_dir = Path("docs/archive")
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, archive_dir / file_name)
                    
                file_path.unlink()
                print(f"  ✅ Removed: {file_name}")
                removed_items.append(file_name)
            except Exception as e:
                print(f"  ⚠️ Could not remove {file_name}: {e}")
        else:
            print(f"  ⏭️ Skipped: {file_name} (doesn't exist)")
            
    # Clean up backend subdirectories
    print("\n🧹 Cleaning backend subdirectories...")
    backend_cleanup = ["backend/nlp", "backend/response_formatter"]
    for dir_name in backend_cleanup:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Removed: {dir_name}/")
                removed_items.append(f"{dir_name}/")
            except Exception as e:
                print(f"  ⚠️ Could not remove {dir_name}: {e}")
                
    # Preserve important items
    print("\n✨ Preserving important items...")
    preserve = [
        "backend/",
        "frontend/",
        "deployment/",
        "docs/",
        "scripts/",
        "tests/",
        "data/",
        "README.md",
        "LICENSE",
        ".gitignore",
        ".git/",
        ".env",
        ".env.example",
        "backup_20251007_045203/",
        "FINAL_STRUCTURE.md",
        "MIGRATION_SUMMARY.md",
        "MIGRATION_REPORT.json"
    ]
    
    for item in preserve:
        if Path(item).exists():
            preserved_items.append(item)
            print(f"  ✅ Preserved: {item}")
            
    # Generate cleanup report
    report = {
        "cleanup_date": datetime.now().isoformat(),
        "removed_items": removed_items,
        "preserved_items": preserved_items,
        "statistics": {
            "items_removed": len(removed_items),
            "items_preserved": len(preserved_items)
        }
    }
    
    # Save report
    report_path = Path("CLEANUP_REPORT.json")
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    
    print("\n" + "="*70)
    print(f"✅ CLEANUP COMPLETE!")
    print(f"  - Removed: {len(removed_items)} items")
    print(f"  - Preserved: {len(preserved_items)} items")
    print(f"  - Report: CLEANUP_REPORT.json")
    print("="*70 + "\n")
    
    # Final structure
    print("📁 FINAL CLEAN STRUCTURE:")
    print("""
kartavya-siem/
├── backend/          # FastAPI backend
├── frontend/         # React frontend  
├── deployment/       # Docker & K8s
├── docs/            # Documentation
├── scripts/         # Utilities
├── tests/           # Tests
├── data/            # Data & models
├── backup_*/        # Backup (can be removed later)
├── README.md
├── LICENSE
└── .gitignore
    """)
    
if __name__ == "__main__":
    response = input("⚠️ This will remove old directories. Continue? (yes/no): ")
    if response.lower() == "yes":
        cleanup_old_directories()
    else:
        print("Cleanup cancelled.")
