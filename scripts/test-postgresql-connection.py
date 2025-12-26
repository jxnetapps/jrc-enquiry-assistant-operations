#!/usr/bin/env python3
"""
Test PostgreSQL Connection Script
This script tests the PostgreSQL connection to identify issues
"""

import asyncio
import asyncpg
import psycopg2
from urllib.parse import urlparse
import socket

def test_dns_resolution(hostname):
    """Test if hostname can be resolved"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"+ DNS Resolution: {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"- DNS Resolution failed: {e}")
        return False

def test_port_connectivity(hostname, port):
    """Test if port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"+ Port {port} is accessible on {hostname}")
            return True
        else:
            print(f"- Port {port} is not accessible on {hostname}")
            return False
    except Exception as e:
        print(f"- Port connectivity test failed: {e}")
        return False

async def test_asyncpg_connection(connection_uri):
    """Test asyncpg connection"""
    try:
        conn = await asyncpg.connect(connection_uri)
        await conn.execute("SELECT 1")
        await conn.close()
        print("+ AsyncPG connection successful")
        return True
    except Exception as e:
        print(f"- AsyncPG connection failed: {e}")
        return False

def test_psycopg2_connection(connection_uri):
    """Test psycopg2 connection"""
    try:
        conn = psycopg2.connect(connection_uri)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        print("+ Psycopg2 connection successful")
        return True
    except Exception as e:
        print(f"- Psycopg2 connection failed: {e}")
        return False

def parse_connection_uri(uri):
    """Parse PostgreSQL connection URI"""
    try:
        parsed = urlparse(uri)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path[1:] if parsed.path else 'postgres'
        }
    except Exception as e:
        print(f"- Failed to parse connection URI: {e}")
        return None

async def main():
    """Main test function"""
    print("=== PostgreSQL Connection Test ===")
    print()
    
    # Get connection URI from config
    try:
        from config import Config
        connection_uri = Config.POSTGRESQL_CONNECTION_URI
        print(f"Testing connection: {connection_uri}")
        print()
    except Exception as e:
        print(f"Failed to get connection URI: {e}")
        return
    
    # Parse connection details
    conn_details = parse_connection_uri(connection_uri)
    if not conn_details:
        return
    
    print("Connection Details:")
    print(f"  Host: {conn_details['host']}")
    print(f"  Port: {conn_details['port']}")
    print(f"  User: {conn_details['user']}")
    print(f"  Database: {conn_details['database']}")
    print()
    
    # Test DNS resolution
    print("1. Testing DNS Resolution...")
    dns_ok = test_dns_resolution(conn_details['host'])
    print()
    
    # Test port connectivity
    print("2. Testing Port Connectivity...")
    port_ok = test_port_connectivity(conn_details['host'], conn_details['port'])
    print()
    
    # Test asyncpg connection
    print("3. Testing AsyncPG Connection...")
    asyncpg_ok = await test_asyncpg_connection(connection_uri)
    print()
    
    # Test psycopg2 connection
    print("4. Testing Psycopg2 Connection...")
    psycopg2_ok = test_psycopg2_connection(connection_uri)
    print()
    
    # Summary
    print("=== Test Results ===")
    tests = [
        ("DNS Resolution", dns_ok),
        ("Port Connectivity", port_ok),
        ("AsyncPG Connection", asyncpg_ok),
        ("Psycopg2 Connection", psycopg2_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ PostgreSQL connection is working correctly!")
    else:
        print("\n✗ PostgreSQL connection has issues.")
        print("\nRecommendations:")
        if not dns_ok:
            print("- Check internet connection and DNS settings")
        if not port_ok:
            print("- Check firewall settings and network connectivity")
        if not (asyncpg_ok or psycopg2_ok):
            print("- Check PostgreSQL credentials and database permissions")
        print("- Consider using SQLite mode for development")

if __name__ == "__main__":
    asyncio.run(main())

