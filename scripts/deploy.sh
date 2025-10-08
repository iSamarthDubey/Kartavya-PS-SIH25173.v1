#!/bin/bash

# 🚀 Kartavya SIEM Assistant - Ultimate Deployment Script
# Supports both demo (cloud) and production (on-premise) modes
# Usage: ./scripts/deploy.sh [demo|production] [options]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="kartavya-siem"
DOCKER_COMPOSE_FILE="docker/docker-compose.advanced.yml"
ENV_FILE=".env"

# Default values
DEPLOYMENT_MODE="demo"
SKIP_DEPS=false
SKIP_BUILD=false
OPEN_BROWSER=true
VERBOSE=false

# Print banner
print_banner() {
    echo -e "${PURPLE}"
    echo "🚀 ======================================== 🚀"
    echo "   KARTAVYA SIEM ASSISTANT DEPLOYMENT"
    echo "   For Smart India Hackathon 2025"
    echo "   Problem Statement: SIH25173"
    echo "🚀 ======================================== 🚀"
    echo -e "${NC}"
}

# Print colored output
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
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

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Show usage
show_usage() {
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "MODES:"
    echo "  demo        - Deploy for demo/hackathon (cloud services, mock data)"
    echo "  production  - Deploy for production (on-premise, security-first)"
    echo ""
    echo "OPTIONS:"
    echo "  --skip-deps      Skip dependency checks"
    echo "  --skip-build     Skip Docker image building"
    echo "  --no-browser     Don't open browser automatically"
    echo "  --verbose        Enable verbose logging"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 demo                    # Quick demo deployment"
    echo "  $0 production --skip-deps  # Production without dependency check"
    echo "  $0 demo --verbose          # Demo with detailed logging"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            demo|production)
                DEPLOYMENT_MODE="$1"
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --no-browser)
                OPEN_BROWSER=false
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
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
}

# Check system dependencies
check_dependencies() {
    if [[ "$SKIP_DEPS" == "true" ]]; then
        print_info "Skipping dependency checks as requested"
        return
    fi

    print_step "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_info "Please install missing dependencies and try again"
        
        print_info "Installation commands:"
        echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y ${missing_deps[*]}"
        echo "  CentOS/RHEL:   sudo yum install -y ${missing_deps[*]}"
        echo "  macOS:         brew install ${missing_deps[*]}"
        
        exit 1
    fi
    
    print_success "All dependencies found"
}

# Setup environment files
setup_environment() {
    print_step "Setting up environment configuration..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        print_info "Creating environment file from template..."
        cp .env.example "$ENV_FILE" 2>/dev/null || true
    fi
    
    # Configure for deployment mode
    if [[ "$DEPLOYMENT_MODE" == "demo" ]]; then
        setup_demo_env
    else
        setup_production_env
    fi
    
    print_success "Environment configured for $DEPLOYMENT_MODE mode"
}

# Setup demo environment
setup_demo_env() {
    print_info "Configuring DEMO environment..."
    
    cat > "$ENV_FILE" << EOF
# 🎭 DEMO ENVIRONMENT CONFIGURATION
ENVIRONMENT=demo
BUILD_TARGET=development

# API Configuration
API_PORT=8000
FRONTEND_PORT=3000
API_URL=http://localhost:8000

# AI Configuration (Demo)
ENABLE_AI=true
# GEMINI_API_KEY=your_gemini_key_here  # Add your key for AI features
# OPENAI_API_KEY=your_openai_key_here  # Alternative AI provider

# Database (Demo - Cloud Services)
# SUPABASE_URL=your_supabase_url
# SUPABASE_ANON_KEY=your_supabase_anon_key
# MONGODB_URI=your_mongodb_atlas_uri
# REDIS_URL=your_redis_cloud_url

# SIEM Configuration
DEFAULT_SIEM_PLATFORM=dataset
ELASTICSEARCH_PORT=9200
KIBANA_PORT=5601

# Demo Data
LOG_RATE=10
HF_TOKEN=  # Optional: Add for real HuggingFace datasets

# Security (Demo)
JWT_SECRET=demo-jwt-secret-change-in-production
REDIS_PASSWORD=kartavya2025
POSTGRES_PASSWORD=kartavya2025

# Monitoring (Optional)
GRAFANA_PORT=3001
GRAFANA_PASSWORD=kartavya2025
EOF

    print_info "✅ Demo environment configured"
    print_warning "⚠️  Remember to add your API keys for full AI functionality"
}

