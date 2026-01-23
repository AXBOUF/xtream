#!/bin/bash
# ============================================================================
# AWS DEPLOYMENT SETUP SCRIPT
# This script sets up the Car Wash Management System on AWS
# ============================================================================

set -e

echo "🚀 Car Wash Management System - AWS Deployment Setup"
echo "======================================================"

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
APP_NAME="xtream-wash"
ENVIRONMENT=${ENVIRONMENT:-production}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    log_info "AWS CLI found"
}

check_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured."
        echo "Please run: aws configure"
        exit 1
    fi
    log_info "AWS credentials verified"
}

# ============================================================================
# CREATE RDS POSTGRESQL DATABASE
# ============================================================================
create_rds_database() {
    echo -e "\n${YELLOW}Creating RDS PostgreSQL Database...${NC}"
    
    DB_INSTANCE_ID="${APP_NAME}-db-${ENVIRONMENT}"
    
    # Check if DB already exists
    if aws rds describe-db-instances --db-instance-identifier "$DB_INSTANCE_ID" \
        --region "$AWS_REGION" &> /dev/null; then
        log_warn "Database instance already exists: $DB_INSTANCE_ID"
    else
        log_info "Creating RDS database: $DB_INSTANCE_ID"
        
        aws rds create-db-instance \
            --db-instance-identifier "$DB_INSTANCE_ID" \
            --db-instance-class db.t3.micro \
            --engine postgres \
            --engine-version 15.3 \
            --master-username postgres \
            --master-user-password "${DB_PASSWORD:-XtreamWash2024!}" \
            --allocated-storage 20 \
            --storage-type gp3 \
            --db-name washdata_db \
            --backup-retention-period 7 \
            --multi-az false \
            --publicly-accessible true \
            --enable-cloudwatch-logs-exports postgresql \
            --region "$AWS_REGION" \
            --tags Key=Application,Value=xtream-wash Key=Environment,Value="$ENVIRONMENT"
        
        log_info "RDS instance creation initiated (this takes a few minutes)"
        
        # Wait for instance to be available
        echo "Waiting for database to be available (this may take 5-10 minutes)..."
        aws rds wait db-instance-available \
            --db-instance-identifier "$DB_INSTANCE_ID" \
            --region "$AWS_REGION"
        
        log_info "RDS database is now available"
    fi
    
    # Get endpoint
    ENDPOINT=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_INSTANCE_ID" \
        --region "$AWS_REGION" \
        --query 'DBInstances[0].Endpoint.Address' \
        --output text)
    
    echo "DB_HOST=$ENDPOINT" >> .env.aws
    log_info "Database endpoint: $ENDPOINT"
}

# ============================================================================
# CREATE S3 BUCKET FOR FILE UPLOADS
# ============================================================================
create_s3_bucket() {
    echo -e "\n${YELLOW}Creating S3 Bucket...${NC}"
    
    BUCKET_NAME="${APP_NAME}-data-${AWS_REGION}-$(date +%s)"
    
    if aws s3 ls "s3://$BUCKET_NAME" 2>/dev/null; then
        log_warn "Bucket already exists: $BUCKET_NAME"
    else
        log_info "Creating S3 bucket: $BUCKET_NAME"
        
        aws s3 mb "s3://$BUCKET_NAME" \
            --region "$AWS_REGION"
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "$BUCKET_NAME" \
            --versioning-configuration Status=Enabled
        
        # Block public access
        aws s3api put-public-access-block \
            --bucket "$BUCKET_NAME" \
            --public-access-block-configuration \
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
        
        log_info "S3 bucket created and configured"
    fi
    
    echo "AWS_S3_BUCKET=$BUCKET_NAME" >> .env.aws
    log_info "Bucket name: $BUCKET_NAME"
}

# ============================================================================
# CREATE ECR REPOSITORIES
# ============================================================================
create_ecr_repositories() {
    echo -e "\n${YELLOW}Creating ECR Repositories...${NC}"
    
    for service in backend dashboard; do
        REPO_NAME="${APP_NAME}-${service}"
        
        if aws ecr describe-repositories \
            --repository-names "$REPO_NAME" \
            --region "$AWS_REGION" &> /dev/null; then
            log_warn "ECR repository already exists: $REPO_NAME"
        else
            log_info "Creating ECR repository: $REPO_NAME"
            
            aws ecr create-repository \
                --repository-name "$REPO_NAME" \
                --region "$AWS_REGION" \
                --image-scan-configuration scanOnPush=true \
                --image-tag-mutability IMMUTABLE \
                --tags Key=Application,Value=xtream-wash Key=Service,Value="$service"
            
            log_info "ECR repository created: $REPO_NAME"
        fi
    done
}

