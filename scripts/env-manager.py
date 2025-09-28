#!/usr/bin/env python3
"""
Simple Environment Manager - One robust method for managing environments
"""

import os
import sys
from pathlib import Path

def show_config():
    """Show current environment configuration"""
    print("Current Environment Configuration")
    print("=" * 50)
    
    # Get current environment
    env = os.getenv("ENVIRONMENT", "development")
    print(f"Environment: {env}")
    
    # Check which .env file would be loaded
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        print(f"Config File: {env_file}")
    elif os.path.exists(".env"):
        print(f"Config File: .env (fallback)")
    else:
        print("Config File: None found!")
        return
    
    # Load and show database configuration
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from config import Config
        
        print(f"Database: PostgreSQL")
        print(f"Connection: {Config.POSTGRESQL_CONNECTION_URI}")
            
    except Exception as e:
        print(f"Error loading config: {e}")

def regenerate_env_files():
    """Regenerate all .env files from templates"""
    print("Regenerating environment files from templates...")
    print("=" * 50)
    
    # Define template and target file paths
    templates = {
        'development': {
            'template': 'config-templates/config_template.env.development',
            'target': '.env.development'
        },
        'production': {
            'template': 'config-templates/config_template.env.production',
            'target': '.env.production'
        },
        'azure': {
            'template': 'config-templates/config_template.env.azure',
            'target': '.env.azure'
        },
        'default': {
            'template': 'config-templates/config_template.env',
            'target': '.env'
        }
    }
    
    # Create environment files
    for env_name, config in templates.items():
        print(f"Creating {env_name} environment...")
        
        if not os.path.exists(config['template']):
            print(f"  ERROR: Template not found: {config['template']}")
            continue
        
        # Read template
        with open(config['template'], 'r') as f:
            content = f.read()
        
        # Set database type
        db_type = "PostgreSQL"
        
        # Write to .env file
        with open(config['target'], 'w') as f:
            f.write(content)
        
        print(f"  SUCCESS: {config['target']} -> {db_type}")
    
    print("\nEnvironment files regenerated successfully!")
    print("\nTo use:")
    print("  Development: python web_app.py")
    print("  Production:  set ENVIRONMENT=production && python web_app.py")

def setup_environment():
    """Initial setup - create all .env files from templates"""
    print("Initial Environment Setup")
    print("=" * 50)
    
    # Check if templates exist
    required_templates = [
        "config-templates/config_template.env.development",
        "config-templates/config_template.env.production", 
        "config-templates/config_template.env.azure",
        "config-templates/config_template.env"
    ]
    
    missing_templates = [t for t in required_templates if not os.path.exists(t)]
    if missing_templates:
        print("ERROR: Missing template files:")
        for template in missing_templates:
            print(f"   - {template}")
        print("Please make sure you're in the project directory.")
        return False
    
    # Create .env files
    regenerate_env_files()
    
    print("\nSUCCESS: Initial setup complete!")
    print("All environment files created successfully.")
    print("\nNext steps:")
    print("1. Run: python scripts/env-manager.py show")
    print("2. Start application:")
    print("   - Development: scripts/start-dev.bat (Windows) or scripts/start-dev.sh (Linux/Mac)")
    print("   - Production:  scripts/start-prod.bat (Windows) or scripts/start-prod.sh (Linux/Mac)")
    
    return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Environment Manager")
        print("=" * 50)
        print("Usage:")
        print("  python scripts/env-manager.py setup    - Initial setup (first time)")
        print("  python scripts/env-manager.py show     - Show current config")
        print("  python scripts/env-manager.py rebuild  - Rebuild all .env files")
        print("")
        print("Quick start:")
        print("  1. First time: python scripts/env-manager.py setup")
        print("  2. Check config: python scripts/env-manager.py show")
        print("  3. Start app: scripts/start-dev.bat (Windows) or scripts/start-dev.sh (Linux/Mac)")
        print("")
        print("To change database settings:")
        print("  1. Edit config-templates/config_template.env.development or config-templates/config_template.env.production")
        print("  2. Run: python scripts/env-manager.py rebuild")
        print("  3. Restart: scripts/start-dev.bat or scripts/start-prod.bat")
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        setup_environment()
    elif command == "show":
        show_config()
    elif command == "rebuild":
        regenerate_env_files()
    else:
        print(f"Unknown command: {command}")
        print("Use 'setup', 'show', or 'rebuild'")

if __name__ == "__main__":
    main()
