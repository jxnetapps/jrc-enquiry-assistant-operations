#!/usr/bin/env python3
"""
Setup script to create .env file with updated configuration.
This script will create a .env file based on the config template.
"""

import os
import shutil

def create_env_file():
    """Create .env file from template"""
    template_file = "config_template.env"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled. .env file not modified.")
            return False
    
    try:
        # Copy template to .env
        shutil.copy2(template_file, env_file)
        print(f"✅ Created .env file from {template_file}")
        
        # Show current configuration
        print("\n📋 Current Configuration:")
        print("=" * 50)
        
        with open(env_file, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if not value.startswith('your_') and not value.startswith('#'):
                    print(f"  {key}={value}")
        
        print("\n🔧 Next Steps:")
        print("1. Edit .env file to add your API keys and credentials")
        print("2. Set CHAT_BEHAVIOR to 'pre_trained' if you want structured conversations")
        print("3. Set DATABASE_TYPE to 'cloud' if you want to use Chroma Cloud")
        print("4. Run: python web_app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_configuration_options():
    """Show different configuration options"""
    print("\n🎯 Configuration Options:")
    print("=" * 50)
    
    print("\n1. Local Development (Knowledge Base Mode):")
    print("   DATABASE_TYPE=local")
    print("   CHAT_BEHAVIOR=knowledge_base")
    print("   OPENAI_API_KEY=your_key_here")
    
    print("\n2. Local Development (Pre-trained Mode):")
    print("   DATABASE_TYPE=local")
    print("   CHAT_BEHAVIOR=pre_trained")
    print("   OPENAI_API_KEY=your_key_here")
    
    print("\n3. Production (Chroma Cloud + Pre-trained):")
    print("   DATABASE_TYPE=cloud")
    print("   CHAT_BEHAVIOR=pre_trained")
    print("   CHROMA_CLOUD_API_KEY=your_chroma_key")
    print("   CHROMA_CLOUD_TENANT_ID=your_tenant_id")
    print("   CHROMA_CLOUD_DATABASE_ID=your_database_id")
    print("   OPENAI_API_KEY=your_openai_key")

def main():
    """Main setup function"""
    print("🚀 Web ChatBot Environment Setup")
    print("=" * 50)
    
    # Check if template exists
    if not os.path.exists("config_template.env"):
        print("❌ config_template.env not found!")
        print("Please make sure you're in the project directory.")
        return False
    
    # Create .env file
    success = create_env_file()
    
    if success:
        show_configuration_options()
        
        print("\n✅ Setup complete!")
        print("You can now edit .env file and run the application.")
    else:
        print("\n❌ Setup failed!")
        print("Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()
