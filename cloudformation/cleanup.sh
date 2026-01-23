#!/bin/bash

# =============================================================================
# Cleanup CloudFormation Stack and Resources
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PROJECT_NAME="${PROJECT_NAME:-rag-pipeline}"
REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${PROJECT_NAME}-stack"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo -e "${RED}"
echo "============================================================"
echo "  WARNING: This will delete all RAG Pipeline resources!"
echo "============================================================"
echo -e "${NC}"

echo "Resources to be deleted:"
echo "  • CloudFormation Stack: $STACK_NAME"
echo "  • S3 Bucket (KB): ${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}"
echo "  • S3 Bucket (Frontend): ${PROJECT_NAME}-frontend-${ACCOUNT_ID}-${REGION}"
echo "  • S3 Vector Store (managed by Bedrock KB)"
echo "  • Lambda Function: ${PROJECT_NAME}-query-function"
echo "  • IAM Roles and Policies"
echo ""

read -p "Are you sure you want to delete all resources? (type 'DELETE' to confirm): " CONFIRM

if [ "$CONFIRM" != "DELETE" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Starting cleanup...${NC}"

# Empty S3 buckets first (required before deletion)
KB_BUCKET="${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}"
FRONTEND_BUCKET="${PROJECT_NAME}-frontend-${ACCOUNT_ID}-${REGION}"

echo "Emptying S3 bucket: $KB_BUCKET"
aws s3 rm s3://${KB_BUCKET} --recursive --region $REGION 2>/dev/null || true

echo "Emptying S3 bucket: $FRONTEND_BUCKET"
aws s3 rm s3://${FRONTEND_BUCKET} --recursive --region $REGION 2>/dev/null || true

# Delete Bedrock Knowledge Base if exists (must be done before stack deletion)
echo "Checking for Bedrock Knowledge Base..."
KB_IDS=$(aws bedrock-agent list-knowledge-bases --query "knowledgeBaseSummaries[?name=='${PROJECT_NAME}-kb'].knowledgeBaseId" --output text --region $REGION 2>/dev/null || echo "")

if [ -n "$KB_IDS" ]; then
    for KB_ID in $KB_IDS; do
        echo "Deleting Knowledge Base: $KB_ID"
        
        # Delete data sources first
        DS_IDS=$(aws bedrock-agent list-data-sources --knowledge-base-id $KB_ID --query "dataSourceSummaries[*].dataSourceId" --output text --region $REGION 2>/dev/null || echo "")
        for DS_ID in $DS_IDS; do
            echo "  Deleting data source: $DS_ID"
            aws bedrock-agent delete-data-source --knowledge-base-id $KB_ID --data-source-id $DS_ID --region $REGION 2>/dev/null || true
        done
        
        # Delete knowledge base
        aws bedrock-agent delete-knowledge-base --knowledge-base-id $KB_ID --region $REGION 2>/dev/null || true
    done
fi

# Delete CloudFormation stack
echo "Deleting CloudFormation stack: $STACK_NAME"
aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION

echo "Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION

echo ""
echo -e "${GREEN}✓ Cleanup complete!${NC}"
echo ""
echo "All resources have been deleted."
