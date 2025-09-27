-- Rollback for migration: 20241227_000001_initial_schema
-- Description: Rollback initial database schema
-- Created: 2024-12-27T00:00:01Z

-- Drop triggers first
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_chat_inquiry_updated_at ON chat_inquiry_information;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in reverse order (due to foreign key constraints)
DROP TABLE IF EXISTS embeddings;
DROP TABLE IF EXISTS crawled_pages;
DROP TABLE IF EXISTS crawling_sessions;
DROP TABLE IF EXISTS chat_inquiry_information;
DROP TABLE IF EXISTS users;

-- Drop extension (optional - only if not used by other tables)
-- DROP EXTENSION IF EXISTS vector;