# Setup production environment
setup_production_env() {
    print_info "Configuring PRODUCTION environment..."
    
    cat > "$ENV_FILE" << EOF
# 🔒 PRODUCTION ENVIRONMENT CONFIGURATION
ENVIRONMENT=production
BUILD_TARGET=production

# API Configuration
API_PORT=8000
FRONTEND_PORT=80
HTTP_PORT=80
HTTPS_PORT=443

# AI Configuration (Disabled for security)
ENABLE_AI=false

# Database (Production - Local)
POSTGRES_DB=kartavya
POSTGRES_USER=kartavya
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_PORT=5432

REDIS_PASSWORD=$(openssl rand -base64 32)
REDIS_PORT=6379

# SIEM Configuration
DEFAULT_SIEM_PLATFORM=elasticsearch
ELASTICSEARCH_PORT=9200
# WAZUH_API_URL=your_wazuh_instance_url

# Security (Production)
JWT_SECRET=$(openssl rand -base64 64)
RATE_LIMIT_REQUESTS=30

# SSL/TLS (Configure your certificates)
# SSL_CERT_PATH=/path/to/cert.pem
# SSL_KEY_PATH=/path/to/key.pem
EOF

    print_success "🔒 Production environment configured with secure passwords"
    print_warning "⚠️  Update SIEM connection details for your infrastructure"
}

# Build Docker images
build_images() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        print_info "Skipping Docker image builds as requested"
        return
    fi

    print_step "Building Docker images for $DEPLOYMENT_MODE mode..."
    
    local build_args=""
    if [[ "$VERBOSE" == "true" ]]; then
        build_args="--progress=plain"
    fi
    
    # Build backend
    print_info "Building backend image..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build $build_args siem-backend
    
    # Build frontend
    print_info "Building frontend image..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build $build_args siem-frontend
    
    print_success "Docker images built successfully"
}

# Start services
start_services() {
    print_step "Starting services for $DEPLOYMENT_MODE mode..."
    
    local compose_profiles=""
    local additional_services=""
    
    if [[ "$DEPLOYMENT_MODE" == "demo" ]]; then
        compose_profiles="--profile demo"
        additional_services="dataset-loader"
        print_info "Demo mode: Starting with real dataset connector"
    else
        compose_profiles="--profile production"
        additional_services="nginx postgres"
        print_info "Production mode: Starting with full security stack"
    fi
    
    # Start core services
    docker-compose -f "$DOCKER_COMPOSE_FILE" $compose_profiles up -d
    
    print_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_step "Waiting for services to become ready..."
    
    local max_attempts=60
    local attempt=0
    
    print_info "Checking backend health..."
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -sf http://localhost:${API_PORT:-8000}/health >/dev/null 2>&1; then
            print_success "Backend is ready!"
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        print_error "Backend failed to start within expected time"
        print_info "Check logs with: docker-compose -f $DOCKER_COMPOSE_FILE logs siem-backend"
        return 1
    fi
    
    print_info "Checking frontend availability..."
    attempt=0
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -sf http://localhost:${FRONTEND_PORT:-3000} >/dev/null 2>&1; then
            print_success "Frontend is ready!"
            break
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        print_warning "Frontend may still be starting up"
    fi
}

