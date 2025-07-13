# Phase 4: Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Phase 4 Distributed Cognitive Mesh API & Embodiment Layer in production environments.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  Production Deployment                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Load        │  │ Load        │  │ Load        │              │
│  │ Balancer    │  │ Balancer    │  │ Balancer    │              │
│  │ (Unity3D)   │  │ (ROS)       │  │ (Web)       │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                 │                 │                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Unity3D     │  │ ROS         │  │ Web Agent   │              │
│  │ Adapters    │  │ Adapters    │  │ Adapters    │              │
│  │ (Port 7777) │  │ (Port 8888) │  │ (Port 6666) │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│              ┌─────────────────────────┐                        │
│              │ Cognitive API Server    │                        │
│              │ (Port 5000)             │                        │
│              │ - REST API              │                        │
│              │ - WebSocket Server      │                        │
│              │ - Neural-Symbolic Core  │                        │
│              │ - Distributed Mesh      │                        │
│              └─────────────────────────┘                        │
│                           │                                     │
│              ┌─────────────────────────┐                        │
│              │ Redis Cluster           │                        │
│              │ - State Management      │                        │
│              │ - Task Queue            │                        │
│              │ - Session Storage       │                        │
│              └─────────────────────────┘                        │
│                           │                                     │
│              ┌─────────────────────────┐                        │
│              │ PostgreSQL Cluster      │                        │
│              │ - Persistent Storage    │                        │
│              │ - Performance Metrics   │                        │
│              │ - Audit Logs           │                        │
│              └─────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements

**Minimum Production Requirements:**
- **CPU**: 8 cores (Intel Xeon E5-2690 v4 or equivalent)
- **Memory**: 32 GB RAM
- **Storage**: 500 GB SSD (NVMe preferred)
- **Network**: 1 Gbps dedicated bandwidth
- **OS**: Ubuntu 20.04 LTS or CentOS 8

**Recommended Production Requirements:**
- **CPU**: 16 cores (Intel Xeon Gold 6248 or equivalent)
- **Memory**: 64 GB RAM
- **Storage**: 1 TB NVMe SSD
- **Network**: 10 Gbps dedicated bandwidth
- **OS**: Ubuntu 22.04 LTS

### Software Dependencies

```bash
# Core system packages
sudo apt update
sudo apt install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    redis-server \
    postgresql-14 \
    postgresql-client-14 \
    postgresql-contrib-14 \
    nginx \
    supervisor \
    htop \
    iotop \
    netstat \
    curl \
    wget \
    git \
    docker.io \
    docker-compose

# Python packages
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

## Installation Steps

### 1. Environment Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash cogmesh
sudo usermod -aG docker cogmesh

# Create application directories
sudo mkdir -p /opt/cognitive-mesh
sudo mkdir -p /var/log/cognitive-mesh
sudo mkdir -p /var/lib/cognitive-mesh
sudo chown -R cogmesh:cogmesh /opt/cognitive-mesh
sudo chown -R cogmesh:cogmesh /var/log/cognitive-mesh
sudo chown -R cogmesh:cogmesh /var/lib/cognitive-mesh

# Clone repository
cd /opt/cognitive-mesh
sudo -u cogmesh git clone https://github.com/OzCog/mlpn.git
cd mlpn
```

### 2. Database Setup

```bash
# PostgreSQL configuration
sudo -u postgres createuser cogmesh
sudo -u postgres createdb cognitive_mesh_prod
sudo -u postgres psql -c "ALTER USER cogmesh WITH ENCRYPTED PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cognitive_mesh_prod TO cogmesh;"

# Redis configuration
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configure Redis for production
sudo tee /etc/redis/redis.conf.d/cognitive-mesh.conf << EOF
maxmemory 8gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
EOF

sudo systemctl restart redis-server
```

### 3. Application Configuration

