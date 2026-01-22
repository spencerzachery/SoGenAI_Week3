# Student Quick Start Guide - RAG Pipeline for Enterprise Support

## 🎯 What You'll Build

A Retrieval-Augmented Generation (RAG) workflow that:
1. Stores Enterprise Support documentation in a vector database
2. Retrieves relevant context based on semantic similarity
3. Augments prompts with retrieved context
4. Generates accurate, contextual responses using Claude

## ⏱️ Time Required

- Deployment: 15 minutes
- Exercise: 45 minutes
- Cleanup: 5 minutes
- **Total: ~65 minutes**

## 📋 Prerequisites

✅ AWS Account (AWS Academy or personal)
✅ Basic terminal/command line knowledge
✅ Completed Week 1 & Week 2 sessions

## 🚀 Step-by-Step Instructions

### Step 1: Open AWS CloudShell (Recommended)

**CloudShell is the easiest way to run this lab - no local setup required!**

1. Log into AWS Console
2. Click the CloudShell icon (terminal icon) in the top navigation bar
3. Wait for CloudShell to initialize

**Verify you're ready:**
```bash
# Check you're logged in
aws sts get-caller-identity
```

**Expected output:**
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/student"
}
```

### Step 2: Upload and Extract Project Files (2 minutes)

1. Download the `SoGenAI_Week3.zip` file from the course repository
2. In CloudShell, click **Actions** → **Upload file**
3. Select the zip file and upload
4. Extract and prepare:

```bash
# Unzip the project
unzip SoGenAI_Week3.zip

# Navigate to project directory
cd SoGenAI_Week3