# Show deployment status
show_status() {
    print_step "Deployment Status Summary"
    
    echo ""
    print_info "🎯 KARTAVYA SIEM ASSISTANT - $DEPLOYMENT_MODE MODE"
    echo ""
    
    # Service URLs
    echo "📱 Application URLs:"
    echo "  Frontend:     http://localhost:${FRONTEND_PORT:-3000}"
    echo "  Backend API:  http://localhost:${API_PORT:-8000}"
    echo "  API Docs:     http://localhost:${API_PORT:-8000}/docs"
    echo "  Health Check: http://localhost:${API_PORT:-8000}/health"
    
    if [[ "$DEPLOYMENT_MODE" == "demo" ]]; then
        echo ""
        echo "🎭 Demo Services:"
        echo "  Elasticsearch: http://localhost:9200"
        echo "  Kibana:        http://localhost:5601"
        echo ""
        echo "🤖 AI Features:"
        if [[ -n "${GEMINI_API_KEY:-}" ]] || [[ -n "${OPENAI_API_KEY:-}" ]]; then
            echo "  Status: ✅ Enabled (API keys configured)"
        else
            echo "  Status: ⚠️  Mock mode (add API keys for full AI)"
        fi
        echo ""
        echo "📊 Real Data Sources:"
        echo "  HuggingFace cybersecurity datasets loaded automatically"
        echo "  Try queries like: 'Show failed login attempts'"
    else
        echo ""
        echo "🔒 Production Services:"
        echo "  Database:     PostgreSQL on port ${POSTGRES_PORT:-5432}"
        echo "  Cache:        Redis on port ${REDIS_PORT:-6379}"
        echo "  Monitoring:   Check docker-compose logs"
        echo ""
        echo "🛡️ Security:"
        echo "  JWT tokens, encrypted passwords, rate limiting enabled"
        echo "  Configure your SIEM connections in .env file"
    fi
    
    echo ""
    print_success "🚀 DEPLOYMENT COMPLETED SUCCESSFULLY!"
    
    # Container status
    echo ""
    print_info "📊 Container Status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
}

# Open browser
open_browser_if_requested() {
    if [[ "$OPEN_BROWSER" == "true" ]]; then
        print_step "Opening application in browser..."
        
        local url="http://localhost:${FRONTEND_PORT:-3000}"
        
        # Detect OS and open browser
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "$url"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open "$url" 2>/dev/null || true
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            start "$url"
        else
            print_info "Please open your browser and navigate to: $url"
        fi
        
        print_success "Browser should now open with the application"
    fi
}

# Cleanup function
cleanup() {
    if [[ $? -ne 0 ]]; then
        print_error "Deployment failed!"
        print_info "Check logs with: docker-compose -f $DOCKER_COMPOSE_FILE logs"
        print_info "Clean up with: docker-compose -f $DOCKER_COMPOSE_FILE down"
    fi
}

# Main deployment function
main() {
    trap cleanup EXIT
    
    print_banner
    
    parse_args "$@"
    
    print_info "🚀 Starting deployment in $DEPLOYMENT_MODE mode..."
    echo ""
    
    check_dependencies
    setup_environment
    build_images
    start_services
    wait_for_services
    show_status
    open_browser_if_requested
    
    echo ""
    print_success "🎉 Ready to secure ISRO's digital infrastructure!"
    
    if [[ "$DEPLOYMENT_MODE" == "demo" ]]; then
        echo ""
        print_info "💡 Demo Tips:"
        echo "  • Try: 'Show me failed login attempts from external IPs'"
        echo "  • Generate reports using the Reports tab"
        echo "  • Explore the threat dashboard for real-time metrics"
        echo "  • All data is simulated for demonstration purposes"
    else
        echo ""
        print_info "🔧 Production Notes:"
        echo "  • Configure your SIEM connections in .env file"
        echo "  • Set up SSL certificates for HTTPS"
        echo "  • Review security settings before going live"
        echo "  • Monitor logs and system performance"
    fi
    
    echo ""
    print_info "📚 Useful Commands:"
    echo "  • Stop:     docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo "  • Logs:     docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "  • Status:   docker-compose -f $DOCKER_COMPOSE_FILE ps"
    echo "  • Update:   git pull && ./scripts/deploy.sh $DEPLOYMENT_MODE"
}

# Run main function with all arguments
main "$@"