```bash
# Create production configuration
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/production.env << EOF
# Environment
ENVIRONMENT=production
DEBUG=false

# API Server
API_HOST=0.0.0.0
API_PORT=5000
SECRET_KEY=your_very_secure_secret_key_here

# Database
DATABASE_URL=postgresql://cogmesh:your_secure_password@localhost/cognitive_mesh_prod
REDIS_URL=redis://localhost:6379/0

# Adapters
UNITY3D_PORT=7777
ROS_PORT=8888
WEB_PORT=6666

# Performance
WORKER_PROCESSES=8
MAX_CONCURRENT_TASKS=1000
SYNTHESIS_TIMEOUT=30

# Security
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/cognitive-mesh/application.log

# Monitoring
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
PERFORMANCE_MONITORING=true
EOF

# Load environment
source /opt/cognitive-mesh/mlpn/production.env
```

### 4. Application Deployment

#### Option A: Docker Deployment (Recommended)

```bash
# Create Docker Compose configuration
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/docker-compose.prod.yml << EOF
version: '3.8'

services:
  cognitive-api:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    image: cognitive-mesh:latest
    container_name: cognitive-api
    restart: always
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - production.env
    volumes:
      - /var/log/cognitive-mesh:/app/logs
      - /var/lib/cognitive-mesh:/app/data
    depends_on:
      - redis
      - postgres
    networks:
      - cognitive-mesh
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'

  unity3d-adapter:
    build:
      context: .
      dockerfile: adapters/unity3d/Dockerfile
    image: unity3d-adapter:latest
    container_name: unity3d-adapter
    restart: always
    ports:
      - "7777:7777"
    env_file:
      - production.env
    depends_on:
      - cognitive-api
    networks:
      - cognitive-mesh
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'

  ros-adapter:
    build:
      context: .
      dockerfile: adapters/ros/Dockerfile
    image: ros-adapter:latest
    container_name: ros-adapter
    restart: always
    ports:
      - "8888:8888"
    env_file:
      - production.env
    depends_on:
      - cognitive-api
    networks:
      - cognitive-mesh
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'

  web-adapter:
    build:
      context: .
      dockerfile: adapters/web/Dockerfile
    image: web-adapter:latest
    container_name: web-adapter
    restart: always
    ports:
      - "6666:6666"
    env_file:
      - production.env
    depends_on:
      - cognitive-api
    networks:
      - cognitive-mesh
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'

  redis:
    image: redis:7-alpine
    container_name: cognitive-redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes --maxmemory 8gb --maxmemory-policy allkeys-lru
    networks:
      - cognitive-mesh

  postgres:
    image: postgres:14-alpine
    container_name: cognitive-postgres
    restart: always
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: cognitive_mesh_prod
      POSTGRES_USER: cogmesh
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - cognitive-mesh

  nginx:
    image: nginx:alpine
    container_name: cognitive-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - /var/log/nginx:/var/log/nginx
    depends_on:
      - cognitive-api
      - web-adapter
    networks:
      - cognitive-mesh

volumes:
  redis-data:
  postgres-data:

networks:
  cognitive-mesh:
    driver: bridge
EOF

# Build and deploy
sudo -u cogmesh docker-compose -f docker-compose.prod.yml build
sudo -u cogmesh docker-compose -f docker-compose.prod.yml up -d
```

#### Option B: Native Deployment

```bash
# Install Python dependencies
cd /opt/cognitive-mesh/mlpn
sudo -u cogmesh pip3 install -r requirements.txt

# Create systemd services
sudo tee /etc/systemd/system/cognitive-api.service << EOF
[Unit]
Description=Cognitive Mesh API Server
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=simple
User=cogmesh
Group=cogmesh
WorkingDirectory=/opt/cognitive-mesh/mlpn
Environment=PYTHONPATH=/opt/cognitive-mesh/mlpn
EnvironmentFile=/opt/cognitive-mesh/mlpn/production.env
ExecStart=/usr/bin/python3 -m erpnext.cognitive.phase4_api_server --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cognitive-api

[Install]
WantedBy=multi-user.target
EOF

# Create adapter services
sudo tee /etc/systemd/system/unity3d-adapter.service << EOF
[Unit]
Description=Unity3D Integration Adapter
After=cognitive-api.service
Requires=cognitive-api.service

[Service]
Type=simple
User=cogmesh
Group=cogmesh
WorkingDirectory=/opt/cognitive-mesh/mlpn
Environment=PYTHONPATH=/opt/cognitive-mesh/mlpn
EnvironmentFile=/opt/cognitive-mesh/mlpn/production.env
ExecStart=/usr/bin/python3 -m erpnext.cognitive.unity3d_adapter --port 7777
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/ros-adapter.service << EOF
[Unit]
Description=ROS Integration Adapter
After=cognitive-api.service
Requires=cognitive-api.service

[Service]
Type=simple
User=cogmesh
Group=cogmesh
WorkingDirectory=/opt/cognitive-mesh/mlpn
Environment=PYTHONPATH=/opt/cognitive-mesh/mlpn
EnvironmentFile=/opt/cognitive-mesh/mlpn/production.env
ExecStart=/usr/bin/python3 -m erpnext.cognitive.ros_adapter --port 8888
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/web-adapter.service << EOF
[Unit]
Description=Web Agent Integration Adapter
After=cognitive-api.service
Requires=cognitive-api.service

[Service]
Type=simple
User=cogmesh
Group=cogmesh
WorkingDirectory=/opt/cognitive-mesh/mlpn
Environment=PYTHONPATH=/opt/cognitive-mesh/mlpn
EnvironmentFile=/opt/cognitive-mesh/mlpn/production.env
ExecStart=/usr/bin/python3 -m erpnext.cognitive.web_agent_adapter --host 0.0.0.0 --port 6666
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable cognitive-api unity3d-adapter ros-adapter web-adapter
sudo systemctl start cognitive-api unity3d-adapter ros-adapter web-adapter
```

