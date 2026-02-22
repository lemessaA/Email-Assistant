#!/bin/bash

# Email Assistant Docker Deployment Script
# This script sets up and deploys the complete Email Assistant stack

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
}

# Create necessary directories
setup_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/knowledge_base
    mkdir -p data/drafts
    mkdir -p data/attachments
    mkdir -p logs
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    print_status "Directories created successfully"
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.production ]; then
            cp .env.production .env
            print_status "Copied .env.production to .env"
        else
            print_warning ".env file not found. Creating from template..."
            cat > .env << EOF
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yourcompany.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourcompany.com

# IMAP Configuration
IMAP_SERVER=imap.gmail.com
IMAP_USERNAME=your-email@yourcompany.com
IMAP_PASSWORD=your-app-password

# LLM Configuration
PRIMARY_LLM=ollama/llama2
OLLAMA_BASE_URL=http://ollama:11434
LLM_TEMPERATURE=0.1

# Search Configuration
SEARCH_API_KEY=your-search-api-key
SEARCH_ENGINE=serper

# Calendar Configuration
CALENDAR_API_KEY=your-calendar-api-key
CALENDAR_PROVIDER=google

# Database Configuration
DATABASE_URL=sqlite:///./data/email_assistant.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-super-secret-key-change-this

# Redis Configuration
REDIS_URL=redis://redis:6379
EOF
            print_warning "Please edit .env file with your actual configuration"
        fi
    fi
}

# Generate SSL certificates (self-signed for development)
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    if [ ! -f nginx/ssl/cert.pem ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
            2>/dev/null || true
        print_status "Self-signed SSL certificates generated"
    fi
}

# Pull required Docker images
pull_images() {
    print_status "Pulling required Docker images..."
    
    docker pull redis:7-alpine
    docker pull ollama/ollama:latest
    docker pull nginx:alpine
    docker pull prom/prometheus:latest
    docker pull grafana/grafana:latest
    
    print_status "Docker images pulled successfully"
}

# Build custom images
build_images() {
    print_status "Building custom Docker images..."
    
    # Build main application
    docker-compose build email-assistant
    
    # Build Streamlit UI
    docker-compose build streamlit-ui
    
    print_status "Custom images built successfully"
}

# Start services
start_services() {
    print_status "Starting Email Assistant services..."
    
    # Start core services first
    docker-compose up -d redis ollama
    
    # Wait for Ollama to be ready
    print_status "Waiting for Ollama to start..."
    sleep 10
    
    # Download LLM model if not present
    docker-compose exec ollama ollama pull llama2 || true
    
    # Start remaining services
    docker-compose up -d email-assistant streamlit-ui nginx
    
    # Start monitoring services (optional)
    read -p "Start monitoring services (Prometheus/Grafana)? [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose up -d prometheus grafana
        print_status "Monitoring services started"
        print_status "Grafana: http://localhost:3000 (admin/admin123)"
        print_status "Prometheus: http://localhost:9090"
    fi
    
    print_status "All services started successfully"
}

# Show service status
show_status() {
    print_header "Service Status"
    docker-compose ps
    
    print_header "Access URLs"
    echo -e "${GREEN}Email Assistant API:${NC} http://localhost:8000"
    echo -e "${GREEN}Streamlit UI:${NC} http://localhost:8501"
    echo -e "${GREEN}Nginx (HTTPS):${NC} https://localhost"
    echo -e "${GREEN}Redis:${NC} localhost:6379"
    echo -e "${GREEN}Ollama:${NC} http://localhost:11434"
    
    if docker-compose ps | grep -q grafana; then
        echo -e "${GREEN}Grafana:${NC} http://localhost:3000 (admin/admin123)"
    fi
    
    if docker-compose ps | grep -q prometheus; then
        echo -e "${GREEN}Prometheus:${NC} http://localhost:9090"
    fi
}

# Stop services
stop_services() {
    print_status "Stopping Email Assistant services..."
    docker-compose down
    print_status "All services stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_status "Cleanup completed"
}

# Show logs
show_logs() {
    service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Main menu
show_menu() {
    echo -e "\n${BLUE}Email Assistant Docker Management${NC}"
    echo "1. Deploy (First time setup)"
    echo "2. Start services"
    echo "3. Stop services"
    echo "4. Show status"
    echo "5. Show logs"
    echo "6. Cleanup"
    echo "7. Exit"
    echo
}

# Main execution
main() {
    check_docker
    
    while true; do
        show_menu
        read -p "Select an option [1-7]: " -n 1 -r
        echo
        
        case $REPLY in
            1)
                setup_directories
                setup_environment
                setup_ssl
                pull_images
                build_images
                start_services
                show_status
                ;;
            2)
                start_services
                show_status
                ;;
            3)
                stop_services
                ;;
            4)
                show_status
                ;;
            5)
                echo "Enter service name (or press Enter for all services):"
                read service
                show_logs "$service"
                ;;
            6)
                cleanup
                ;;
            7)
                print_status "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-7."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..." -n 1 -r
        clear
    done
}

# Run main function
main
