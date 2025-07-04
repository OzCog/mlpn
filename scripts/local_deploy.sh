#!/bin/bash

# ERPNext Local Deployment Script
# This script helps with local deployment for production use

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SITE_NAME="erpnext.local"
BENCH_DIR="./frappe-bench"
NGINX_CONF="yes"
SSL_CERT="no"
SUPERVISOR_CONF="yes"
PRODUCTION_MODE="yes"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup production configuration
setup_production_config() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Setting up production configuration..."
    
    # Switch to production mode
    if [[ "$PRODUCTION_MODE" == "yes" ]]; then
        bench --site "$SITE_NAME" set-config developer_mode 0
        bench --site "$SITE_NAME" set-config server_script_enabled 0
        bench --site "$SITE_NAME" set-config disable_website_cache 0
    fi
    
    # Set maintenance mode temporarily
    bench --site "$SITE_NAME" set-maintenance-mode on
    
    # Migrate database
    bench --site "$SITE_NAME" migrate
    
    # Build assets for production
    bench build --production
    
    # Turn off maintenance mode
    bench --site "$SITE_NAME" set-maintenance-mode off
    
    print_success "Production configuration completed"
}

# Function to setup nginx
setup_nginx() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Setting up nginx configuration..."
    
    # Install nginx if not present
    if ! command_exists nginx; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y nginx
        elif command_exists yum; then
            sudo yum install -y nginx
        elif command_exists dnf; then
            sudo dnf install -y nginx
        fi
    fi
    
    # Generate nginx configuration
    bench setup nginx
    
    # Enable and start nginx
    if command_exists systemctl; then
        sudo systemctl enable nginx
        sudo systemctl start nginx
    fi
    
    print_success "Nginx configuration completed"
}

# Function to setup supervisor
setup_supervisor() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Setting up supervisor configuration..."
    
    # Install supervisor if not present
    if ! command_exists supervisord; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y supervisor
        elif command_exists yum; then
            sudo yum install -y supervisor
        elif command_exists dnf; then
            sudo dnf install -y supervisor
        fi
    fi
    
    # Generate supervisor configuration
    bench setup supervisor
    
    # Enable and start supervisor
    if command_exists systemctl; then
        sudo systemctl enable supervisor
        sudo systemctl start supervisor
    fi
    
    print_success "Supervisor configuration completed"
}

# Function to setup SSL certificate
setup_ssl() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Setting up SSL certificate..."
    
    # Install certbot if not present
    if ! command_exists certbot; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        elif command_exists yum; then
            sudo yum install -y certbot python3-certbot-nginx
        elif command_exists dnf; then
            sudo dnf install -y certbot python3-certbot-nginx
        fi
    fi
    
    # Setup SSL certificate
    print_status "Please run the following command to get SSL certificate:"
    print_status "sudo certbot --nginx -d $SITE_NAME"
    
    print_success "SSL setup instructions provided"
}

# Function to optimize database
optimize_database() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Optimizing database..."
    
    # Run database optimizations
    bench --site "$SITE_NAME" execute frappe.utils.bench_helper.optimize_database
    
    print_success "Database optimization completed"
}

# Function to setup log rotation
setup_log_rotation() {
    local bench_dir="$1"
    
    print_status "Setting up log rotation..."
    
    # Create logrotate configuration
    sudo tee /etc/logrotate.d/frappe-bench > /dev/null <<EOF
$bench_dir/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 frappe frappe
    postrotate
        systemctl reload supervisor
    endscript
}
EOF
    
    print_success "Log rotation setup completed"
}

# Function to setup backup
setup_backup() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Setting up automated backup..."
    
    # Create backup directory
    sudo mkdir -p /var/backups/frappe-bench
    sudo chown -R $(whoami):$(whoami) /var/backups/frappe-bench
    
    # Create backup script
    cat > backup_script.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/frappe-bench"
DATE=$(date +"%Y%m%d_%H%M%S")
SITE_NAME="erpnext.local"

cd /path/to/frappe-bench

# Create backup
bench --site $SITE_NAME backup --with-files

