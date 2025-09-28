#!/usr/bin/env python3
"""
Migration script to add user_id column to existing SQLite database
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

def migrate_add_user_id_column():
    """Add user_id column to existing chat_inquiry_information table"""
    try:
        with sqlite3.connect('database/chat_inquiries.db') as conn:
            cursor = conn.cursor()
            
            # Check if user_id column already exists
            cursor.execute("PRAGMA table_info(chat_inquiry_information)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' in columns:
                print("✅ user_id column already exists")
                return True
            
            print("🔄 Adding user_id column to chat_inquiry_information table...")
            
            # Add user_id column
            cursor.execute('ALTER TABLE chat_inquiry_information ADD COLUMN user_id TEXT')
            
            # Create index for user_id
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON chat_inquiry_information(user_id)')
            
            conn.commit()
            print("✅ Successfully added user_id column and index")
            
            # Verify the column was added
            cursor.execute("PRAGMA table_info(chat_inquiry_information)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"📋 Current columns: {columns}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error adding user_id column: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    try:
        with sqlite3.connect('database/chat_inquiries.db') as conn:
            cursor = conn.cursor()
            
            # Check table structure
            cursor.execute("PRAGMA table_info(chat_inquiry_information)")
            columns = cursor.fetchall()
            
            print("\n📋 Table structure after migration:")
            for column in columns:
                print(f"  {column[1]}: {column[2]} {'(NOT NULL)' if column[3] else '(NULL)'}")
            
            # Check if there are any existing records
            cursor.execute("SELECT COUNT(*) FROM chat_inquiry_information")
            count = cursor.fetchone()[0]
            print(f"\n📊 Total records in database: {count}")
            
            # Show sample records
            if count > 0:
                cursor.execute("SELECT id, user_id, firstName, mobile FROM chat_inquiry_information ORDER BY id DESC LIMIT 3")
                rows = cursor.fetchall()
                print("\n📝 Sample records:")
                for row in rows:
                    print(f"  ID: {row[0]}, user_id: {row[1]}, firstName: {row[2]}, mobile: {row[3]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting SQLite Migration: Adding user_id column")
    print("=" * 60)
    
    # Run migration
    if migrate_add_user_id_column():
        print("\n✅ Migration completed successfully!")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        verify_migration()
        
        print("\n🎉 Migration and verification completed!")
    else:
        print("\n❌ Migration failed!")
