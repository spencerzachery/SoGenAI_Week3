#!/bin/bash

# =============================================================================
# Week 3: Prompt Engineering & Context Management - Setup Script
# =============================================================================
# This script deploys the complete RAG pipeline for Enterprise Support scenarios
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="${PROJECT_NAME:-rag-pipeline}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")

echo -e "${BLUE}"
echo "============================================================"
echo "  Week 3: Prompt Engineering & Context Management"
echo "  RAG Pipeline Deployment"
echo "============================================================"
echo -e "${NC}"

# =============================================================================
# Prerequisites Check
# =============================================================================
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ AWS CLI installed${NC}"
    
    # Check AWS credentials
    if [ -z "$ACCOUNT_ID" ]; then
        echo -e "${RED}❌ AWS credentials not configured. Run 'aws configure' first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ AWS credentials configured (Account: $ACCOUNT_ID)${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found. Please install it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python 3 installed${NC}"
    
    # Check region
    echo -e "${GREEN}✓ Region: $REGION${NC}"
    
    echo ""
}

# =============================================================================
# Check Bedrock Model Access
# =============================================================================
check_bedrock_access() {
    echo -e "${YELLOW}Checking Bedrock model access...${NC}"
    
    # Check Claude access
    CLAUDE_ACCESS=$(aws bedrock list-foundation-models --region $REGION \
        --query "modelSummaries[?modelId=='anthropic.claude-sonnet-4-5-20250929-v1:0'].modelId" \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$CLAUDE_ACCESS" ]; then
        echo -e "${RED}⚠️  Claude 3.5 Sonnet may not be accessible.${NC}"
        echo -e "${YELLOW}   Please enable it in Bedrock Console → Model access${NC}"
    else
        echo -e "${GREEN}✓ Claude 3.5 Sonnet available${NC}"
    fi
    
    # Check Titan Embeddings access
    TITAN_ACCESS=$(aws bedrock list-foundation-models --region $REGION \
        --query "modelSummaries[?contains(modelId, 'titan-embed')].modelId" \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$TITAN_ACCESS" ]; then
        echo -e "${RED}⚠️  Titan Embeddings may not be accessible.${NC}"
        echo -e "${YELLOW}   Please enable it in Bedrock Console → Model access${NC}"
    else
        echo -e "${GREEN}✓ Titan Embeddings available${NC}"
    fi
    
    echo ""
}

# =============================================================================
# Deploy CloudFormation Stack
# =============================================================================
deploy_infrastructure() {
    echo -e "${YELLOW}Deploying CloudFormation infrastructure...${NC}"
    
    # Use the deploy script for consistent deployment
    cd cloudformation && ./deploy.sh
    cd ..
    
    echo -e "${GREEN}✓ Infrastructure deployed${NC}"
    echo ""
}

# =============================================================================
# Upload Knowledge Base Content (handled by deploy.sh, but kept for manual re-sync)
# =============================================================================
upload_knowledge_base() {
    echo -e "${YELLOW}Verifying knowledge base content...${NC}"
    
    BUCKET_NAME="${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}"
    
    # Sync to ensure all files are uploaded (deploy.sh does this too)
    aws s3 sync knowledge-base/support-cases/ s3://${BUCKET_NAME}/support-cases/ --region $REGION
    
    echo -e "${GREEN}✓ Knowledge base content verified in s3://${BUCKET_NAME}${NC}"
    echo ""
}

# =============================================================================
# Create and Sync Bedrock Knowledge Base
# =============================================================================
setup_knowledge_base() {
    echo -e "${YELLOW}Setting up Bedrock Knowledge Base...${NC}"
    
    # Get the Knowledge Base ID from CloudFormation outputs
    KB_ID=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
        --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseId'].OutputValue" \
        --output text --region $REGION 2>/dev/null || echo "")
    
    if [ -z "$KB_ID" ]; then
        echo -e "${YELLOW}Knowledge Base not yet created via CloudFormation.${NC}"
        echo -e "${YELLOW}Please create it manually or wait for stack completion.${NC}"
    else
        echo "Knowledge Base ID: $KB_ID"
        
        # Get Data Source ID
        DS_ID=$(aws bedrock-agent list-data-sources --knowledge-base-id $KB_ID \
            --query "dataSourceSummaries[0].dataSourceId" --output text --region $REGION 2>/dev/null || echo "")
        
        if [ -n "$DS_ID" ]; then
            echo "Syncing data source: $DS_ID"
            # Try to start ingestion, but ignore if one is already running
            INGESTION_RESULT=$(aws bedrock-agent start-ingestion-job \
                --knowledge-base-id $KB_ID \
                --data-source-id $DS_ID \
                --region $REGION 2>&1) || true
            
            if echo "$INGESTION_RESULT" | grep -q "ConflictException"; then
                echo -e "${YELLOW}Ingestion job already in progress - skipping${NC}"
            else
                echo "Waiting for sync to complete (this may take a few minutes)..."
                sleep 30
            fi
        fi
        
        echo -e "${GREEN}✓ Knowledge Base setup complete${NC}"
    fi
    
    echo ""
}

# =============================================================================
# Deploy Frontend
# =============================================================================
deploy_frontend() {
    echo -e "${YELLOW}Deploying RAG Playground frontend...${NC}"
    
    # Get API endpoint from CloudFormation
    API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
        --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
        --output text --region $REGION 2>/dev/null)
    
    if [ -z "$API_ENDPOINT" ] || [ "$API_ENDPOINT" == "None" ]; then
        echo -e "${RED}⚠️  Could not get API endpoint. Frontend deployment skipped.${NC}"
        return
    fi
    
    # Get Knowledge Base ID from CloudFormation outputs
    KB_ID=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
        --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseId'].OutputValue" \
        --output text --region $REGION 2>/dev/null || echo "")
    
    if [ -n "$KB_ID" ] && [ "$KB_ID" != "None" ]; then
        echo "  Knowledge Base ID: $KB_ID"
    else
        KB_ID=""
    fi
    
    # Generate config.js with API endpoint and KB ID
    cat > frontend/config.js << EOF
// Configuration - Auto-generated by setup.sh
// Generated: $(date)

const API_ENDPOINT = '${API_ENDPOINT}';

// Knowledge Base ID - auto-populated if found during deployment
const DEFAULT_KB_ID = '${KB_ID}';
EOF
    
    # Get frontend bucket name
    FRONTEND_BUCKET="${PROJECT_NAME}-frontend-${ACCOUNT_ID}-${REGION}"
    
    # Wait for bucket to be ready
    echo "  Uploading frontend files to s3://${FRONTEND_BUCKET}..."
    for i in {1..5}; do
        if aws s3 ls "s3://${FRONTEND_BUCKET}" --region $REGION >/dev/null 2>&1; then
            break
        fi
        echo "  Waiting for bucket to be ready..."
        sleep 5
    done
    
    # Upload frontend files
    aws s3 sync frontend/ s3://${FRONTEND_BUCKET}/ \
        --exclude "deploy-frontend.sh" \
        --exclude ".DS_Store" \
        --region $REGION
    
    # Invalidate CloudFront cache
    CF_DIST_ID=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
        --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
        --output text --region $REGION 2>/dev/null || echo "")
    
    if [ -n "$CF_DIST_ID" ] && [ "$CF_DIST_ID" != "None" ]; then
        echo "  Invalidating CloudFront cache..."
        aws cloudfront create-invalidation --distribution-id $CF_DIST_ID --paths "/*" >/dev/null 2>&1 || true
    fi
    
    echo -e "${GREEN}✓ Frontend deployed${NC}"
    echo ""
}

