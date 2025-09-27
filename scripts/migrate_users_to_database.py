"""
Migration script to create default users in PostgreSQL database.
This script migrates users from the old in-memory UserStore to the new database system.
"""

import asyncio
import logging
from database.user_repository import user_repository
from models.user_models import UserCreate, UserRole, UserStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default users from the old UserStore
DEFAULT_USERS = [
    {
        "username": "admin",
        "email": "admin@webchatbot.com",
        "password": "Wildcat@007",
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "status": UserStatus.ACTIVE
    },
    {
        "username": "edifyho",
        "email": "edifyho@webchatbot.com",
        "password": "Wildcat@007",
        "full_name": "Edify HO User",
        "role": UserRole.USER,
        "status": UserStatus.ACTIVE
    },
    {
        "username": "edifykids",
        "email": "edifykids@webchatbot.com",
        "password": "Wildcat@007",
        "full_name": "Edify Kids User",
        "role": UserRole.USER,
        "status": UserStatus.ACTIVE
    },
    {
        "username": "drsis",
        "email": "drsis@webchatbot.com",
        "password": "Wildcat@007",
        "full_name": "DRSIS User",
        "role": UserRole.USER,
        "status": UserStatus.ACTIVE
    }
]

async def migrate_users():
    """Migrate default users to the database."""
    try:
        logger.info("Starting user migration...")
        
        # Check if users already exist
        existing_users = await user_repository.list_users(0, 100)
        if existing_users:
            logger.info(f"Found {len(existing_users)} existing users. Skipping migration.")
            return
        
        # Create default users
        created_count = 0
        for user_data in DEFAULT_USERS:
            try:
                user_create = UserCreate(**user_data)
                user_id = await user_repository.create_user(user_create)
                logger.info(f"Created user: {user_data['username']} -> {user_id}")
                created_count += 1
            except ValueError as e:
                logger.warning(f"User {user_data['username']} already exists: {e}")
            except Exception as e:
                logger.error(f"Error creating user {user_data['username']}: {e}")
        
        logger.info(f"Migration completed. Created {created_count} users.")
        
        # Display user statistics
        stats = await user_repository.get_user_stats()
        logger.info(f"Database now contains:")
        logger.info(f"  Total users: {stats.get('total_users', 0)}")
        logger.info(f"  Admin users: {stats.get('admin_users', 0)}")
        logger.info(f"  Regular users: {stats.get('regular_users', 0)}")
        logger.info(f"  Active users: {stats.get('active_users', 0)}")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

async def verify_migration():
    """Verify that the migration was successful."""
    try:
        logger.info("Verifying migration...")
        
        # Test authentication for each user
        for user_data in DEFAULT_USERS:
            user_id = await user_repository.authenticate_user(
                user_data['username'], 
                user_data['password']
            )
            if user_id:
                logger.info(f"✓ Authentication successful for {user_data['username']}")
            else:
                logger.error(f"✗ Authentication failed for {user_data['username']}")
        
        # Test user retrieval
        for user_data in DEFAULT_USERS:
            user = await user_repository.get_user_by_username(user_data['username'])
            if user:
                logger.info(f"✓ User retrieval successful for {user_data['username']}")
                logger.info(f"  User ID: {user.user_id}")
                logger.info(f"  Role: {user.role}")
                logger.info(f"  Status: {user.status}")
            else:
                logger.error(f"✗ User retrieval failed for {user_data['username']}")
        
        logger.info("Migration verification completed.")
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise

async def main():
    """Main migration function."""
    try:
        # Check database connection
        if not await user_repository._is_connected():
            logger.error("PostgreSQL not connected. Please check your database connection.")
            return
        
        logger.info("PostgreSQL connected. Starting migration...")
        
        # Run migration
        await migrate_users()
        
        # Verify migration
        await verify_migration()
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
