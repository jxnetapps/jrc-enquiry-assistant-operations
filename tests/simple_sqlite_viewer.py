#!/usr/bin/env python3
"""
Simple SQLite Data Viewer for Chat Inquiries
This script helps you view and manage data from the SQLite database.
"""

import sqlite3
import json
from datetime import datetime

class SimpleSQLiteViewer:
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
    
    def search_data(self, search_term):
        """Search data by specific fields"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        # Search in multiple fields
        query = """
            SELECT * FROM chat_inquiry_information 
            WHERE firstName LIKE ? OR childName LIKE ? OR email LIKE ? 
               OR mobile LIKE ? OR schoolName LIKE ? OR city LIKE ?
            ORDER BY created_at DESC
        """
        
        search_pattern = f"%{search_term}%"
        cursor.execute(query, (search_pattern, search_pattern, search_pattern, 
                              search_pattern, search_pattern, search_pattern))
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
            print("📭 No data to analyze")
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
    
    def add_sample_data(self):
        """Add sample data for testing"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        sample_data = [
            {
                'parentType': 'New Parent',
                'schoolType': 'Day School',
                'firstName': 'John Doe',
                'mobile': '9876543210',
                'email': 'john@example.com',
                'city': 'New York',
                'childName': 'Jane Doe',
                'grade': 'Grade 1',
                'academicYear': '2024-2025',
                'dateOfBirth': '2020-01-01',
                'schoolName': 'Test School',
                'status': 'new',
                'source': 'api'
            },
            {
                'parentType': 'Existing Parent',
                'schoolType': 'Boarding School',
                'firstName': 'Alice Smith',
                'mobile': '9876543211',
                'email': 'alice@example.com',
                'city': 'Los Angeles',
                'childName': 'Bob Smith',
                'grade': 'Grade 5',
                'academicYear': '2024-2025',
                'dateOfBirth': '2016-03-15',
                'schoolName': 'Elite School',
                'status': 'new',
                'source': 'api'
            }
        ]
        
        for data in sample_data:
            cursor.execute('''
                INSERT INTO chat_inquiry_information 
                (parentType, schoolType, firstName, mobile, email, city, 
                 childName, grade, academicYear, dateOfBirth, schoolName, 
                 status, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['parentType'], data['schoolType'], data['firstName'],
                data['mobile'], data['email'], data['city'], data['childName'],
                data['grade'], data['academicYear'], data['dateOfBirth'],
                data['schoolName'], data['status'], data['source']
            ))
        
        self.conn.commit()
        print(f"✅ Added {len(sample_data)} sample records")

def main():
    """Main function to run the data viewer"""
    viewer = SimpleSQLiteViewer()
    
    if not viewer.connect():
        return
    
    try:
        print("\n🎯 Simple SQLite Data Viewer for Chat Inquiries")
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
            print("5. Add sample data")
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
                viewer.add_sample_data()
            
            elif choice == '6':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    finally:
        viewer.disconnect()

if __name__ == "__main__":
    main()
