#!/usr/bin/env bash
# ====================================================================
# Автоматизований скрипт налаштування сайту на Raspberry Pi 5
# ====================================================================

set -e

echo "========================================================="
echo "  Налаштування сайту «Шинковий Вісник» на Raspberry Pi 5"
echo "========================================================="

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

echo "[1/5] Оновлення пакетів системи та встановлення Python..."
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv curl libsqlite3-dev

echo "[2/5] Створення віртуального середовища Python (venv)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Віртуальне середовище створено."
fi

echo "[3/5] Встановлення залежностей проєкту (Flask, Gunicorn)..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "[4/5] Ініціалізація бази даних SQLite..."
./venv/bin/python database.py

echo "[5/5] Налаштування автозапуску через systemd (bar.service)..."
CURRENT_USER=$(whoami)
SERVICE_FILE="/etc/systemd/system/bar.service"

sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=Шинковий Вісник — Bar Newspaper Web App
After=network.target

[Service]
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$APP_DIR
Environment=\"PATH=$APP_DIR/venv/bin\"
Environment=\"SECRET_KEY=bar_production_key_rpi5_2026\"
Environment=\"ADMIN_PASSWORD=bar123\"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable bar.service
sudo systemctl restart bar.service

echo ""
echo "========================================================="
echo "✓ САЙТ УСПІШНО ЗАПУЩЕНО ТА ДОДАНО В АВТОЗАПУСК!"
echo "---------------------------------------------------------"
echo "  Локальна адреса у вашій Wi-Fi мережі:"
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "  http://$LOCAL_IP:8000"
echo "  Кабінет редактора: http://$LOCAL_IP:8000/admin"
echo "---------------------------------------------------------"
echo "  Для підключення через Cloudflare Tunnel перегляньте:"
echo "  cat deploy/cloudflared_setup.md"
echo "========================================================="
