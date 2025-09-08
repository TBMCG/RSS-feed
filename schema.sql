-- TBMCG News Dashboard Database Schema
-- PostgreSQL

-- Users table (synced from Azure AD)
CREATE TABLE users (
    id UUID PRIMARY KEY,                    -- Azure AD Object ID
    email VARCHAR(255) UNIQUE NOT NULL,     -- User email
    name VARCHAR(255) NOT NULL,             -- Display name
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Feed categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6366f1',     -- Hex color
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- RSS feeds
CREATE TABLE feeds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    enabled BOOLEAN DEFAULT TRUE,
    refresh_interval INTEGER DEFAULT 60,    -- Minutes
    last_updated TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT feeds_url_unique UNIQUE(url)
);

-- User roles from Azure AD (cached locally)
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    role_name VARCHAR(50) NOT NULL,         -- 'admin', 'editor', 'viewer'
    assigned_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT user_roles_unique UNIQUE(user_id, role_name)
);

-- Feed articles cache (optional - for performance)
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    feed_id INTEGER REFERENCES feeds(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT articles_url_unique UNIQUE(feed_id, url)
);

-- Default categories
INSERT INTO categories (name, color, description) VALUES
('Technology', '#6366f1', 'Technology and software news'),
('Business', '#0ea5e9', 'Business and industry news'),
('Finance', '#10b981', 'Financial markets and economics'),
('Industry News', '#f59e0b', 'Industry-specific updates'),
('Startups', '#8b5cf6', 'Startup and entrepreneurship news');

-- Indexes for performance
CREATE INDEX idx_feeds_category ON feeds(category_id);
CREATE INDEX idx_feeds_enabled ON feeds(enabled);
CREATE INDEX idx_articles_feed ON articles(feed_id);
CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_user_roles_user ON user_roles(user_id);