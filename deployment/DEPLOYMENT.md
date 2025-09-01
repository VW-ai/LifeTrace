# SmartHistory - Industry-Ready Deployment Guide

SmartHistory now features a modern, scalable architecture with dynamic configuration and multi-environment deployment support.

## 🏗️ Architecture Overview

### Backend (FastAPI)
- **Dynamic Configuration**: Environment-based settings with fallbacks
- **Multi-environment Support**: Development, staging, production configs
- **Industry Security**: CORS, trusted hosts, request logging
- **Health Checks**: Built-in monitoring endpoints
- **Containerization**: Docker-ready with multi-stage builds

### Frontend (React + TypeScript + Vite)
- **Environment Detection**: Automatic API URL resolution
- **Enhanced Error Handling**: Request logging and user-friendly errors
- **Professional UI**: Styled-components with responsive design
- **Development Tools**: Hot reload, debugging features

## 🚀 Quick Start

### Local Development
```bash
# Start both services
./deploy.sh local

# Or start individually:
# Backend: cd src/backend && python start.py development
# Frontend: cd src/frontend && npm run dev
```

### Docker Deployment
```bash
# Development with Docker
./deploy.sh docker

# Production deployment
./deploy.sh production
```

### Cloud Deployment
```bash
# AWS deployment (requires AWS CLI setup)
./deploy.sh aws
```

## 🔧 Configuration

### Backend Configuration
Environment variables are loaded from `.env.{environment}` files:

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
DATABASE_URL=sqlite:///./smarthistory_dev.db
LOG_LEVEL=DEBUG
```

### Frontend Configuration
Automatic environment detection with fallbacks:
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://yourdomain.com/api/v1`
- **Custom**: Set `VITE_API_BASE_URL` environment variable

## 📊 Monitoring & Observability

### Health Checks
- Backend: `GET /health`
- System status: `GET /api/v1/system/health`
- Metrics: `GET /api/v1/system/stats`

### Logging
- Structured logging with request IDs
- Environment-specific log levels
- Request/response correlation

### Docker Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

## 🌐 Cloud Deployment Options

### Docker Compose (Recommended)
- **Local development**: `docker-compose.yml`
- **Production**: `deployment/docker-compose.prod.yml`
- **Includes**: PostgreSQL, Redis, monitoring (Prometheus, Grafana)

### AWS ECS
- **Task Definition**: `deployment/aws/ecs-task-definition.json`
- **ECR Integration**: Automatic image builds and pushes
- **Secrets Management**: AWS Secrets Manager integration
- **Load Balancing**: Application Load Balancer ready

### Kubernetes (Future)
- Helm charts for easy deployment
- Horizontal pod autoscaling
- Service mesh integration

## 🔒 Security Features

### Backend Security
- **CORS Configuration**: Environment-specific origins
- **Trusted Host Middleware**: Production domain validation
- **Request ID Tracking**: Request correlation and logging
- **Error Handling**: User-friendly error messages without leaking internals

### Container Security
- **Non-root User**: Containers run as unprivileged user
- **Minimal Base Images**: Alpine Linux for smaller attack surface
- **Security Headers**: Comprehensive HTTP security headers
- **Secret Management**: Environment-based secret injection

## 📁 Project Structure

```
smartHistory/
├── src/
│   ├── backend/
│   │   ├── api/           # FastAPI application
│   │   ├── config.py      # Dynamic configuration
│   │   ├── start.py       # Startup script
│   │   └── .env.*         # Environment configs
│   └── frontend/
│       ├── src/
│       │   ├── config/    # Environment detection
│       │   ├── api/       # Enhanced API client
│       │   └── components/ # UI components
├── deployment/            # Cloud deployment configs
├── Dockerfile.*          # Container definitions
├── docker-compose*.yml   # Orchestration configs
└── deploy.sh            # Unified deployment script
```

## 🎯 Production Checklist

### Before Deployment
- [ ] Set production environment variables
- [ ] Configure allowed CORS origins
- [ ] Set up database (PostgreSQL recommended)
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and alerting
- [ ] Review security settings

### Environment Variables (Production)
```bash
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secure-secret-key
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=INFO
```

## 🔧 Development Workflow

1. **Local Development**: Use `./deploy.sh local`
2. **Testing**: Run with Docker: `./deploy.sh docker`
3. **Staging**: Deploy to staging environment
4. **Production**: Use `./deploy.sh production`

## 🐳 Container Features

- **Multi-stage Builds**: Optimized image sizes
- **Health Checks**: Built-in container health monitoring
- **Logging**: Structured logs for container orchestration
- **Resource Limits**: Memory and CPU constraints
- **Auto-restart**: Restart policies for resilience

## 📈 Scalability

- **Horizontal Scaling**: Stateless application design
- **Load Balancing**: Multiple backend instances
- **Database Pooling**: Connection management
- **Caching**: Redis integration ready
- **CDN Ready**: Static asset optimization

This architecture provides a solid foundation for scaling from development to production with enterprise-grade reliability and security.