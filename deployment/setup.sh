#!/bin/bash
# Einmalig ausführen nach dem ersten Login auf dem Server
# Ausführen als root: bash setup.sh

set -e

echo "=== 1. System aktualisieren ==="
apt update && apt upgrade -y

echo "=== 2. Pakete installieren ==="
apt install -y python3 python3-pip python3-venv nginx git postgresql postgresql-contrib

echo "=== 3. Projektverzeichnis anlegen ==="
mkdir -p /var/www/coderr
mkdir -p /var/log/coderr
chown -R www-data:www-data /var/www/coderr /var/log/coderr

echo "=== 4. Projekt-Dateien hierher kopieren (per git clone oder scp) ==="
echo "    Beispiel: git clone <dein-repo> /var/www/coderr"
echo "    Dann weiter mit Schritt 5"
echo ""
read -p "Drücke Enter sobald die Dateien unter /var/www/coderr liegen..."

echo "=== 5. Python Virtual Environment erstellen ==="
cd /var/www/coderr
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

echo "=== 6. .env Datei anlegen ==="
echo "    Kopiere .env.template nach .env und trage deine Werte ein:"
echo "    cp /var/www/coderr/.env.template /var/www/coderr/.env"
echo "    nano /var/www/coderr/.env"
echo ""
read -p "Drücke Enter sobald .env befüllt ist..."

echo "=== 7. Django vorbereiten ==="
cd /var/www/coderr
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data /var/www/coderr

echo "=== 8. systemd Service einrichten ==="
cp /var/www/coderr/deployment/coderr.service /etc/systemd/system/coderr.service
systemctl daemon-reload
systemctl enable coderr
systemctl start coderr

echo "=== 9. Nginx einrichten ==="
cp /var/www/coderr/deployment/nginx.conf /etc/nginx/sites-available/coderr
ln -sf /etc/nginx/sites-available/coderr /etc/nginx/sites-enabled/coderr
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo ""
echo "=== Fertig! Backend läuft unter http://217.154.174.108 ==="
echo "Logs prüfen: journalctl -u coderr -f"
