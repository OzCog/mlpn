#!/usr/bin/env python3
"""
ERPNext Local Setup Helper
A Python script to help with local ERPNext setup and management tasks.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path

# Colors for output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def print_status(message):
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {message}")

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        sanitized_cmd = cmd.replace(db_password, "[REDACTED]") if 'db_password' in locals() else cmd
        sanitized_stderr = e.stderr.replace(db_password, "[REDACTED]") if 'db_password' in locals() else e.stderr
        print_error(f"Command failed: {sanitized_cmd}")
        print_error(f"Error: {sanitized_stderr}")
        return None

def check_system_requirements():
    """Check if system requirements are met."""
    print_status("Checking system requirements...")
    
    requirements = {
        'python3': {'cmd': 'python3 --version', 'min_version': '3.10'},
        'node': {'cmd': 'node --version', 'min_version': '18.0'},
        'npm': {'cmd': 'npm --version', 'min_version': '8.0'},
        'git': {'cmd': 'git --version', 'min_version': '2.0'},
        'mysql': {'cmd': 'mysql --version', 'min_version': '10.6'},
        'redis': {'cmd': 'redis-server --version', 'min_version': '5.0'},
    }
    
    for tool, info in requirements.items():
        result = run_command(info['cmd'], check=False)
        if result and result.returncode == 0:
            print_success(f"✓ {tool} is installed")
        else:
            print_error(f"✗ {tool} is not installed or not in PATH")
    
    return True

def install_dependencies():
    """Install system dependencies."""
    print_status("Installing system dependencies...")
    
    # Detect OS
    import platform
    os_name = platform.system().lower()
    
    if os_name == 'linux':
        # Check if Ubuntu/Debian
        if Path('/etc/debian_version').exists():
            cmd = """
            sudo apt-get update && 
            sudo apt-get install -y python3-dev python3-pip python3-venv redis-server \
                                   mariadb-server mariadb-client libmariadb-dev libffi-dev \
                                   libssl-dev wkhtmltopdf curl git npm nodejs libcups2-dev
            """
            run_command(cmd)
        # Check if CentOS/RHEL/Fedora
        elif Path('/etc/redhat-release').exists():
            cmd = """
            sudo yum install -y python3-devel python3-pip redis mariadb-server mariadb-devel \
                               libffi-devel openssl-devel wkhtmltopdf curl git npm nodejs cups-devel
            """
            run_command(cmd)
    elif os_name == 'darwin':
        # macOS
        cmd = "brew install python3 redis mariadb node npm wkhtmltopdf"
        run_command(cmd)
    
    print_success("Dependencies installed successfully")

def setup_database(site_name="erpnext.local", db_user=None, db_password=None):
    """Setup MariaDB database."""
    print_status("Setting up database...")
    
    db_user = db_user or site_name.replace('.', '_')
    db_password = db_password or db_user
    
    # Start MariaDB
    run_command("sudo systemctl start mariadb", check=False)
    run_command("sudo systemctl enable mariadb", check=False)
    
    # Create database and user
    sql_commands = f"""
    CREATE DATABASE IF NOT EXISTS `{db_user}`;
    CREATE USER IF NOT EXISTS '{db_user}'@'localhost' IDENTIFIED BY '{db_password}';
    GRANT ALL PRIVILEGES ON `{db_user}`.* TO '{db_user}'@'localhost';
    FLUSH PRIVILEGES;
    """
    
    run_command(f'mysql -u root -p -e "{sql_commands}"')
    print_success("Database setup completed")

def install_bench():
    """Install frappe-bench."""
    print_status("Installing frappe-bench...")
    
    # Install frappe-bench
    run_command("pip3 install --user frappe-bench")
    
    # Add to PATH
    home_dir = Path.home()
    bashrc_path = home_dir / '.bashrc'
    
    path_export = 'export PATH="$HOME/.local/bin:$PATH"'
    
    if bashrc_path.exists():
        with open(bashrc_path, 'r') as f:
            content = f.read()
        
        if path_export not in content:
            with open(bashrc_path, 'a') as f:
                f.write(f'\n{path_export}\n')
    
    print_success("frappe-bench installed successfully")

def init_bench(bench_dir="frappe-bench", frappe_branch="develop"):
    """Initialize bench."""
    print_status(f"Initializing bench at {bench_dir}...")
    
    if Path(bench_dir).exists():
        print_warning(f"Bench directory {bench_dir} already exists")
        return
    
    cmd = f"bench init {bench_dir} --frappe-branch {frappe_branch}"
    run_command(cmd)
    
    print_success("Bench initialized successfully")

def create_site(bench_dir, site_name, db_name=None, admin_password="admin"):
    """Create a new site."""
    print_status(f"Creating site: {site_name}")
    
    db_name = db_name or site_name.replace('.', '_')
    
    cmd = f"bench new-site {site_name} --db-name {db_name} --admin-password {admin_password}"
    run_command(cmd, cwd=bench_dir)
    
    print_success(f"Site {site_name} created successfully")

def install_erpnext(bench_dir, site_name, repo_url=None):
    """Install ERPNext app."""
    print_status("Installing ERPNext...")
    
    # Get ERPNext app
    if repo_url:
        cmd = f"bench get-app erpnext {repo_url}"
    else:
        cmd = "bench get-app erpnext"
    
    run_command(cmd, cwd=bench_dir)
    
    # Install ERPNext on site
    cmd = f"bench --site {site_name} install-app erpnext"
    run_command(cmd, cwd=bench_dir)
    
    print_success("ERPNext installed successfully")

def start_development_server(bench_dir):
    """Start the development server."""
    print_status("Starting development server...")
    print_status("Press Ctrl+C to stop the server")
    
    cmd = "bench start"
    subprocess.run(cmd, shell=True, cwd=bench_dir)

def setup_production(bench_dir, site_name):
    """Setup production environment."""
    print_status("Setting up production environment...")
    
    # Switch to production mode
    commands = [
        f"bench --site {site_name} set-config developer_mode 0",
        f"bench --site {site_name} set-config server_script_enabled 0",
        f"bench --site {site_name} set-config disable_website_cache 0",
        "bench build --production",
        "bench setup nginx",
        "bench setup supervisor"
    ]
    
    for cmd in commands:
        run_command(cmd, cwd=bench_dir)
    
    print_success("Production environment setup completed")

def backup_site(bench_dir, site_name, with_files=True):
    """Backup a site."""
    print_status(f"Backing up site: {site_name}")
    
    cmd = f"bench --site {site_name} backup"
    if with_files:
        cmd += " --with-files"
    
    run_command(cmd, cwd=bench_dir)
    print_success("Backup completed")

def restore_site(bench_dir, site_name, backup_file):
    """Restore a site from backup."""
    print_status(f"Restoring site: {site_name}")
    
    cmd = f"bench --site {site_name} restore {backup_file}"
    run_command(cmd, cwd=bench_dir)
    print_success("Restore completed")

def update_system(bench_dir):
    """Update ERPNext and apps."""
    print_status("Updating system...")
    
    cmd = "bench update"
    run_command(cmd, cwd=bench_dir)
    print_success("System updated")

def main():
    parser = argparse.ArgumentParser(description="ERPNext Local Setup Helper")
    parser.add_argument("action", choices=[
        "check", "install-deps", "setup-db", "install-bench", 
        "init-bench", "create-site", "install-erpnext", "start", 
        "setup-production", "backup", "restore", "update", "full-setup"
    ], help="Action to perform")
    
    parser.add_argument("--site-name", default="erpnext.local", help="Site name")
    parser.add_argument("--bench-dir", default="frappe-bench", help="Bench directory")
    parser.add_argument("--db-name", help="Database name")
    parser.add_argument("--admin-password", default="admin", help="Admin password")
    parser.add_argument("--repo-url", help="ERPNext repository URL")
    parser.add_argument("--backup-file", help="Backup file to restore")
    
    args = parser.parse_args()
    
    if args.action == "check":
        check_system_requirements()
    elif args.action == "install-deps":
        install_dependencies()
    elif args.action == "setup-db":
        setup_database(args.site_name)
    elif args.action == "install-bench":
        install_bench()
    elif args.action == "init-bench":
        init_bench(args.bench_dir)
    elif args.action == "create-site":
        create_site(args.bench_dir, args.site_name, args.db_name, args.admin_password)
    elif args.action == "install-erpnext":
        install_erpnext(args.bench_dir, args.site_name, args.repo_url)
    elif args.action == "start":
        start_development_server(args.bench_dir)
    elif args.action == "setup-production":
        setup_production(args.bench_dir, args.site_name)
    elif args.action == "backup":
        backup_site(args.bench_dir, args.site_name)
    elif args.action == "restore":
        if not args.backup_file:
            print_error("--backup-file is required for restore action")
            sys.exit(1)
        restore_site(args.bench_dir, args.site_name, args.backup_file)
    elif args.action == "update":
        update_system(args.bench_dir)
    elif args.action == "full-setup":
        # Full setup process
        print_status("Starting full ERPNext setup...")
        check_system_requirements()
        install_dependencies()
        setup_database(args.site_name)
        install_bench()
        init_bench(args.bench_dir)
        create_site(args.bench_dir, args.site_name, args.db_name, args.admin_password)
        install_erpnext(args.bench_dir, args.site_name, args.repo_url)
        print_success("Full setup completed!")
        print_status(f"You can now run: python3 setup.py start --bench-dir {args.bench_dir}")

if __name__ == "__main__":
    main()