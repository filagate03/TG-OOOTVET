# Deployment Guide for Beget Hosting

This guide explains how to deploy the TG-Otvet Telegram Bot Funnel System on Beget hosting.

## Prerequisites

- Active Beget hosting account
- Domain name pointing to your Beget hosting
- SSH access enabled (if needed)
- Python 3.8+ support on the server

## Method 1: Using Beget Control Panel (Recommended)

### Step 1: Upload Files
1. Go to your Beget control panel
2. Use the file manager to upload all project files to your domain directory (e.g., `~/domains/yourdomain.com/`)
3. Or use FTP/SFTP to upload the files

### Step 2: Set Up Python Application
1. In the control panel, go to "Websites" → "Python"
2. Click "Add Python application"
3. Fill in the form:
   - Domain: your domain
   - Application root: `/domains/yourdomain.com` (or your project path)
   - Application file: `app.py`
   - Application object: `application`
   - Python version: 3.9 or higher
   - Virtual environment: `.venv` (or your preferred name)

### Step 3: Install Dependencies
1. In the Python application management section, you can usually install packages
2. Or use SSH to install: `pip install -r requirements.txt`

### Step 4: Configure Environment Variables
1. Create a `.env` file in your project root based on `.env.example`
2. Add your bot token and other configuration values

### Step 5: Set Up Database
1. The application uses SQLite by default
2. Make sure the `bot.db` file has proper write permissions
3. Or set up your database configuration in `.env`

## Method 2: Using SSH (Advanced)

### Step 1: Connect via SSH
```bash
ssh username@yourdomain.com
```

### Step 2: Clone or Upload Project
```bash
# If using git
git clone https://your-repo-url.git

# Or upload files via SFTP to your domain directory
```

### Step 3: Set Up Virtual Environment
```bash
cd ~/domains/yourdomain.com  # or your project directory
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
nano .env
```

### Step 6: Set Up Database
```bash
python init_db.py
```

### Step 7: Set File Permissions
```bash
chmod -R 755 media/
chmod 644 .env
```

## Running the Application

### Using Gunicorn (Recommended for production)
```bash
gunicorn app:app -c gunicorn.conf.py
```

### Using Uvicorn (For development/testing)
```bash
uvicorn backend.api.main:app --host 0.0.0 --port 8000
```

## Configuration for Beget

### Using the Control Panel
1. In the Python application settings, you can specify:
   - Entry point: `app:application`
   - Working directory: your project root
   - Environment variables directly in the control panel

### Using Environment Variables
Set these variables in your Beget control panel or .env file:
- `BOT_TOKEN`: Your Telegram bot token
- `DATABASE_URL`: Database connection string (default uses SQLite)
- `API_BASE_URL`: Public URL of your API

## Setting Up the Telegram Bot

1. Create a bot with @BotFather on Telegram
2. Get the bot token
3. Set the webhook URL to your API endpoint:
   ```
   https://api.telegram.org/bot<your_token>/setWebhook?url=https://yourdomain.com/webhook
   ```

## Media Files Configuration

The application stores media files in the `media/` directory. Make sure this directory:
- Has write permissions for the web server
- Is located in the correct path as configured in your environment
- Is properly backed up

## Database Configuration

The application uses SQLite by default, which is suitable for small to medium applications. The database file (`bot.db`) should:
- Be in a location with read/write permissions
- Be backed up regularly
- Be located outside the web root for security (if possible)

## Frontend Integration

If you're serving the frontend separately:
1. Build the React app: `npm run build` in the frontend directory
2. Configure your domain to serve static files from the build directory
3. Update API endpoints to point to your backend

## Troubleshooting

### Common Issues:

1. **Permission errors**: Make sure your application has write access to the database and media directories
2. **Import errors**: Verify all dependencies are installed in the correct virtual environment
3. **Database connection errors**: Check that the database file path is correct and accessible
4. **Bot not responding**: Verify the bot token is correct and the webhook is properly configured

### Checking Application Status:
```bash
# Check running processes
ps aux | grep gunicorn

# Check application logs
tail -f /path/to/your/logs
```

## Security Considerations

1. Never commit your `.env` file to version control
2. Use strong passwords and API keys
3. Regularly update dependencies
4. Monitor access logs for suspicious activity
5. Use HTTPS for all communications

## Updating the Application

1. Backup your database and configuration
2. Upload new files via FTP/SFTP or git pull
3. Update dependencies: `pip install -r requirements.txt --upgrade`
4. Restart the Python application from the control panel

## Support

If you encounter issues with deployment:
1. Check the Beget knowledge base for Python application guides
2. Review your application logs
3. Ensure all dependencies are compatible with the Beget environment
4. Contact Beget support for server-specific issues