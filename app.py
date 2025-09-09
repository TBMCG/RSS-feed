import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from functools import wraps
import requests
try:
    import feedparser
except ImportError:
    import rss_parser as feedparser
from datetime import datetime, timedelta
import json
import msal
import jwt
from config import Config

# Removed db_retry function - no longer needed with proper IP whitelisting

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize CORS
    allowed_origins = [
        'http://localhost:5000',
        'https://tbmcg-news-dashboard.onrender.com'
    ]
    CORS(app, 
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         resources={
             r"/static/*": {"origins": "*"},  # Allow static files from any origin
             r"/api/*": {"origins": allowed_origins}
         })
    
    # Initialize Flask-Session
    Session(app)
    
    # Initialize SQLAlchemy with engine options
    from models import db, User, Category, Feed, UserRole, Article, Roles
    db.init_app(app)
    
    # Initialize MSAL app
    msal_app = msal.ConfidentialClientApplication(
        app.config['CLIENT_ID'],
        authority=app.config['AUTHORITY'],
        client_credential=app.config['CLIENT_SECRET']
    )
    
    def is_allowed_domain(email):
        """Check if user's email domain is allowed"""
        if not email:
            return False
        domain = email.split('@')[-1].lower()
        return domain in app.config['ALLOWED_DOMAINS']
    
    def get_user_roles_from_token(token_claims):
        """Extract roles from Azure AD token claims"""
        roles = []
        
        # Debug: Print all token claims to understand what we're receiving
        print(f"DEBUG: All token claims: {token_claims}")
        
        # Azure AD roles can be in 'roles' claim (for app roles) or 'groups' claim
        if 'roles' in token_claims:
            roles = token_claims['roles']
            print(f"DEBUG: Found roles in token: {roles}")
        elif 'groups' in token_claims:
            # Map group IDs to role names if using groups
            roles = token_claims['groups']
            print(f"DEBUG: Found groups in token: {roles}")
        else:
            print("DEBUG: No roles or groups found in token claims")
            
        return roles
    
    def sync_user_to_db(user_claims, azure_roles):
        """Sync user from Azure AD to local database"""
        user_id = user_claims.get('oid', '')
        email = user_claims.get('preferred_username', '')
        name = user_claims.get('name', '')
        
        print(f"DEBUG: Syncing user {email} (ID: {user_id}) with roles: {azure_roles}")
        
        # Find or create user
        user = db.session.get(User, user_id)
        if not user:
            user = User(id=user_id, email=email, name=name)
            db.session.add(user)
            print(f"DEBUG: Created new user: {email}")
        else:
            user.email = email
            user.name = name
            user.updated_at = datetime.utcnow()
            print(f"DEBUG: Updated existing user: {email}")
        
        # Sync roles from Azure AD
        # Clear existing roles
        deleted_count = UserRole.query.filter_by(user_id=user_id).delete()
        print(f"DEBUG: Cleared {deleted_count} existing roles for user")
        
        # Add new roles from Azure AD
        roles_added = 0
        for role_name in azure_roles:
            if role_name in Roles.ALL_ROLES:
                user_role = UserRole(user_id=user_id, role_name=role_name)
                db.session.add(user_role)
                roles_added += 1
                print(f"DEBUG: Added role '{role_name}' for user {email}")
            else:
                print(f"DEBUG: Skipped unknown role '{role_name}' for user {email}")
        
        print(f"DEBUG: Added {roles_added} roles total")
        
        db.session.commit()
        return user

    def get_user_for_template(session_user):
        """Get user object for template rendering with proper role handling"""
        if not session_user:
            return None
            
        user_id = session_user.get('oid')
        user_email = session_user.get('preferred_username', '')
        
        print(f"DEBUG: Getting user for template - ID: {user_id}, Email: {user_email}")
        
        if not user_id:
            return session_user
            
        # Fetch the database user object for proper role handling
        db_user = db.session.get(User, user_id)
        
        if db_user:
            print(f"DEBUG: Found database user: {db_user.email}")
            print(f"DEBUG: User roles: {[role.role_name for role in db_user.roles]}")
            print(f"DEBUG: Can manage feeds: {db_user.can_manage_feeds}")
            
            # Add session data as attributes for template compatibility
            db_user.session_name = session_user.get('name', db_user.name)
            db_user.session_email = session_user.get('preferred_username', db_user.email)
            return db_user
        else:
            print(f"DEBUG: Database user not found for ID: {user_id}")
            # If database user not found, create a fallback object with basic admin check
            class FallbackUser:
                def __init__(self, session_data):
                    self.session_data = session_data
                    self.name = session_data.get('name', '')
                    self.session_name = session_data.get('name', '')
                    self.email = session_data.get('preferred_username', '')
                    self.session_email = session_data.get('preferred_username', '')
                
                def get(self, key, default=None):
                    return self.session_data.get(key, default)
                
                @property
                def can_manage_feeds(self):
                    # No roles available in fallback mode - deny access
                    return False
                
                def has_role(self, role_name):
                    # No roles available in fallback mode
                    return False
            
            return FallbackUser(session_user)
    
    def generate_auth_token(user_claims):
        """Generate JWT token for cross-domain authentication"""
        payload = {
            'user_id': user_claims.get('oid'),
            'email': user_claims.get('preferred_username'),
            'name': user_claims.get('name'),
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    def verify_auth_token(token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
    
    def get_user_from_token():
        """Get user info from JWT token in Authorization header"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        payload = verify_auth_token(token)
        if not payload:
            print(f"DEBUG: Invalid or expired JWT token")
            return None
            
        print(f"DEBUG: Valid JWT token for user: {payload.get('email')}")
        return payload
    
    def login_required(f):
        """Decorator to require authentication (supports both session and JWT token)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First try session-based auth (for local development and traditional web flow)
            if session.get('user'):
                return f(*args, **kwargs)
            
            # Then try token-based auth (for cross-domain API calls)
            token_user = get_user_from_token()
            if token_user:
                # Set session for compatibility with existing code
                session['user'] = {
                    'oid': token_user.get('user_id'),
                    'preferred_username': token_user.get('email'),
                    'name': token_user.get('name')
                }
                return f(*args, **kwargs)
            
            # For API endpoints, return JSON error instead of redirect
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            
            return redirect(url_for('login', next=request.url))
        return decorated_function

    def requires_tbmcg_email(f):
        """Decorator to ensure user has @tbmcg.com email"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get('user')
            if not user:
                return redirect(url_for('login'))
            
            if not is_allowed_domain(user.get('preferred_username', '')):
                flash('Access denied. Only @tbmcg.com email addresses are allowed.', 'error')
                return redirect(url_for('logout'))
            
            return f(*args, **kwargs)
        return decorated_function

    def requires_role(role_name):
        """Decorator to require specific role"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_id = session.get('user', {}).get('oid')
                if not user_id:
                    return redirect(url_for('login'))
                
                user = db.session.get(User, user_id)
                if not user or not user.has_role(role_name):
                    flash(f'Access denied. {role_name} role required.', 'error')
                    return redirect(url_for('index'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def requires_feed_management(f):
        """Decorator to ensure user can manage feeds"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user', {}).get('oid')
            if not user_id:
                return redirect(url_for('login'))
            
            user = db.session.get(User, user_id)
            if not user:
                return redirect(url_for('login'))
            
            # Check if user has admin or editor role
            user_roles = user.get_roles()
            can_manage = any(Roles.can_manage_feeds(role) for role in user_roles)
            
            if not can_manage:
                flash('You do not have permission to manage feeds.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function

    @app.context_processor
    def inject_user():
        """Inject user info into all templates"""
        user_data = session.get('user')
        if user_data:
            user_id = user_data.get('oid')
            if user_id:
                db_user = db.session.get(User, user_id)
                if db_user:
                    user_data['roles'] = db_user.get_roles()
                    user_data['can_manage_feeds'] = any(Roles.can_manage_feeds(role) for role in user_data['roles'])
        return dict(user=user_data)

    def init_default_data():
        """Initialize default categories if they don't exist"""
        with app.app_context():
            try:
                # Create all tables first
                db.create_all()
                print("Database tables created/verified successfully")
                
                # Check if categories exist
                if Category.query.count() == 0:
                    default_categories = [
                        ('Technology', '#6366f1', 'Technology and software news'),
                        ('Business', '#0ea5e9', 'Business and industry news'),
                        ('Finance', '#10b981', 'Financial markets and economics'),
                        ('Industry News', '#f59e0b', 'Industry-specific updates'),
                        ('Startups', '#8b5cf6', 'Startup and entrepreneurship news')
                    ]
                    
                    for name, color, description in default_categories:
                        category = Category(name=name, color=color, description=description)
                        db.session.add(category)
                    
                    db.session.commit()
                    print("Default categories created")
            except Exception as e:
                print(f"Database initialization error: {e}")
                # Don't fail the entire app if database init fails
                pass

    # Routes
    @app.route('/')
    @login_required
    @requires_tbmcg_email
    def index():
        """Main dashboard page"""
        session_user = session.get('user')
        user_for_template = get_user_for_template(session_user)
        return render_template('dashboard.html', user=user_for_template)

    @app.route('/login')
    def login():
        """Initiate Microsoft OAuth login"""
        # Always clear session completely to avoid redirect loops
        session.clear()
        
        # Use dynamic redirect URI based on current host
        redirect_uri = url_for('authorized', _external=True)
        flow = msal_app.initiate_auth_code_flow(
            scopes=app.config['SCOPE'],
            redirect_uri=redirect_uri
        )
        
        if 'error' in flow:
            flash(f'Authentication error: {flow.get("error_description", "Unknown error")}', 'error')
            return render_template('error.html', error=flow)
        
        session['flow'] = flow
        return redirect(flow['auth_uri'])

    @app.route(app.config['REDIRECT_PATH'])
    def authorized():
        """Handle Microsoft OAuth callback"""
        try:
            # Get the stored flow from session
            flow = session.get('flow', {})
            if not flow:
                flash('Authentication session expired. Please try again.', 'error')
                return redirect(url_for('login'))
            
            # Complete the OAuth flow
            result = msal_app.acquire_token_by_auth_code_flow(
                flow,
                request.args
            )
            
            if 'error' in result:
                flash(f'Authentication failed: {result.get("error_description", "Unknown error")}', 'error')
                return render_template('error.html', error=result)
            
            # Extract user information
            user_claims = result.get('id_token_claims')
            if not user_claims:
                flash('Failed to retrieve user information', 'error')
                return redirect(url_for('login'))
            
            email = user_claims.get('preferred_username', '')
            
            # Check domain access
            if not is_allowed_domain(email):
                session.clear()
                flash('Access denied. Only @tbmcg.com email addresses are allowed.', 'error')
                return render_template('error.html', error={'error': 'unauthorized_domain', 'error_description': 'Only @tbmcg.com email addresses are allowed.'})
            
            # Extract roles from Azure AD token
            azure_roles = get_user_roles_from_token(user_claims)
            
            # Sync user to database
            db_user = sync_user_to_db(user_claims, azure_roles)
            
            # Store user session
            session['user'] = user_claims
            session['tokens'] = result
            session.permanent = True
            
            # Clear flow from session
            session.pop('flow', None)
            
            flash(f'Welcome, {db_user.name or email}!', 'success')
            
            # Redirect to index page after successful authentication
            return redirect(url_for('index'))
            
        except Exception as e:
            session.clear()
            flash(f'Authentication error: {str(e)}', 'error')
            return redirect(url_for('login'))

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        """Log out the user"""
        session.clear()
        
        # Clear MSAL token cache if it exists
        if hasattr(msal_app, 'token_cache') and msal_app.token_cache:
            try:
                accounts = msal_app.token_cache.find(msal.TokenCache.CredentialType.ACCOUNT)
                for account in accounts:
                    msal_app.token_cache.remove_account(account)
            except:
                # Ignore errors in cache clearing
                pass
        
        # Azure AD logout URL with proper Render redirect
        azure_logout_url = (
            f"{app.config['AUTHORITY']}/oauth2/v2.0/logout"
            f"?post_logout_redirect_uri=https://tbmcg-news-dashboard.onrender.com/logout-complete"
        )
        
        # Handle API request (POST) vs web request (GET)
        if request.method == 'POST' or request.headers.get('Content-Type') == 'application/json':
            # Return JSON response for API calls from Netlify frontend
            return jsonify({
                'success': True,
                'message': 'Logged out successfully',
                'azure_logout_url': azure_logout_url
            })
        else:
            # Traditional web logout with flash message and redirect
            flash('You have been logged out.', 'info')
            return redirect(azure_logout_url)

    @app.route('/clear-session')
    def clear_session():
        """Clear session - useful for debugging"""
        session.clear()
        return "Session cleared. <a href='/'>Go to home</a>"
    
    @app.route('/api/auth/status')
    def auth_status():
        """Check authentication status for debugging"""
        user_session = session.get('user')
        token_user = get_user_from_token()
        
        return jsonify({
            'session_user': bool(user_session),
            'session_details': {
                'user_id': user_session.get('oid') if user_session else None,
                'email': user_session.get('preferred_username') if user_session else None,
                'name': user_session.get('name') if user_session else None
            } if user_session else None,
            'token_user': bool(token_user),
            'token_details': token_user if token_user else None,
            'auth_header': request.headers.get('Authorization', 'Not provided')
        })

    @app.route('/api/feeds', methods=['GET', 'POST'])
    @login_required
    @requires_tbmcg_email
    @requires_feed_management
    def handle_feeds():
        """Handle GET and POST requests for feeds"""
        if request.method == 'POST':
            # Add new feed
            data = request.json
            user_id = session.get('user', {}).get('oid')
            
            feed = Feed(
                name=data['name'],
                url=data['url'],
                category_id=data['category_id'],
                created_by=user_id
            )
            
            try:
                db.session.add(feed)
                db.session.commit()
                return jsonify({
                    'message': 'Feed added successfully',
                    'feed': {
                        'id': feed.id,
                        'name': feed.name,
                        'url': feed.url,
                        'category_id': feed.category_id,
                        'enabled': feed.enabled
                    }
                }), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 400
        
        # GET request - return all feeds organized by category
        categories = Category.query.all()
        result = []
        
        for category in categories:
            cat_data = {
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'feeds': []
            }
            
            for feed in category.feeds:
                if feed.enabled:
                    cat_data['feeds'].append({
                        'id': feed.id,
                        'name': feed.name,
                        'url': feed.url,
                        'enabled': feed.enabled
                    })
            
            result.append(cat_data)
        
        return jsonify(result)

    @app.route('/api/articles')
    @login_required
    @requires_tbmcg_email
    def get_articles():
        """Fetch and return articles from all enabled feeds"""
        category_id = request.args.get('category_id')
        sort_order = request.args.get('sort', 'newest')  # Default to newest first
        
        if category_id:
            feeds = Feed.query.filter_by(category_id=category_id, enabled=True).all()
        else:
            feeds = Feed.query.filter_by(enabled=True).all()
        
        articles = []
        for feed in feeds:
            try:
                parsed_feed = feedparser.parse(feed.url)
                
                for entry in parsed_feed.entries[:10]:  # Limit to 10 articles per feed
                    articles.append({
                        'title': entry.get('title', 'No title'),
                        'link': entry.get('link', ''),
                        'description': entry.get('summary', entry.get('description', '')),
                        'published': entry.get('published', ''),
                        'feed_name': feed.name,
                        'feed_id': feed.id,
                        'category': feed.category.name if feed.category else None
                    })
            except Exception as e:
                print(f"Error fetching feed {feed.name}: {e}")
                continue
        
        # Sort articles by published date based on sort_order parameter
        if sort_order == 'oldest':
            articles.sort(key=lambda x: x.get('published', ''))  # Oldest first
        else:
            articles.sort(key=lambda x: x.get('published', ''), reverse=True)  # Newest first (default)
        
        return jsonify(articles)

    @app.route('/manage')
    @login_required
    @requires_tbmcg_email
    @requires_feed_management
    def manage_feeds():
        """Feed management page"""
        session_user = session.get('user')
        user_for_template = get_user_for_template(session_user)
        return render_template('manage.html', user=user_for_template)
    
    @app.route('/api/feeds/add', methods=['POST'])
    @login_required
    @requires_tbmcg_email
    @requires_feed_management
    def add_feed():
        """Add a new feed"""
        data = request.json
        user_id = session.get('user', {}).get('oid')
        
        # Check if feed URL already exists
        existing_feed = Feed.query.filter_by(url=data['url']).first()
        if existing_feed:
            return jsonify({'error': 'Feed URL already exists'}), 400
        
        feed = Feed(
            name=data['name'],
            url=data['url'],
            category_id=data.get('category_id'),
            created_by=user_id
        )
        
        db.session.add(feed)
        db.session.commit()
        
        return jsonify({'message': 'Feed added successfully', 'id': feed.id})
    
    @app.route('/api/feeds/<int:feed_id>/toggle', methods=['POST'])
    @login_required
    @requires_tbmcg_email
    @requires_feed_management
    def toggle_feed(feed_id):
        """Enable/disable a feed"""
        feed = Feed.query.get_or_404(feed_id)
        feed.enabled = not feed.enabled
        db.session.commit()
        
        return jsonify({'enabled': feed.enabled})
    
    @app.route('/api/feeds/<int:feed_id>', methods=['DELETE'])
    @login_required
    @requires_tbmcg_email
    @requires_role(Roles.ADMIN)
    def delete_feed(feed_id):
        """Delete a feed (admin only)"""
        feed = Feed.query.get_or_404(feed_id)
        db.session.delete(feed)
        db.session.commit()
        
        return jsonify({'message': 'Feed deleted successfully'})
    
    @app.route('/api/categories', methods=['GET'])
    @login_required
    @requires_tbmcg_email
    def get_categories():
        """Get all categories"""
        categories = Category.query.all()
        return jsonify([{
            'id': cat.id,
            'name': cat.name,
            'color': cat.color,
            'description': cat.description
        } for cat in categories])
    
    @app.route('/api/categories', methods=['POST'])
    @login_required
    @requires_tbmcg_email
    @requires_role(Roles.ADMIN)
    def add_category():
        """Add a new category (admin only)"""
        data = request.json
        user_id = session.get('user', {}).get('oid')
        
        # Check if category already exists
        existing = Category.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Category already exists'}), 400
        
        category = Category(
            name=data['name'],
            color=data.get('color', '#6366f1'),
            description=data.get('description', ''),
            created_by=user_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category added successfully',
            'id': category.id,
            'name': category.name,
            'color': category.color
        })
    
    @app.route('/api/categories/<int:category_id>', methods=['PUT'])
    @login_required
    @requires_tbmcg_email
    @requires_role(Roles.ADMIN)
    def update_category(category_id):
        """Update a category (admin only)"""
        category = Category.query.get_or_404(category_id)
        data = request.json
        
        if 'name' in data:
            # Check if new name conflicts with another category
            existing = Category.query.filter_by(name=data['name']).first()
            if existing and existing.id != category_id:
                return jsonify({'error': 'Category name already exists'}), 400
            category.name = data['name']
        
        if 'color' in data:
            category.color = data['color']
        
        if 'description' in data:
            category.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Category updated successfully',
            'id': category.id,
            'name': category.name,
            'color': category.color
        })
    
    @app.route('/api/categories/<int:category_id>', methods=['DELETE'])
    @login_required
    @requires_tbmcg_email
    @requires_role(Roles.ADMIN)
    def delete_category(category_id):
        """Delete a category (admin only)"""
        category = Category.query.get_or_404(category_id)
        
        # Check if category has feeds
        if category.feeds:
            return jsonify({'error': 'Cannot delete category with feeds. Move or delete feeds first.'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'Category deleted successfully'})
    
    @app.route('/api/feeds/<int:feed_id>', methods=['PUT'])
    @login_required
    @requires_tbmcg_email
    @requires_feed_management
    def update_feed(feed_id):
        """Update a feed"""
        feed = Feed.query.get_or_404(feed_id)
        data = request.json
        
        if 'name' in data:
            feed.name = data['name']
        
        if 'url' in data:
            # Check if URL already exists
            existing = Feed.query.filter_by(url=data['url']).first()
            if existing and existing.id != feed_id:
                return jsonify({'error': 'Feed URL already exists'}), 400
            feed.url = data['url']
        
        if 'category_id' in data:
            feed.category_id = data['category_id']
        
        if 'enabled' in data:
            feed.enabled = data['enabled']
        
        if 'refresh_interval' in data:
            feed.refresh_interval = data['refresh_interval']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Feed updated successfully',
            'id': feed.id,
            'name': feed.name,
            'url': feed.url
        })
    
    @app.route('/api/user/info')
    @login_required
    def user_info():
        """Get current user info including roles"""
        user_id = session.get('user', {}).get('oid')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'roles': user.get_roles(),
            'can_manage_feeds': any(Roles.can_manage_feeds(role) for role in user.get_roles()),
            'can_manage_categories': any(Roles.can_manage_categories(role) for role in user.get_roles()),
            'can_manage_users': any(Roles.can_manage_users(role) for role in user.get_roles())
        })
    
    @app.route('/api/user')
    @login_required  
    def api_user():
        """Get current user info for frontend authentication checks"""
        user_id = session.get('user', {}).get('oid')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_roles = user.get_roles()
        primary_role = 'Admin' if 'admin' in user_roles else ('Editor' if 'editor' in user_roles else 'Viewer')
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': primary_role,  # Frontend expects this specific format
                'roles': user_roles,
                'can_manage_feeds': any(Roles.can_manage_feeds(role) for role in user_roles)
            }
        })
    
    # Initialize default data
    init_default_data()
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)