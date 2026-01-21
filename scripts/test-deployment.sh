#!/bin/bash
# Test deployment script for RAG Pipeline
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_NAME="${PROJECT_NAME:-rag-pipeline}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")

echo "============================================"
echo "  RAG Pipeline Deployment Validation"
echo "============================================"
echo ""

PASSED=0
FAILED=0

# Check AWS credentials
if [ -n "$ACCOUNT_ID" ]; then
    echo -e "${GREEN}✓ AWS credentials configured${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    ((FAILED++))
fi

# Check CloudFormation stack
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
    --query 'Stacks[0].StackStatus' --output text --region $REGION 2>/dev/null || echo "NOT_FOUND")

if [ "$STACK_STATUS" == "CREATE_COMPLETE" ] || [ "$STACK_STATUS" == "UPDATE_COMPLETE" ]; then
    echo -e "${GREEN}✓ CloudFormation stack: $STACK_STATUS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ CloudFormation stack: $STACK_STATUS${NC}"
    ((FAILED++))
fi

# Check S3 bucket
BUCKET="${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}"
BUCKET_EXISTS=$(aws s3 ls s3://${BUCKET} 2>/dev/null && echo "yes" || echo "no")

if [ "$BUCKET_EXISTS" == "yes" ]; then
    echo -e "${GREEN}✓ S3 bucket exists with content${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ S3 bucket not found${NC}"
    ((FAILED++))
fi

echo ""
echo "============================================"
echo "  Results: $PASSED passed, $FAILED failed"
echo "============================================"

exit $FAILED
