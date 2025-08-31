-- SmartHistory Database Schema
-- This schema implements the data storage design from DESIGN.md
-- Supporting both raw activity data and processed activity aggregations

-- Schema versioning for migrations
CREATE TABLE IF NOT EXISTS schema_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL UNIQUE,
    description TEXT NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial version
INSERT OR IGNORE INTO schema_versions (version, description) 
VALUES (1, 'Initial schema with raw_activities, processed_activities, tags, and user_sessions');

-- Raw activity table - stores individual activity records from different sources
CREATE TABLE IF NOT EXISTS raw_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                    -- Date in YYYY-MM-DD format
    time TEXT,                             -- Time in HH:MM format (optional)
    duration_minutes INTEGER DEFAULT 0,    -- Duration in minutes
    details TEXT DEFAULT '',               -- Thorough summary of raw information
    source TEXT NOT NULL DEFAULT '',       -- Source: 'notion', 'google_calendar', etc.
    orig_link TEXT DEFAULT '',             -- Link to original information
    raw_data TEXT DEFAULT '{}',            -- JSON string of additional metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Processed activity table - aggregated and tagged activities
CREATE TABLE IF NOT EXISTS processed_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                    -- Date in YYYY-MM-DD format
    time TEXT,                             -- Time in HH:MM format (optional)
    total_duration_minutes INTEGER DEFAULT 0, -- Total duration across all raw activities
    combined_details TEXT DEFAULT '',      -- Combined details from raw activities
    raw_activity_ids TEXT DEFAULT '[]',    -- JSON array of raw activity IDs
    sources TEXT DEFAULT '[]',             -- JSON array of sources
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tags table - manages tag vocabulary and metadata
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,            -- Tag name (e.g., 'work', 'exercise')
    description TEXT DEFAULT '',           -- Optional tag description
    color TEXT,                           -- Optional color for UI display
    usage_count INTEGER DEFAULT 0,        -- Number of times this tag is used
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Activity tags - many-to-many relationship between processed activities and tags
CREATE TABLE IF NOT EXISTS activity_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processed_activity_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    confidence_score REAL DEFAULT 1.0,    -- AI confidence in tag assignment (0-1)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (processed_activity_id) REFERENCES processed_activities(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(processed_activity_id, tag_id)
);

-- User sessions - tracks processing runs and system state
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_type TEXT NOT NULL,           -- 'daily_processing', 'insights_generation', etc.
    status TEXT NOT NULL DEFAULT 'started', -- 'started', 'completed', 'failed'
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    metadata TEXT DEFAULT '{}',           -- JSON string with session details
    error_message TEXT,                   -- Error details if status is 'failed'
    processed_raw_count INTEGER DEFAULT 0,
    processed_activity_count INTEGER DEFAULT 0,
    tags_generated INTEGER DEFAULT 0
);

-- Tag generation history - tracks system-wide tag regeneration events
CREATE TABLE IF NOT EXISTS tag_generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generation_type TEXT NOT NULL,       -- 'system_wide', 'incremental', 'manual'
    trigger_reason TEXT,                 -- Why tag generation was triggered
    total_activities INTEGER DEFAULT 0,
    tags_created INTEGER DEFAULT 0,
    tags_updated INTEGER DEFAULT 0,
    tag_event_ratio REAL,               -- Ratio that triggered regeneration
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'          -- Additional generation context
);

-- Performance indexes for common query patterns

-- Indexes for raw_activities
CREATE INDEX IF NOT EXISTS idx_raw_activities_date ON raw_activities(date);
CREATE INDEX IF NOT EXISTS idx_raw_activities_source ON raw_activities(source);
CREATE INDEX IF NOT EXISTS idx_raw_activities_date_source ON raw_activities(date, source);
CREATE INDEX IF NOT EXISTS idx_raw_activities_created_at ON raw_activities(created_at);

-- Indexes for processed_activities  
CREATE INDEX IF NOT EXISTS idx_processed_activities_date ON processed_activities(date);
CREATE INDEX IF NOT EXISTS idx_processed_activities_created_at ON processed_activities(created_at);

-- Indexes for tags
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_tags_usage_count ON tags(usage_count DESC);

-- Indexes for activity_tags
CREATE INDEX IF NOT EXISTS idx_activity_tags_processed_activity ON activity_tags(processed_activity_id);
CREATE INDEX IF NOT EXISTS idx_activity_tags_tag ON activity_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_activity_tags_confidence ON activity_tags(confidence_score DESC);

-- Indexes for user_sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_type ON user_sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_user_sessions_status ON user_sessions(status);
CREATE INDEX IF NOT EXISTS idx_user_sessions_start_time ON user_sessions(start_time DESC);

-- Indexes for tag_generations
CREATE INDEX IF NOT EXISTS idx_tag_generations_type ON tag_generations(generation_type);
CREATE INDEX IF NOT EXISTS idx_tag_generations_created_at ON tag_generations(created_at DESC);

-- Triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_raw_activities_timestamp 
AFTER UPDATE ON raw_activities
BEGIN
    UPDATE raw_activities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_processed_activities_timestamp
AFTER UPDATE ON processed_activities  
BEGIN
    UPDATE processed_activities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_tags_timestamp
AFTER UPDATE ON tags
BEGIN
    UPDATE tags SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger to update tag usage count when activity_tags are inserted/deleted
CREATE TRIGGER IF NOT EXISTS increment_tag_usage
AFTER INSERT ON activity_tags
BEGIN
    UPDATE tags SET usage_count = usage_count + 1 WHERE id = NEW.tag_id;
END;

CREATE TRIGGER IF NOT EXISTS decrement_tag_usage
AFTER DELETE ON activity_tags  
BEGIN
    UPDATE tags SET usage_count = usage_count - 1 WHERE id = OLD.tag_id;
END;