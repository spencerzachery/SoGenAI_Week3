# RAG Reference Architecture for Enterprise Applications

## Take This With You

This architecture is designed to be reusable. Fork this repo, swap out the knowledge base content, and you have a production-ready RAG system for your team.

---

## Architecture Diagram

![RAG Pipeline Architecture](../diagrams/rag-pipeline-architecture.png)

---

## Architecture Overview

The RAG pipeline consists of these key components:

| Component | AWS Service | Purpose |
|-----------|-------------|---------|
| Frontend | CloudFront + S3 | Secure static hosting with edge caching |
| API Layer | API Gateway + Lambda | Serverless query handling |
| Knowledge Base | Bedrock Knowledge Base | Document storage, chunking, retrieval |
| Vector Store | S3 Vectors | Cost-effective vector storage |
| Embeddings | Titan Embeddings V2 | Semantic search |
| Generation | Claude 4.5 Sonnet | Response generation |

---

## What Makes This Production-Ready

### 1. Security
- **No public S3 buckets** — [CloudFront with Origin Access Control](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- **IAM least privilege** — Each component has minimal required permissions
- **HTTPS everywhere** — CloudFront enforces TLS
- **Private knowledge base** — S3 vector store, no external dependencies

### 2. Scalability
- **Serverless** — [Lambda + API Gateway](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html) scale automatically
- **S3 vector store** — No cluster management, [scales with data](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-bedrock-kb.html)
- **CloudFront caching** — Reduces origin load for static assets

### 3. Cost Efficiency
- **Pay-per-use** — No idle compute costs
- **S3 vector store** — Cheaper than OpenSearch Serverless for most workloads
- **Titan embeddings** — Cost-effective embedding model

### 4. Maintainability
- **Infrastructure as Code** — Everything in CloudFormation
- **Single deploy script** — `./setup.sh` does everything
- **Automatic ingestion** — Documents sync on deploy

---

## Adapting for Your Use Case

### Step 1: Fork and Clone
```bash
git clone https://github.com/YOUR_ORG/YOUR_RAG_PROJECT.git
cd YOUR_RAG_PROJECT
```

### Step 2: Replace Knowledge Base Content
```bash
# Remove sample content
rm -rf knowledge-base/support-cases/*

# Add your documents
cp -r /path/to/your/docs/* knowledge-base/support-cases/

# Supported formats: .txt, .md, .pdf, .html, .docx, .csv
```

### Step 3: Customize the System Prompt
Edit the Lambda function's default system prompt in `cloudformation/rag-pipeline-stack.yaml`:

```python
system_prompt = body.get('systemPrompt') or 'You are a [YOUR ROLE]. Provide [YOUR GUIDELINES].'
```

### Step 4: Deploy
```bash
export AWS_REGION=us-west-2  # Your preferred region
./setup.sh
```

### Step 5: Integrate with Your Application
```javascript
// Example: Call the RAG API from your app
const response = await fetch(`${API_ENDPOINT}/query`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: userQuestion,
    useRag: true,
    systemPrompt: 'You are a helpful assistant for our product...'
  })
});

const { response: answer, citations } = await response.json();
```

---

## Common Customizations

### Add Metadata Filtering
Filter retrieval by document attributes:

```python
# In your Lambda or client code
response = bedrock_agent.retrieve(
    knowledgeBaseId=kb_id,
    retrievalQuery={'text': query},
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 5,
            'filter': {
                'equals': {'key': 'category', 'value': 'troubleshooting'}
            }
        }
    }
)
```

Add metadata to documents by creating sidecar files:
```
documents/
  guide.txt
  guide.txt.metadata.json  ← {"category": "troubleshooting", "product": "widget"}
```

### Change Chunking Strategy
Edit the data source configuration in the CloudFormation template. See [How content chunking works](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html) for details.

```yaml
VectorIngestionConfiguration:
  ChunkingConfiguration:
    ChunkingStrategy: SEMANTIC  # or FIXED_SIZE, HIERARCHICAL
    SemanticChunkingConfiguration:
      MaxTokens: 500
      BufferSize: 0
      BreakpointPercentileThreshold: 95
```

### Add Authentication
Add Cognito or IAM authentication to API Gateway:

```yaml
ApiGateway:
  Type: AWS::ApiGatewayV2::Api
  Properties:
    # ... existing config ...
    
ApiAuthorizer:
  Type: AWS::ApiGatewayV2::Authorizer
  Properties:
    ApiId: !Ref ApiGateway
    AuthorizerType: JWT
    IdentitySource:
      - '$request.header.Authorization'
    JwtConfiguration:
      Audience:
        - !Ref CognitoUserPoolClient
      Issuer: !Sub 'https://cognito-idp.${AWS::Region}.amazonaws.com/${CognitoUserPool}'
```

### Use a Different LLM
Change the model in the Lambda environment or pass it per-request:

```yaml
Environment:
  Variables:
    DEFAULT_MODEL_ID: 'anthropic.claude-sonnet-4-5-20250929-v1:0'  # Default (best quality)
    # Or: 'anthropic.claude-3-5-sonnet-20241022-v2:0'  # Previous gen, still excellent
    # Or: 'anthropic.claude-3-haiku-20240307-v1:0'  # Faster, cheaper
```

### Add Streaming Responses
For chat interfaces, enable streaming:

```python
response = bedrock.invoke_model_with_response_stream(
    modelId=model_id,
    body=json.dumps({...})
)

for event in response['body']:
    chunk = json.loads(event['chunk']['bytes'])
    yield chunk['completion']
```

---

## Operational Considerations

### Monitoring
Key CloudWatch metrics to watch:
- `AWS/Lambda`: Invocations, Errors, Duration, Throttles
- `AWS/ApiGateway`: 4XXError, 5XXError, Latency
- `AWS/Bedrock`: InvocationCount, InvocationLatency

### Cost Estimation
For a typical internal tool (~1000 queries/day):

| Component | Estimated Monthly Cost |
|-----------|----------------------|
| Lambda | ~$5 |
| API Gateway | ~$3 |
| Bedrock (Claude) | ~$50-100 |
| Bedrock (Embeddings) | ~$5 |
| S3 | ~$1 |
| CloudFront | ~$1 |
| **Total** | **~$65-115/month** |

### Updating Content
To refresh knowledge base content:

```bash
# Upload new documents
aws s3 sync ./new-docs/ s3://${KB_BUCKET}/

# Trigger re-ingestion
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id ${KB_ID} \
  --data-source-id ${DS_ID}
```

Or automate with EventBridge + Lambda (see `docs/CUSTOM_CONNECTOR_GUIDE.md`).

---

## When to Use This vs. Alternatives

### Use This Architecture When:
- ✅ You need grounded, accurate responses from your own data
- ✅ Your document corpus is < 10GB
- ✅ You want serverless, low-maintenance infrastructure
- ✅ You need quick deployment (< 15 minutes)
- ✅ Your team is familiar with AWS

### Consider Alternatives When:
- ❌ You need real-time data (use agents with tools instead)
- ❌ Your corpus is > 100GB (consider OpenSearch Serverless)
- ❌ You need sub-100ms latency (consider caching layer)
- ❌ You're multi-cloud (consider vendor-neutral vector DB)

---

## Architecture Decision Records

### Why S3 Vector Store?
- **Simpler**: No cluster management
- **Faster to provision**: Minutes vs 15-20 min for OpenSearch
- **Cheaper**: No minimum compute costs
- **Good enough**: For most enterprise use cases with < 1M documents
- See: [Using S3 Vectors with Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-bedrock-kb.html)

### Why CloudFront + OAC?
- **Security**: No public S3 buckets
- **Performance**: Edge caching for static assets
- **Best practice**: AWS recommended pattern
- See: [Restrict access to an Amazon S3 origin](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)

### Why Titan Embeddings?
- **Cost**: ~10x cheaper than alternatives
- **Quality**: Excellent for English text
- **Integration**: Native Bedrock support, no external calls

### Why Lambda over ECS/Fargate?
- **Simplicity**: No container management
- **Cost**: Pay only for execution time
- **Scale**: Automatic scaling to thousands of concurrent requests
- **Cold starts**: Acceptable for most RAG use cases (< 1s)
- See: [Invoking Lambda with API Gateway](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)

---

## Next Steps

1. **Fork this repo** for your team
2. **Replace the sample docs** with your content
3. **Customize the system prompt** for your use case
4. **Deploy and test** with real queries
5. **Iterate on prompts** based on response quality
6. **Add authentication** if exposing externally
7. **Set up monitoring** for production use

---

## AWS Documentation References

### Core Services
- [Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [S3 Vectors with Bedrock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-bedrock-kb.html)
- [Knowledge Base Chunking Strategies](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html)
- [CloudFront Origin Access Control](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [Lambda with API Gateway](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)

### Additional Resources
- [Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [Custom Connectors Guide](./CUSTOM_CONNECTOR_GUIDE.md) — Build pipelines for your data sources
- [Data Preparation Guide](./DATA_PREPARATION_GUIDE.md) — Optimize content for retrieval
