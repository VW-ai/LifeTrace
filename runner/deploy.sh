#!/bin/bash
# SmartHistory Deployment Script
# Supports multiple deployment targets: local, docker, aws, gcp, azure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

# Check dependencies
check_dependencies() {
    local deps=("$@")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep is required but not installed"
            exit 1
        fi
    done
}

# Deploy locally
deploy_local() {
    log_info "Deploying SmartHistory locally..."

    # Start backend
    log_info "Starting backend server..."
    cd src/backend || { log_error "Failed to change to backend directory from $(pwd)"; exit 1; }
    source ../../venv/bin/activate
    python start.py development &
    BACKEND_PID=$!
    cd ../../

    # Start frontend
    log_info "Starting frontend server..."
    cd src/frontend || { log_error "Failed to change to frontend directory"; exit 1; }
    npm run dev &
    FRONTEND_PID=$!
    cd ../../
    
    log_success "SmartHistory deployed locally!"
    log_info "Backend: http://localhost:8000"
    log_info "Frontend: http://localhost:3000"
    log_info "API Docs: http://localhost:8000/docs"
    
    # Wait for Ctrl+C
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
}

# Deploy with Docker
deploy_docker() {
    log_info "Deploying SmartHistory with Docker..."
    check_dependencies "docker" "docker-compose"
    
    # Build and start services
    cd ../deployment
    docker-compose up -d --build
    cd ../runner
    
    log_success "SmartHistory deployed with Docker!"
    log_info "Services started. Check status with: docker-compose ps"
    log_info "Frontend: http://localhost:3000"
    log_info "Backend: http://localhost:8000"
    log_info "Database: localhost:5432"
}

# Deploy to production
deploy_production() {
    log_info "Deploying SmartHistory to production..."
    check_dependencies "docker" "docker-compose"
    
    # Use production compose file
    cd ../deployment
    docker-compose -f docker-compose.prod.yml up -d --build
    cd ../runner
    
    log_success "SmartHistory deployed to production!"
    log_info "Monitor with: cd ../deployment && docker-compose -f docker-compose.prod.yml logs -f"
}

# Deploy to AWS
deploy_aws() {
    log_info "Deploying SmartHistory to AWS..."
    check_dependencies "aws" "docker"
    
    # Build and push to ECR
    log_info "Building and pushing Docker images to ECR..."
    
    # Get AWS account ID and region
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region)
    ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
    
    # Build and push API image
    cd ../
    docker build -f deployment/Dockerfile.backend -t smarthistory/api .
    docker tag smarthistory/api:latest $ECR_REGISTRY/smarthistory/api:latest
    docker push $ECR_REGISTRY/smarthistory/api:latest
    
    # Build and push frontend image
    docker build -f deployment/Dockerfile.frontend -t smarthistory/frontend .
    docker tag smarthistory/frontend:latest $ECR_REGISTRY/smarthistory/frontend:latest
    docker push $ECR_REGISTRY/smarthistory/frontend:latest
    cd runner
    
    # Update ECS service
    log_info "Updating ECS service..."
    aws ecs update-service --cluster smarthistory --service smarthistory-api --force-new-deployment
    
    log_success "SmartHistory deployed to AWS!"
    log_info "Check ECS console for deployment status"
}

# Show usage
show_usage() {
    echo "SmartHistory Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  local       Deploy locally for development"
    echo "  docker      Deploy with Docker Compose"
    echo "  production  Deploy to production with Docker"
    echo "  aws         Deploy to AWS ECS"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local           # Start local development servers"
    echo "  $0 docker          # Deploy with Docker Compose"
    echo "  $0 production      # Deploy to production"
    echo "  $0 aws             # Deploy to AWS"
}

# Main script
case "${1:-help}" in
    local)
        deploy_local
        ;;
    docker)
        deploy_docker
        ;;
    production)
        deploy_production
        ;;
    aws)
        deploy_aws
        ;;
    help|*)
        show_usage
        ;;
esac
