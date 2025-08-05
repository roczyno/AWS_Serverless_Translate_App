#!/bin/bash

# AWS Serverless Translation - Fully Automated Destruction
# This script destroys all infrastructure with ZERO manual intervention after confirmation

set -e

echo "🚨 Starting FULLY AUTOMATED destruction of AWS infrastructure..."

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


if ! command -v aws &> /dev/null; then
    print_error "AWS CLI is not installed. Please install it first."
    exit 1
fi


if ! command -v terraform &> /dev/null; then
    print_error "Terraform is not installed. Please install it first."
    exit 1
fi


cd Backend

print_status "Initializing Terraform..."
terraform init

print_warning "This is a DESTRUCTIVE operation and will remove all AWS resources managed by this Terraform configuration."
print_warning "Please back up any important data before proceeding."

read -p "To confirm destruction, please type the word 'destroy': " user_confirmation

if [ "$user_confirmation" != "destroy" ]; then
    print_error "Confirmation failed. Destruction cancelled."
    exit 1
fi

print_status "Starting infrastructure destruction..."
terraform destroy -auto-approve

print_success "💀 All infrastructure has been successfully destroyed."
echo ""
print_status "Thank you for using the automated scripts. Your environment is now clean."

# Return to the root directory
cd ..
