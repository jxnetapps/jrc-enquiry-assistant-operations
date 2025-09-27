#!/usr/bin/env python3
"""
Environment setup script for Web ChatBot
Usage: python scripts/setup-env.py [environment]
"""

import os
import sys
import shutil
from pathlib import Path

def setup_environment(env_name):
    """Setup environment configuration"""
    
    # Valid environments
    valid_envs = ['development', 'staging', 'production']
    
    if env_name not in valid_envs:
        print(f"ERROR: Invalid environment: {env_name}")
        print(f"Valid environments: {', '.join(valid_envs)}")
        return False
    
    # Template file path
    template_file = f"config_template.env.{env_name}"
    env_file = f".env.{env_name}"
    
    # Check if template exists
    if not os.path.exists(template_file):
        print(f"ERROR: Template file not found: {template_file}")
        return False
    
    # Copy template to .env file
    try:
        shutil.copy2(template_file, env_file)
        print(f"SUCCESS: Created {env_file} from {template_file}")
        
        # Set environment variable for current session
        os.environ['ENVIRONMENT'] = env_name
        print(f"SUCCESS: Set ENVIRONMENT={env_name}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error creating {env_file}: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python scripts/setup-env.py [environment]")
        print("Environments: development, staging, production")
        sys.exit(1)
    
    env_name = sys.argv[1].lower()
    
    print(f"Setting up {env_name} environment...")
    
    if setup_environment(env_name):
        print(f"SUCCESS: {env_name} environment setup complete!")
        print(f"INFO: Edit .env.{env_name} with your specific configuration values")
        print(f"INFO: Run with: ENVIRONMENT={env_name} python web_app.py")
    else:
        print(f"ERROR: Failed to setup {env_name} environment")
        sys.exit(1)

if __name__ == "__main__":
    main()
