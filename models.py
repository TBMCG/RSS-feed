from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_categories = db.relationship('Category', backref='creator', lazy=True)
    created_feeds = db.relationship('Feed', backref='creator', lazy=True)
    roles = db.relationship('UserRole', backref='user', lazy=True)
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(role.role_name == role_name for role in self.roles)
    
    def get_roles(self):
        """Get list of role names for this user"""
        return [role.role_name for role in self.roles]
    
    @property
    def can_manage_feeds(self):
        """Check if user can manage feeds"""
        return self.has_role(Roles.ADMIN) or self.has_role(Roles.EDITOR)
    
    @property 
    def can_manage_categories(self):
        """Check if user can manage categories"""
        return self.has_role(Roles.ADMIN)
    
    @property
    def can_manage_users(self):
        """Check if user can manage users"""
        return self.has_role(Roles.ADMIN)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6366f1')
    description = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feeds = db.relationship('Feed', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Feed(db.Model):
    __tablename__ = 'feeds'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(2000), nullable=False)  # Reduced from Text for unique constraint
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    enabled = db.Column(db.Boolean, default=True)
    refresh_interval = db.Column(db.Integer, default=60)  # Minutes
    last_updated = db.Column(db.DateTime)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    articles = db.relationship('Article', backref='feed', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('url', name='uq_feed_url'),
    )
    
    def __repr__(self):
        return f'<Feed {self.name}>'

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    role_name = db.Column(db.String(50), nullable=False)  # 'admin', 'editor', 'viewer'
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'role_name', name='user_roles_unique'),)
    
    def __repr__(self):
        return f'<UserRole {self.role_name} for {self.user_id}>'

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey('feeds.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(2000), nullable=False)  # Reduced from Text
    description = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('feed_id', 'url', name='uq_article_feed_url'),
    )
    
    def __repr__(self):
        return f'<Article {self.title[:50]}>'

# Role constants
class Roles:
    ADMIN = 'admin'
    EDITOR = 'editor' 
    VIEWER = 'viewer'
    
    ALL_ROLES = [ADMIN, EDITOR, VIEWER]
    
    @classmethod
    def can_manage_feeds(cls, role):
        return role in [cls.ADMIN, cls.EDITOR]
    
    @classmethod
    def can_manage_categories(cls, role):
        return role == cls.ADMIN
    
    @classmethod
    def can_manage_users(cls, role):
        return role == cls.ADMIN