# ============================================================================
# CREATE IAM ROLE FOR ECS TASKS
# ============================================================================
create_iam_role() {
    echo -e "\n${YELLOW}Creating IAM Role for ECS...${NC}"
    
    ROLE_NAME="${APP_NAME}-ecs-task-role"
    
    if aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
        log_warn "IAM role already exists: $ROLE_NAME"
    else
        log_info "Creating IAM role: $ROLE_NAME"
        
        # Create trust policy
        cat > /tmp/trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
        
        aws iam create-role \
            --role-name "$ROLE_NAME" \
            --assume-role-policy-document file:///tmp/trust-policy.json
        
        # Attach policies
        aws iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
        
        aws iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
        
        # Create and attach custom S3 policy
        cat > /tmp/s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::xtream-wash-*/*"
    }
  ]
}
EOF
        
        aws iam put-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-name "${APP_NAME}-s3-access" \
            --policy-document file:///tmp/s3-policy.json
        
        log_info "IAM role created with policies"
    fi
}

# ============================================================================
# CREATE ECS CLUSTER
# ============================================================================
create_ecs_cluster() {
    echo -e "\n${YELLOW}Creating ECS Cluster...${NC}"
    
    CLUSTER_NAME="${APP_NAME}-${ENVIRONMENT}"
    
    if aws ecs describe-clusters \
        --clusters "$CLUSTER_NAME" \
        --region "$AWS_REGION" \
        --query 'clusters[0].clusterArn' \
        --output text &> /dev/null; then
        log_warn "ECS cluster already exists: $CLUSTER_NAME"
    else
        log_info "Creating ECS cluster: $CLUSTER_NAME"
        
        aws ecs create-cluster \
            --cluster-name "$CLUSTER_NAME" \
            --region "$AWS_REGION" \
            --tags key=Application,value=xtream-wash key=Environment,value="$ENVIRONMENT"
        
        log_info "ECS cluster created"
    fi
}

# ============================================================================
# CREATE SECURITY GROUP
# ============================================================================
create_security_group() {
    echo -e "\n${YELLOW}Creating Security Group...${NC}"
    
    SG_NAME="${APP_NAME}-sg"
    
    # Get VPC ID
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters Name=isDefault,Values=true \
        --region "$AWS_REGION" \
        --query 'Vpcs[0].VpcId' \
        --output text)
    
    if aws ec2 describe-security-groups \
        --filters Name=group-name,Values="$SG_NAME" \
        --region "$AWS_REGION" &> /dev/null; then
        log_warn "Security group already exists: $SG_NAME"
    else
        log_info "Creating security group: $SG_NAME"
        
        SG_ID=$(aws ec2 create-security-group \
            --group-name "$SG_NAME" \
            --description "Security group for Xtream Wash application" \
            --vpc-id "$VPC_ID" \
            --region "$AWS_REGION" \
            --query 'GroupId' \
            --output text)
        
        # Add inbound rules
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ID" \
            --protocol tcp \
            --port 80 \
            --cidr 0.0.0.0/0 \
            --region "$AWS_REGION"
        
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ID" \
            --protocol tcp \
            --port 443 \
            --cidr 0.0.0.0/0 \
            --region "$AWS_REGION"
        
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ID" \
            --protocol tcp \
            --port 8000 \
            --cidr 0.0.0.0/0 \
            --region "$AWS_REGION"
        
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ID" \
            --protocol tcp \
            --port 8501 \
            --cidr 0.0.0.0/0 \
            --region "$AWS_REGION"
        
        log_info "Security group created: $SG_ID"
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    echo "AWS Region: $AWS_REGION"
    echo "Environment: $ENVIRONMENT"
    echo "App Name: $APP_NAME"
    echo ""
    
    # Initialize .env.aws file
    > .env.aws
    
    check_aws_cli
    check_credentials
    
    create_rds_database
    create_s3_bucket
    create_ecr_repositories
    create_iam_role
    create_ecs_cluster
    create_security_group
    
    echo ""
    log_info "AWS infrastructure setup completed!"
    echo ""
    echo "Configuration saved to .env.aws"
    echo "Next steps:"
    echo "  1. Review .env.aws and merge with .env"
    echo "  2. Build and push Docker images to ECR"
    echo "  3. Deploy ECS task definitions"
    echo "  4. Configure Application Load Balancer"
}

main "$@"
