# Sample Queries for RAG Testing

Use these queries to test your RAG pipeline and compare responses with and without retrieval augmentation.

## Service Limits Queries

### Basic Queries
1. "How do I request an EC2 instance limit increase?"
2. "What is the default Lambda concurrent execution limit?"
3. "What are the API Gateway throttling limits?"
4. "What's the difference between soft and hard limits?"

### Complex Queries
5. "My Lambda function is being throttled. What should I check and how do I fix it?"
6. "I'm getting a LimitExceededException error. What does this mean and how do I resolve it?"
7. "What's the best way to monitor my service quotas proactively?"

### Expected RAG Improvement
- Without RAG: Generic information about AWS limits
- With RAG: Specific steps from our knowledge base, including console URLs, TAM guidance, and escalation procedures

## Outage and Incident Queries

### Basic Queries
8. "How do I set up Route 53 health checks for failover?"
9. "Where can I check AWS service health status?"
10. "What should I include in an incident communication to customers?"

### Complex Queries
11. "Our production system is down. What's the escalation process for Enterprise Support?"
12. "How do I conduct a post-incident review after an outage?"
13. "What's the difference between Active-Active and Active-Passive failover?"

### Expected RAG Improvement
- Without RAG: General incident response advice
- With RAG: Specific templates, checklists, severity levels, and communication templates from our documentation

## Troubleshooting Queries

### EC2 Troubleshooting
14. "My EC2 instance is unreachable. What should I check?"
15. "I'm getting 'Permission denied (publickey)' when trying to SSH. How do I fix this?"
16. "What's the difference between system status checks and instance status checks?"
17. "How do I troubleshoot high CPU utilization on my EC2 instance?"

### Lambda Troubleshooting
18. "My Lambda function is timing out. What are the common causes?"
19. "How do I fix 'Runtime exited with error: signal: killed' in Lambda?"
20. "My Lambda in VPC can't access the internet. What's wrong?"
21. "How do I reduce Lambda cold start latency?"

### Database and Storage
22. "I'm getting 'Too many connections' error on RDS. How do I fix this?"
23. "My DynamoDB table is being throttled during a product launch. What should I do?"
24. "S3 is returning SlowDown errors. What's happening?"

### Expected RAG Improvement
- Without RAG: Generic troubleshooting steps
- With RAG: Detailed step-by-step procedures with specific commands, code examples, and resolution patterns from real cases

## Resolved Case Queries

These queries should retrieve information from our resolved support cases:

25. "How did we resolve the Lambda timeout issue with RDS connections?"
26. "What happened when a customer locked themselves out of an S3 bucket?"
27. "How do we handle DynamoDB hot partition issues?"
28. "What's the resolution for API Gateway 502 errors with large payloads?"

### Expected RAG Improvement
- Without RAG: Generic advice
- With RAG: Specific case resolutions with root cause analysis, resolution steps, and prevention recommendations

## Best Practices Queries

### Basic Queries
29. "What are IAM best practices for security?"
30. "How should I structure my CloudWatch logs?"
31. "What information should I include in a support case?"

### Complex Queries
32. "How do I implement connection pooling for Lambda with RDS?"
33. "What's the best way to handle Lambda environment variables for large configs?"
34. "How should I design partition keys to avoid DynamoDB hot partitions?"

### Expected RAG Improvement
- Without RAG: High-level best practice summaries
- With RAG: Detailed implementation guidance with code examples and specific recommendations

## Testing Script Usage

```bash
# Test without RAG
python3 scripts/query-knowledge-base.py --no-rag "How do I request an EC2 limit increase?"

# Test with RAG
python3 scripts/query-knowledge-base.py "How do I request an EC2 limit increase?"

# Compare side-by-side
python3 scripts/compare-responses.py "How do I request an EC2 limit increase?"
```

## Evaluation Criteria

When comparing RAG vs non-RAG responses, look for:

| Criteria | Without RAG | With RAG |
|----------|-------------|----------|
| Specificity | Generic | Detailed, specific |
| Accuracy | May hallucinate | Grounded in docs |
| Actionability | Vague steps | Clear procedures |
| Relevance | Broad coverage | Focused on query |
| Sources | None cited | References docs |
| Code Examples | Generic | From real cases |

## Advanced Testing

### Multi-Turn Conversations
Test context retention across multiple queries:
1. "What are Lambda limits?"
2. "How do I increase them?"
3. "What if I need it urgently?"

### Edge Cases
- Queries outside knowledge base scope
- Ambiguous queries
- Queries requiring multiple document sources
- Queries with typos or informal language
