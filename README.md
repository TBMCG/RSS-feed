# TBMCG News Dashboard

A secure, company-only RSS feed management dashboard built with Flask and Microsoft authentication. Designed for easy deployment and maintenance by TBMCG team members.

## Features

### 🔐 **Secure Access**
- **Microsoft OAuth Integration**: Single sign-on with company Microsoft accounts
- **Domain Restriction**: Only `@tbmcg.com` email addresses allowed
- **Role-based Permissions**: Specific users can manage feeds and categories

### 📰 **RSS Feed Management** 
- **Categorized Organization**: Organize feeds into folders (Technology, Business, Finance, etc.)
- **Real-time Feed Parsing**: Live RSS feed fetching and parsing
- **Enable/Disable Feeds**: Toggle feeds on/off without deletion
- **Import/Export**: Backup and restore feed configurations

### 🎨 **Modern Interface**
- **Material Design**: Clean, professional interface following company style guide
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Search**: Filter articles across all feeds instantly
- **Loading States**: Smooth user experience with progress indicators

### ⚡ **Easy Maintenance**
- **Self-contained**: All dependencies included, no external services required
- **SQLite Database**: Simple file-based database, no complex setup
- **Environment Configuration**: Easy setup with `.env` file
- **Docker Ready**: Optional containerization for easy deployment

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Microsoft Azure account (for OAuth app registration)

### Option A: Automated Setup (Recommended)

```bash
git clone <repository-url>
cd company-news-dashboard

# Run automated setup script
python setup.py
```

The script will:
- ✅ Check Python version
- 📦 Create virtual environment
- 📚 Install all dependencies  
- 📝 Create .env file from template

Then follow the displayed instructions to configure Azure credentials.

### Option B: Manual Setup

### 1. Clone and Setup Python Environment

```bash
git clone <repository-url>
cd company-news-dashboard

# Create virtual environment (isolates Python packages from system)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify you're in the virtual environment (should show venv path)
which python  # On macOS/Linux
where python   # On Windows

# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Important**: Always activate the virtual environment before running the application:
- When you open a new terminal, run the activation command again
- You should see `(venv)` at the beginning of your command prompt
- To deactivate: run `deactivate` command

### 2. Microsoft Azure Setup

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Configure:
   - **Name**: TBMCG News Dashboard
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Web - `http://localhost:5000/auth/callback` (for development)
5. After creation, note the **Application (client) ID**
6. Go to **Certificates & secrets** > **New client secret**
7. Note the **Value** (client secret)

### 3. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your values
SECRET_KEY=your-super-secret-key-here
MICROSOFT_CLIENT_ID=your-client-id-from-azure
MICROSOFT_CLIENT_SECRET=your-client-secret-from-azure
MICROSOFT_TENANT_ID=your-tenant-id-or-common
REDIRECT_URI=http://localhost:5000/auth/callback
```

### 4. Run the Application

```bash
# Make sure virtual environment is activated (you should see (venv) in prompt)
# If not, run: source venv/bin/activate  (macOS/Linux) or venv\Scripts\activate (Windows)

# Start the application
python app.py
```

Visit `http://localhost:5000` and sign in with your `@tbmcg.com` Microsoft account.

**Note**: The application will automatically create the database file (`feeds.db`) and populate it with default categories and sample feeds on first run.

## User Permissions

### Default Access
- All `@tbmcg.com` users can view the dashboard and read articles
- Search and filter functionality available to all users

### Feed Management Access
To grant feed management permissions to specific users:

1. User must log in at least once
2. Admin manually updates database or modify the `can_manage` logic in `app.py`:

```python
# In the auth_callback function, modify this line:
can_manage = email in ['admin@tbmcg.com', 'manager@tbmcg.com']  # Add specific emails
```

## Default Feeds

The application comes with sample feeds in these categories:
- **Technology**: TechCrunch, The Verge, Ars Technica
- **Business**: Reuters Business  
- **Finance**: MarketWatch
- **Startups**: Hacker News

Users with management permissions can add, edit, or remove feeds as needed.

## Production Deployment

### Environment Variables for Production

```bash
SECRET_KEY=generate-a-strong-secret-key
MICROSOFT_CLIENT_ID=your-production-client-id
MICROSOFT_CLIENT_SECRET=your-production-client-secret
MICROSOFT_TENANT_ID=your-tenant-id
REDIRECT_URI=https://yourdomain.com/auth/callback
```

### Using Gunicorn (Recommended)

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Gunicorn is already included in requirements.txt
# Run with gunicorn for production
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# For production with more options:
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
```

### Using Docker

```dockerfile
# Dockerfile (create this file)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
# Build and run
docker build -t tbmcg-news-dashboard .
docker run -p 5000:5000 --env-file .env tbmcg-news-dashboard
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## File Structure

```
company-news-dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── feeds.db              # SQLite database (auto-created)
├── .env.example          # Environment template
├── STYLE_GUIDE.md        # Design system documentation
├── templates/
│   ├── base.html         # Base template
│   ├── dashboard.html    # Main dashboard
│   └── manage.html       # Feed management
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── app.js        # JavaScript utilities
└── README.md
```

## API Endpoints

- `GET /` - Main dashboard (requires auth)
- `GET /login` - Microsoft OAuth login
- `GET /auth/callback` - OAuth callback
- `GET /logout` - Logout user
- `GET /api/feeds` - Get all categories and feeds
- `GET /api/articles` - Get articles from all feeds
- `GET /manage` - Feed management page (requires manage permission)

## Customization

### Adding New Feed Categories

1. Log in with a management account
2. Go to **Manage Feeds**  
3. Click **Add Category**
4. Choose name and color
5. Add feeds to the category

### Modifying User Permissions

Edit the `can_manage` logic in `app.py`:

```python
# Grant management access to specific users
can_manage = email in [
    'admin@tbmcg.com',
    'manager@tbmcg.com', 
    'teamlead@tbmcg.com'
]
```

### Styling Customization

The application follows the design system documented in `STYLE_GUIDE.md`. Customize colors and styling in `static/css/style.css` using the CSS custom properties.

## Troubleshooting

### Common Issues

1. **Authentication fails**: Check Azure app registration and redirect URI
2. **Feeds not loading**: Check internet connectivity and RSS feed URLs
3. **Permission denied**: Ensure user email ends with `@tbmcg.com`
4. **Database errors**: Ensure write permissions for SQLite database file

### Logs

Check console output for detailed error messages. In production, configure proper logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Support

For technical issues or feature requests, contact the development team or create an issue in the project repository.

## License

Internal TBMCG project - All rights reserved.