#!/bin/bash
# Kartavya CLI Installation Script
# Quick installation for Kartavya SIEM NLP Assistant CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/kartavya-team/kartavya-cli.git"
INSTALL_DIR="$HOME/.local/share/kartavya-cli"
BIN_DIR="$HOME/.local/bin"
PYTHON_MIN_VERSION="3.9"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi

    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    required_version=$PYTHON_MIN_VERSION
    
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= tuple(map(int, '$required_version'.split('.'))) else 1)"; then
        log_error "Python $required_version or higher is required. Found: $python_version"
        exit 1
    fi
    
    log_info "Python version: $python_version ✓"
}

check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
    log_info "Git is available ✓"
}

create_directories() {
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    log_info "Created installation directories"
}

install_kartavya_cli() {
    log_info "Cloning Kartavya CLI repository..."
    
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR" || {
        log_error "Failed to clone repository"
        exit 1
    }
    
    log_info "Installing Kartavya CLI..."
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install the CLI
    pip install -e . || {
        log_error "Failed to install Kartavya CLI"
        exit 1
    }
    
    log_success "Kartavya CLI installed successfully!"
}

create_launcher_script() {
    cat > "$BIN_DIR/kartavya" << EOF
#!/bin/bash
source "$INSTALL_DIR/venv/bin/activate"
exec python -m kartavya_cli.main "\$@"
EOF
    
    chmod +x "$BIN_DIR/kartavya"
    
    # Create short alias
    cat > "$BIN_DIR/kvya" << EOF
#!/bin/bash
source "$INSTALL_DIR/venv/bin/activate"
exec python -m kartavya_cli.main "\$@"
EOF
    
    chmod +x "$BIN_DIR/kvya"
    
    log_info "Created launcher scripts"
}

setup_shell_integration() {
    # Add to PATH if not already there
    for shell_config in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
        if [ -f "$shell_config" ]; then
            if ! grep -q "$BIN_DIR" "$shell_config"; then
                echo "" >> "$shell_config"
                echo "# Kartavya CLI" >> "$shell_config"
                echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$shell_config"
                log_info "Added $BIN_DIR to PATH in $shell_config"
            fi
        fi
    done
}

show_completion_message() {
    echo ""
    echo -e "${GREEN}🎉 Kartavya CLI installation completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Reload your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo "2. Set up your API connection:"
    echo -e "   ${YELLOW}kartavya setup --url YOUR_API_URL --api-key YOUR_API_KEY${NC}"
    echo "3. Test the installation:"
    echo -e "   ${YELLOW}kartavya health${NC}"
    echo "4. Start using the CLI:"
    echo -e "   ${YELLOW}kartavya chat interactive${NC}"
    echo ""
    echo -e "${BLUE}Available commands:${NC}"
    echo "  - kartavya (or kvya) --help    Show all available commands"
    echo "  - kartavya chat interactive     Start interactive AI chat"
    echo "  - kartavya events list          List security events"
    echo "  - kartavya reports generate     Generate security reports"
    echo "  - kartavya query execute        Execute natural language queries"
    echo ""
    echo -e "${BLUE}Documentation:${NC} https://kartavya-cli.readthedocs.io"
    echo -e "${BLUE}Support:${NC} support@kartavya.dev"
}

# Main installation process
main() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    Kartavya CLI Installer                    ║
║                                                              ║
║            SIEM NLP Assistant Command Line Tool             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    log_info "Starting Kartavya CLI installation..."
    
    # Pre-flight checks
    check_python
    check_git
    
    # Installation
    create_directories
    install_kartavya_cli
    create_launcher_script
    setup_shell_integration
    
    # Completion
    show_completion_message
}

# Handle command line arguments
case "${1:-}" in
    --uninstall)
        log_info "Uninstalling Kartavya CLI..."
        rm -rf "$INSTALL_DIR"
        rm -f "$BIN_DIR/kartavya" "$BIN_DIR/kvya"
        log_success "Kartavya CLI uninstalled successfully!"
        ;;
    --help|-h)
        echo "Kartavya CLI Installation Script"
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (no option)   Install Kartavya CLI"
        echo "  --uninstall   Uninstall Kartavya CLI"
        echo "  --help, -h    Show this help message"
        ;;
    *)
        main
        ;;
esac
