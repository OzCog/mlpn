#!/bin/bash

# ERPNext Installation Validation Script
# This script validates the installation scripts and documentation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if file exists and is executable
check_file() {
    local file="$1"
    local desc="$2"
    
    if [[ -f "$file" ]]; then
        if [[ -x "$file" ]]; then
            print_success "✓ $desc exists and is executable"
            return 0
        else
            print_warning "⚠ $desc exists but is not executable"
            return 1
        fi
    else
        print_error "✗ $desc does not exist"
        return 1
    fi
}

# Function to check if directory exists
check_directory() {
    local dir="$1"
    local desc="$2"
    
    if [[ -d "$dir" ]]; then
        print_success "✓ $desc exists"
        return 0
    else
        print_error "✗ $desc does not exist"
        return 1
    fi
}

# Function to validate script syntax
validate_script() {
    local script="$1"
    local desc="$2"
    
    if bash -n "$script" 2>/dev/null; then
        print_success "✓ $desc has valid syntax"
        return 0
    else
        print_error "✗ $desc has syntax errors"
        return 1
    fi
}

# Function to validate JSON syntax
validate_json() {
    local json_file="$1"
    local desc="$2"
    
    if python3 -m json.tool "$json_file" > /dev/null 2>&1; then
        print_success "✓ $desc has valid JSON syntax"
        return 0
    else
        print_error "✗ $desc has invalid JSON syntax"
        return 1
    fi
}

# Function to check documentation completeness
check_documentation() {
    local file="$1"
    local desc="$2"
    
    if [[ -f "$file" && -s "$file" ]]; then
        local word_count=$(wc -w < "$file")
        if [[ $word_count -gt 100 ]]; then
            print_success "✓ $desc is comprehensive ($word_count words)"
            return 0
        else
            print_warning "⚠ $desc is too short ($word_count words)"
            return 1
        fi
    else
        print_error "✗ $desc is missing or empty"
        return 1
    fi
}

# Main validation function
main() {
    print_status "Starting ERPNext installation validation..."
    
    local errors=0
    
    # Check scripts
    print_status "Checking installation scripts..."
    check_file "scripts/local_install.sh" "Local installation script" || ((errors++))
    check_file "scripts/local_deploy.sh" "Local deployment script" || ((errors++))
    check_file "setup.py" "Python setup script" || ((errors++))
    
    # Validate script syntax
    print_status "Validating script syntax..."
    validate_script "scripts/local_install.sh" "Local installation script" || ((errors++))
    validate_script "scripts/local_deploy.sh" "Local deployment script" || ((errors++))
    
    # Check Python script syntax
    if python3 -m py_compile setup.py 2>/dev/null; then
        print_success "✓ Python setup script has valid syntax"
    else
        print_error "✗ Python setup script has syntax errors"
        ((errors++))
    fi
    
    # Check configuration templates
    print_status "Checking configuration templates..."
    check_directory "config/templates" "Configuration templates directory" || ((errors++))
    
    for template in config/templates/*.json; do
        if [[ -f "$template" ]]; then
            validate_json "$template" "$(basename "$template")" || ((errors++))
        fi
    done
    
    # Check documentation
    print_status "Checking documentation..."
    check_documentation "README.md" "README.md" || ((errors++))
    check_documentation "docs/installation.md" "Installation guide" || ((errors++))
    check_documentation "docs/troubleshooting.md" "Troubleshooting guide" || ((errors++))
    
    # Check Makefile
    print_status "Checking Makefile..."
    if [[ -f "Makefile" ]]; then
        if make -n help > /dev/null 2>&1; then
            print_success "✓ Makefile is valid"
        else
            print_error "✗ Makefile has errors"
            ((errors++))
        fi
    else
        print_error "✗ Makefile is missing"
        ((errors++))
    fi
    
    # Test script help functions
    print_status "Testing script help functions..."
    if ./scripts/local_install.sh --help > /dev/null 2>&1; then
        print_success "✓ Local installation script help works"
    else
        print_error "✗ Local installation script help fails"
        ((errors++))
    fi
    
    if ./scripts/local_deploy.sh --help > /dev/null 2>&1; then
        print_success "✓ Local deployment script help works"
    else
        print_error "✗ Local deployment script help fails"
        ((errors++))
    fi
    
    if python3 setup.py check > /dev/null 2>&1; then
        print_success "✓ Python setup script check works"
    else
        print_error "✗ Python setup script check fails"
        ((errors++))
    fi
    
    # Check for required directories
    print_status "Checking directory structure..."
    for dir in "scripts" "config" "docs" "erpnext"; do
        check_directory "$dir" "$dir directory" || ((errors++))
    done
    
    # Summary
    print_status "Validation complete!"
    
    if [[ $errors -eq 0 ]]; then
        print_success "All checks passed! ✓"
        print_status "Installation scripts and documentation are ready to use."
        print_status ""
        print_status "Quick start commands:"
        print_status "  ./scripts/local_install.sh --dev"
        print_status "  make quick-setup"
        print_status "  python3 setup.py full-setup"
        return 0
    else
        print_error "Found $errors error(s). Please fix them before using the scripts."
        return 1
    fi
}

# Run validation
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi