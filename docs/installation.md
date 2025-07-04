# ERPNext Local Installation & Deployment Guide

This comprehensive guide covers local installation and deployment of ERPNext for both development and production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Installation](#quick-installation)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [Development Setup](#development-setup)
6. [Production Deployment](#production-deployment)
7. [Maintenance](#maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- 4GB RAM
- 40GB free disk space
- 2 CPU cores
- Ubuntu 20.04+, CentOS 8+, or macOS 10.15+

**Recommended Requirements:**
- 8GB RAM
- 100GB free disk space
- 4 CPU cores
- SSD storage

### Software Dependencies

**Required:**
- Python 3.10+
- Node.js 18.x+
- MariaDB 10.6+
- Redis 5.0+
- Git
- wkhtmltopdf

**Optional:**
- Nginx (for production)
- Supervisor (for production)
- Certbot (for SSL)

## Quick Installation

### Using Installation Script

The fastest way to get ERPNext running locally:

```bash
# Clone repository
git clone https://github.com/OzCog/mlpn.git
cd mlpn

# Run installation script
./scripts/local_install.sh --dev

# Start development server
cd frappe-bench
bench start
```

### Using Docker

For a containerized setup:

```bash
# Clone frappe_docker
git clone https://github.com/frappe/frappe_docker
cd frappe_docker

# Start containers
docker compose -f pwd.yml up -d

# Access at http://localhost:8080
```

## Manual Installation

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev python3-pip python3-venv \
    redis-server mariadb-server mariadb-client \
    libmariadb-dev libffi-dev libssl-dev \
    wkhtmltopdf curl git npm nodejs \
    libcups2-dev

# Install latest Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**CentOS/RHEL/Fedora:**
```bash
# CentOS/RHEL
sudo yum install -y epel-release
sudo yum install -y python3-devel python3-pip redis mariadb-server mariadb-devel \
                   libffi-devel openssl-devel wkhtmltopdf curl git npm nodejs cups-devel

# Fedora
sudo dnf install -y python3-devel python3-pip redis mariadb-server mariadb-devel \
                   libffi-devel openssl-devel wkhtmltopdf curl git npm nodejs cups-devel
```

**macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 redis mariadb node npm wkhtmltopdf
```

### Step 2: Configure Database

```bash
# Start MariaDB
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Secure MariaDB installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p << EOF
CREATE DATABASE erpnext_local;
CREATE USER 'erpnext_local'@'localhost' IDENTIFIED BY 'erpnext_local';
GRANT ALL PRIVILEGES ON erpnext_local.* TO 'erpnext_local'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### Step 3: Install frappe-bench

```bash
# Install frappe-bench
pip3 install --user frappe-bench

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
bench --version
```

### Step 4: Initialize Bench

```bash
# Initialize bench
bench init frappe-bench --frappe-branch develop
cd frappe-bench

# Set developer mode (optional)
bench set-config developer_mode 1
```

### Step 5: Create Site

```bash
# Create new site
bench new-site erpnext.local --db-name erpnext_local --admin-password admin

# Add site to hosts file (optional)
echo "127.0.0.1 erpnext.local" | sudo tee -a /etc/hosts
```

### Step 6: Install ERPNext

```bash
# Get ERPNext app
bench get-app erpnext https://github.com/OzCog/mlpn

# Install ERPNext
bench --site erpnext.local install-app erpnext

# Start development server
bench start
```

## Configuration

### Environment Variables

Create a `.env` file in your bench directory:

```bash
# Copy template
cp config/templates/.env.local .env

# Edit configuration
nano .env
```

### Site Configuration

Edit `sites/erpnext.local/site_config.json`:

```json
{
  "db_host": "localhost",
  "db_port": 3306,
  "db_name": "erpnext_local",
  "db_user": "erpnext_local",
  "db_password": "erpnext_local",
  "developer_mode": 1,
  "auto_update": 0,
  "scheduler_enabled": 1,
  "background_workers": 1
}
```

### Common Configuration Options

```bash
# Set configuration values
bench config set developer_mode 1
bench config set server_script_enabled 1
bench config set disable_website_cache 1
bench config set background_workers 2

# Database settings
bench config set db_host localhost
bench config set db_port 3306

# Redis settings
bench config set redis_cache "redis://localhost:6379/0"
bench config set redis_queue "redis://localhost:6379/1"

# Email settings
bench config set mail_server "smtp.gmail.com"
bench config set mail_port 587
bench config set use_ssl 1
```

## Development Setup

### Development Tools

```bash
# Install development dependencies
bench setup requirements --dev

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Setup IDE integration
bench setup procfile  # For process management
```

### Building Assets

```bash
# Build assets for development
bench build

# Watch for changes (in development)
bench watch
```

### Running Tests

```bash
# Run all tests
bench --site erpnext.local run-tests

# Run specific app tests
bench --site erpnext.local run-tests --app erpnext

# Run specific test
bench --site erpnext.local run-tests --doctype "Sales Order"
```

### Database Management

```bash
# Backup database
bench --site erpnext.local backup

# Restore database
bench --site erpnext.local restore backup_file.sql.gz

# Migrate database
bench --site erpnext.local migrate

# Reset database (WARNING: This will delete all data)
bench --site erpnext.local reinstall
```

## Production Deployment

### Using Deployment Script

```bash
# Run deployment script
./scripts/local_deploy.sh --site-name your-domain.com --ssl

# Check deployment status
sudo supervisorctl status
```

### Manual Production Setup

#### Step 1: Production Configuration

```bash
# Switch to production mode
bench --site erpnext.local set-config developer_mode 0
bench --site erpnext.local set-config server_script_enabled 0
bench --site erpnext.local set-config disable_website_cache 0

# Build production assets
bench build --production
```

#### Step 2: Setup Nginx

```bash
# Install Nginx
sudo apt-get install -y nginx

# Generate Nginx configuration
bench setup nginx

# Enable site
sudo ln -s $(pwd)/config/nginx.conf /etc/nginx/sites-enabled/frappe-bench
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 3: Setup Supervisor

```bash
# Install Supervisor
sudo apt-get install -y supervisor

# Generate Supervisor configuration
bench setup supervisor

# Enable configuration
sudo ln -s $(pwd)/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

#### Step 4: Setup SSL (Optional)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Setup auto-renewal
sudo crontab -e
# Add: 0 3 * * * /usr/bin/certbot renew --quiet
```

#### Step 5: Setup Backups

```bash
# Create backup directory
sudo mkdir -p /var/backups/frappe-bench
sudo chown -R $(whoami):$(whoami) /var/backups/frappe-bench

# Setup automated backups
crontab -e
# Add: 0 2 * * * cd /home/$(whoami)/frappe-bench && bench --site erpnext.local backup --with-files && mv sites/erpnext.local/backups/* /var/backups/frappe-bench/
```

## Maintenance

### Regular Tasks

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade

# Update ERPNext
bench update

# Clear cache
bench --site erpnext.local clear-cache

# Optimize database
bench --site erpnext.local execute frappe.utils.bench_helper.optimize_database

# Check system health
bench doctor
```

### Monitoring

```bash
# Check service status
sudo systemctl status mariadb redis-server nginx supervisor

# Monitor logs
tail -f logs/web.log
tail -f logs/worker.log
tail -f logs/schedule.log

# Check system resources
htop
df -h
free -h
```

### Backup Strategy

```bash
# Daily backups
bench --site erpnext.local backup --with-files

# Weekly full backup
bench --site erpnext.local backup --with-files --backup-path /var/backups/weekly/

# Monthly archive
tar -czf /var/backups/monthly/erpnext-$(date +%Y%m).tar.gz /var/backups/frappe-bench/
```

### Security Best Practices

1. **Change default passwords**
2. **Enable firewall**
3. **Regular security updates**
4. **Monitor access logs**
5. **Use SSL/HTTPS**
6. **Limit database privileges**
7. **Regular security audits**

## Troubleshooting

For detailed troubleshooting instructions, see our [Troubleshooting Guide](troubleshooting.md).

### Quick Fixes

**Permission Issues:**
```bash
sudo chown -R $(whoami):$(whoami) frappe-bench
chmod -R 755 frappe-bench
```

**Database Connection:**
```bash
mysql -u erpnext_local -p -e "SELECT 1;"
```

**Port Conflicts:**
```bash
bench config set webserver_port 8001
```

**Clear Cache:**
```bash
bench --site erpnext.local clear-cache
bench restart
```

## Additional Resources

- [Official Documentation](https://docs.frappe.io)
- [Community Forum](https://discuss.frappe.io)
- [GitHub Repository](https://github.com/frappe/erpnext)
- [Frappe School](https://frappe.school)
- [Telegram Group](https://t.me/erpnext_public)

## Support

If you encounter any issues:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Search the [community forum](https://discuss.frappe.io)
3. Create an issue on [GitHub](https://github.com/OzCog/mlpn/issues)
4. Join our [Telegram group](https://t.me/erpnext_public)