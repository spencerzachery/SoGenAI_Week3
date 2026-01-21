# Prompt Engineering & Context Management with RAG

Complete AWS solution for building a Retrieval-Augmented Generation (RAG) workflow using Amazon Bedrock Knowledge Bases, designed for Enterprise Support case resolution scenarios.

## 🎯 What This Is

A hands-on learning experience that teaches prompt engineering strategies, embeddings, and RAG pipelines through building a functional support case resolution system.

**Perfect for:**
- Learning prompt engineering techniques (zero-shot, few-shot, chain-of-thought)
- Understanding embeddings and vector similarity search
- Building RAG pipelines with Bedrock Knowledge Bases
- Enterprise Support case resolution scenarios
- Classroom exercises (40+ students tested)

## ✨ Key Features

- 🤖 **Amazon Bedrock Knowledge Bases** - Managed RAG with automatic chunking and embedding
- 📚 **Enterprise Support Content** - Realistic case scenarios (service limits, outages, best practices)
- 🔍 **Semantic Search** - Vector-based retrieval with OpenSearch Serverless
- 💡 **Prompt Engineering Examples** - Zero-shot, few-shot, CoT, role-based prompts
- 🌐 **RAG Playground Web UI** - Interactive interface for testing prompts and comparing responses
- 📊 **RAG vs Non-RAG Comparison** - Side-by-side view of how context improves responses
- 🛡️ **Production-ready** - CloudFormation deployment, error handling
- 👥 **Multi-account** - Ready for 40+ students (no hardcoded values)

## 🚀 Quick Deploy (15-20 minutes)

### Prerequisites

1. **AWS Account** with admin access
2. **Enable Bedrock Models:**
   - Go to AWS Console → Amazon Bedrock → Model access
   - Enable: **Anthropic Claude 3.5 Sonnet**
   - Enable: **Amazon Titan Embeddings V2**
   - Wait for "Access granted" status

### Deployment via CloudShell (Recommended for Students)

**CloudShell requires no local setup - everything runs in your browser!**

1. Log into AWS Console
2. Click the **CloudShell** icon (terminal) in the top navigation
3. Upload and extract the project:

```bash
# After uploading SoGenAI_Week3.zip via Actions → Upload file
unzip SoGenAI_Week3.zip
cd SoGenAI_Week3

# Make scripts executable
chmod +x setup.sh cloudformation/*.sh scripts/*.sh scripts/*.py

# Deploy everything
./setup.sh
```

### Deployment via Local CLI

If you have AWS CLI configured locally:

```bash
cd SoGenAI_Week3
./setup.sh
```

This single script handles everything:
- ✅ CloudFormation infrastructure deployment
- ✅ S3 bucket creation and knowledge base content upload
- ✅ Bedrock Knowledge Base creation and sync
- ✅ OpenSearch Serverless collection setup
- ✅ Query interface deployment
- ✅ Deployment validation

**Time:** 15-20 minutes, fully automated

### Manual Step-by-Step

```bash
# 1. Deploy infrastructure
cd cloudformation
./deploy.sh

# 2. Upload knowledge base content
cd ../knowledge-base
./upload-content.sh

# 3. Sync Knowledge Base
./sync-knowledge-base.sh

# 4. Test the deployment
cd ../scripts
./test-deployment.sh
```

## 📋 What Gets Deployed

- S3 Bucket for knowledge base content
- S3 Bucket for RAG Playground web UI (static website hosting)
- Bedrock Knowledge Base with Titan Embeddings
- OpenSearch Serverless collection for vectors
- Lambda function for query API
- API Gateway HTTP endpoint
- IAM roles and policies

## 🌐 RAG Playground & Prompt Engineering Lab

After deployment, you'll get a web-based interface with two modes:

### RAG Playground
- Testing different prompt engineering strategies with RAG
- Comparing RAG vs Direct (non-RAG) responses side-by-side
- Experimenting with prompt styles (zero-shot, few-shot, CoT, role-based)
- Viewing citations from retrieved documents

### Prompt Engineering Lab
- Side-by-side comparison of different prompting techniques
- 8 built-in techniques: Zero-Shot, Few-Shot, Chain-of-Thought, Role-Based (TAM/SA), Structured Output (JSON/List), Self-Consistency
- Technique info cards explaining when to use each approach
- See the actual prompts being sent to the model

Access the UI at the Frontend URL provided after deployment.

## 🎓 Session Structure (2 Hours)

| Component | Duration | Description |
|-----------|----------|-------------|
| Presentation | 40 min | Prompt engineering, embeddings, RAG concepts |
| Hands-On Lab | 60 min | Build and test RAG workflow |
| Kahoot Quiz | 15 min | Knowledge assessment |
| Buffer | 5 min | Q&A and wrap-up |

## 📚 Documentation

- **[STUDENT_GUIDE.md](STUDENT_GUIDE.md)** - Quick start for students
- **[exercise-guide.md](exercise-guide.md)** - Detailed 60-minute lab
- **[presentation-slides.md](presentation-slides.md)** - 25 slides for instructors
- **[prompts/](prompts/)** - Prompt engineering examples
- **[docs/DATA_PREPARATION_GUIDE.md](docs/DATA_PREPARATION_GUIDE.md)** - Enterprise data preparation for RAG (wiki, support cases, connectors)
- **[scripts/prepare-data-for-rag.py](scripts/prepare-data-for-rag.py)** - Data preparation utility script

## 💰 Cost: ~$1-2/session or FREE with AWS Academy

## 🧹 Cleanup

```bash
cd cloudformation && ./cleanup.sh
```

## 🎉 Ready for Production and 40+ Students!

**Your RAG Pipeline is complete, tested, and ready to use!** 🚀