### 5. Load Balancer Configuration

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/cognitive-mesh << EOF
upstream cognitive_api {
    server 127.0.0.1:5000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream unity3d_adapter {
    server 127.0.0.1:7777 max_fails=3 fail_timeout=30s;
}

upstream ros_adapter {
    server 127.0.0.1:8888 max_fails=3 fail_timeout=30s;
}

upstream web_adapter {
    server 127.0.0.1:6666 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# Rate limiting
limit_req_zone \$binary_remote_addr zone=api:10m rate=100r/s;
limit_req_zone \$binary_remote_addr zone=websocket:10m rate=50r/s;

server {
    listen 80;
    server_name api.your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    ssl_certificate /etc/nginx/ssl/api.your-domain.com.crt;
    ssl_certificate_key /etc/nginx/ssl/api.your-domain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://cognitive_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # WebSocket endpoints
    location /socket.io/ {
        limit_req zone=websocket burst=10 nodelay;
        
        proxy_pass http://web_adapter;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 7s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check
    location /health {
        proxy_pass http://cognitive_api;
        access_log off;
    }

    # Static files
    location /static/ {
        alias /opt/cognitive-mesh/mlpn/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Unity3D adapter
server {
    listen 7777 ssl;
    server_name unity.your-domain.com;

    ssl_certificate /etc/nginx/ssl/unity.your-domain.com.crt;
    ssl_certificate_key /etc/nginx/ssl/unity.your-domain.com.key;

    location / {
        proxy_pass http://unity3d_adapter;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

# ROS adapter
server {
    listen 8888 ssl;
    server_name ros.your-domain.com;

    ssl_certificate /etc/nginx/ssl/ros.your-domain.com.crt;
    ssl_certificate_key /etc/nginx/ssl/ros.your-domain.com.key;

    location / {
        proxy_pass http://ros_adapter;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/cognitive-mesh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring & Observability

### 1. Prometheus & Grafana Setup

```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz
sudo mv prometheus-2.40.0.linux-amd64 /opt/prometheus
sudo chown -R cogmesh:cogmesh /opt/prometheus

# Configure Prometheus
sudo -u cogmesh tee /opt/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "cognitive_mesh_rules.yml"

scrape_configs:
  - job_name: 'cognitive-api'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'unity3d-adapter'
    static_configs:
      - targets: ['localhost:7777']
    metrics_path: '/metrics'

  - job_name: 'ros-adapter'
    static_configs:
      - targets: ['localhost:8888']
    metrics_path: '/metrics'

  - job_name: 'web-adapter'
    static_configs:
      - targets: ['localhost:6666']
    metrics_path: '/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
EOF

# Create systemd service for Prometheus
sudo tee /etc/systemd/system/prometheus.service << EOF
[Unit]
Description=Prometheus Server
After=network.target

[Service]
Type=simple
User=cogmesh
Group=cogmesh
ExecStart=/opt/prometheus/prometheus --config.file=/opt/prometheus/prometheus.yml --storage.tsdb.path=/opt/prometheus/data --web.console.templates=/opt/prometheus/consoles --web.console.libraries=/opt/prometheus/console_libraries --web.listen-address=0.0.0.0:9090
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable prometheus
sudo systemctl start prometheus
```

### 2. Application Metrics

```python
# Add to each service (example for API server)
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics definitions
REQUEST_COUNT = Counter('cognitive_api_requests_total', 
                       'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('cognitive_api_request_duration_seconds',
                           'Request latency')
ACTIVE_SYNTHESES = Gauge('cognitive_api_active_syntheses',
                        'Number of active synthesis operations')
SYNTHESIS_RATE = Counter('cognitive_api_syntheses_total',
                        'Total synthesis operations', ['type', 'status'])

# Start metrics server
start_http_server(8000)
```

### 3. Logging Configuration

```bash
# Configure centralized logging with rsyslog
sudo tee /etc/rsyslog.d/50-cognitive-mesh.conf << EOF
# Cognitive Mesh application logs
if \$programname startswith 'cognitive-' then {
    /var/log/cognitive-mesh/application.log
    stop
}

# Unity3D adapter logs
if \$programname == 'unity3d-adapter' then {
    /var/log/cognitive-mesh/unity3d.log
    stop
}

# ROS adapter logs
if \$programname == 'ros-adapter' then {
    /var/log/cognitive-mesh/ros.log
    stop
}

# Web adapter logs
if \$programname == 'web-adapter' then {
    /var/log/cognitive-mesh/web.log
    stop
}
EOF

sudo systemctl restart rsyslog

# Configure log rotation
sudo tee /etc/logrotate.d/cognitive-mesh << EOF
/var/log/cognitive-mesh/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 cogmesh cogmesh
    postrotate
        systemctl reload cognitive-api unity3d-adapter ros-adapter web-adapter
    endscript
}
EOF
```

## Security Configuration

### 1. Firewall Setup

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow adapter ports (restrict to specific IPs in production)
sudo ufw allow from 10.0.0.0/8 to any port 7777
sudo ufw allow from 10.0.0.0/8 to any port 8888
sudo ufw allow from 10.0.0.0/8 to any port 6666

# Allow monitoring
sudo ufw allow from 10.0.0.0/8 to any port 9090  # Prometheus
sudo ufw allow from 10.0.0.0/8 to any port 3000  # Grafana

sudo ufw enable
```

### 2. SSL/TLS Configuration

```bash
# Generate SSL certificates (using Let's Encrypt)
sudo apt install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot --nginx -d api.your-domain.com
sudo certbot --nginx -d unity.your-domain.com
sudo certbot --nginx -d ros.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Authentication & Authorization

```bash
# Create API key management script
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/scripts/manage_api_keys.py << EOF
#!/usr/bin/env python3
"""API Key management for Cognitive Mesh"""

import hashlib
import secrets
import json
import argparse
from datetime import datetime, timedelta

def generate_api_key(name, expiry_days=365):
    """Generate a new API key"""
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    expiry = datetime.utcnow() + timedelta(days=expiry_days)
    
    api_key_data = {
        "name": name,
        "key_hash": key_hash,
        "created": datetime.utcnow().isoformat(),
        "expires": expiry.isoformat(),
        "active": True
    }
    
    print(f"Generated API key for {name}:")
    print(f"Key: {key}")
    print(f"Hash: {key_hash}")
    print(f"Expires: {expiry.isoformat()}")
    
    return api_key_data

def revoke_api_key(key_hash):
    """Revoke an API key"""
    # Implementation would update database/config
    print(f"Revoked API key: {key_hash}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["generate", "revoke"])
    parser.add_argument("--name", help="API key name")
    parser.add_argument("--key-hash", help="Key hash to revoke")
    parser.add_argument("--days", type=int, default=365, help="Expiry days")
    
    args = parser.parse_args()
    
    if args.action == "generate":
        generate_api_key(args.name, args.days)
    elif args.action == "revoke":
        revoke_api_key(args.key_hash)
EOF

chmod +x /opt/cognitive-mesh/mlpn/scripts/manage_api_keys.py
```

## Performance Tuning

### 1. System Optimization

```bash
# Kernel parameters for high performance
sudo tee /etc/sysctl.d/99-cognitive-mesh.conf << EOF
# Network optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq

# File descriptor limits
fs.file-max = 1000000

# Memory management
vm.swappiness = 10
vm.dirty_ratio = 80
vm.dirty_background_ratio = 5

# CPU scheduling
kernel.sched_migration_cost_ns = 5000000
EOF

sudo sysctl -p /etc/sysctl.d/99-cognitive-mesh.conf
```

### 2. Application Tuning

```bash
# Configure service limits
sudo tee /etc/systemd/system/cognitive-api.service.d/limits.conf << EOF
[Service]
LimitNOFILE=65536
LimitNPROC=4096
LimitMEMLOCK=infinity
EOF

# Python optimization
export PYTHONOPTIMIZE=2
export PYTHONUNBUFFERED=1
```

### 3. Database Optimization

```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();
```

## Backup & Recovery

### 1. Database Backup

```bash
# Create backup script
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/scripts/backup.sh << EOF
#!/bin/bash

BACKUP_DIR="/var/backups/cognitive-mesh"
DATE=\$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p \$BACKUP_DIR

# PostgreSQL backup
pg_dump -h localhost -U cogmesh cognitive_mesh_prod | gzip > \$BACKUP_DIR/postgres_\$DATE.sql.gz

# Redis backup
redis-cli --rdb \$BACKUP_DIR/redis_\$DATE.rdb

# Application data backup
tar -czf \$BACKUP_DIR/app_data_\$DATE.tar.gz /var/lib/cognitive-mesh

# Remove old backups (keep 30 days)
find \$BACKUP_DIR -name "*.gz" -mtime +30 -delete
find \$BACKUP_DIR -name "*.rdb" -mtime +30 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x /opt/cognitive-mesh/mlpn/scripts/backup.sh

# Schedule daily backups
sudo -u cogmesh crontab -e
# Add: 0 2 * * * /opt/cognitive-mesh/mlpn/scripts/backup.sh
```

### 2. Disaster Recovery

```bash
# Create recovery script
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/scripts/restore.sh << EOF
#!/bin/bash

BACKUP_FILE=\$1
if [ -z "\$BACKUP_FILE" ]; then
    echo "Usage: \$0 <backup_file>"
    exit 1
fi

echo "Stopping services..."
sudo systemctl stop cognitive-api unity3d-adapter ros-adapter web-adapter

echo "Restoring database..."
gunzip -c \$BACKUP_FILE | psql -h localhost -U cogmesh cognitive_mesh_prod

echo "Starting services..."
sudo systemctl start cognitive-api unity3d-adapter ros-adapter web-adapter

echo "Recovery completed"
EOF

chmod +x /opt/cognitive-mesh/mlpn/scripts/restore.sh
```

## Health Checks & Maintenance

### 1. Health Check Scripts

```bash
# Create comprehensive health check
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/scripts/health_check.sh << EOF
#!/bin/bash

echo "Cognitive Mesh Health Check - \$(date)"
echo "========================================"

# Check services
services=("cognitive-api" "unity3d-adapter" "ros-adapter" "web-adapter" "redis" "postgresql")
for service in "\${services[@]}"; do
    if systemctl is-active --quiet \$service; then
        echo "✓ \$service: Running"
    else
        echo "✗ \$service: Not running"
    fi
done

# Check API endpoints
echo -e "\nAPI Health Checks:"
curl -s http://localhost:5000/health | jq '.status' || echo "✗ API health check failed"

# Check resource usage
echo -e "\nResource Usage:"
echo "CPU: \$(top -bn1 | grep "Cpu(s)" | awk '{print \$2}' | cut -d'%' -f1)%"
echo "Memory: \$(free | grep Mem | awk '{printf("%.1f%%", \$3/\$2 * 100.0)}')"
echo "Disk: \$(df / | tail -1 | awk '{print \$5}')"

# Check database connections
echo -e "\nDatabase:"
psql -h localhost -U cogmesh cognitive_mesh_prod -c "SELECT version();" > /dev/null 2>&1 && echo "✓ PostgreSQL: Connected" || echo "✗ PostgreSQL: Connection failed"

redis-cli ping > /dev/null 2>&1 && echo "✓ Redis: Connected" || echo "✗ Redis: Connection failed"

echo "========================================"
EOF

chmod +x /opt/cognitive-mesh/mlpn/scripts/health_check.sh

# Schedule regular health checks
sudo -u cogmesh crontab -e
# Add: */5 * * * * /opt/cognitive-mesh/mlpn/scripts/health_check.sh >> /var/log/cognitive-mesh/health.log 2>&1
```

### 2. Automated Maintenance

```bash
# Create maintenance script
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/scripts/maintenance.sh << EOF
#!/bin/bash

echo "Starting maintenance - \$(date)"

# Update application
cd /opt/cognitive-mesh/mlpn
git pull origin main

# Restart services if needed
if [ "\$1" = "--restart" ]; then
    sudo systemctl restart cognitive-api unity3d-adapter ros-adapter web-adapter
fi

# Clean up logs
find /var/log/cognitive-mesh -name "*.log" -size +100M -exec truncate -s 0 {} \;

# Clean up temporary files
find /tmp -name "cognitive_*" -mtime +1 -delete

# Database maintenance
psql -h localhost -U cogmesh cognitive_mesh_prod -c "VACUUM ANALYZE;"

echo "Maintenance completed - \$(date)"
EOF

chmod +x /opt/cognitive-mesh/mlpn/scripts/maintenance.sh
```

## Scaling Considerations

### 1. Horizontal Scaling

```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cognitive-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cognitive-api
  template:
    metadata:
      labels:
        app: cognitive-api
    spec:
      containers:
      - name: cognitive-api
        image: cognitive-mesh:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        env:
        - name: REDIS_URL
          value: "redis://redis-cluster:6379"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
```

### 2. Load Testing

```bash
# Install load testing tools
pip3 install locust

# Create load test script
sudo -u cogmesh tee /opt/cognitive-mesh/mlpn/scripts/load_test.py << EOF
from locust import HttpUser, task, between

class CognitiveAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
    
    @task(2)
    def synthesize(self):
        payload = {
            "symbolic_input": {
                "concept": "test_synthesis",
                "truth_value": {"strength": 0.8, "confidence": 0.9}
            },
            "neural_input": [0.1] * 256,
            "synthesis_type": "conceptual_embedding"
        }
        self.client.post("/api/cognitive/synthesize", json=payload)
    
    @task(1)
    def create_task(self):
        payload = {
            "task_type": "test_task",
            "input_data": {"test": True}
        }
        self.client.post("/api/cognitive/tasks", json=payload)
EOF

# Run load test
# locust -f /opt/cognitive-mesh/mlpn/scripts/load_test.py --host=http://localhost:5000
```

## Troubleshooting Guide

### Common Issues

1. **High Memory Usage**
   ```bash
   # Check memory usage by component
   sudo systemctl status cognitive-api
   ps aux | grep cognitive
   
   # Adjust memory limits
   sudo systemctl edit cognitive-api
   # Add: [Service]
   #      MemoryLimit=4G
   ```

2. **Connection Timeouts**
   ```bash
   # Check network connections
   netstat -tlnp | grep :5000
   
   # Increase timeout values
   # Edit production.env:
   # SYNTHESIS_TIMEOUT=60
   # CONNECTION_TIMEOUT=30
   ```

3. **Database Performance**
   ```sql
   -- Check slow queries
   SELECT query, mean_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 10;
   
   -- Check connections
   SELECT count(*) FROM pg_stat_activity;
   ```

### Emergency Procedures

```bash
# Emergency shutdown
sudo systemctl stop cognitive-api unity3d-adapter ros-adapter web-adapter

# Emergency restart
sudo systemctl restart cognitive-api unity3d-adapter ros-adapter web-adapter

# Reset to safe state
sudo -u cogmesh /opt/cognitive-mesh/mlpn/scripts/restore.sh /var/backups/cognitive-mesh/latest.sql.gz
```

## Conclusion

This production deployment guide provides a comprehensive foundation for deploying the Phase 4 Distributed Cognitive Mesh API & Embodiment Layer in enterprise environments. Regular monitoring, maintenance, and security updates are essential for optimal performance and reliability.

For additional support, refer to the troubleshooting documentation or contact the development team.