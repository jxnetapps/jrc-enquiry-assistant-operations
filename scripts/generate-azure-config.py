#!/usr/bin/env python3
"""
Generate Azure App Service configuration from template
"""

import os
import sys
from pathlib import Path

def generate_azure_config():
    """Generate Azure App Service configuration"""
    
    print("Azure App Service Configuration Generator")
    print("=" * 50)
    
    # Read the Azure template
    template_file = "config-templates/config_template.env.azure"
    if not os.path.exists(template_file):
        print(f"ERROR: Template file not found: {template_file}")
        return False
    
    print(f"Reading template: {template_file}")
    
    # Parse template and generate Azure App Service settings
    azure_settings = []
    
    with open(template_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Skip section headers
        if line.startswith('='):
            continue
        
        # Parse key=value pairs
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Skip placeholder values
            if value.startswith('your_') or value.startswith('${'):
                continue
            
            # Add to Azure settings
            azure_settings.append((key, value))
    
    # Display Azure App Service configuration
    print("\nAzure App Service Application Settings:")
    print("=" * 50)
    print("Copy these settings to Azure Portal -> Your App Service -> Configuration -> Application Settings")
    print()
    
    for key, value in azure_settings:
        print(f"{key} = {value}")
    
    print("\n" + "=" * 50)
    print("Instructions:")
    print("1. Go to Azure Portal")
    print("2. Navigate to your App Service")
    print("3. Go to Configuration -> Application Settings")
    print("4. Add each setting above")
    print("5. Save and restart your App Service")
    
    return True

def show_required_settings():
    """Show required settings for Azure deployment"""
    
    print("\nRequired Azure App Service Settings:")
    print("=" * 50)
    
    required_settings = [
        ("ENVIRONMENT", "azure", "Set environment to azure"),
        ("POSTGRESQL_CONNECTION_URI", "postgresql://postgres:password@db.umwxkbcvqvqqybjwcash.supabase.co:5432/postgres", "PostgreSQL connection string"),
        ("POSTGRESQL_DATABASE_NAME", "postgres", "Database name"),
        ("JWT_SECRET_KEY", "your_super_secure_production_jwt_secret_key", "JWT secret for authentication"),
        ("ADMIN_USERNAME", "admin", "Admin username"),
        ("ADMIN_PASSWORD", "your_secure_admin_password", "Admin password"),
        ("OPENAI_API_KEY", "sk-your-openai-api-key", "OpenAI API key"),
        ("DATABASE_TYPE", "cloud", "Use Chroma Cloud"),
        ("CHROMA_CLOUD_API_KEY", "your_chroma_cloud_api_key", "Chroma Cloud API key"),
        ("CHROMA_CLOUD_TENANT_ID", "your_tenant_id", "Chroma Cloud tenant ID"),
        ("CHROMA_CLOUD_DATABASE_ID", "your_database_id", "Chroma Cloud database ID"),
    ]
    
    for key, value, description in required_settings:
        print(f"{key} = {value}")
        print(f"  # {description}")
        print()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "required":
        show_required_settings()
    else:
        generate_azure_config()

if __name__ == "__main__":
    main()
