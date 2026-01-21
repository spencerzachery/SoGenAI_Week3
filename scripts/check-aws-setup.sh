#!/bin/bash
# Check AWS setup prerequisites
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "  AWS Setup Prerequisites Check"
echo "============================================"
echo ""

# Check AWS CLI
if command -v aws &> /dev/null; then
    echo -e "${GREEN}✓ AWS CLI installed${NC}"
else
    echo -e "${RED}✗ AWS CLI not found${NC}"
    exit 1
fi

# Check credentials
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
if [ -n "$ACCOUNT_ID" ]; then
    echo -e "${GREEN}✓ AWS credentials configured (Account: $ACCOUNT_ID)${NC}"
else
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 installed${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Check Bedrock access
REGION="${AWS_REGION:-us-east-1}"
CLAUDE=$(aws bedrock list-foundation-models --region $REGION \
    --query "modelSummaries[?contains(modelId,'claude')].modelId" --output text 2>/dev/null | head -1)

if [ -n "$CLAUDE" ]; then
    echo -e "${GREEN}✓ Bedrock Claude models available${NC}"
else
    echo -e "${YELLOW}⚠ Check Bedrock model access in console${NC}"
fi

echo ""
echo -e "${GREEN}All prerequisites met!${NC}"
