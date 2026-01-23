# Exercise Guide: Building a RAG Workflow for Enterprise Support

## Learning Objectives

By completing this exercise, you will:
- Create and configure an Amazon Bedrock Knowledge Base
- Upload and sync Enterprise Support documentation
- Query the knowledge base using semantic search
- Compare RAG vs non-RAG response quality
- Apply prompt engineering techniques to improve responses

## Part 1: Setup and Knowledge Base Creation (20 minutes)

### Step 1.1: Deploy Infrastructure (5 minutes)

If you haven't already deployed the infrastructure:

```bash
# Navigate to project directory
cd SoGenAI_Week3

# Run the setup script
./setup.sh
```

Or deploy manually:

```bash
cd cloudformation
./deploy.sh
```

**Verify deployment:**
```bash
# Check stack status
aws cloudformation describe-stacks --stack-name rag-pipeline-stack \
    --query 'Stacks[0].StackStatus' --output text
```

Expected output: `CREATE_COMPLETE`

### Step 1.2: Upload Knowledge Base Content (3 minutes)

```bash
# Get your account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

# Upload support case documents
aws s3 sync knowledge-base/support-cases/ \
    s3://rag-pipeline-kb-${ACCOUNT_ID}-${REGION}/support-cases/
```

**Verify upload:**
```bash
aws s3 ls s3://rag-pipeline-kb-${ACCOUNT_ID}-${REGION}/support-cases/
```

You should see:
- service-limits.txt
- outage-scenarios.txt
- troubleshooting.txt
- best-practices.txt

### Step 1.3: Create Bedrock Knowledge Base (10 minutes)

**Option A: AWS Console**

1. Go to AWS Console → Amazon Bedrock → Knowledge bases
2. Click "Create knowledge base"
3. Configure:
   - Name: `rag-pipeline-kb`
   - Description: `Enterprise Support case resolution knowledge base`
   - IAM role: Select the role created by CloudFormation (`rag-pipeline-bedrock-kb-role`)

4. Configure data source:
   - Data source name: `support-cases`
   - S3 URI: `s3://rag-pipeline-kb-{ACCOUNT_ID}-{REGION}/support-cases/`

5. Configure embeddings:
   - Embeddings model: Amazon Titan Embeddings V2
   - Vector database: S3 Vectors (auto-created)

6. Review and create

7. After creation, click "Sync" to ingest documents

**Option B: AWS CLI**

```bash
# Create knowledge base (simplified - full script in scripts/create-knowledge-base.sh)
python3 scripts/create-knowledge-base.py
```

### Step 1.4: Verify Knowledge Base Sync (2 minutes)

1. In Bedrock console, go to your knowledge base
2. Check the data source status: Should show "Available"
3. Check sync status: Should show "Completed"

**Note the Knowledge Base ID** - you'll need it for queries.

```bash
# Or get it via CLI
aws bedrock-agent list-knowledge-bases \
    --query "knowledgeBaseSummaries[?name=='rag-pipeline-kb'].knowledgeBaseId" \
    --output text
```

## Part 2: Query and Compare Using the RAG Playground (25 minutes)

### Step 2.1: Deploy the Web UI (3 minutes)

```bash
# Navigate to frontend directory
cd frontend

# Deploy the RAG Playground
./deploy-frontend.sh
```

Copy the **Frontend URL** from the output and open it in your browser.

### Step 2.2: Configure the RAG Playground (2 minutes)

1. Open the RAG Playground URL in your browser
2. In the sidebar, enter your **Knowledge Base ID**
3. The ID is saved locally, so you won't need to enter it again

### Step 2.3: Test Direct Model Query (No RAG) (5 minutes)

First, let's see how Claude responds without access to our knowledge base:

1. In the RAG Playground, set **Compare Mode** to "Compare Both"
2. Enter this query:
   ```
   How do I request an EC2 instance limit increase?
   ```
3. Click **Submit Query**

**Observe the "Direct" panel (right side):**
- Is the response accurate?
- Is it specific to your organization's process?
- Does it include current, detailed steps?

### Step 2.4: Compare RAG vs Direct Responses (10 minutes)

Look at both panels side-by-side:

**RAG Response (left panel):**
- Includes specific steps from your knowledge base
- Shows citations to source documents
- More detailed and actionable

**Direct Response (right panel):**
- Generic AWS knowledge
- No organization-specific context
- May be less current

**Try these additional queries:**

1. **Service Limits:**
   ```
   What should I do if my Lambda function is being throttled?
   ```

2. **Outage Response:**
   ```
   How do I set up Route 53 health checks for failover?
   ```

3. **Troubleshooting:**
   ```
   My EC2 instance is unreachable. What should I check?
   ```

4. **Best Practices:**
   ```
   What are the IAM best practices for security?
   ```

### Step 2.5: Document Your Findings (5 minutes)

For each query, note:

| Query | Without RAG | With RAG | Improvement |
|-------|-------------|----------|-------------|
| EC2 limit increase | Generic steps | Specific console URL, detailed process | ✓ More actionable |
| Lambda throttling | Basic explanation | Troubleshooting checklist, resolution steps | ✓ More comprehensive |
| ... | ... | ... | ... |

## Part 3: Prompt Engineering Lab (20 minutes)

The Prompt Engineering Lab lets you compare different prompting techniques side-by-side to see how they affect response quality.

### Step 3.1: Access the Prompt Engineering Lab (2 minutes)

1. In the RAG Playground, click the **"✨ Prompt Engineering Lab"** tab at the top
2. You'll see a sidebar with technique cards and a comparison area

