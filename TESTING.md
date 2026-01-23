# Testing Guide: Week 3 RAG Pipeline

This document provides comprehensive testing procedures for validating the Week 3 deployment.

## Pre-Deployment Testing

### 1. Validate CloudFormation Template

```bash
# Validate template syntax
aws cloudformation validate-template \
    --template-body file://cloudformation/rag-pipeline-stack.yaml

# Expected: No errors, returns template parameters
```

### 2. Check Prerequisites

```bash
./scripts/check-aws-setup.sh
```

**Expected output:**
```
✓ AWS CLI installed
✓ AWS credentials configured (Account: XXXXXXXXXXXX)
✓ Python 3 installed
✓ Bedrock Claude models available
All prerequisites met!
```

## Deployment Testing

### 1. Deploy Infrastructure

```bash
./setup.sh
```

**Verify:**
- [ ] CloudFormation stack creates successfully
- [ ] S3 bucket is created
- [ ] S3 Vector Store is created
- [ ] IAM roles are created
- [ ] Lambda function is deployed

### 2. Validate Deployment

```bash
./scripts/test-deployment.sh
```

**Expected output:**
```
✓ AWS credentials configured
✓ CloudFormation stack: CREATE_COMPLETE
✓ S3 bucket exists with content
Results: 3 passed, 0 failed
```

### 3. Verify Knowledge Base

```bash
# List knowledge bases
aws bedrock-agent list-knowledge-bases \
    --query "knowledgeBaseSummaries[?contains(name,'rag-pipeline')]"

# Check sync status
aws bedrock-agent list-data-sources \
    --knowledge-base-id YOUR_KB_ID
```

## Functional Testing

### 1. Test Non-RAG Query

```bash
python3 scripts/query-knowledge-base.py --no-rag \
    "How do I request an EC2 instance limit increase?"
```

**Expected:** Generic response about EC2 limits without specific documentation references.

### 2. Test RAG Query

```bash
export KB_ID=YOUR_KNOWLEDGE_BASE_ID

python3 scripts/query-knowledge-base.py \
    "How do I request an EC2 instance limit increase?"
```

**Expected:** 
- Response includes specific steps from our documentation
- Citations reference S3 source documents
- More detailed and actionable than non-RAG response

### 3. Test Comparison

```bash
python3 scripts/compare-responses.py \
    "How do I request an EC2 instance limit increase?"
```

**Expected:**
- Side-by-side comparison shows clear difference
- RAG response has higher specificity score
- Analysis indicates RAG improvement

### 4. Test Prompt Styles

```bash
# Zero-shot
python3 scripts/query-knowledge-base.py --no-rag --prompt-style default \
    "Explain Lambda throttling"

# Few-shot
python3 scripts/query-knowledge-base.py --no-rag --prompt-style few-shot \
    "Explain Lambda throttling"

# Chain-of-thought
python3 scripts/query-knowledge-base.py --no-rag --prompt-style cot \
    "A customer's Lambda is timing out. What should they check?"

# Role-based (TAM)
python3 scripts/query-knowledge-base.py --no-rag --role tam \
    "How should we optimize our EC2 costs?"
```

**Expected:** Different prompt styles produce noticeably different response formats and detail levels.

## Content Validation

### 1. Verify Knowledge Base Content

```bash
# List uploaded files
aws s3 ls s3://rag-pipeline-kb-${ACCOUNT_ID}-${REGION}/support-cases/
```

**Expected files:**
- service-limits.txt
- outage-scenarios.txt
- troubleshooting.txt
- best-practices.txt

### 2. Test Each Content Category

| Category | Test Query | Expected Content |
|----------|------------|------------------|
| Service Limits | "How do I increase Lambda concurrent executions?" | Steps to request limit increase |
| Outages | "How do I set up Route 53 failover?" | Health check configuration steps |
| Troubleshooting | "My EC2 instance is unreachable" | Troubleshooting checklist |
| Best Practices | "What are IAM best practices?" | Security recommendations |

### 3. Verify Quiz Content

```bash
# Count questions in quiz file
grep -c "^### Question" quiz/kahoot-questions.md
# Expected: 20

# Verify answer distribution
grep -c "✓" quiz/kahoot-questions.md
# Expected: 20 (one correct answer per question)
```

## Performance Testing

### 1. Response Time

```bash
# Time a RAG query
time python3 scripts/query-knowledge-base.py \
    "How do I troubleshoot Lambda timeouts?"
```

**Expected:** Response within 5-10 seconds

### 2. Multiple Queries

```bash
# Test multiple queries in sequence
for query in \
    "How do I increase EC2 limits?" \
    "What is the Lambda timeout maximum?" \
    "How do I set up Route 53 health checks?"; do
    echo "Query: $query"
    python3 scripts/query-knowledge-base.py "$query" 2>/dev/null | head -5
    echo "---"
done
```

## Error Handling Testing

### 1. Invalid Knowledge Base ID

```bash
export KB_ID=invalid-kb-id
python3 scripts/query-knowledge-base.py "test query"
# Expected: Clear error message about invalid KB
```

### 2. Missing Credentials

```bash
# Temporarily unset credentials
AWS_ACCESS_KEY_ID= python3 scripts/query-knowledge-base.py --no-rag "test"
# Expected: Clear error about missing credentials
```

### 3. Empty Query

```bash
python3 scripts/query-knowledge-base.py ""
# Expected: Error or prompt for valid query
```

## Cleanup Testing

### 1. Run Cleanup

```bash
cd cloudformation
./cleanup.sh
```

### 2. Verify Cleanup

```bash
# Stack should not exist
aws cloudformation describe-stacks --stack-name rag-pipeline-stack
# Expected: "Stack does not exist" error

# S3 bucket should not exist
aws s3 ls s3://rag-pipeline-kb-${ACCOUNT_ID}-${REGION}
# Expected: "NoSuchBucket" error
```

## Test Checklist

### Deployment
- [ ] CloudFormation template validates
- [ ] Stack deploys successfully
- [ ] All resources created
- [ ] Knowledge Base syncs successfully

### Functionality
- [ ] Non-RAG queries work
- [ ] RAG queries return contextual responses
- [ ] Comparison script shows improvement
- [ ] All prompt styles work
- [ ] Role-based prompts work

### Content
- [ ] All 4 knowledge base files uploaded
- [ ] Queries return relevant content
- [ ] Citations reference correct sources
- [ ] Quiz has 20 questions with answers

### Error Handling
- [ ] Invalid KB ID handled gracefully
- [ ] Missing credentials show clear error
- [ ] Network errors handled

### Cleanup
- [ ] All resources deleted
- [ ] No orphaned resources remain

## Troubleshooting Test Failures

### "Knowledge Base not found"
1. Verify KB was created: `aws bedrock-agent list-knowledge-bases`
2. Check KB_ID environment variable
3. Verify region matches

### "Empty retrieval results"
1. Check S3 bucket has content
2. Verify sync completed successfully
3. Try different query terms

### "Access Denied"
1. Check Bedrock model access in console
2. Verify IAM role permissions
3. Check VPC endpoint policies if applicable

### "Timeout errors"
1. Increase Lambda timeout
2. Check network connectivity
3. Verify S3 Vector Store is active
