# Sample Queries for RAG Testing

Use these queries to test your RAG pipeline and compare responses with and without retrieval augmentation.

## Service Limits Queries

### Basic Queries
1. "How do I request an EC2 instance limit increase?"
2. "What is the default Lambda concurrent execution limit?"
3. "How many S3 buckets can I have per account?"
4. "What are the API Gateway throttling limits?"

### Complex Queries
5. "My Lambda function is being throttled. What should I check and how do I fix it?"
6. "I'm getting a LimitExceededException error. What does this mean and how do I resolve it?"
7. "What's the best way to monitor my service quotas proactively?"

### Expected RAG Improvement
- Without RAG: Generic information about AWS limits
- With RAG: Specific steps from our knowledge base, including console URLs and best practices

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
- With RAG: Specific templates, checklists, and procedures from our documentation

## Troubleshooting Queries

### Basic Queries
14. "What does AccessDenied error mean in AWS?"
15. "How do I analyze CloudWatch Logs?"
16. "What information should I include in a support case?"

### Complex Queries
17. "My EC2 instance is unreachable. Walk me through the troubleshooting steps."
18. "I'm getting 'Too many connections' error on RDS. How do I fix this?"
19. "How do I use X-Ray to debug a slow Lambda function?"

### Expected RAG Improvement
- Without RAG: Generic troubleshooting steps
- With RAG: Detailed step-by-step procedures with specific commands and checks

## Best Practices Queries

### Basic Queries
20. "What are the six pillars of the Well-Architected Framework?"
21. "How do I optimize costs for EC2 instances?"
22. "What are IAM best practices?"

### Complex Queries
23. "How should I design my VPC for security?"
24. "What's the difference between Reserved Instances and Savings Plans?"
25. "How do I implement encryption at rest for all my AWS resources?"

### Expected RAG Improvement
- Without RAG: High-level best practice summaries
- With RAG: Detailed implementation guidance with specific recommendations

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
| Sources | None cited | Can reference docs |

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
