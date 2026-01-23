# 🚗 Xtream Wash - Car Wash Management System

## End-to-End Data Migration, Web Forms, Live Dashboard & Cloud Deployment

A complete modernization platform for car wash businesses featuring real-time data collection, interactive dashboards, and scalable AWS deployment.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Features](#features)
4. [Quick Start](#quick-start)
5. [Local Development](#local-development)
6. [Docker Deployment](#docker-deployment)
7. [AWS Deployment](#aws-deployment)
8. [API Documentation](#api-documentation)
9. [Dashboard](#dashboard)
10. [Data Migration](#data-migration)
11. [Database Schema](#database-schema)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

### Problem Statement
Legacy car wash businesses need modernization:
- Manual record-keeping (Excel files in folders)
- No real-time data collection
- Limited insights into sales patterns
- Difficulty scaling operations

### Solution
Xtream Wash provides:
- ✅ **Web Form**: Real-time daily wash record submission
- ✅ **API Backend**: FastAPI REST endpoints for data management
- ✅ **Live Dashboard**: Streamlit-based interactive analytics
- ✅ **Data Migration**: Automated ETL from legacy Excel to modern PostgreSQL
- ✅ **Docker**: Complete containerization for consistent environments
- ✅ **AWS**: Scalable cloud deployment with RDS, S3, ECS

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB CLIENTS                              │
├──────────────────────────────┬──────────────────────────────────┤
│  Web Form (wash_form.html)   │   Streamlit Dashboard            │
│  Port: 80/3000              │   Port: 8501                     │
└──────────────────┬───────────┴──────────────────┬───────────────┘
                   │                              │
┌──────────────────▼──────────────────────────────▼────────────────┐
│                    REVERSE PROXY (Optional)                      │
│                         NGINX                                    │
│                      Port: 80, 443                               │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                   FASTAPI BACKEND                               │
│                      Port: 8000                                 │
│  • Orders Management (CRUD)                                    │
│  • Dashboard Data Aggregation                                  │
│  • Real-time Analytics                                         │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                                │
│                      Port: 5432                                 │
│  • wash_orders (main table)                                   │
│  • service_prices (lookup)                                     │
│  • Views (daily_summary, service_breakdown, etc.)             │
│  • Triggers (auto-pricing, audit timestamps)                  │
└──────────────────────────────────────────────────────────────────┘

AWS CLOUD (Production):
┌─────────────────┐   ┌────────────────┐   ┌──────────────┐
│  ECS (Fargate)  │──▶│  RDS PostgreSQL│   │   S3 Bucket  │
│  API Container  │   │  (Managed DB)  │   │ (File Store) │
└─────────────────┘   └────────────────┘   └──────────────┘
```

---

## ✨ Features

### 1. **Web Form for Daily Records**
- Mobile-responsive HTML form
- Real-time validation
- Phone number normalization
- Service type selection (handpolish, xtream, deluxe)
- Payment method tracking
- Optional operator, vehicle, discount fields
- Success/error notifications

**Location**: `/frontend/wash_form.html`

### 2. **FastAPI Backend**
- RESTful API endpoints (CRUD)
- Request/response validation with Pydantic
- PostgreSQL integration
- CORS middleware for cross-origin requests
- Health check endpoint
- Comprehensive logging
- Auto-generated OpenAPI documentation

**Endpoints**:
```
POST   /api/orders                 # Create new order
GET    /api/orders                 # List orders (with filters)
GET    /api/orders/{id}            # Get specific order
PATCH  /api/orders/{id}            # Update order status
GET    /api/dashboard/stats        # Overall statistics
GET    /api/dashboard/daily-summary # Daily sales data
GET    /api/dashboard/service-breakdown # Service distribution
GET    /api/dashboard/top-customers # Customer rankings
GET    /health                     # Health check
```

**Location**: `/backend/main.py`

### 3. **Interactive Live Dashboard**
- Real-time sales metrics
- Daily revenue trends (line chart)
- Service type distribution (pie chart)
- Top customers rankings
- Daily summary table
- Service performance breakdown
- Auto-refresh capability
- Responsive design

**Location**: `/dashboard/app.py`

### 4. **Data Migration Pipeline**
- Reads legacy Excel files from monthly folders
- Parses DDMMYYYY filename format
- Maps old schema to new unified schema
- Handles service type normalization
- Bulk inserts with PostgreSQL
- Audit trail with migration metadata

**Usage**:
```bash
python load.py
```

### 5. **Unified Database Schema**
- Consolidated from two legacy schemas (wash_orders + washdata)
- Proper constraints and validation
- Audit timestamps (created_at, updated_at)
- Service pricing lookup table
- Automated triggers for price calculation
- Multiple views for analytics

### 6. **Docker Containerization**
- Individual Dockerfiles for each service
- Docker Compose orchestration
- Health checks for all services
- Volume management for data persistence
- Network isolation

### 7. **AWS Integration**
- RDS PostgreSQL (managed database)
- S3 (file storage and backups)
- ECR (container registry)
- ECS Fargate (serverless containers)
- CloudWatch (logging and monitoring)
- IAM roles and policies

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL client (optional)
- AWS CLI (for cloud deployment)

### 1. Clone & Setup
```bash
cd /workspaces/xtream
cp .env.example .env
```

### 2. Local Development (Without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Configure database
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=washdata_db
export DB_USER=postgres
export DB_PASSWORD=postgres

# Start PostgreSQL (if not running)
# psql -h localhost -U postgres -c "CREATE DATABASE washdata_db;"

# Initialize schema
psql -h localhost -U postgres -d washdata_db < project0/dataschema/dailyreport.sql

# Start backend
cd backend
uvicorn main:app --reload --port 8000

# In another terminal, start dashboard
cd dashboard
streamlit run app.py
```

### 3. Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f dashboard

# Stop services
docker-compose down
```

**Access Points**:
- **Web Form**: http://localhost (with nginx) or open `frontend/wash_form.html` directly
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

---

## 🛠️ Local Development

### Setup Development Environment

```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Edit with your settings
```

### Database Setup

**Option 1: Using Docker**
```bash
docker run --name postgres_wash -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15-alpine

# Wait for container to be ready, then initialize schema
docker exec -i postgres_wash psql -U postgres -d postgres < project0/dataschema/dailyreport.sql
```

**Option 2: Local PostgreSQL**
```bash
# Create database
createdb washdata_db

# Initialize schema
psql -d washdata_db < project0/dataschema/dailyreport.sql
```

### Running Services Individually

```bash
# Terminal 1: Start FastAPI Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Streamlit Dashboard
cd dashboard
streamlit run app.py --server.port=8501

# Terminal 3: Test with curl
curl http://localhost:8000/health
```

### Data Migration

```bash
# Migrate Excel data to PostgreSQL
python load.py

# Or with logging
python load.py 2>&1 | tee migration.log
```

---

## 🐳 Docker Deployment

### Build Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build dashboard
```

### Start Services

```bash
# Start all services in background
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up -d backend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f dashboard
```

### Health Checks

```bash
# Check service health
docker-compose ps

# Test API
curl http://localhost:8000/health

# Test database
docker exec washdata_postgres pg_isready -U postgres
```

### Stop & Cleanup

```bash
# Stop services (keep volumes)
docker-compose stop

# Remove services
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

---

## ☁️ AWS Deployment

### Prerequisites

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Configure credentials
aws configure
```

### Automated Setup

```bash
# Make script executable
chmod +x deploy_aws.sh

# Run deployment setup
./deploy_aws.sh

# Review and merge .env.aws
cat .env.aws >> .env
```

The script will:
- ✅ Create RDS PostgreSQL database
- ✅ Create S3 bucket for data
- ✅ Create ECR repositories
- ✅ Create IAM roles and policies
- ✅ Create ECS cluster
- ✅ Create security groups

### Manual Steps

1. **Build & Push Images to ECR**
```bash
# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Build and push backend
docker build -f backend.dockerfile -t $ECR_REGISTRY/xtream-wash-backend:latest .
docker push $ECR_REGISTRY/xtream-wash-backend:latest

# Build and push dashboard
docker build -f dashboard.dockerfile -t $ECR_REGISTRY/xtream-wash-dashboard:latest .
docker push $ECR_REGISTRY/xtream-wash-dashboard:latest
```

2. **Create ECS Task Definitions** (via AWS Console or CLI)

3. **Create Application Load Balancer**

4. **Configure Auto-Scaling**

---

## 📚 API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.xtream-wash.com` (example)

### Authentication
Currently uses API key in header:
```bash
Authorization: Bearer YOUR_API_KEY
```

### Example Requests

**Create Order**
```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+628100000001",
    "customer_name": "Budi",
    "wash_type": "xtream",
    "payment_method": "cash",
    "operator_name": "Hendra"
  }'
```

**Get Orders**
```bash
curl http://localhost:8000/api/orders?status=completed&limit=10
```

**Get Dashboard Stats**
```bash
curl http://localhost:8000/api/dashboard/stats
```

**Interactive API Docs**
Open browser: `http://localhost:8000/docs`

---

## 📊 Dashboard

### Features
- **Key Metrics**: Total orders, revenue, customers, last order time
- **Daily Trend**: Revenue over last 30 days
- **Service Breakdown**: Sales distribution by service type
- **Top Customers**: Most frequent customers with spend
- **Auto-Refresh**: Updates every 10 seconds when enabled
- **Date Filtering**: View specific date ranges

### Access
- URL: `http://localhost:8501`
- Auto-refresh: Toggle in sidebar
- Custom date range: Slider control

---

## 🔄 Data Migration

### Process

1. **Historical Data**: Excel files organized in monthly folders
   ```
   project0/dataschema/
   ├── January/
   │   └── washdata_*.xlsx
   ├── February/
   │   └── washdata_*.xlsx
   └── ...
   ```

2. **Run Migration**
   ```bash
   python load.py
   ```

3. **Verification**
   ```bash
   # Check migration status
   curl http://localhost:8000/api/dashboard/stats
   
   # Query database directly
   psql -h localhost -U postgres -d washdata_db
   SELECT COUNT(*) FROM wash_orders WHERE status = 'completed';
   ```

### Field Mapping

| Old Field | New Field | Notes |
|-----------|-----------|-------|
| phone | phone_number | - |
| wash_service | wash_type | Normalized to enum |
| entry_time | entry_time | - |
| out_time | checkout_estimated_time | - |
| payment_method | payment_method | - |
| amount_paid | price_paid | - |
| comments | comments | Prefixed with "Migrated: " |
| - | created_date | Set from filename |
| - | status | Set to "completed" |
| - | operator_name | Set to "migrated_operator" |

---

## 📋 Database Schema

### Tables

#### `wash_orders` (Main Table)
Primary table storing all car wash orders.

```sql
id                    SERIAL PRIMARY KEY
phone_number          VARCHAR(20) NOT NULL
customer_name         VARCHAR(100)
wash_type             ENUM ('handpolish', 'xtream', 'deluxe')
operator_name         VARCHAR(100)
dockerid              TEXT
station_id            INT
vehicle_plate         VARCHAR(20)
vehicle_type          VARCHAR(50)
entry_time            TIMESTAMP WITH TIME ZONE
checkout_estimated_time TIMESTAMP WITH TIME ZONE
checkout_actual_time  TIMESTAMP WITH TIME ZONE
payment_method        VARCHAR(20)
price_paid            NUMERIC(8,2)
discount_applied      NUMERIC(8,2)
status                VARCHAR(20) ('pending', 'in_progress', 'completed', 'cancelled')
created_date          DATE
created_at            TIMESTAMP WITH TIME ZONE
updated_at            TIMESTAMP WITH TIME ZONE
comments              TEXT
```

#### `service_prices` (Lookup Table)
Service type pricing configuration.

```sql
service_type  wash_service_type PRIMARY KEY
base_price    NUMERIC(8,2) NOT NULL
description   TEXT
updated_at    TIMESTAMP WITH TIME ZONE
```

### Views

- **vw_daily_sales_summary**: Daily aggregated metrics
- **vw_hourly_service_breakdown**: Hourly sales by service type
- **vw_top_customers**: Customer rankings and metrics

### Triggers

- **trig_set_price_paid**: Auto-calculate price from service type
- **trig_update_updated_at**: Update timestamp on modification

---

## 🔍 Troubleshooting

### Common Issues

#### 1. "Connection refused" on port 5432
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not running with Docker Compose:
docker-compose up -d postgres
```

#### 2. "No such table: wash_orders"
```bash
# Initialize database schema
docker exec washdata_postgres psql -U postgres -d washdata_db -f /docker-entrypoint-initdb.d/01-schema.sql

# Or locally:
psql -h localhost -U postgres -d washdata_db < project0/dataschema/dailyreport.sql
```

#### 3. FastAPI 502 Bad Gateway
```bash
# Check backend logs
docker-compose logs backend

# Check if backend is healthy
curl http://localhost:8000/health

# Restart backend
docker-compose restart backend
```

#### 4. Dashboard won't load
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/

# Check dashboard logs
docker-compose logs dashboard

# Verify API is accessible
curl http://backend:8000/health  # From inside container
```

#### 5. CORS errors in browser
```bash
# CORS is enabled for all origins in development
# For production, update frontend/wash_form.html API_URL
# and backend/main.py CORS settings
```

### Debug Mode

```bash
# Enable verbose logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Restart services
docker-compose restart backend
```

### Database Queries

```bash
# Connect to database
docker exec -it washdata_postgres psql -U postgres -d washdata_db

# Useful queries
SELECT COUNT(*) FROM wash_orders;
SELECT * FROM vw_daily_sales_summary LIMIT 5;
SELECT * FROM wash_orders WHERE status = 'pending';
SELECT SUM(price_paid) FROM wash_orders WHERE created_date = CURRENT_DATE;
```

---

## 📁 Project Structure

```
xtream/
├── backend/
│   └── main.py                 # FastAPI application
├── frontend/
│   └── wash_form.html          # Web form for data entry
├── dashboard/
│   └── app.py                  # Streamlit dashboard
├── project0/
│   ├── dataschema/
│   │   ├── dailyreport.sql     # Unified database schema
│   │   ├── hello.py            # (Legacy)
│   │   ├── mockdatagenerator.ipynb
│   │   └── [monthly folders]/  # Legacy Excel data
│   └── Readme.md
├── postgres/
│   └── Readme.md               # Database setup guide
├── load.py                     # Data migration script
├── deploy_aws.sh               # AWS deployment script
├── docker-compose.yml          # Docker orchestration
├── backend.dockerfile          # Backend container definition
├── dashboard.dockerfile        # Dashboard container definition
├── postgres.dockerfile         # Database container definition
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## 📝 License & Notes

- **Author**: Xtream Wash Development Team
- **Date**: January 2026
- **Status**: Active Development
- **License**: Proprietary

---

## 🤝 Contributing

Contributions welcome! Please:
1. Create feature branches
2. Test locally with Docker Compose
3. Document API changes
4. Update this README

---

## ❓ Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review API documentation at `/docs`
3. Check service logs with `docker-compose logs`
4. Verify database connectivity

---

**Last Updated**: January 23, 2026

Happy car washing! 🚗💦
