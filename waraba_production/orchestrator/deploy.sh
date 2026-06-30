#!/bin/bash
# Deploy WARABA Orchestrator on Contabo VPS
# Run once: bash deploy.sh
set -e

echo "=== WARABA Orchestrator Deploy ==="

# Install deps
apt-get update -qq && apt-get install -y python3-pip python3-venv -qq

PROJECT_DIR="/opt/waraba-orchestrator"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Venv
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# Copy .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edit .env before starting services!"
    exit 1
fi

# Systemd service: FastAPI
cat > /etc/systemd/system/waraba-api.service << EOF
[Unit]
Description=WARABA Orchestrator API
After=network.target

[Service]
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Systemd service: Gradio UI
cat > /etc/systemd/system/waraba-ui.service << EOF
[Unit]
Description=WARABA Director UI
After=network.target waraba-api.service

[Service]
WorkingDirectory=$PROJECT_DIR
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/python ui.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable waraba-api waraba-ui
systemctl start waraba-api waraba-ui

echo "=== Done ==="
echo "API:  http://$(hostname -I | awk '{print $1}'):8000"
echo "UI:   http://$(hostname -I | awk '{print $1}'):7860"
