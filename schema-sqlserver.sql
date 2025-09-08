-- TBMCG News Dashboard Database Schema
-- SQL Server / Azure SQL Database

-- Users table (synced from Azure AD)
CREATE TABLE users (
    id NVARCHAR(36) PRIMARY KEY,               -- Azure AD Object ID (UUID as string)
    email NVARCHAR(255) UNIQUE NOT NULL,       -- User email
    name NVARCHAR(255) NOT NULL,               -- Display name
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Feed categories
CREATE TABLE categories (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    color NVARCHAR(7) DEFAULT '#6366f1',       -- Hex color
    description NTEXT,
    created_by NVARCHAR(36) REFERENCES users(id),
    created_at DATETIME2 DEFAULT GETUTCDATE()
);

-- RSS feeds
CREATE TABLE feeds (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    url NTEXT NOT NULL,
    category_id INT REFERENCES categories(id),
    enabled BIT DEFAULT 1,
    refresh_interval INT DEFAULT 60,           -- Minutes
    last_updated DATETIME2,
    created_by NVARCHAR(36) REFERENCES users(id),
    created_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Unique constraint on URL (separate from table definition for NTEXT)
CREATE UNIQUE INDEX IX_feeds_url ON feeds(url) 
WHERE url IS NOT NULL;

-- User roles from Azure AD (cached locally)
CREATE TABLE user_roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id NVARCHAR(36) REFERENCES users(id),
    role_name NVARCHAR(50) NOT NULL,           -- 'admin', 'editor', 'viewer'
    assigned_at DATETIME2 DEFAULT GETUTCDATE(),
    
    CONSTRAINT user_roles_unique UNIQUE(user_id, role_name)
);

-- Feed articles cache (optional - for performance)
CREATE TABLE articles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    feed_id INT REFERENCES feeds(id) ON DELETE CASCADE,
    title NTEXT NOT NULL,
    url NTEXT NOT NULL,
    description NTEXT,
    published_at DATETIME2,
    fetched_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Unique constraint on article URL per feed
CREATE UNIQUE INDEX IX_articles_feed_url ON articles(feed_id, url)
WHERE url IS NOT NULL;

-- Default categories
INSERT INTO categories (name, color, description) VALUES
('Technology', '#6366f1', 'Technology and software news'),
('Business', '#0ea5e9', 'Business and industry news'),
('Finance', '#10b981', 'Financial markets and economics'),
('Industry News', '#f59e0b', 'Industry-specific updates'),
('Startups', '#8b5cf6', 'Startup and entrepreneurship news');

-- Indexes for performance
CREATE INDEX IX_feeds_category ON feeds(category_id);
CREATE INDEX IX_feeds_enabled ON feeds(enabled);
CREATE INDEX IX_articles_feed ON articles(feed_id);
CREATE INDEX IX_articles_published ON articles(published_at DESC);
CREATE INDEX IX_user_roles_user ON user_roles(user_id);