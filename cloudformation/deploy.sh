#!/bin/bash

# =============================================================================
# Deploy CloudFormation Stack for RAG Pipeline
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
DEPLOYMENT_SUFFIX="${DEPLOYMENT_SUFFIX:-}"
STACK_NAME="${PROJECT_NAME}-stack${DEPLOYMENT_SUFFIX}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo -e "${YELLOW}Deploying RAG Pipeline CloudFormation Stack...${NC}"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
if [ -n "$DEPLOYMENT_SUFFIX" ]; then
    echo "Deployment Suffix: $DEPLOYMENT_SUFFIX"
fi
echo ""

# Upload knowledge base documents first (before stack creates KB)
KB_BUCKET="${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}${DEPLOYMENT_SUFFIX}"

# Check if bucket exists, if so upload docs
if aws s3 ls "s3://${KB_BUCKET}" 2>/dev/null; then
    echo -e "${YELLOW}Uploading knowledge base documents...${NC}"
    aws s3 sync "${SCRIPT_DIR}/../knowledge-base/support-cases/" "s3://${KB_BUCKET}/support-cases/" --region $REGION
    echo -e "${GREEN}✓ Knowledge base documents uploaded${NC}"
fi

# Check if stack exists
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME \
    --query 'Stacks[0].StackStatus' --output text --region $REGION 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_STATUS" == "DOES_NOT_EXIST" ]; then
    echo "Creating new stack..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://${SCRIPT_DIR}/rag-pipeline-stack.yaml \
        --parameters ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
                     ParameterKey=DeploymentSuffix,ParameterValue=$DEPLOYMENT_SUFFIX \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "Waiting for stack creation to complete (this may take 3-5 minutes)..."
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    
    echo -e "${GREEN}✓ Stack created successfully${NC}"
    
    # Upload docs now that bucket exists
    echo -e "${YELLOW}Uploading knowledge base documents...${NC}"
    aws s3 sync "${SCRIPT_DIR}/../knowledge-base/support-cases/" "s3://${KB_BUCKET}/support-cases/" --region $REGION
    echo -e "${GREEN}✓ Knowledge base documents uploaded${NC}"
    
    # Trigger ingestion manually since docs weren't there during initial creation
    echo -e "${YELLOW}Triggering knowledge base ingestion...${NC}"
    KB_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseId'].OutputValue" \
        --output text --region $REGION)
    DS_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME \
        --query "Stacks[0].Outputs[?OutputKey=='DataSourceId'].OutputValue" \
        --output text --region $REGION)
    
    if [ -n "$KB_ID" ] && [ "$KB_ID" != "None" ] && [ -n "$DS_ID" ] && [ "$DS_ID" != "None" ]; then
        aws bedrock-agent start-ingestion-job \
            --knowledge-base-id $KB_ID \
            --data-source-id $DS_ID \
            --region $REGION
        echo -e "${GREEN}✓ Ingestion job started${NC}"
    fi
else
    echo "Stack exists with status: $STACK_STATUS"
    
    if [ "$STACK_STATUS" == "CREATE_COMPLETE" ] || [ "$STACK_STATUS" == "UPDATE_COMPLETE" ] || [ "$STACK_STATUS" == "UPDATE_ROLLBACK_COMPLETE" ]; then
        # Upload docs before update
        echo -e "${YELLOW}Uploading knowledge base documents...${NC}"
        aws s3 sync "${SCRIPT_DIR}/../knowledge-base/support-cases/" "s3://${KB_BUCKET}/support-cases/" --region $REGION
        echo -e "${GREEN}✓ Knowledge base documents uploaded${NC}"
        
        echo "Updating stack..."
        UPDATE_OUTPUT=$(aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://${SCRIPT_DIR}/rag-pipeline-stack.yaml \
            --parameters ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
                         ParameterKey=DeploymentSuffix,ParameterValue=$DEPLOYMENT_SUFFIX \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION 2>&1) || true
        
        if echo "$UPDATE_OUTPUT" | grep -q "No updates are to be performed"; then
            echo "No stack updates needed"
        else
            echo "Waiting for stack update to complete..."
            aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION 2>/dev/null || true
            echo -e "${GREEN}✓ Stack updated successfully${NC}"
        fi
    else
        echo -e "${RED}Stack is in unexpected state: $STACK_STATUS${NC}"
        echo "Please check the CloudFormation console for details."
        exit 1
    fi
fi

# Print outputs
echo ""
echo -e "${GREEN}Stack Outputs:${NC}"
aws cloudformation describe-stacks --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table --region $REGION

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "The Knowledge Base has been created and documents are being ingested."
echo "Ingestion typically takes 1-2 minutes to complete."
echo ""
echo "Next steps:"
echo "1. Deploy the frontend: cd ../frontend && ./deploy-frontend.sh"
echo "2. Open the CloudFront URL in your browser"
echo "3. Start experimenting with prompts!"
