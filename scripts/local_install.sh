#!/bin/bash

# ERPNext Local Installation Script
# This script helps with local installation and setup of ERPNext

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SITE_NAME="erpnext.local"
FRAPPE_BRANCH="develop"
ERPNEXT_BRANCH="develop"
INSTALL_BENCH="yes"
INSTALL_DEPS="yes"
PYTHON_VERSION="python3"

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

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            echo "ubuntu"
        elif command_exists yum; then
            echo "centos"
        elif command_exists dnf; then
            echo "fedora"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    local os=$(detect_os)
    print_status "Installing system dependencies for $os..."
    
    case $os in
        ubuntu)
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev python3-pip python3-venv \
                redis-server mariadb-server mariadb-client \
                libmariadb-dev libffi-dev libssl-dev \
                wkhtmltopdf curl git npm nodejs \
                libcups2-dev
            ;;
        centos|fedora)
            if [[ "$os" == "centos" ]]; then
                sudo yum install -y epel-release
                sudo yum install -y \
                    python3-devel python3-pip \
                    redis mariadb-server mariadb-devel \
                    libffi-devel openssl-devel \
                    wkhtmltopdf curl git npm nodejs \
                    cups-devel
            else
                sudo dnf install -y \
                    python3-devel python3-pip \
                    redis mariadb-server mariadb-devel \
                    libffi-devel openssl-devel \
                    wkhtmltopdf curl git npm nodejs \
                    cups-devel
            fi
            ;;
        macos)
            if command_exists brew; then
                brew install python3 redis mariadb node npm wkhtmltopdf
            else
                print_error "Homebrew not found. Please install Homebrew first."
                exit 1
            fi
            ;;
        *)
            print_error "Unsupported operating system: $os"
            exit 1
            ;;
    esac
    
    print_success "System dependencies installed successfully"
}

# Function to setup database
setup_database() {
    print_status "Setting up MariaDB database..."
    
    # Start MariaDB service
    if command_exists systemctl; then
        sudo systemctl start mariadb
        sudo systemctl enable mariadb
    elif command_exists service; then
        sudo service mariadb start
    fi
    
    # Secure MariaDB installation
    print_status "Please run 'sudo mysql_secure_installation' manually after this script completes"
    
    # Create database and user
    sudo mysql -u root -e "CREATE DATABASE IF NOT EXISTS \`${SITE_NAME}\`;"
    sudo mysql -u root -e "CREATE USER IF NOT EXISTS '${SITE_NAME}'@'localhost' IDENTIFIED BY '${SITE_NAME}';"
    sudo mysql -u root -e "GRANT ALL PRIVILEGES ON \`${SITE_NAME}\`.* TO '${SITE_NAME}'@'localhost';"
    sudo mysql -u root -e "FLUSH PRIVILEGES;"
    
    print_success "Database setup completed"
}

# Function to install frappe-bench
install_frappe_bench() {
    print_status "Installing frappe-bench..."
    
    # Install using pip
    pip3 install --user frappe-bench
    
    # Add to PATH if not already there
    if ! command_exists bench; then
        export PATH="$HOME/.local/bin:$PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        print_status "Added bench to PATH. You may need to restart your terminal."
    fi
    
    print_success "frappe-bench installed successfully"
}

# Function to create new site
create_site() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Creating new site: $SITE_NAME"
    
    # Create site with admin password
    bench new-site "$SITE_NAME" --db-name "$SITE_NAME" --admin-password admin
    
    print_success "Site created successfully"
}

# Function to install ERPNext
install_erpnext() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Getting ERPNext app..."
    
    # Get ERPNext from current repository
    if [[ -d "$(pwd)/erpnext" ]]; then
        print_status "Using local ERPNext repository"
        bench get-app erpnext "$(pwd)"
    else
        bench get-app erpnext --branch "$ERPNEXT_BRANCH"
    fi
    
    print_status "Installing ERPNext on site..."
    bench --site "$SITE_NAME" install-app erpnext
    
    print_success "ERPNext installed successfully"
}

# Function to setup development environment
setup_development() {
    local bench_dir="$1"
    cd "$bench_dir"
    
    print_status "Setting up development environment..."
    
    # Install development dependencies
    bench setup requirements --dev
    
    # Build assets
    bench build
    
    print_success "Development environment setup completed"
}

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --site-name NAME      Site name (default: erpnext.local)"
    echo "  -b, --bench-dir PATH      Bench directory (default: ./frappe-bench)"
    echo "  --frappe-branch BRANCH    Frappe branch (default: develop)"
    echo "  --erpnext-branch BRANCH   ERPNext branch (default: develop)"
    echo "  --skip-deps              Skip system dependencies installation"
    echo "  --skip-bench             Skip frappe-bench installation"
    echo "  --dev                    Setup development environment"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --site-name mysite.local --dev"
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
        --frappe-branch)
            FRAPPE_BRANCH="$2"
            shift 2
            ;;
        --erpnext-branch)
            ERPNEXT_BRANCH="$2"
            shift 2
            ;;
        --skip-deps)
            INSTALL_DEPS="no"
            shift
            ;;
        --skip-bench)
            INSTALL_BENCH="no"
            shift
            ;;
        --dev)
            SETUP_DEV="yes"
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

# Set default bench directory
BENCH_DIR="${BENCH_DIR:-./frappe-bench}"

# Main installation process
main() {
    print_status "Starting ERPNext local installation..."
    print_status "Site name: $SITE_NAME"
    print_status "Bench directory: $BENCH_DIR"
    
    # Install system dependencies
    if [[ "$INSTALL_DEPS" == "yes" ]]; then
        install_system_dependencies
    fi
    
    # Setup database
    setup_database
    
    # Install frappe-bench
    if [[ "$INSTALL_BENCH" == "yes" ]]; then
        install_frappe_bench
    fi
    
    # Initialize bench if it doesn't exist
    if [[ ! -d "$BENCH_DIR" ]]; then
        print_status "Initializing bench at $BENCH_DIR"
        bench init "$BENCH_DIR" --frappe-branch "$FRAPPE_BRANCH"
    fi
    
    # Create site and install ERPNext
    create_site "$BENCH_DIR"
    install_erpnext "$BENCH_DIR"
    
    # Setup development environment if requested
    if [[ "$SETUP_DEV" == "yes" ]]; then
        setup_development "$BENCH_DIR"
    fi
    
    print_success "ERPNext installation completed successfully!"
    print_status "You can now run 'bench start' in $BENCH_DIR to start the server"
    print_status "Access your site at: http://$SITE_NAME:8000"
    print_status "Admin credentials: Administrator / admin"
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi