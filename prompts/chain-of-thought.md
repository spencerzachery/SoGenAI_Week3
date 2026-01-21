# Chain-of-Thought Prompting Examples

Chain-of-thought (CoT) prompting guides the model to reason step-by-step.

## Basic CoT

```
A customer reports their Lambda function is timing out.
Let's troubleshoot step by step:

1. First, what is the current timeout setting?
2. What does the function do?
3. Are there external dependencies?
4. What do CloudWatch logs show?

Based on this analysis, provide recommendations.
```

## CoT for Complex Troubleshooting

```
Problem: Customer's application is experiencing intermittent 503 errors.

Let's analyze this systematically:

Step 1: Identify the error source
- Is it from the load balancer, application, or backend?
- What does the error message say?

Step 2: Check recent changes
- Were there any deployments?
- Configuration changes?
- Traffic pattern changes?

Step 3: Analyze metrics
- CPU/Memory utilization?
- Request latency?
- Error rates over time?

Step 4: Review logs
- Application logs
- Load balancer access logs
- CloudWatch metrics

Step 5: Formulate hypothesis
Based on the above, what's the likely cause?

Step 6: Recommend solution
What actions should the customer take?

Now provide your analysis:
```

## CoT for Architecture Decisions

```
A customer wants to migrate their monolithic application to AWS.

Let's think through this step by step:

1. Current State Analysis
   - What's the current architecture?
   - What are the pain points?
   - What are the requirements?

2. Target Architecture Options
   - Option A: Lift and shift to EC2
   - Option B: Containerize with ECS/EKS
   - Option C: Refactor to serverless

3. Evaluation Criteria
   - Cost implications
   - Operational complexity
   - Time to migrate
   - Future scalability

4. Recommendation
   Based on the analysis, which option is best and why?

Provide your recommendation:
```

## When to Use CoT

- Complex problem-solving
- Multi-step reasoning required
- Debugging and troubleshooting
- Architecture decisions
- When you need to show your work
