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
STACK_NAME="${PROJECT_NAME}-stack"

echo -e "${YELLOW}Deploying RAG Pipeline CloudFormation Stack...${NC}"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo ""

# Check if stack exists
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME \
    --query 'Stacks[0].StackStatus' --output text --region $REGION 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_STATUS" == "DOES_NOT_EXIST" ]; then
    echo "Creating new stack..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://rag-pipeline-stack.yaml \
        --parameters ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "Waiting for stack creation to complete..."
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    
    echo -e "${GREEN}✓ Stack created successfully${NC}"
else
    echo "Stack exists with status: $STACK_STATUS"
    
    if [ "$STACK_STATUS" == "CREATE_COMPLETE" ] || [ "$STACK_STATUS" == "UPDATE_COMPLETE" ]; then
        echo "Updating stack..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://rag-pipeline-stack.yaml \
            --parameters ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION 2>/dev/null || echo "No updates needed"
        
        echo "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION 2>/dev/null || true
        
        echo -e "${GREEN}✓ Stack updated successfully${NC}"
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
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Upload knowledge base content: cd .. && aws s3 sync knowledge-base/support-cases/ s3://${PROJECT_NAME}-kb-\$(aws sts get-caller-identity --query Account --output text)-${REGION}/support-cases/"
echo "2. Create Bedrock Knowledge Base in console (or use create-knowledge-base.sh)"
echo "3. Sync the data source"
echo "4. Test with: python3 ../scripts/query-knowledge-base.py"
