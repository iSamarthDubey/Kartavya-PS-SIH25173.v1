#!/bin/bash

# Kartavya CLI Installation Script
# Supports Linux, macOS, and Windows (via Git Bash/WSL)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
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

# Check if Python is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python 3.9+ is required but not found"
        print_info "Please install Python from https://python.org"
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_info "Found Python $PYTHON_VERSION"
    
    if [[ "$(echo "$PYTHON_VERSION 3.9" | tr " " "\n" | sort -V | head -n1)" != "3.9" ]]; then
        print_error "Python 3.9+ is required, but found Python $PYTHON_VERSION"
        exit 1
    fi
}

# Check if pip is available
check_pip() {
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_error "pip is required but not found"
        print_info "Please install pip or use the --get-pip option"
        exit 1
    fi
    print_info "pip is available"
}

# Install via pip
install_pip() {
    print_info "Installing Kartavya CLI via pip..."
    
    if command -v pipx &> /dev/null; then
        print_info "pipx detected, using isolated installation"
        pipx install kartavya-cli
    else
        print_info "Installing with pip"
        $PYTHON_CMD -m pip install --user kartavya-cli
        
        # Add user bin to PATH if not already there
        USER_BIN_PATH="$($PYTHON_CMD -m site --user-base)/bin"
        if [[ ":$PATH:" != *":$USER_BIN_PATH:"* ]]; then
            print_warning "Add $USER_BIN_PATH to your PATH to use kartavya command"
            echo "Add this to your shell profile (.bashrc, .zshrc, etc.):"
            echo "export PATH=\"\$PATH:$USER_BIN_PATH\""
        fi
    fi
}

# Install from source
install_source() {
    print_info "Installing Kartavya CLI from source..."
    
    if [[ ! -f "pyproject.toml" ]]; then
        print_error "pyproject.toml not found. Are you in the correct directory?"
        exit 1
    fi
    
    print_info "Installing dependencies..."
    $PYTHON_CMD -m pip install --user -e .
    
    print_success "Kartavya CLI installed from source"
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    if command -v kartavya &> /dev/null; then
        VERSION=$(kartavya version --json 2>/dev/null | grep -o '"version": "[^"]*"' | cut -d'"' -f4)
        print_success "Kartavya CLI v$VERSION installed successfully!"
        return 0
    else
        print_error "Installation verification failed"
        print_info "Try running: kartavya --help"
        return 1
    fi
}

# Setup configuration
setup_config() {
    print_info "Setting up initial configuration..."
    
    if command -v kartavya &> /dev/null; then
        print_info "Run 'kartavya setup' to configure your API settings"
        
        # Ask if user wants to run setup now
        read -p "Would you like to run the setup wizard now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kartavya setup
        fi
    else
        print_warning "kartavya command not found. Please check your PATH."
    fi
}

# Main installation function
main() {
    echo "🔒 Kartavya CLI Installation Script"
    echo "=================================="
    echo
    
    # Parse command line arguments
    INSTALL_METHOD="pip"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --source)
                INSTALL_METHOD="source"
                shift
                ;;
            --pip)
                INSTALL_METHOD="pip"
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --pip     Install from PyPI (default)"
                echo "  --source  Install from source"
                echo "  --help    Show this help"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    check_python
    check_pip
    
    # Install based on method
    case $INSTALL_METHOD in
        "pip")
            install_pip
            ;;
        "source")
            install_source
            ;;
    esac
    
    # Verify and setup
    if verify_installation; then
        setup_config
        
        echo
        print_success "Installation complete!"
        print_info "Quick start commands:"
        echo "  kartavya setup          # Configure API settings"
        echo "  kartavya health         # Test connectivity"
        echo "  kartavya chat ask 'help' # Start chatting"
        echo "  kartavya --help         # View all commands"
        echo
        print_info "Documentation: https://github.com/kartavya-team/kartavya-cli"
    else
        print_error "Installation failed"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
