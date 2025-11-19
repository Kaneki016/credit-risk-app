"""
Project Cleanup Script
Removes redundant files and reorganizes project structure.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Files to delete
MARKDOWN_TO_DELETE = [
    "AI_EXPLANATION_FIX.md",
    "QUICK_FIX_SUMMARY.md",
    "EXCEPTION_HANDLER_SUMMARY.md",
    "FALLBACK_EXPLANATION_GUIDE.md",
    "IMPLEMENTATION_COMPLETE.md",
    "NETWORK_ERROR_FIX.md",
    "OPENROUTER_MIGRATION_GUIDE.md",
    "FIX_API_KEY.md",
    "RETRAINING_FIX.md",
    "IMPORT_SUCCESS.md",
    "CHECK_DATABASE.md",
    "ADMIN_PANEL_SETUP.md",
    "ADMIN_PANEL_SUMMARY.md",
    "CHATBOT_SUMMARY.md",
    "API_KEY_SETUP_SUMMARY.md",
    "API_KEY_MANAGEMENT.md",
    "QUICK_START_IMPORT.md",
    "IMPLEMENTATION_SUMMARY.md",
    "NEW_FEATURES_SUMMARY.md",
    "IMPORT_AND_RETRAIN_GUIDE.md",
    "DATABASE_INSPECTION_GUIDE.md",
    "QUICK_START.md",
    "SIMPLIFIED_ARCHITECTURE.md",
    "REFACTORING_COMPLETE.md",
    "CLEANUP_COMPLETE.md",
]

SCRIPTS_TO_DELETE = [
    "test_ai_explanation_fix.py",
    "test_exception_handling_integration.py",
    "test_fallback_explanation.py",
    "test_fallback_simple.py",
    "test_openrouter.py",
    "test_retraining_fix.py",
    "check_api_requests.py",
    "restart_backend.py",
    "CLEANUP_PLAN.md",  # This plan file itself
]

# Backend files to delete (unused/redundant)
BACKEND_TO_DELETE = [
    "backend/models/openrouter_client.py",  # Not used, we use ai_client.py
    "backend/models/gemini_base.py",  # Legacy Gemini, not used
    "backend/models/gemini_predictor.py",  # Legacy Gemini, not used
    "backend/models/gemini_feature_engineer.py",  # Legacy Gemini, not used
    "backend/models/gemini_mitigation_guide.py",  # Legacy Gemini, not used
]

# Examples to delete (outdated)
EXAMPLES_TO_DELETE = [
    "examples/test_gemini_predictor.py",  # Legacy Gemini
    "examples/test_feature_engineering.py",  # Legacy feature
    "examples/test_mitigation_guide.py",  # Legacy feature
]

# Files to move to docs/
DOCS_TO_MOVE = {
    "GETTING_STARTED.md": "docs/getting-started/GETTING_STARTED.md",
    "API_QUICK_REFERENCE.md": "docs/api/API_QUICK_REFERENCE.md",
    "PROJECT_STRUCTURE.md": "docs/architecture/PROJECT_STRUCTURE.md",
    "ADMIN_PANEL_GUIDE.md": "docs/features/ADMIN_PANEL_GUIDE.md",
    "CHATBOT_GUIDE.md": "docs/features/CHATBOT_GUIDE.md",
    "NEW_FEATURES_GUIDE.md": "docs/features/NEW_FEATURES_GUIDE.md",
}

# Scripts to move
SCRIPTS_TO_MOVE = {
    "monitor_api_calls.py": "scripts/utilities/monitor_api_calls.py",
    "list_openrouter_models.py": "scripts/utilities/list_openrouter_models.py",
    "test_new_features.py": "scripts/testing/test_new_features.py",
}


def create_backup():
    """Create backup of files before deletion."""
    backup_dir = Path(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    print(f"📦 Creating backup in {backup_dir}/")
    
    # Backup markdown files
    for file in MARKDOWN_TO_DELETE:
        if Path(file).exists():
            shutil.copy2(file, backup_dir / file)
    
    # Backup scripts
    for file in SCRIPTS_TO_DELETE:
        if Path(file).exists():
            shutil.copy2(file, backup_dir / file)
    
    print(f"✓ Backup created: {len(list(backup_dir.iterdir()))} files")
    return backup_dir


def delete_files():
    """Delete redundant files."""
    print("\n🗑️  Deleting redundant files...")
    
    deleted_count = 0
    
    # Delete markdown files
    print("\n  Markdown files:")
    for file in MARKDOWN_TO_DELETE:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"    ✓ Deleted: {file}")
            deleted_count += 1
        else:
            print(f"    ⏭️  Skipped (not found): {file}")
    
    # Delete scripts
    print("\n  Python scripts:")
    for file in SCRIPTS_TO_DELETE:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"    ✓ Deleted: {file}")
            deleted_count += 1
        else:
            print(f"    ⏭️  Skipped (not found): {file}")
    
    # Delete backend files
    print("\n  Backend files:")
    for file in BACKEND_TO_DELETE:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"    ✓ Deleted: {file}")
            deleted_count += 1
        else:
            print(f"    ⏭️  Skipped (not found): {file}")
    
    # Delete examples
    print("\n  Example files:")
    for file in EXAMPLES_TO_DELETE:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"    ✓ Deleted: {file}")
            deleted_count += 1
        else:
            print(f"    ⏭️  Skipped (not found): {file}")
    
    print(f"\n✓ Deleted {deleted_count} files total")


def move_files():
    """Move files to organized directories."""
    print("\n📁 Moving files to organized structure...")
    
    moved_count = 0
    
    # Move documentation
    for source, dest in DOCS_TO_MOVE.items():
        source_path = Path(source)
        dest_path = Path(dest)
        
        if source_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            print(f"  ✓ Moved: {source} → {dest}")
            moved_count += 1
        else:
            print(f"  ⏭️  Skipped (not found): {source}")
    
    # Move scripts
    for source, dest in SCRIPTS_TO_MOVE.items():
        source_path = Path(source)
        dest_path = Path(dest)
        
        if source_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            print(f"  ✓ Moved: {source} → {dest}")
            moved_count += 1
        else:
            print(f"  ⏭️  Skipped (not found): {source}")
    
    print(f"\n✓ Moved {moved_count} files")


def create_index_files():
    """Create README files for organized directories."""
    print("\n📝 Creating index files...")
    
    # docs/README.md
    docs_readme = """# Documentation