### Step 3.2: Explore Technique Information (3 minutes)

Click on each technique card in the sidebar to learn about it:

- **Zero-Shot**: Direct instruction without examples
- **Few-Shot**: Provide examples to guide format
- **Chain-of-Thought**: Step-by-step reasoning
- **Role-Based**: Assign persona (TAM, SA)
- **Structured Output**: Request specific format (JSON, lists)
- **Self-Consistency**: Model verifies its own answer

Each card shows:
- When to use the technique
- Limitations to be aware of

### Step 3.3: Compare Zero-Shot vs Few-Shot (5 minutes)

1. Set **Technique A** to "Zero-Shot"
2. Set **Technique B** to "Few-Shot"
3. Enter this query:
   ```
   How do I troubleshoot a Lambda function timeout?
   ```
4. Click **Compare Techniques**

**Observe the differences:**
- Zero-Shot: May have inconsistent formatting
- Few-Shot: Follows the structured format from examples

**Look at the prompt previews** to see exactly what's being sent to the model.

### Step 3.4: Compare Chain-of-Thought vs Direct (5 minutes)

1. Set **Technique A** to "Zero-Shot"
2. Set **Technique B** to "Chain-of-Thought"
3. Enter this complex query:
   ```
   A customer reports their application is slow. They're using EC2, RDS, and ElastiCache. Help me troubleshoot.
   ```
4. Click **Compare Techniques**

**Observe:**
- Zero-Shot: May jump to conclusions
- Chain-of-Thought: Shows systematic reasoning process

### Step 3.5: Compare Role-Based Prompts (5 minutes)

1. Set **Technique A** to "Role: TAM"
2. Set **Technique B** to "Role: Solutions Architect"
3. Enter:
   ```
   A customer wants to improve their application's availability. What do you recommend?
   ```
4. Click **Compare Techniques**

**Observe the different perspectives:**
- **TAM**: Focuses on business outcomes, relationship, proactive guidance
- **SA**: Focuses on architecture patterns, trade-offs, technical options

### Step 3.6: Explore Structured Output (Optional)

1. Set **Technique A** to "Structured: JSON"
2. Set **Technique B** to "Structured: Numbered List"
3. Enter:
   ```
   What are the steps to enable CloudWatch detailed monitoring for EC2?
   ```
4. Compare the output formats

**Use cases:**
- JSON: Great for automation and parsing
- Numbered List: Great for documentation and checklists

## Part 4: Advanced Prompt Optimization (10 minutes)

## Part 4: Advanced Prompt Optimization (10 minutes)

### Step 4.1: Combine RAG with Prompt Engineering

Go back to the **RAG Playground** tab and try combining RAG with different prompt styles:

1. Set mode to **RAG Only**
2. Try the same query with different prompt styles:
   - Default
   - Chain-of-Thought
   - TAM Role

**Observe:** How does prompt style affect RAG responses?

### Step 4.2: Custom Prompts

1. Select **Prompt Style: Custom**
2. Edit the system prompt to create your own:
   ```
   You are a senior AWS support engineer specializing in serverless architectures.
   Always provide:
   1. Root cause analysis
   2. Immediate fix
   3. Long-term prevention
   Format your response with clear headers.
   ```
3. Test with a serverless-related query

## Verification Checklist

- [ ] CloudFormation stack deployed successfully
- [ ] S3 bucket contains knowledge base documents
- [ ] Bedrock Knowledge Base created and synced
- [ ] Non-RAG queries return generic responses
- [ ] RAG queries return contextual, specific responses
- [ ] Comparison shows clear improvement with RAG
- [ ] Prompt Engineering Lab: Compared Zero-Shot vs Few-Shot
- [ ] Prompt Engineering Lab: Compared Chain-of-Thought vs Direct
- [ ] Prompt Engineering Lab: Compared TAM vs SA roles
- [ ] Different prompt styles produce different response qualities

## Troubleshooting

### Issue: "Knowledge Base not found"
```bash
# Verify KB exists
aws bedrock-agent list-knowledge-bases

# Check KB_ID environment variable
echo $KB_ID
```

### Issue: "Access Denied" on Bedrock
1. Go to Bedrock console → Model access
2. Enable Claude 4.5 Sonnet and Titan Embeddings
3. Wait for "Access granted" status

### Issue: "Empty retrieval results"
1. Verify S3 bucket has content
2. Check Knowledge Base sync status
3. Try a different query that matches document content

### Issue: "Sync failed"
1. Check IAM role permissions
2. Verify S3 bucket policy allows Bedrock access
3. Check CloudWatch logs for detailed errors

## Clean Up

When you're done with the exercise:

```bash
cd cloudformation
./cleanup.sh
```

This will delete:
- CloudFormation stack
- S3 bucket and contents
- Bedrock Knowledge Base
- S3 Vector Store
- IAM roles

## Additional Resources

- **Prompt Examples:** See `prompts/` directory
- **Sample Queries:** See `knowledge-base/sample-queries.md`
- **AWS Documentation:** [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)

## What You Learned

✅ How to create and configure Bedrock Knowledge Bases
✅ The difference RAG makes in response quality
✅ How to apply prompt engineering techniques
✅ How to compare prompting strategies side-by-side
✅ When to use different techniques (zero-shot, few-shot, CoT, role-based)
✅ Best practices for Enterprise Support scenarios
✅ How to evaluate and compare LLM responses

**Great job completing the exercise!** 🎉
