#!/bin/bash

echo "=========================================="
echo "TG-Otvet: Auto-Install & Start (VPS/Linux)"
echo "=========================================="

# 0. Install system dependencies
echo "[0/7] Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv python3-full curl

if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# 1. Create and activate virtual environment
echo "[1/7] Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 2. Install Python dependencies
echo "[2/7] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Clean and install Node.js dependencies
echo "[3/7] Installing Node.js dependencies..."
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..

# 4. Build Frontend
echo "[4/7] Building Frontend..."
cd frontend
npm run build
cd ..

# 5. Initialize Database
echo "[5/7] Initializing Database..."
python3 init_db.py

# 6. Create .env if not exists
echo "[6/7] Checking .env file..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///bot.db
FRONTEND_URL=http://$(curl -s ifconfig.me):8002
BACKEND_URL=http://$(curl -s ifconfig.me):8002
EOF
fi

# 7. Start everything
echo "[7/7] Starting Backend + Bot Manager..."
# Kill old processes
pkill -f "gunicorn" 2>/dev/null || true
pkill -f "run.py" 2>/dev/null || true
pkill -f "bot/main.py" 2>/dev/null || true

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "=========================================="
echo "✅ System is ready!"
echo "=========================================="
echo "🌐 Access URL: http://$SERVER_IP:8002"
echo "📝 Open in browser and create your project"
echo "=========================================="
echo ""

python3 run.py