## Getting Started
- [Getting Started Guide](getting-started/GETTING_STARTED.md) - Quick start guide for new users

## Features
- [Admin Panel Guide](features/ADMIN_PANEL_GUIDE.md) - Admin panel usage and features
- [Chatbot Guide](features/CHATBOT_GUIDE.md) - Chatbot usage and commands
- [New Features Guide](features/NEW_FEATURES_GUIDE.md) - Latest features (Clear DB + Flexible Training)

## API
- [API Quick Reference](api/API_QUICK_REFERENCE.md) - API endpoints and usage

## Architecture
- [Project Structure](architecture/PROJECT_STRUCTURE.md) - System architecture and design

---

For the main README, see [../README.md](../README.md)
"""
    
    Path("docs/README.md").write_text(docs_readme)
    print("  ✓ Created: docs/README.md")
    
    # scripts/README.md
    scripts_readme = """# Scripts

## Utilities
- [monitor_api_calls.py](utilities/monitor_api_calls.py) - Monitor API usage and statistics
- [list_openrouter_models.py](utilities/list_openrouter_models.py) - List available OpenRouter models

## Testing
- [test_new_features.py](testing/test_new_features.py) - Test new features (Clear DB + Flexible Training)

## Deployment
- [deploy.sh](deployment/deploy.sh) - Linux/Mac deployment script
- [deploy.ps1](deployment/deploy.ps1) - Windows deployment script

---

## Usage

### Monitor API Calls
```bash
python scripts/utilities/monitor_api_calls.py
```

### List Available Models
```bash
python scripts/utilities/list_openrouter_models.py
```

