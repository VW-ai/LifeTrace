-- Migration 2: Add Performance Indexes
-- Created: 2025-08-31T12:00:00

-- Additional indexes for common query patterns and performance optimization

-- Raw activities performance indexes
CREATE INDEX IF NOT EXISTS idx_raw_activities_source_date ON raw_activities(source, date DESC);
CREATE INDEX IF NOT EXISTS idx_raw_activities_duration ON raw_activities(duration_minutes DESC);
CREATE INDEX IF NOT EXISTS idx_raw_activities_updated_at ON raw_activities(updated_at DESC);

-- Processed activities performance indexes  
CREATE INDEX IF NOT EXISTS idx_processed_activities_duration ON processed_activities(total_duration_minutes DESC);
CREATE INDEX IF NOT EXISTS idx_processed_activities_date_time ON processed_activities(date, time);

-- Tags performance indexes
CREATE INDEX IF NOT EXISTS idx_tags_created_at ON tags(created_at DESC);

-- Activity tags performance indexes
CREATE INDEX IF NOT EXISTS idx_activity_tags_combined ON activity_tags(processed_activity_id, tag_id, confidence_score);

-- User sessions performance indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_type_status ON user_sessions(session_type, status);
CREATE INDEX IF NOT EXISTS idx_user_sessions_date_range ON user_sessions(start_time, end_time);

-- Tag generations performance indexes
CREATE INDEX IF NOT EXISTS idx_tag_generations_ratio ON tag_generations(tag_event_ratio);

-- DOWN
-- Remove the performance indexes

DROP INDEX IF EXISTS idx_raw_activities_source_date;
DROP INDEX IF EXISTS idx_raw_activities_duration;
DROP INDEX IF EXISTS idx_raw_activities_updated_at;
DROP INDEX IF EXISTS idx_processed_activities_duration;
DROP INDEX IF EXISTS idx_processed_activities_date_time;
DROP INDEX IF EXISTS idx_tags_created_at;
DROP INDEX IF EXISTS idx_activity_tags_combined;
DROP INDEX IF EXISTS idx_user_sessions_type_status;
DROP INDEX IF EXISTS idx_user_sessions_date_range;
DROP INDEX IF EXISTS idx_tag_generations_ratio;