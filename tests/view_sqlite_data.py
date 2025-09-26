#!/usr/bin/env python3
"""
SQLite Data Viewer for Chat Inquiries
This script helps you view, manage, and export data from the SQLite database.
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
import sys

class SQLiteDataViewer:
    def __init__(self, db_path="chat_inquiries.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            print(f"✅ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            print("🔌 Database connection closed")
    
    def get_table_info(self):
        """Get information about the table structure"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(chat_inquiry_information)")
        columns = cursor.fetchall()
        
        print("\n📋 Table Structure:")
        print("=" * 60)
        for col in columns:
            print(f"Column: {col[1]:<20} Type: {col[2]:<15} Nullable: {col[3]}")
        print("=" * 60)
    
    def get_record_count(self):
        """Get total number of records"""
        if not self.conn:
            return 0
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_inquiry_information")
        count = cursor.fetchone()[0]
        return count
    
    def view_all_data(self, limit=10):
        """View all data in the table"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM chat_inquiry_information ORDER BY created_at DESC LIMIT {limit}")
        rows = cursor.fetchall()
        
        if not rows:
            print("📭 No data found in the database")
            return
        
        print(f"\n📊 Showing {len(rows)} records (most recent first):")
        print("=" * 100)
        
        for i, row in enumerate(rows, 1):
            print(f"\n🔍 Record #{i}:")
            for key in row.keys():
                print(f"  {key}: {row[key]}")
            print("-" * 50)
    
    def search_data(self, search_term, search_fields=None):
        """Search data by specific fields"""
        if not self.conn:
            return
        
        if search_fields is None:
            search_fields = ['firstName', 'childName', 'email', 'mobile', 'schoolName']
        
        cursor = self.conn.cursor()
        
        # Build search query
        where_conditions = []
        params = []
        
        for field in search_fields:
            where_conditions.append(f"{field} LIKE ?")
            params.append(f"%{search_term}%")
        
        query = f"""
            SELECT * FROM chat_inquiry_information 
            WHERE {' OR '.join(where_conditions)}
            ORDER BY created_at DESC
        """
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            print(f"🔍 No records found matching '{search_term}'")
            return
        
        print(f"\n🔍 Found {len(rows)} records matching '{search_term}':")
        print("=" * 100)
        
        for i, row in enumerate(rows, 1):
            print(f"\n📝 Record #{i}:")
            for key in row.keys():
                print(f"  {key}: {row[key]}")
            print("-" * 50)
    
    def get_statistics(self):
        """Get statistics about the data"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        # Total count
        total = self.get_record_count()
        print(f"\n📈 Statistics:")
        print("=" * 40)
        print(f"Total Records: {total}")
        
        if total == 0:
            return
        
        # Parent type distribution
        cursor.execute("SELECT parentType, COUNT(*) FROM chat_inquiry_information GROUP BY parentType")
        parent_types = cursor.fetchall()
        print(f"\n👨‍👩‍👧‍👦 Parent Type Distribution:")
        for parent_type, count in parent_types:
            print(f"  {parent_type}: {count}")
        
        # School type distribution
        cursor.execute("SELECT schoolType, COUNT(*) FROM chat_inquiry_information GROUP BY schoolType")
        school_types = cursor.fetchall()
        print(f"\n🏫 School Type Distribution:")
        for school_type, count in school_types:
            print(f"  {school_type}: {count}")
        
        # Status distribution
        cursor.execute("SELECT status, COUNT(*) FROM chat_inquiry_information GROUP BY status")
        statuses = cursor.fetchall()
        print(f"\n📊 Status Distribution:")
        for status, count in statuses:
            print(f"  {status}: {count}")
        
        # Recent records
        cursor.execute("SELECT COUNT(*) FROM chat_inquiry_information WHERE created_at >= date('now', '-7 days')")
        recent = cursor.fetchone()[0]
        print(f"\n📅 Records in last 7 days: {recent}")
    
    def export_to_json(self, filename="chat_inquiries_export.json"):
        """Export data to JSON file"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chat_inquiry_information ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(row))
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"📤 Data exported to: {filename}")
        print(f"📊 Exported {len(data)} records")
    
    def export_to_csv(self, filename="chat_inquiries_export.csv"):
        """Export data to CSV file"""
        if not self.conn:
            return
        
        try:
            df = pd.read_sql_query("SELECT * FROM chat_inquiry_information ORDER BY created_at DESC", self.conn)
            df.to_csv(filename, index=False)
            print(f"📤 Data exported to: {filename}")
            print(f"📊 Exported {len(df)} records")
        except ImportError:
            print("❌ pandas not installed. Install with: pip install pandas")
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")

def main():
    """Main function to run the data viewer"""
    viewer = SQLiteDataViewer()
    
    if not viewer.connect():
        return
    
    try:
        print("\n🎯 SQLite Data Viewer for Chat Inquiries")
        print("=" * 50)
        
        # Show table info
        viewer.get_table_info()
        
        # Show statistics
        viewer.get_statistics()
        
        # Show recent data
        viewer.view_all_data(limit=5)
        
        # Interactive menu
        while True:
            print("\n🔧 Available Commands:")
            print("1. View all data")
            print("2. Search data")
            print("3. Show statistics")
            print("4. Export to JSON")
            print("5. Export to CSV")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                limit = input("Enter number of records to show (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                viewer.view_all_data(limit)
            
            elif choice == '2':
                search_term = input("Enter search term: ").strip()
                if search_term:
                    viewer.search_data(search_term)
            
            elif choice == '3':
                viewer.get_statistics()
            
            elif choice == '4':
                filename = input("Enter filename (default: chat_inquiries_export.json): ").strip()
                filename = filename if filename else "chat_inquiries_export.json"
                viewer.export_to_json(filename)
            
            elif choice == '5':
                filename = input("Enter filename (default: chat_inquiries_export.csv): ").strip()
                filename = filename if filename else "chat_inquiries_export.csv"
                viewer.export_to_csv(filename)
            
            elif choice == '6':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    finally:
        viewer.disconnect()

if __name__ == "__main__":
    main()