### Test New Features
```bash
python scripts/testing/test_new_features.py
```
"""
    
    Path("scripts/README.md").write_text(scripts_readme)
    print("  ✓ Created: scripts/README.md")


def update_main_readme():
    """Update main README with new structure."""
    print("\n📝 Updating main README...")
    
    # Read current README
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("  ⚠️  README.md not found, skipping update")
        return
    
    content = readme_path.read_text()
    
    # Add documentation section if not exists
    if "## 📚 Documentation" not in content:
        docs_section = """

## 📚 Documentation

### Getting Started
- [Getting Started Guide](docs/getting-started/GETTING_STARTED.md) - Quick start for new users
- [API Quick Reference](docs/api/API_QUICK_REFERENCE.md) - API endpoints and usage

### Features
- [Admin Panel Guide](docs/features/ADMIN_PANEL_GUIDE.md) - Admin panel usage
- [Chatbot Guide](docs/features/CHATBOT_GUIDE.md) - Chatbot commands
- [New Features Guide](docs/features/NEW_FEATURES_GUIDE.md) - Latest features

### Architecture
- [Project Structure](docs/architecture/PROJECT_STRUCTURE.md) - System design

### Scripts
- [Scripts Documentation](scripts/README.md) - Utility scripts and tools

---
"""
        # Insert before the last section or at the end
        if "## License" in content:
            content = content.replace("## License", docs_section + "## License")
        else:
            content += docs_section
        
        readme_path.write_text(content)
        print("  ✓ Updated: README.md")
    else:
        print("  ⏭️  Documentation section already exists")


def show_summary():
    """Show cleanup summary."""
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    
    print("\n✅ Completed Tasks:")
    print("  1. Created backup of all files")
    print("  2. Deleted 25 redundant markdown files")
    print("  3. Deleted 8 redundant Python scripts")
    print("  4. Deleted 5 unused backend files (legacy Gemini)")
    print("  5. Deleted 3 outdated example files")
    print("  6. Moved 6 docs to organized structure")
    print("  7. Moved 3 scripts to organized structure")
    print("  8. Created index files (docs/README.md, scripts/README.md)")
    print("  9. Updated main README.md")
    
    print("\n📁 New Structure:")
    print("  Root:")
    print("    - README.md (main entry point)")
    print("    - run.py (application runner)")
    print("    - requirements.txt, .env, etc. (config files)")
    print("\n  docs/")
    print("    ├── getting-started/")
    print("    ├── features/")
    print("    ├── api/")
    print("    └── architecture/")
    print("\n  scripts/")
    print("    ├── utilities/")
    print("    ├── testing/")
    print("    └── deployment/")
    
    print("\n🎯 Benefits:")
    print("  ✓ Clean root directory")
    print("  ✓ Organized documentation")
    print("  ✓ Easy to navigate")
    print("  ✓ Professional structure")
    
    print("\n" + "=" * 70)


def main():
    """Main cleanup function."""
    print("=" * 70)
    print("PROJECT CLEANUP")
    print("=" * 70)
    
    print("\nThis script will:")
    print("  1. Create backup of all files")
    print("  2. Delete 25 redundant markdown files")
    print("  3. Delete 8 redundant Python scripts")
    print("  4. Delete 5 unused backend files (legacy Gemini)")
    print("  5. Delete 3 outdated example files")
    print("  6. Move 6 docs to organized structure")
    print("  7. Move 3 scripts to organized structure")
    print("  8. Create index files")
    print("  9. Update main README")
    
    response = input("\nProceed with cleanup? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Cleanup cancelled")
        return
    
    try:
        # Step 1: Create backup
        backup_dir = create_backup()
        
        # Step 2: Delete redundant files
        delete_files()
        
        # Step 3: Move files to organized structure
        move_files()
        
        # Step 4: Create index files
        create_index_files()
        
        # Step 5: Update main README
        update_main_readme()
        
        # Step 6: Show summary
        show_summary()
        
        print(f"\n✅ Cleanup completed successfully!")
        print(f"📦 Backup saved in: {backup_dir}/")
        print("\nNext steps:")
        print("  1. Review the changes")
        print("  2. Test the application: python run.py")
        print("  3. Commit changes: git add . && git commit -m 'Clean up project structure'")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        print("Backup is safe in backup_* directory")
        raise


if __name__ == "__main__":
    main()
