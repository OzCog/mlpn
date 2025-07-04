# ERPNext Local Setup Makefile
# Common tasks for ERPNext local installation and deployment

.PHONY: help install check setup start stop restart clean backup restore update deps

# Default site and bench configuration
SITE_NAME ?= erpnext.local
BENCH_DIR ?= frappe-bench
ADMIN_PASSWORD ?= admin

# Colors for output
BLUE = \033[94m
GREEN = \033[92m
YELLOW = \033[93m
RED = \033[91m
NC = \033[0m

help: ## Show this help message
	@echo "$(BLUE)ERPNext Local Setup Makefile$(NC)"
	@echo
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo
	@echo "$(GREEN)Configuration:$(NC)"
	@echo "  SITE_NAME: $(SITE_NAME)"
	@echo "  BENCH_DIR: $(BENCH_DIR)"
	@echo "  ADMIN_PASSWORD: $(ADMIN_PASSWORD)"

check: ## Check system requirements
	@echo "$(BLUE)[INFO]$(NC) Checking system requirements..."
	@python3 setup.py check

deps: ## Install system dependencies
	@echo "$(BLUE)[INFO]$(NC) Installing system dependencies..."
	@./scripts/local_install.sh --skip-bench

install: ## Full installation (development setup)
	@echo "$(BLUE)[INFO]$(NC) Starting full ERPNext installation..."
	@./scripts/local_install.sh --site-name $(SITE_NAME) --bench-dir $(BENCH_DIR) --dev

setup: ## Setup development environment
	@echo "$(BLUE)[INFO]$(NC) Setting up development environment..."
	@cd $(BENCH_DIR) && bench setup requirements --dev
	@cd $(BENCH_DIR) && bench build

start: ## Start development server
	@echo "$(BLUE)[INFO]$(NC) Starting development server..."
	@cd $(BENCH_DIR) && bench start

stop: ## Stop development server
	@echo "$(BLUE)[INFO]$(NC) Stopping development server..."
	@pkill -f "bench start" || true

restart: stop start ## Restart development server

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)[INFO]$(NC) Cleaning build artifacts..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) clear-cache
	@cd $(BENCH_DIR) && find . -name "*.pyc" -delete
	@cd $(BENCH_DIR) && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

backup: ## Create backup of site
	@echo "$(BLUE)[INFO]$(NC) Creating backup..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) backup --with-files

restore: ## Restore site from backup (requires BACKUP_FILE)
	@echo "$(BLUE)[INFO]$(NC) Restoring from backup..."
	@if [ -z "$(BACKUP_FILE)" ]; then echo "$(RED)[ERROR]$(NC) BACKUP_FILE is required"; exit 1; fi
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) restore $(BACKUP_FILE)

update: ## Update ERPNext and apps
	@echo "$(BLUE)[INFO]$(NC) Updating ERPNext..."
	@cd $(BENCH_DIR) && bench update

migrate: ## Migrate database
	@echo "$(BLUE)[INFO]$(NC) Migrating database..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) migrate

build: ## Build assets
	@echo "$(BLUE)[INFO]$(NC) Building assets..."
	@cd $(BENCH_DIR) && bench build

build-prod: ## Build assets for production
	@echo "$(BLUE)[INFO]$(NC) Building assets for production..."
	@cd $(BENCH_DIR) && bench build --production

deploy: ## Deploy to production
	@echo "$(BLUE)[INFO]$(NC) Deploying to production..."
	@./scripts/local_deploy.sh --site-name $(SITE_NAME) --bench-dir $(BENCH_DIR)

test: ## Run tests
	@echo "$(BLUE)[INFO]$(NC) Running tests..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) run-tests

test-app: ## Run tests for ERPNext app
	@echo "$(BLUE)[INFO]$(NC) Running ERPNext tests..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) run-tests --app erpnext

console: ## Open ERPNext console
	@echo "$(BLUE)[INFO]$(NC) Opening ERPNext console..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) console

shell: ## Open Python shell with ERPNext context
	@echo "$(BLUE)[INFO]$(NC) Opening Python shell..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) execute "import frappe; frappe.init(site='$(SITE_NAME)'); frappe.connect()"

logs: ## View logs
	@echo "$(BLUE)[INFO]$(NC) Viewing logs..."
	@cd $(BENCH_DIR) && tail -f logs/web.log

status: ## Show service status
	@echo "$(BLUE)[INFO]$(NC) Service status:"
	@systemctl is-active --quiet mariadb && echo "$(GREEN)✓$(NC) MariaDB: Running" || echo "$(RED)✗$(NC) MariaDB: Not running"
	@systemctl is-active --quiet redis-server && echo "$(GREEN)✓$(NC) Redis: Running" || echo "$(RED)✗$(NC) Redis: Not running"
	@systemctl is-active --quiet nginx && echo "$(GREEN)✓$(NC) Nginx: Running" || echo "$(RED)✗$(NC) Nginx: Not running"
	@systemctl is-active --quiet supervisor && echo "$(GREEN)✓$(NC) Supervisor: Running" || echo "$(RED)✗$(NC) Supervisor: Not running"

doctor: ## Run bench doctor
	@echo "$(BLUE)[INFO]$(NC) Running bench doctor..."
	@cd $(BENCH_DIR) && bench doctor

info: ## Show system information
	@echo "$(BLUE)[INFO]$(NC) System Information:"
	@echo "OS: $$(lsb_release -d 2>/dev/null | cut -f2 || uname -s)"
	@echo "Python: $$(python3 --version)"
	@echo "Node.js: $$(node --version 2>/dev/null || echo 'Not installed')"
	@echo "npm: $$(npm --version 2>/dev/null || echo 'Not installed')"
	@echo "Bench: $$(cd $(BENCH_DIR) 2>/dev/null && bench version 2>/dev/null || echo 'Not installed')"
	@echo "Site: $(SITE_NAME)"
	@echo "Bench Directory: $(BENCH_DIR)"

new-site: ## Create new site (requires SITE_NAME)
	@echo "$(BLUE)[INFO]$(NC) Creating new site: $(SITE_NAME)"
	@cd $(BENCH_DIR) && bench new-site $(SITE_NAME) --admin-password $(ADMIN_PASSWORD)
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) install-app erpnext

remove-site: ## Remove site (requires SITE_NAME)
	@echo "$(YELLOW)[WARNING]$(NC) This will permanently delete the site: $(SITE_NAME)"
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd $(BENCH_DIR) && bench drop-site $(SITE_NAME) --db-root-password; \
	fi

maintenance-on: ## Enable maintenance mode
	@echo "$(BLUE)[INFO]$(NC) Enabling maintenance mode..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) set-maintenance-mode on

maintenance-off: ## Disable maintenance mode
	@echo "$(BLUE)[INFO]$(NC) Disabling maintenance mode..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) set-maintenance-mode off

reset-db: ## Reset database (WARNING: This will delete all data)
	@echo "$(RED)[WARNING]$(NC) This will delete all data in the database!"
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		cd $(BENCH_DIR) && bench --site $(SITE_NAME) reinstall; \
	fi

quick-setup: ## Quick setup for development
	@echo "$(BLUE)[INFO]$(NC) Quick setup for development..."
	@make check
	@make deps
	@make install
	@echo "$(GREEN)[SUCCESS]$(NC) Setup completed! Run 'make start' to begin."

production-setup: ## Setup production environment
	@echo "$(BLUE)[INFO]$(NC) Setting up production environment..."
	@make install
	@make deploy
	@echo "$(GREEN)[SUCCESS]$(NC) Production setup completed!"

# Advanced targets
lint: ## Run linting
	@echo "$(BLUE)[INFO]$(NC) Running linting..."
	@cd $(BENCH_DIR) && find . -name "*.py" -path "./apps/*" -exec python3 -m flake8 {} \; || true

format: ## Format code
	@echo "$(BLUE)[INFO]$(NC) Formatting code..."
	@cd $(BENCH_DIR) && find . -name "*.py" -path "./apps/*" -exec python3 -m black {} \; || true

security-check: ## Run security checks
	@echo "$(BLUE)[INFO]$(NC) Running security checks..."
	@cd $(BENCH_DIR) && python3 -m bandit -r apps/erpnext/ -ll || true

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)[INFO]$(NC) Running benchmarks..."
	@cd $(BENCH_DIR) && bench --site $(SITE_NAME) execute "import frappe; frappe.utils.bench_helper.run_performance_test()"

# Help for advanced usage
advanced-help: ## Show advanced usage help
	@echo "$(BLUE)Advanced Usage:$(NC)"
	@echo
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make install SITE_NAME=mysite.local"
	@echo "  make backup SITE_NAME=production.local"
	@echo "  make restore SITE_NAME=mysite.local BACKUP_FILE=backup.sql.gz"
	@echo "  make new-site SITE_NAME=newsite.local ADMIN_PASSWORD=secret"
	@echo
	@echo "$(GREEN)Environment Variables:$(NC)"
	@echo "  SITE_NAME       - Site name (default: erpnext.local)"
	@echo "  BENCH_DIR       - Bench directory (default: frappe-bench)"
	@echo "  ADMIN_PASSWORD  - Admin password (default: admin)"
	@echo "  BACKUP_FILE     - Backup file for restore"
	@echo
	@echo "$(GREEN)Configuration Files:$(NC)"
	@echo "  config/templates/.env.local          - Local environment variables"
	@echo "  config/templates/.env.production     - Production environment variables"
	@echo "  config/templates/site_config_local.json - Local site configuration"
	@echo "  config/templates/site_config_production.json - Production site configuration"