# =============================================================================
# Validate Deployment
# =============================================================================
validate_deployment() {
    echo -e "${YELLOW}Validating deployment...${NC}"
    
    # Check stack status
    STACK_STATUS=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
        --query 'Stacks[0].StackStatus' --output text --region $REGION 2>/dev/null || echo "FAILED")
    
    if [ "$STACK_STATUS" == "CREATE_COMPLETE" ] || [ "$STACK_STATUS" == "UPDATE_COMPLETE" ]; then
        echo -e "${GREEN}✓ CloudFormation stack: $STACK_STATUS${NC}"
    else
        echo -e "${RED}❌ CloudFormation stack: $STACK_STATUS${NC}"
    fi
    
    # Check S3 bucket for knowledge base content
    BUCKET_NAME="${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}"
    BUCKET_CONTENT=$(aws s3 ls s3://${BUCKET_NAME}/support-cases/ --region $REGION 2>/dev/null | head -1)
    
    if [ -n "$BUCKET_CONTENT" ]; then
        echo -e "${GREEN}✓ S3 bucket exists with content${NC}"
    else
        echo -e "${RED}❌ S3 bucket not found or empty${NC}"
    fi
    
    echo ""
}

# =============================================================================
# Print Summary
# =============================================================================
print_summary() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "  Deployment Complete!"
    echo "============================================================"
    echo -e "${NC}"
    
    # Get outputs
    FRONTEND_URL=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
        --query "Stacks[0].Outputs[?OutputKey=='FrontendURL'].OutputValue" \
        --output text --region $REGION 2>/dev/null)
    
    API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name ${PROJECT_NAME}-stack \
        --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
        --output text --region $REGION 2>/dev/null)
    
    echo -e "${GREEN}Resources Created:${NC}"
    echo "  • S3 Bucket: ${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}"
    echo "  • CloudFormation Stack: ${PROJECT_NAME}-stack"
    echo "  • API Gateway: ${API_ENDPOINT}"
    echo ""
    
    echo -e "${GREEN}RAG Playground Web UI:${NC}"
    echo -e "  ${YELLOW}${FRONTEND_URL}${NC}"
    echo ""
    
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Create a Bedrock Knowledge Base in the console"
    echo "     - Go to: Amazon Bedrock → Knowledge bases → Create"
    echo "     - Use S3 bucket: ${PROJECT_NAME}-kb-${ACCOUNT_ID}-${REGION}"
    echo "     - Select 'Quick create' for vector store"
    echo "  2. Copy the Knowledge Base ID"
    echo "  3. Open the RAG Playground: ${FRONTEND_URL}"
    echo "  4. Enter your Knowledge Base ID and start testing!"
    echo ""
    
    echo -e "${RED}Don't forget to clean up when done:${NC}"
    echo "  cd cloudformation && ./cleanup.sh"
    echo ""
}

# =============================================================================
# Main Execution
# =============================================================================
main() {
    check_prerequisites
    check_bedrock_access
    deploy_infrastructure
    upload_knowledge_base
    setup_knowledge_base
    deploy_frontend
    validate_deployment
    print_summary
}

# Run main function
main
