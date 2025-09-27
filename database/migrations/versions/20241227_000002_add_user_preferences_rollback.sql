-- Rollback for migration: 20241227_000002_add_user_preferences
-- Description: Rollback user preferences and settings
-- Created: 2024-12-27T00:00:02Z

-- Drop trigger
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;

-- Drop tables
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS user_preferences;
