# ERPNext Local Installation & Deployment Troubleshooting Guide

This guide helps you resolve common issues during local installation and deployment of ERPNext.

## Common Installation Issues

### 1. Permission Errors

**Problem**: Permission denied errors during installation or operation.

**Solution**:
```bash
# Fix ownership of bench directory
sudo chown -R $(whoami):$(whoami) ~/frappe-bench

# Fix permissions
chmod -R 755 ~/frappe-bench

# Add user to required groups
sudo usermod -a -G sudo $(whoami)
```

### 2. Database Connection Issues

**Problem**: Cannot connect to MariaDB database.

**Solutions**:

a) **Check MariaDB Service**:
```bash
sudo systemctl status mariadb
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

b) **Test Database Connection**:
```bash
mysql -u erpnext_local -p -e "SELECT 1;"
```

c) **Reset Database Password**:
```bash
sudo mysql -u root -p -e "ALTER USER 'erpnext_local'@'localhost' IDENTIFIED BY 'new_password';"
sudo mysql -u root -p -e "FLUSH PRIVILEGES;"
```

d) **Check Database Configuration**:
```bash
# Check site_config.json
cat sites/your-site.local/site_config.json

# Verify database exists
mysql -u root -p -e "SHOW DATABASES;"
```

### 3. Port Already in Use

**Problem**: Port 8000 or other ports are already in use.

**Solutions**:

a) **Find Process Using Port**:
```bash
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000
```

b) **Change Port**:
```bash
bench config set webserver_port 8001
bench config set socketio_port 9001
```

c) **Kill Process**:
```bash
sudo kill -9 PID_NUMBER
```

### 4. Node.js/npm Issues

**Problem**: Node.js version compatibility or npm errors.

**Solutions**:

a) **Check Versions**:
```bash
node --version  # Should be >= 18.x
npm --version   # Should be >= 8.x
```

b) **Update Node.js**:
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Using nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

c) **Clear npm Cache**:
```bash
npm cache clean --force
```

### 5. Python/pip Issues

**Problem**: Python version compatibility or pip installation errors.

**Solutions**:

a) **Check Python Version**:
```bash
python3 --version  # Should be >= 3.10
pip3 --version
```

b) **Update pip**:
```bash
python3 -m pip install --upgrade pip
```

c) **Install in Virtual Environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install frappe-bench
```

### 6. Redis Connection Issues

**Problem**: Cannot connect to Redis server.

**Solutions**:

a) **Check Redis Service**:
```bash
sudo systemctl status redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

b) **Test Redis Connection**:
```bash
redis-cli ping
```

c) **Check Redis Configuration**:
```bash
# Check Redis is listening on correct port
sudo netstat -tulpn | grep :6379

# Check Redis configuration
sudo nano /etc/redis/redis.conf
```

### 7. SSL/HTTPS Issues

**Problem**: SSL certificate errors or HTTPS not working.

**Solutions**:

a) **Check Certificate**:
```bash
sudo certbot certificates
```

b) **Renew Certificate**:
```bash
sudo certbot renew --dry-run
sudo certbot renew
```

c) **Check Nginx Configuration**:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Common Deployment Issues

### 1. Nginx Configuration Issues

**Problem**: Nginx not serving the site correctly.

**Solutions**:

a) **Check Nginx Configuration**:
```bash
sudo nginx -t
sudo systemctl status nginx
```

b) **Regenerate Nginx Configuration**:
```bash
cd ~/frappe-bench
bench setup nginx
sudo systemctl reload nginx
```

c) **Check Nginx Logs**:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 2. Supervisor Issues

**Problem**: Supervisor not managing processes correctly.

**Solutions**:

a) **Check Supervisor Status**:
```bash
sudo supervisorctl status
sudo systemctl status supervisor
```

b) **Restart Supervisor**:
```bash
sudo supervisorctl restart all
sudo systemctl restart supervisor
```

c) **Check Supervisor Logs**:
```bash
sudo tail -f /var/log/supervisor/supervisord.log
```

### 3. Performance Issues

**Problem**: Site is slow or unresponsive.

**Solutions**:

a) **Check System Resources**:
```bash
top
htop
df -h
free -h
```

b) **Check Process Logs**:
```bash
tail -f ~/frappe-bench/logs/web.log
tail -f ~/frappe-bench/logs/worker.log
```

c) **Optimize Database**:
```bash
cd ~/frappe-bench
bench --site your-site.local execute frappe.utils.bench_helper.optimize_database
```

d) **Increase Worker Processes**:
```bash
bench config set background_workers 4
bench setup supervisor
sudo supervisorctl reload
```

### 4. Backup and Restore Issues

**Problem**: Backup or restore operations failing.

**Solutions**:

a) **Check Backup Directory Permissions**:
```bash
ls -la /var/backups/frappe-bench/
sudo chown -R $(whoami):$(whoami) /var/backups/frappe-bench/
```

b) **Manual Backup**:
```bash
cd ~/frappe-bench
bench --site your-site.local backup --with-files
```

c) **Restore from Backup**:
```bash
cd ~/frappe-bench
bench --site your-site.local restore /path/to/backup.sql.gz --with-public-files /path/to/files.tar --with-private-files /path/to/private-files.tar
```

## Diagnostic Commands

### System Information
```bash
# OS Information
lsb_release -a
uname -a

# Hardware Information
lscpu
free -h
df -h
```

### ERPNext/Frappe Information
```bash
cd ~/frappe-bench
bench version
bench config show
bench doctor
```

### Service Status
```bash
sudo systemctl status mariadb
sudo systemctl status redis-server
sudo systemctl status nginx
sudo systemctl status supervisor
```

### Log Files
```bash
# ERPNext logs
tail -f ~/frappe-bench/logs/web.log
tail -f ~/frappe-bench/logs/worker.log
tail -f ~/frappe-bench/logs/schedule.log

# System logs
sudo journalctl -u mariadb
sudo journalctl -u nginx
sudo journalctl -u supervisor
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs** for specific error messages
2. **Search the documentation** at https://docs.frappe.io
3. **Visit the community forum** at https://discuss.frappe.io
4. **Check GitHub issues** at https://github.com/frappe/erpnext/issues
5. **Join the Telegram group** at https://t.me/erpnext_public

## Useful Commands Reference

### Bench Commands
```bash
# Start development server
bench start

# Update apps
bench update

# Migrate site
bench --site your-site.local migrate

# Install app
bench --site your-site.local install-app app_name

# Build assets
bench build

# Clear cache
bench --site your-site.local clear-cache

# Enable/disable maintenance mode
bench --site your-site.local set-maintenance-mode on
bench --site your-site.local set-maintenance-mode off

# Create new site
bench new-site your-site.local

# Backup site
bench --site your-site.local backup

# Restore site
bench --site your-site.local restore backup_file.sql.gz
```

### Database Commands
```bash
# Access MariaDB console
mysql -u root -p

# Access site database
mysql -u erpnext_local -p erpnext_local

# Show databases
mysql -u root -p -e "SHOW DATABASES;"

# Show tables
mysql -u erpnext_local -p erpnext_local -e "SHOW TABLES;"
```

### System Service Commands
```bash
# Start services
sudo systemctl start mariadb redis-server nginx supervisor

# Stop services
sudo systemctl stop mariadb redis-server nginx supervisor

# Restart services
sudo systemctl restart mariadb redis-server nginx supervisor

# Check service status
sudo systemctl status mariadb redis-server nginx supervisor

# Enable services to start on boot
sudo systemctl enable mariadb redis-server nginx supervisor
```