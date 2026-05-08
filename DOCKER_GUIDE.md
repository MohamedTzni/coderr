# Docker & Deployment Guide

Dieses Dokument erklärt Schritt für Schritt, wie das Coderr-Backend mit Docker und PostgreSQL aufgesetzt wird — lokal und auf einem Produktionsserver.

---

## Inhaltsverzeichnis

1. [Was ist Docker und warum benutzen wir es?](#1-was-ist-docker-und-warum-benutzen-wir-es)
2. [Projektstruktur der Docker-Dateien](#2-projektstruktur-der-docker-dateien)
3. [Das Dockerfile erklärt](#3-das-dockerfile-erklärt)
4. [Das entrypoint.sh erklärt](#4-das-entrypointsh-erklärt)
5. [Das docker-compose.yml erklärt](#5-das-docker-composeyml-erklärt)
6. [Die .env Datei](#6-die-env-datei)
7. [Lokales Setup mit Docker Desktop](#7-lokales-setup-mit-docker-desktop)
8. [Deployment auf dem Produktionsserver](#8-deployment-auf-dem-produktionsserver)
9. [Nginx Konfiguration](#9-nginx-konfiguration)
10. [Nützliche Docker-Befehle](#10-nützliche-docker-befehle)
11. [Häufige Probleme und Lösungen](#11-häufige-probleme-und-lösungen)

---

## 1. Was ist Docker und warum benutzen wir es?

### Das Problem ohne Docker

Ohne Docker laufen Anwendungen direkt auf dem Betriebssystem. Das führt zu typischen Problemen:

- „Bei mir funktioniert es, aber auf dem Server nicht" — unterschiedliche Python-Versionen, unterschiedliche Systempackages
- Abhängigkeitskonflikte zwischen verschiedenen Projekten
- Aufwendiges manuelles Setup auf jedem neuen Server

### Die Docker-Lösung

Docker packt die Anwendung zusammen mit allem was sie braucht (Python, Packages, Konfiguration) in einen **Container**. Dieser Container läuft überall gleich — egal ob auf deinem Windows-PC, einem Mac oder einem Linux-Server.

### Wichtige Begriffe

| Begriff | Erklärung |
|---|---|
| **Image** | Ein fertiges, unveränderliches Paket (wie eine ISO-Datei). Wird aus dem Dockerfile gebaut. |
| **Container** | Eine laufende Instanz eines Images. Wie ein gestartetes Programm. |
| **Volume** | Persistenter Speicher außerhalb des Containers. Daten überleben einen Neustart. |
| **Netzwerk** | Docker-interne Verbindung zwischen Containern. |
| **docker-compose** | Werkzeug zum gleichzeitigen Starten mehrerer Container (z.B. Django + PostgreSQL). |

### Unsere Architektur

```
Internet
    │
    ▼
 Nginx (auf dem Host)          ← HTTPS, static files, media files
    │
    ▼ proxy_pass :8000
┌─────────────────────────────────┐
│        Docker Netzwerk          │
│                                 │
│  ┌──────────┐  ┌─────────────┐  │
│  │  web     │  │     db      │  │
│  │ (Django/ │──│ (PostgreSQL)│  │
│  │ Gunicorn)│  │             │  │
│  └──────────┘  └─────────────┘  │
│                                 │
└─────────────────────────────────┘
```

---

## 2. Projektstruktur der Docker-Dateien

```
coderr/
├── Dockerfile          ← Bauanleitung für das Django-Image
├── entrypoint.sh       ← Startskript (migrate, collectstatic, gunicorn)
├── docker-compose.yml  ← Definiert alle Services (web + db)
├── .dockerignore       ← Dateien die NICHT ins Image kopiert werden
├── .env                ← Geheime Konfiguration (nicht im Git!)
└── .env.docker         ← Template für die .env (im Git, ohne echte Werte)
```

---

## 3. Das Dockerfile erklärt

```dockerfile
FROM python:3.12-slim
```
**Was:** Startet mit einem offiziellen Python 3.12 Image in der "slim"-Variante.
**Warum slim:** Enthält nur das Nötigste — kein unnötiger Ballast. Das Image wird kleiner und sicherer.

```dockerfile
WORKDIR /app
```
**Was:** Setzt das Arbeitsverzeichnis im Container auf `/app`.
**Warum:** Alle folgenden Befehle (COPY, RUN) beziehen sich auf diesen Pfad. Entspricht einem `cd /app`.

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```
**Was:** Installiert den PostgreSQL-Client im Container.
**Warum postgresql-client:** Das Startskript (`entrypoint.sh`) nutzt `pg_isready`, ein Tool aus diesem Paket, um zu prüfen ob die Datenbank bereit ist bevor Django startet.
**Warum `--no-install-recommends`:** Verhindert die Installation empfohlener aber nicht notwendiger Pakete → kleineres Image.
**Warum `rm -rf /var/lib/apt/lists/*`:** Löscht den apt-Cache nach der Installation → kleineres Image.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
**Was:** Kopiert zuerst nur die `requirements.txt` und installiert dann die Python-Pakete.
**Warum in zwei Schritten:** Docker cached jeden Schritt (Layer). Solange sich `requirements.txt` nicht ändert, wird dieser Schritt beim nächsten Build übersprungen → viel schneller.

```dockerfile
COPY . .
```
**Was:** Kopiert den gesamten Projektcode in den Container.
**Warum nach pip install:** Wenn der Code sich ändert, muss nur dieser Layer neu gebaut werden, nicht die gesamte pip-Installation.

```dockerfile
RUN mkdir -p media staticfiles \
    && sed -i 's/\r$//' entrypoint.sh \
    && chmod +x entrypoint.sh
```
**Was:** Erstellt Ordner, bereinigt Zeilenenden und macht das Startskript ausführbar.
**Warum `sed -i 's/\r$//'`:** Auf Windows werden Dateien mit CRLF (`\r\n`) gespeichert, Linux erwartet LF (`\n`). Dieses Kommando entfernt das `\r` damit das Shell-Skript unter Linux funktioniert.
**Warum `chmod +x`:** Ohne dieses Flag könnte Linux das Skript nicht ausführen.

```dockerfile
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
```
**Was:** Dokumentiert Port 8000 und legt das Startskript als Einstiegspunkt fest.
**Wichtig:** `EXPOSE` öffnet den Port nicht wirklich — das macht erst `docker-compose.yml` mit `ports:`. Es ist nur eine Dokumentation.

---

## 4. Das entrypoint.sh erklärt

```bash
#!/bin/sh
set -e
```
**Was:** Definiert den Shell-Interpreter (`/bin/sh`) und aktiviert den "fail fast"-Modus.
**Warum `set -e`:** Das Skript bricht sofort ab wenn ein Befehl fehlschlägt. Ohne diese Option würde Django starten obwohl `migrate` fehlgeschlagen ist.

```bash
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER" -q; do
  sleep 1
done
```
**Was:** Wartet in einer Schleife bis PostgreSQL bereit ist.
**Warum:** Docker startet beide Container (web + db) fast gleichzeitig. PostgreSQL braucht einige Sekunden zum Hochfahren. Ohne diese Warteschleife würde Django versuchen sich zu verbinden bevor die Datenbank bereit ist → Fehler.
**`${DB_PORT:-5432}`:** Nimmt `DB_PORT` aus der Umgebung, oder `5432` als Standardwert falls nicht gesetzt.

```bash
python manage.py migrate --noinput
```
**Was:** Führt alle ausstehenden Datenbankmigrationen aus.
**Warum beim Start:** So werden neue Migrationen automatisch angewendet sobald der Container startet — kein manueller Eingriff nötig.
**`--noinput`:** Verhindert interaktive Rückfragen (wichtig in automatisierten Umgebungen).

```bash
python manage.py collectstatic --noinput
```
**Was:** Sammelt alle statischen Dateien (CSS, JS, Bilder) in den `staticfiles/` Ordner.
**Warum:** Django sucht statische Dateien in verschiedenen App-Ordnern. `collectstatic` kopiert sie alle an einen zentralen Ort damit Nginx oder WhiteNoise sie ausliefern kann.

```bash
exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
```
**Was:** Startet den Gunicorn WSGI-Server.
**Warum `exec`:** Ersetzt den Shell-Prozess durch Gunicorn. So wird Gunicorn zu PID 1 im Container und empfängt Signale (z.B. zum sauberen Beenden) direkt.
**`--bind 0.0.0.0:8000`:** Lauscht auf allen Netzwerkinterfaces des Containers auf Port 8000.
**`--workers 3`:** Startet 3 parallele Worker-Prozesse. Faustregel: `2 * CPU-Kerne + 1`.
**`--timeout 120`:** Beendet Worker die länger als 120 Sekunden brauchen (verhindert hängende Prozesse).

---

## 5. Das docker-compose.yml erklärt

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
```
**Was:** Definiert den Datenbankservice mit dem offiziellen PostgreSQL 16 Image.
**Warum alpine:** Alpine Linux ist eine sehr kleine Linux-Distribution. Das Image ist nur ~40MB statt ~200MB.
**`restart: unless-stopped`:** Der Container startet automatisch neu wenn er abstürzt oder der Server neu gestartet wird — außer er wurde manuell gestoppt.

```yaml
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
```
**Was:** Übergibt Umgebungsvariablen an den PostgreSQL-Container.
**Wie `${DB_NAME}` funktioniert:** Docker Compose liest beim Start automatisch die `.env` Datei im gleichen Verzeichnis und ersetzt `${VARIABLE}` durch den entsprechenden Wert.
**Was diese Variablen bewirken:** Das PostgreSQL-Image liest sie beim ersten Start und erstellt automatisch die Datenbank, den Benutzer und setzt das Passwort.

```yaml
    volumes:
      - postgres_data:/var/lib/postgresql/data
```
**Was:** Speichert die Datenbankdaten in einem benannten Volume.
**Warum wichtig:** Container sind flüchtig — ohne Volume gehen alle Daten verloren wenn der Container gestoppt wird. Das Volume überlebt Neustarts und Container-Neuerstellungen.

```yaml
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5
```
**Was:** Prüft regelmäßig ob PostgreSQL wirklich bereit ist Verbindungen anzunehmen.
**Warum:** `depends_on` allein wartet nur bis der Container *gestartet* ist, nicht bis PostgreSQL *bereit* ist. Mit `healthcheck` und `condition: service_healthy` wartet der web-Container wirklich bis die DB Anfragen annimmt.

```yaml
  web:
    build: .
    env_file: .env
    ports:
      - "127.0.0.1:8000:8000"
```
**Was:** Baut das Django-Image aus dem lokalen Dockerfile und bindet Port 8000.
**Warum `127.0.0.1:8000:8000` statt `8000:8000`:** `127.0.0.1:8000` ist nur lokal erreichbar — nicht aus dem Internet. Nginx auf dem Host übernimmt die Außenkommunikation. `0.0.0.0:8000` würde den Port öffentlich exponieren, was ein Sicherheitsrisiko wäre.

```yaml
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles
```
**Was:** Bind Mounts — verbinden Ordner auf dem Host direkt mit Ordnern im Container.
**Warum Bind Mounts statt benannte Volumes:** Nginx auf dem Host muss die Dateien direkt lesen können. Mit Bind Mounts liegen die Dateien unter `/var/www/coderr/media/` und `/var/www/coderr/staticfiles/` auf dem Host — genau wo Nginx sie erwartet.

```yaml
    depends_on:
      db:
        condition: service_healthy
```
**Was:** Der web-Container startet erst wenn der db-Container den Healthcheck bestanden hat.
**Warum:** Verhindert dass Django startet bevor PostgreSQL bereit ist.

```yaml
volumes:
  postgres_data:
```
**Was:** Deklariert das benannte Volume für PostgreSQL-Daten.
**Wichtig:** Benannte Volumes werden von Docker verwaltet und überleben `docker compose down`. Nur `docker compose down -v` löscht sie.

---

## 6. Die .env Datei

Die `.env` Datei enthält alle geheimen und umgebungsspezifischen Konfigurationen. Sie wird **niemals** ins Git eingecheckt (steht in `.gitignore`).

```env
# Django
SECRET_KEY=sehr-langer-zufaelliger-string
DEBUG=False

# Erlaubte Hosts
ALLOWED_HOSTS=api.mohamed-touzani.de,localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=https://coderr.mohamed-touzani.de

# Datenbank
DB_ENGINE=django.db.backends.postgresql
DB_NAME=coderr_db
DB_USER=coderr_user
DB_PASSWORD=sicheres-passwort
DB_HOST=db        ← WICHTIG: "db" ist der Name des Docker-Services, nicht "localhost"!
DB_PORT=5432
```

### SECRET_KEY generieren

```bash
python3 -c "import secrets; print(secrets.token_hex(50))"
```

### Warum DB_HOST=db?

Im Docker-Netzwerk können Container sich gegenseitig über ihren **Service-Namen** ansprechen. Da der Datenbankservice in `docker-compose.yml` `db` heißt, ist er intern unter dem Hostnamen `db` erreichbar — nicht unter `localhost`.

---

## 7. Lokales Setup mit Docker Desktop

### Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installiert

### Schritt 1: Repository klonen

```bash
git clone https://github.com/MohamedTzni/coderr.git
cd coderr
```

### Schritt 2: .env Datei erstellen

```bash
cp .env.docker .env
```

Dann `.env` öffnen und anpassen:

```env
SECRET_KEY=irgendein-string-reicht-lokal
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
DB_ENGINE=django.db.backends.postgresql
DB_NAME=coderr_db
DB_USER=coderr_user
DB_PASSWORD=lokales-passwort
DB_HOST=db
DB_PORT=5432
```

### Schritt 3: Container bauen und starten

```bash
docker compose up --build
```

**Was passiert in dieser Reihenfolge:**
1. Docker lädt das `postgres:16-alpine` Image herunter (nur beim ersten Mal)
2. Docker baut das `coderr-web` Image aus dem Dockerfile
3. PostgreSQL-Container startet, initialisiert die Datenbank
4. Healthcheck prüft ob PostgreSQL bereit ist
5. Django-Container startet, `entrypoint.sh` wird ausgeführt:
   - Wartet auf PostgreSQL
   - Führt `migrate` aus
   - Führt `collectstatic` aus
   - Startet Gunicorn

### Schritt 4: Superuser erstellen

In einem neuen Terminal:

```bash
docker compose exec web python manage.py createsuperuser
```

### Schritt 5: Testen

- API: `http://localhost:8000/api/offers/`
- Admin: `http://localhost:8000/admin/`

### Im Hintergrund starten

```bash
docker compose up -d --build
```

Das `-d` Flag (detached) startet die Container im Hintergrund.

---

## 8. Deployment auf dem Produktionsserver

### Voraussetzungen

- Ubuntu Server (24.04 empfohlen)
- Docker installiert
- Nginx installiert
- Domain mit DNS-Einträgen die auf den Server zeigen

### Docker auf Ubuntu installieren

```bash
curl -fsSL https://get.docker.com | sh
```

### Schritt 1: Alten Service stoppen

Falls Gunicorn bisher als systemd-Service lief:

```bash
systemctl stop coderr
systemctl disable coderr
```

### Schritt 2: Code holen

```bash
cd /var/www/coderr
git pull
```

### Schritt 3: Produktions-.env erstellen

```bash
cp .env.docker .env
nano .env
```

**Produktionswerte:**

```env
SECRET_KEY=        # Langen zufälligen String generieren!
DEBUG=False        # NIEMALS True in Produktion!
ALLOWED_HOSTS=api.mohamed-touzani.de,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://coderr.mohamed-touzani.de
DB_ENGINE=django.db.backends.postgresql
DB_NAME=coderr_db
DB_USER=coderr_user
DB_PASSWORD=       # Sicheres Passwort wählen und merken!
DB_HOST=db
DB_PORT=5432
```

**SECRET_KEY generieren:**

```bash
python3 -c "import secrets; print(secrets.token_hex(50))"
```

### Schritt 4: Container starten

```bash
docker compose up -d --build
```

### Schritt 5: Superuser anlegen

```bash
docker compose exec web python manage.py createsuperuser
```

### Schritt 6: Logs prüfen

```bash
docker compose logs web
```

Erfolgreich wenn folgendes erscheint:
```
web-1  | PostgreSQL ready.
web-1  | Running migrations: ... OK
web-1  | 166 static files copied...
web-1  | [INFO] Starting gunicorn 23.0.0
web-1  | [INFO] Listening at: http://0.0.0.0:8000
```

---

## 9. Nginx Konfiguration

Nginx läuft direkt auf dem Host (nicht in Docker) und übernimmt:
- HTTPS-Terminierung
- Auslieferung statischer Dateien direkt vom Dateisystem (schnell)
- Weiterleitung aller anderen Anfragen an Gunicorn im Container

```nginx
server {
    server_name api.mohamed-touzani.de;

    # Statische Dateien direkt vom Host ausliefern (schnell, kein Django-Overhead)
    location /static/ {
        alias /var/www/coderr/staticfiles/;
    }

    # Media-Dateien (Uploads) direkt vom Host ausliefern
    location /media/ {
        alias /var/www/coderr/media/;
    }

    # Alle anderen Anfragen an Gunicorn im Docker-Container weiterleiten
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/api.mohamed-touzani.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.mohamed-touzani.de/privkey.pem;
}
```

**Warum Bind Mounts für static/media:** Die Ordner `staticfiles/` und `media/` sind in `docker-compose.yml` als Bind Mounts konfiguriert (`./staticfiles:/app/staticfiles`). Das bedeutet: was der Container in `/app/staticfiles/` schreibt, landet direkt unter `/var/www/coderr/staticfiles/` auf dem Host — genau wo Nginx sucht.

Nach Nginx-Änderungen neu laden:

```bash
nginx -t          # Konfiguration testen
nginx -s reload   # Nginx neu laden (ohne Downtime)
```

---

## 10. Nützliche Docker-Befehle

### Container verwalten

```bash
# Container starten (im Hintergrund, neu bauen)
docker compose up -d --build

# Container stoppen (Daten bleiben erhalten)
docker compose down

# Container stoppen UND alle Volumes löschen (Daten weg!)
docker compose down -v

# Status aller Container anzeigen
docker compose ps
```

### Logs anschauen

```bash
# Logs des Django-Containers
docker compose logs web

# Logs des Datenbank-Containers
docker compose logs db

# Live-Logs verfolgen (Ctrl+C zum Beenden)
docker compose logs -f web
```

### In Container einsteigen

```bash
# Shell im Django-Container öffnen
docker compose exec web sh

# Shell im PostgreSQL-Container öffnen
docker compose exec db sh
```

### Django Management Commands

```bash
# Superuser erstellen
docker compose exec web python manage.py createsuperuser

# Migrationen manuell ausführen
docker compose exec web python manage.py migrate

# Neue Migration erstellen
docker compose exec web python manage.py makemigrations

# Tests ausführen
docker compose exec web python manage.py test

# Django Shell öffnen
docker compose exec web python manage.py shell
```

### Datenbank verwalten

```bash
# Alle Daten löschen, Tabellen bleiben erhalten
docker compose exec web python manage.py flush --noinput

# Datenbankdump erstellen
docker compose exec db pg_dump -U coderr_user coderr_db > backup.sql

# Dump wiederherstellen
docker compose exec -T db psql -U coderr_user coderr_db < backup.sql

# PostgreSQL-Konsole öffnen
docker compose exec db psql -U coderr_user -d coderr_db
```

### Updates deployen

```bash
cd /var/www/coderr
git pull
docker compose up -d --build
```

### Datenbank komplett zurücksetzen

```bash
docker compose down -v        # Stoppt Container und löscht Volumes
docker compose up -d --build  # Startet neu, migrate läuft automatisch
docker compose exec web python manage.py createsuperuser  # Superuser neu anlegen
```

---

## 11. Häufige Probleme und Lösungen

### Problem: "variable is not set" Warnings

```
WARN[0000] The "t" variable is not set. Defaulting to a blank string.
```

**Ursache:** Das Datenbankpasswort enthält Sonderzeichen wie `$`, `{`, `}` die Docker Compose als Variablen interpretiert.

**Lösung:** Diese Warnings sind harmlos — Django liest die `.env` direkt über `python-dotenv` und bekommt das Passwort korrekt. Alternativ: ein Passwort ohne `$`, `{`, `}` wählen.

### Problem: Container startet nicht, DB-Verbindungsfehler

```
django.db.utils.OperationalError: could not connect to server
```

**Ursache:** `DB_HOST` ist falsch gesetzt (z.B. `localhost` statt `db`).

**Lösung:** In der `.env` sicherstellen dass `DB_HOST=db` steht. `db` ist der Service-Name aus `docker-compose.yml`.

### Problem: Static files werden nicht gefunden (404)

**Ursache:** `collectstatic` wurde nicht ausgeführt oder der Bind Mount fehlt.

**Lösung:**
```bash
docker compose exec web python manage.py collectstatic --noinput
ls /var/www/coderr/staticfiles/   # Prüfen ob Dateien da sind
```

### Problem: Änderungen im Code haben keine Wirkung

**Ursache:** Der Container läuft noch mit dem alten Image.

**Lösung:**
```bash
docker compose up -d --build   # Image neu bauen
```

### Problem: Port 8000 bereits belegt

```
Error: bind: address already in use
```

**Ursache:** Ein anderer Prozess (z.B. alter Gunicorn-Service) nutzt Port 8000.

**Lösung:**
```bash
lsof -i :8000                    # Wer nutzt Port 8000?
systemctl stop coderr            # Alten Service stoppen
```

### Problem: Kein Speicherplatz mehr

**Ursache:** Alte Docker-Images und -Container belegen Speicher.

**Lösung:**
```bash
docker system prune              # Unbenutzte Ressourcen löschen
docker system prune -a           # Alle ungenutzten Images löschen (aggressiv)
docker system df                 # Speicherverbrauch anzeigen
```