# Make scripts executable
chmod +x setup.sh
chmod +x cloudformation/*.sh
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Step 3: Enable Bedrock Models (3 minutes)

**IMPORTANT:** Do this before deploying!

1. Open a new browser tab → AWS Console → Amazon Bedrock
2. Click "Model access" in left menu
3. Click "Manage model access"
4. Enable these models:
   - ✅ **Anthropic Claude 4.5 Sonnet** (for generation)
   - ✅ **Amazon Titan Text Embeddings V2** (for embeddings)
5. Click "Save changes"
6. Wait for "Access granted" status

### Step 4: Deploy Infrastructure (10 minutes)

**Option A: Using setup.sh (Recommended)**
```bash
# Make sure you're in the project directory
cd SoGenAI_Week3

# Run deployment script
./setup.sh
```

**Option B: Using CloudFormation directly**
```bash
# Navigate to cloudformation directory
cd SoGenAI_Week3/cloudformation

# Run deploy script
./deploy.sh
```

**Wait for completion** (10-15 minutes). You'll see:
```
✓ Stack deployed successfully
✓ Knowledge Base created and synced
✓ All resources ready
Knowledge Base ID: XXXXXXXXXX
```

**SAVE THE KNOWLEDGE BASE ID!** You'll need it.

### Step 5: Validate Deployment (2 minutes)

```bash
# Run validation script
./scripts/test-deployment.sh
```

**Expected output:**
```
✓ AWS credentials configured
✓ CloudFormation stack exists
✓ S3 bucket created with content
✓ Knowledge Base synced
✓ All checks passed!
```

### Step 6: Deploy the RAG Playground Web UI (3 minutes)

```bash
# Navigate to frontend directory
cd frontend

# Deploy the web UI
./deploy-frontend.sh
```

**You'll see output like:**
```
✓ Generated config.js
✓ Frontend deployed
Frontend URL: http://rag-pipeline-frontend-123456789012-us-east-1.s3-website-us-east-1.amazonaws.com
```

**Open the Frontend URL in your browser!**

### Step 7: Test RAG Queries with the Web UI (10 minutes)

1. Open the RAG Playground URL in your browser
2. Enter your **Knowledge Base ID** in the sidebar
3. Try the sample queries or enter your own
4. Toggle between "Compare Both" and "RAG Only" modes
5. Experiment with different prompt styles:
   - **Zero-Shot**: Direct, concise answers
   - **Few-Shot**: Follows example patterns
   - **Chain-of-Thought**: Step-by-step reasoning
   - **TAM Role**: Enterprise relationship focus
   - **SA Role**: Architecture best practices

**Compare the responses!** Notice how RAG responses include citations and more specific information.

### Step 8: Explore the Prompt Engineering Lab (10 minutes)

1. Click the **"✨ Prompt Engineering Lab"** tab at the top
2. Select a technique from the sidebar to learn about it
3. Choose two techniques to compare (A vs B)
4. Enter a question and click "Compare Techniques"
5. See how different prompting strategies affect the response!

**Techniques to try:**
- **Zero-Shot vs Few-Shot**: See how examples improve formatting
- **Zero-Shot vs Chain-of-Thought**: Compare direct answers vs step-by-step reasoning
- **Role: TAM vs Role: SA**: See how persona affects tone and focus
- **Structured: JSON vs Structured: List**: Compare output formats

### Step 9: Complete the Exercise Guide

Follow the detailed instructions in `exercise-guide.md` to:
- Part 1: Explore the Knowledge Base
- Part 2: Compare RAG vs Non-RAG responses using the Web UI
- Part 3: Apply prompt engineering techniques in the Prompt Engineering Lab

### Step 10: Cleanup (5 minutes)

**IMPORTANT:** Clean up to avoid charges!

```bash
cd ../cloudformation
./cleanup.sh
```

## 🎓 What You Learned

✅ Prompt engineering strategies (zero-shot, few-shot, CoT)
✅ How embeddings enable semantic search
✅ RAG pipeline architecture and components
✅ Amazon Bedrock Knowledge Bases
✅ Context management for better LLM responses
✅ Enterprise Support use cases for RAG

## 📊 Architecture Overview

![RAG Pipeline Architecture](diagrams/rag-pipeline-architecture.png)

| Component | AWS Service | Purpose |
|-----------|-------------|---------|
| Frontend | CloudFront + S3 | Secure static hosting |
| API | API Gateway + Lambda | Query handling |
| Knowledge Base | Bedrock KB + S3 Vectors | Document retrieval |
| Generation | Claude 4.5 Sonnet | Response generation |

## 🔍 Troubleshooting

### Issue: "Knowledge Base not found"
- Verify the Knowledge Base ID is correct
- Check CloudFormation stack status
- Ensure sync completed successfully

### Issue: "Model access denied"
- Go to Bedrock console → Model access
- Enable Claude 4.5 Sonnet and Titan Embeddings
- Wait for "Access granted" status

### Issue: "Empty retrieval results"
- Verify S3 bucket has content uploaded
- Check Knowledge Base sync status
- Try a different query

## ✅ Completion Checklist

- [ ] AWS CLI configured
- [ ] Bedrock models enabled
- [ ] Infrastructure deployed
- [ ] Validation passed
- [ ] RAG queries tested
- [ ] Exercise guide completed
- [ ] Cleanup completed

## 🎉 Success!

You've successfully built a RAG pipeline using:
- Amazon Bedrock Knowledge Bases
- Amazon Titan Embeddings
- S3 Vector Store
- Claude 4.5 Sonnet
- AWS CloudFormation

**Great job!** 🚀

---

## 📚 Take-Home Resources

### Reusable Architecture (Start Here!)
**This is yours to keep and reuse:**
- **Guide:** `docs/RAG_REFERENCE_ARCHITECTURE.md`
  - Fork this repo, swap the docs, deploy for your team in 15 minutes
  - Complete architecture with security, scalability, and cost considerations
  - Step-by-step customization (change prompts, add auth, use different models)
  - Cost estimation (~$65-115/month for typical internal tool)

### Go Deeper (Optional)
- **Data Preparation:** `docs/DATA_PREPARATION_GUIDE.md`
  - Chunking strategies and their tradeoffs
  - Metadata filtering for better retrieval
  - Data quality best practices

- **Custom Connectors:** `docs/CUSTOM_CONNECTOR_GUIDE.md`
  - Build pipelines to ingest your own data (tickets, wikis, docs)
  - Lambda + EventBridge patterns for scheduled sync
  - Real-world examples with code

---

**Remember to clean up after the lab to avoid charges!**

```bash
cd cloudformation && ./cleanup.sh
```
