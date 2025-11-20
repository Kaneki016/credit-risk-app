"""
Final Project Cleanup Script
Removes CI/CD files, unused code, and performs comprehensive cleanup.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# CI/CD and Docker files to remove
CICD_FILES = [
    ".github",  # Entire directory
    ".dockerignore",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "frontend/Dockerfile",
]

# Unused backend files
UNUSED_BACKEND = [
    "backend/services/explanation_service.py",  # Functionality moved to ai_client.py
    "backend/services/retraining.py",  # Replaced by database_retraining.py
]

# Docs files to remove (CI/CD related)
UNUSED_DOCS = [
    "docs/CI_CD_TROUBLESHOOTING.md",
    "docs/PROJECT_CLEANUP_PLAN.md",
    "docs/CLEANUP_SUMMARY.md",
    "docs/TEST_CLEANUP_SUMMARY.md",
]

# Redundant markdown files (from previous analysis)
REDUNDANT_MARKDOWN = [
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
    "CLEANUP_PLAN.md",
    "PROJECT_CLEANUP_SUMMARY.md",
    "CLEANUP_QUICK_REFERENCE.md",
]

# Redundant test scripts
REDUNDANT_SCRIPTS = [
    "test_ai_explanation_fix.py",
    "test_exception_handling_integration.py",
    "test_fallback_explanation.py",
    "test_fallback_simple.py",
    "test_openrouter.py",
    "test_retraining_fix.py",
    "check_api_requests.py",
    "restart_backend.py",
]

# Legacy backend files (Gemini)
LEGACY_BACKEND = [
    "backend/models/openrouter_client.py",
    "backend/models/gemini_base.py",
    "backend/models/gemini_predictor.py",
    "backend/models/gemini_feature_engineer.py",
    "backend/models/gemini_mitigation_guide.py",
]

# Outdated examples
OUTDATED_EXAMPLES = [
    "examples/test_gemini_predictor.py",
    "examples/test_feature_engineering.py",
    "examples/test_mitigation_guide.py",
]

# Files to move
DOCS_TO_MOVE = {
    "GETTING_STARTED.md": "docs/getting-started/GETTING_STARTED.md",
    "API_QUICK_REFERENCE.md": "docs/api/API_QUICK_REFERENCE.md",
    "PROJECT_STRUCTURE.md": "docs/architecture/PROJECT_STRUCTURE.md",
    "ADMIN_PANEL_GUIDE.md": "docs/features/ADMIN_PANEL_GUIDE.md",
    "CHATBOT_GUIDE.md": "docs/features/CHATBOT_GUIDE.md",
    "NEW_FEATURES_GUIDE.md": "docs/features/NEW_FEATURES_GUIDE.md",
}

SCRIPTS_TO_MOVE = {
    "monitor_api_calls.py": "scripts/utilities/monitor_api_calls.py",
    "list_openrouter_models.py": "scripts/utilities/list_openrouter_models.py",
    "test_new_features.py": "scripts/testing/test_new_features.py",
}


def create_backup():
    """Create backup of all files before deletion."""
    backup_dir = Path(f"backup_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    print(f"📦 Creating comprehensive backup in {backup_dir}/")
    
    all_files = (
        CICD_FILES +
        UNUSED_BACKEND +
        UNUSED_DOCS +
        REDUNDANT_MARKDOWN +
        REDUNDANT_SCRIPTS +
        LEGACY_BACKEND +
        OUTDATED_EXAMPLES
    )
    
    backed_up = 0
    for file in all_files:
        file_path = Path(file)
        if file_path.exists():
            if file_path.is_dir():
                shutil.copytree(file_path, backup_dir / file_path.name, dirs_exist_ok=True)
            else:
                dest = backup_dir / file_path.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
            backed_up += 1
    
    print(f"✓ Backup created: {backed_up} items")
    return backup_dir


def delete_cicd_files():
    """Remove all CI/CD and Docker related files."""
    print("\n🗑️  Removing CI/CD and Docker files...")
    
    deleted = 0
    for file in CICD_FILES:
        file_path = Path(file)
        if file_path.exists():
            if file_path.is_dir():
                shutil.rmtree(file_path)
                print(f"  ✓ Deleted directory: {file}")
            else:
                file_path.unlink()
                print(f"  ✓ Deleted: {file}")
            deleted += 1
        else:
            print(f"  ⏭️  Skipped (not found): {file}")
    
    print(f"\n✓ Deleted {deleted} CI/CD items")


def delete_unused_backend():
    """Remove unused backend files."""
    print("\n🗑️  Removing unused backend files...")
    
    deleted = 0
    all_unused = UNUSED_BACKEND + LEGACY_BACKEND
    
    for file in all_unused:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ Deleted: {file}")
            deleted += 1
        else:
            print(f"  ⏭️  Skipped (not found): {file}")
    
    print(f"\n✓ Deleted {deleted} backend files")


def delete_unused_docs():
    """Remove unused documentation files."""
    print("\n🗑️  Removing unused documentation...")
    
    deleted = 0
    for file in UNUSED_DOCS:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ Deleted: {file}")
            deleted += 1
        else:
            print(f"  ⏭️  Skipped (not found): {file}")
    
    print(f"\n✓ Deleted {deleted} doc files")


def delete_redundant_files():
    """Delete redundant markdown and script files."""
    print("\n🗑️  Removing redundant files...")
    
    deleted = 0
    
    # Markdown files
    print("\n  Markdown files:")
    for file in REDUNDANT_MARKDOWN:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"    ✓ Deleted: {file}")
            deleted += 1
    
    # Scripts
    print("\n  Python scripts:")
    for file in REDUNDANT_SCRIPTS:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"    ✓ Deleted: {file}")
            deleted += 1
    
    # Examples
    print("\n  Example files:")
    for file in OUTDATED_EXAMPLES:
        file_path = Path(file)
        if file_path.exists():
            file_path.unlink()
            print(f"    ✓ Deleted: {file}")
            deleted += 1
    
    print(f"\n✓ Deleted {deleted} redundant files")


def move_files():
    """Move files to organized directories."""
    print("\n📁 Moving files to organized structure...")
    
    moved = 0
    
    # Move documentation
    print("\n  Documentation:")
    for source, dest in DOCS_TO_MOVE.items():
        source_path = Path(source)
        dest_path = Path(dest)
        
        if source_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            print(f"    ✓ Moved: {source} → {dest}")
            moved += 1
        else:
            print(f"    ⏭️  Skipped (not found): {source}")
    
    # Move scripts
    print("\n  Scripts:")
    for source, dest in SCRIPTS_TO_MOVE.items():
        source_path = Path(source)
        dest_path = Path(dest)
        
        if source_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            print(f"    ✓ Moved: {source} → {dest}")
            moved += 1
        else:
            print(f"    ⏭️  Skipped (not found): {source}")
    
    print(f"\n✓ Moved {moved} files")


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


def update_readme():
    """Update main README to remove Docker references and add new structure."""
    print("\n📝 Updating main README...")
    
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("  ⚠️  README.md not found")
        return
    
    content = readme_path.read_text()
    
    # Remove Docker deployment section
    if "Docker Deployment" in content or "docker-compose" in content:
        # Remove docker-compose references
        content = content.replace("- [Docker Deployment](docker-compose.yml)\n", "")
        content = content.replace("docker-compose up -d\n", "python run.py\n")
        content = content.replace("docker-compose up -d --env-file .env\n", "python run.py\n")
        
        print("  ✓ Removed Docker references")
    
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
        # Insert before License section or at the end
        if "## License" in content:
            content = content.replace("## License", docs_section + "## License")
        else:
            content += docs_section
        
        print("  ✓ Added documentation section")
    
    readme_path.write_text(content)
    print("  ✓ Updated: README.md")


def show_summary():
    """Show comprehensive cleanup summary."""
    print("\n" + "=" * 70)
    print("FINAL CLEANUP SUMMARY")
    print("=" * 70)
    
    print("\n✅ Completed Tasks:")
    print("  1. Created comprehensive backup")
    print("  2. Removed all CI/CD files (.github, Dockerfile, docker-compose)")
    print("  3. Removed unused backend files (7 files)")
    print("  4. Removed unused documentation (4 files)")
    print("  5. Removed redundant markdown files (28 files)")
    print("  6. Removed redundant scripts (8 files)")
    print("  7. Removed outdated examples (3 files)")
    print("  8. Moved 6 docs to organized structure")
    print("  9. Moved 3 scripts to organized structure")
    print(" 10. Created index files")
    print(" 11. Updated main README")
    
    print("\n📊 Statistics:")
    print(f"  CI/CD files removed: {len(CICD_FILES)}")
    print(f"  Backend files removed: {len(UNUSED_BACKEND) + len(LEGACY_BACKEND)}")
    print(f"  Doc files removed: {len(UNUSED_DOCS)}")
    print(f"  Markdown files removed: {len(REDUNDANT_MARKDOWN)}")
    print(f"  Scripts removed: {len(REDUNDANT_SCRIPTS)}")
    print(f"  Examples removed: {len(OUTDATED_EXAMPLES)}")
    print(f"  Total files removed: ~50+")
    
    print("\n📁 New Clean Structure:")
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
    print("\n  backend/ (cleaned)")
    print("    ├── api/")
    print("    ├── core/")
    print("    ├── database/")
    print("    ├── models/ (no legacy code)")
    print("    ├── services/ (no unused files)")
    print("    └── utils/")
    
    print("\n🎯 Benefits:")
    print("  ✓ No CI/CD complexity")
    print("  ✓ No Docker overhead")
    print("  ✓ Clean backend code")
    print("  ✓ Organized documentation")
    print("  ✓ Professional structure")
    print("  ✓ Easy to maintain")
    
    print("\n" + "=" * 70)


def main():
    """Main cleanup function."""
    print("=" * 70)
    print("FINAL PROJECT CLEANUP")
    print("=" * 70)
    
    print("\nThis script will:")
    print("  1. Remove all CI/CD files (.github, Dockerfile, docker-compose)")
    print("  2. Remove unused backend files (7 files)")
    print("  3. Remove unused documentation (4 files)")
    print("  4. Remove redundant markdown files (28 files)")
    print("  5. Remove redundant scripts (8 files)")
    print("  6. Remove outdated examples (3 files)")
    print("  7. Move 6 docs to organized structure")
    print("  8. Move 3 scripts to organized structure")
    print("  9. Create index files")
    print(" 10. Update main README")
    print("\n  Total: ~50+ files will be removed/moved")
    
    response = input("\nProceed with final cleanup? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Cleanup cancelled")
        return
    
    try:
        # Step 1: Create backup
        backup_dir = create_backup()
        
        # Step 2: Delete CI/CD files
        delete_cicd_files()
        
        # Step 3: Delete unused backend
        delete_unused_backend()
        
        # Step 4: Delete unused docs
        delete_unused_docs()
        
        # Step 5: Delete redundant files
        delete_redundant_files()
        
        # Step 6: Move files
        move_files()
        
        # Step 7: Create index files
        create_index_files()
        
        # Step 8: Update README
        update_readme()
        
        # Step 9: Show summary
        show_summary()
        
        print(f"\n✅ Final cleanup completed successfully!")
        print(f"📦 Backup saved in: {backup_dir}/")
        print("\nNext steps:")
        print("  1. Review the changes")
        print("  2. Test the application: python run.py")
        print("  3. Delete cleanup scripts: final_cleanup.py, cleanup_project.py")
        print("  4. Commit changes: git add . && git commit -m 'Final cleanup: remove CI/CD and unused code'")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        print("Backup is safe in backup_final_* directory")
        raise


if __name__ == "__main__":
    main()
