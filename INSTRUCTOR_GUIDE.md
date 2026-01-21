# Instructor Guide: Week 3 - Prompt Engineering & Context Management

## Session Overview

| Component | Duration | Description |
|-----------|----------|-------------|
| Presentation | 40 min | Prompt engineering, embeddings, RAG concepts |
| Hands-On Lab | 60 min | Build and test RAG workflow |
| Kahoot Quiz | 15 min | Knowledge assessment |
| Buffer | 5 min | Q&A and wrap-up |
| **Total** | **120 min** | |

## Pre-Session Checklist

### 1 Week Before
- [ ] Test deployment in your AWS account (via CloudShell or local CLI)
- [ ] Create Kahoot quiz from `quiz/kahoot-questions.md`
- [ ] Review presentation slides
- [ ] Prepare demo environment
- [ ] Upload `SoGenAI_Week3.zip` to course repository for students

### Day Before
- [ ] Verify Bedrock model access is enabled in your account
- [ ] Test all scripts work correctly in CloudShell
- [ ] Prepare backup slides/demo if AWS issues occur
- [ ] Send reminder to students with prerequisites:
  - AWS account access
  - Enable Bedrock models BEFORE class

### Day Of
- [ ] Deploy infrastructure 30 minutes early
- [ ] Verify Knowledge Base is synced
- [ ] Test a few queries to warm up the system
- [ ] Have Kahoot quiz ready to launch
- [ ] Remind students to use CloudShell (no local setup needed)

## Presentation Tips

### Slides 1-3: Introduction
- Connect to Week 1 & 2 learnings
- Set expectations for hands-on portion
- **Key message:** "Today we'll make our AI smarter with context"

### Slides 4-10: Prompt Engineering
- Use live demos for each technique
- Show real Enterprise Support examples
- **Interactive:** Ask students to suggest prompts

### Slides 11-14: Embeddings
- Use visual analogies (words as points in space)
- Demo semantic similarity with simple examples
- **Key message:** "Similar meaning = similar vectors"

### Slides 15-20: RAG Architecture
- Walk through the diagram step by step
- Emphasize the "retrieval" before "generation"
- **Key message:** "Ground the AI in your data"

### Slides 21-23: Exercise Overview
- Show the architecture they'll build
- Set time expectations
- **Tip:** Have students start deployment during this section

### Slides 24-25: Best Practices
- Summarize key takeaways
- Preview Week 4 (Agents and Tool Use)

## Hands-On Lab Facilitation

### Part 1: Setup (20 min)
**Common Issues:**
- Bedrock models not enabled → Show console steps
- CloudFormation timeout → Usually resolves with retry
- S3 bucket naming conflicts → Use unique project names

**Instructor Actions:**
- Walk around and check progress
- Help students who are stuck on deployment
- Have backup KB ID ready if students can't create their own

### Part 2: Query and Compare (25 min)
**Key Demonstrations:**
1. Show non-RAG response first (generic)
2. Show RAG response (specific, contextual)
3. Use comparison script for side-by-side

**Discussion Points:**
- "What differences do you notice?"
- "Which response would be more helpful for a customer?"
- "What information is in the RAG response that wasn't in the other?"

### Part 3: Prompt Optimization (15 min)
**Exercises:**
1. Have students try different prompt styles
2. Compare TAM vs Solutions Architect roles
3. Test chain-of-thought for troubleshooting

**Discussion:**
- "When would you use each technique?"
- "How does this apply to your daily work?"

## Kahoot Quiz Administration

### Setup
1. Go to kahoot.it
2. Enter game PIN
3. Wait for all students to join

### Tips
- Read questions aloud for accessibility
- Allow 20-30 seconds per question
- Discuss wrong answers briefly
- Celebrate top scorers

### Question Categories
- Questions 1-7: Prompt Engineering
- Questions 8-12: Embeddings
- Questions 13-17: RAG Architecture
- Questions 18-20: Best Practices

## Troubleshooting Guide

### "InsufficientCapabilitiesException: Requires CAPABILITY_NAMED_IAM"
This is fixed in the latest scripts. If students see this:
1. Make sure they're using the latest `setup.sh` or `deploy.sh`
2. The scripts now include `--capabilities CAPABILITY_NAMED_IAM`

### "My deployment failed"
1. Check CloudFormation events for specific error
2. Most common: Bedrock models not enabled
3. Fallback: Share your KB ID with the student

### "CloudShell session timed out"
1. CloudShell sessions timeout after 20 minutes of inactivity
2. Students can reconnect and `cd SoGenAI_Week3` to continue
3. Deployed resources persist - no need to redeploy

### "RAG returns empty results"
1. Verify S3 content was uploaded
2. Check Knowledge Base sync status
3. Try a different query that matches document content

### "Responses are slow"
1. First query may have cold start
2. OpenSearch Serverless may be scaling
3. Normal response time: 3-8 seconds

### "Access Denied errors"
1. Check IAM role permissions
2. Verify Bedrock model access
3. Check region consistency

## Demo Scripts

### Quick RAG Demo
```bash
# Set your KB ID
export KB_ID=YOUR_KB_ID

# Show non-RAG
echo "=== Without RAG ==="
python3 scripts/query-knowledge-base.py --no-rag \
    "How do I increase my EC2 limit?"

# Show RAG
echo "=== With RAG ==="
python3 scripts/query-knowledge-base.py \
    "How do I increase my EC2 limit?"
```

### Prompt Style Demo
```bash
# Default
python3 scripts/query-knowledge-base.py --no-rag \
    "Explain Lambda throttling"

# Chain-of-thought
python3 scripts/query-knowledge-base.py --no-rag --prompt-style cot \
    "A customer's Lambda is timing out. Help me troubleshoot."

# TAM role
python3 scripts/query-knowledge-base.py --no-rag --role tam \
    "How should we optimize our AWS costs?"
```

## Backup Plans

### If AWS is Down
- Use pre-recorded demo videos
- Focus on conceptual discussion
- Have students work through prompt examples on paper

### If Time is Short
- Skip Part 3 of exercise (prompt optimization)
- Reduce quiz to 10 questions
- Provide take-home exercises

### If Students Finish Early
- Challenge: Create custom prompts for their use cases
- Explore: Try queries outside the knowledge base
- Discuss: How would they apply this to their work?
- Advanced: Review `docs/DATA_PREPARATION_GUIDE.md` for enterprise data ingestion patterns

## Advanced Topics (Optional)

### Data Preparation for Enterprise RAG
For students interested in preparing their own data for RAG:
- **Guide:** `docs/DATA_PREPARATION_GUIDE.md` - Comprehensive guide covering:
  - Data quality principles
  - Document preprocessing (HTML, Wiki, Confluence)
  - Chunking strategies
  - Metadata and filtering
  - Data connectors
- **Script:** `scripts/prepare-data-for-rag.py` - Utility for processing various data sources

## Post-Session

### Collect Feedback
- What worked well?
- What was confusing?
- What would they like more of?

### Share Resources
- GitHub repo link
- AWS documentation links
- Recording (if available)

### Remind About Cleanup
```bash
cd cloudformation && ./cleanup.sh
```

## Week 4 Preview

**Topic:** Agents and Tool Use

**Teaser:** "Next week, we'll give our AI the ability to take actions - not just answer questions, but actually do things in AWS."

## Contact

For issues with this session materials:
- Check TESTING.md for troubleshooting
- Review CloudFormation events for deployment issues
- Consult AWS documentation for service-specific questions
