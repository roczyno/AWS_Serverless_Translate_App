#!/bin/bash

# AWS Serverless Translation - Fully Automated Deployment
# This script deploys everything with ZERO manual intervention

set -e

echo "🚀 Starting FULLY AUTOMATED deployment with ZERO manual intervention..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install it first."
    exit 1
fi

# Check if terraform.tfvars exists and contains GitHub configuration
if [ ! -f "Backend/terraform.tfvars" ]; then
    print_error "terraform.tfvars file not found in Backend directory."
    print_status "Please create Backend/terraform.tfvars with your GitHub configuration:"
    echo "  github_repo_url = \"your_github_repo_url\""
    echo "  github_access_token = \"your_github_token\""
    exit 1
fi

# Check if GitHub configuration exists in terraform.tfvars
if ! grep -q "github_repo_url" Backend/terraform.tfvars || ! grep -q "github_access_token" Backend/terraform.tfvars; then
    print_error "GitHub configuration not found in terraform.tfvars"
    print_status "Please add the following to Backend/terraform.tfvars:"
    echo "  github_repo_url = \"your_github_repo_url\""
    echo "  github_access_token = \"your_github_token\""
    exit 1
fi

print_success "GitHub configuration found in terraform.tfvars"

# Navigate to the Backend directory
cd Backend

print_status "Initializing Terraform..."
terraform init

print_status "Planning Terraform deployment..."
terraform plan -out=tfplan

print_status "Applying Terraform configuration..."
terraform apply tfplan

# Get the outputs
print_status "Getting deployment outputs..."
AMPLIFY_APP_ID=$(terraform output -raw amplify_app_id)
FRONTEND_URL=$(terraform output -raw frontend_url)
API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
COGNITO_USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
COGNITO_USER_POOL_CLIENT_ID=$(terraform output -raw cognito_user_pool_client_id)

print_success "🎉 FULLY AUTOMATED deployment completed!"
echo ""
print_status "Deployment Summary:"
echo "  • Amplify App ID: $AMPLIFY_APP_ID"
echo "  • Frontend URL: $FRONTEND_URL"
echo "  • API Gateway URL: $API_GATEWAY_URL"
echo "  • Cognito User Pool ID: $COGNITO_USER_POOL_ID"
echo "  • Cognito User Pool Client ID: $COGNITO_USER_POOL_CLIENT_ID"
echo ""
print_status "What was automated:"
echo "  ✅ Infrastructure deployment"
echo "  ✅ Amplify app creation"
echo "  ✅ Git repository connection"
echo "  ✅ Environment configuration"
echo "  ✅ Build settings setup"
echo "  ✅ Automatic build trigger"
echo "  ✅ Initial deployment"
echo ""
print_status "Your application is being deployed automatically!"
echo "  • Check build status: https://console.aws.amazon.com/amplify/home"
echo "  • Visit your app: $FRONTEND_URL"
echo ""
print_success "ZERO manual intervention required! 🚀" 