# Move backup to backup directory
mv sites/$SITE_NAME/backups/* $BACKUP_DIR/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar" -mtime +30 -delete

echo "Backup completed at $(date)"
EOF
    
    # Make backup script executable
    chmod +x backup_script.sh
    
    # Add cron job for daily backup
    (crontab -l 2>/dev/null; echo "0 2 * * * $bench_dir/backup_script.sh >> /var/log/frappe-backup.log 2>&1") | crontab -
    
    print_success "Automated backup setup completed"
}

# Function to setup monitoring
setup_monitoring() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Setting up monitoring..."
    
    # Create monitoring script
    cat > monitor_script.sh << 'EOF'
#!/bin/bash
SITE_NAME="erpnext.local"
BENCH_DIR="/path/to/frappe-bench"

cd $BENCH_DIR

# Check if site is accessible
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200"; then
    echo "Site is not accessible, restarting services..."
    supervisorctl restart all
fi

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Warning: Disk usage is at $DISK_USAGE%"
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "Warning: Memory usage is at $MEM_USAGE%"
fi
EOF
    
    # Make monitoring script executable
    chmod +x monitor_script.sh
    
    # Add cron job for monitoring
    (crontab -l 2>/dev/null; echo "*/5 * * * * $bench_dir/monitor_script.sh >> /var/log/frappe-monitor.log 2>&1") | crontab -
    
    print_success "Monitoring setup completed"
}

# Function to display deployment summary
show_deployment_summary() {
    print_success "Local deployment completed successfully!"
    print_status "Site URL: http://$SITE_NAME"
    print_status "Admin credentials: Administrator / admin"
    print_status ""
    print_status "Important files and commands:"
    print_status "- Nginx config: /etc/nginx/sites-enabled/$SITE_NAME"
    print_status "- Supervisor config: /etc/supervisor/conf.d/frappe-bench.conf"
    print_status "- Logs: $BENCH_DIR/logs/"
    print_status "- Backups: /var/backups/frappe-bench/"
    print_status ""
    print_status "Useful commands:"
    print_status "- Start services: sudo supervisorctl start all"
    print_status "- Stop services: sudo supervisorctl stop all"
    print_status "- Restart services: sudo supervisorctl restart all"
    print_status "- Check status: sudo supervisorctl status"
    print_status "- View logs: tail -f $BENCH_DIR/logs/web.log"
    print_status "- Manual backup: bench --site $SITE_NAME backup"
    print_status "- Update apps: bench update"
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --site-name NAME      Site name (default: erpnext.local)"
    echo "  -b, --bench-dir PATH      Bench directory (default: ./frappe-bench)"
    echo "  --skip-nginx             Skip nginx configuration"
    echo "  --skip-supervisor        Skip supervisor configuration"
    echo "  --skip-production        Skip production mode setup"
    echo "  --ssl                    Setup SSL certificate"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --site-name mysite.com --ssl"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--site-name)
            SITE_NAME="$2"
            shift 2
            ;;
        -b|--bench-dir)
            BENCH_DIR="$2"
            shift 2
            ;;
        --skip-nginx)
            NGINX_CONF="no"
            shift
            ;;
        --skip-supervisor)
            SUPERVISOR_CONF="no"
            shift
            ;;
        --skip-production)
            PRODUCTION_MODE="no"
            shift
            ;;
        --ssl)
            SSL_CERT="yes"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main deployment process
main() {
    print_status "Starting ERPNext local deployment..."
    print_status "Site name: $SITE_NAME"
    print_status "Bench directory: $BENCH_DIR"
    
    # Check if bench directory exists
    if [[ ! -d "$BENCH_DIR" ]]; then
        print_error "Bench directory $BENCH_DIR does not exist"
        print_error "Please run the installation script first"
        exit 1
    fi
    
    # Setup production configuration
    if [[ "$PRODUCTION_MODE" == "yes" ]]; then
        setup_production_config "$BENCH_DIR"
    fi
    
    # Setup nginx
    if [[ "$NGINX_CONF" == "yes" ]]; then
        setup_nginx "$BENCH_DIR"
    fi
    
    # Setup supervisor
    if [[ "$SUPERVISOR_CONF" == "yes" ]]; then
        setup_supervisor "$BENCH_DIR"
    fi
    
    # Setup SSL certificate
    if [[ "$SSL_CERT" == "yes" ]]; then
        setup_ssl "$BENCH_DIR"
    fi
    
    # Optimize database
    optimize_database "$BENCH_DIR"
    
    # Setup log rotation
    setup_log_rotation "$BENCH_DIR"
    
    # Setup backup
    setup_backup "$BENCH_DIR"
    
    # Setup monitoring
    setup_monitoring "$BENCH_DIR"
    
    # Show deployment summary
    show_deployment_summary
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi