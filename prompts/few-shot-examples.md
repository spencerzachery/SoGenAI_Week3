# Few-Shot Prompting Examples

Few-shot prompting provides examples to guide the model's response format and style.

## Basic Few-Shot (2 examples)

```
Here are examples of good AWS support responses:

Q: How do I reset my password?
A: To reset your AWS console password:
1. Go to the AWS sign-in page
2. Click "Forgot password?"
3. Enter your email address
4. Follow the reset link in your email

Q: How do I check my EC2 instance status?
A: To check your EC2 instance status:
1. Open the EC2 console
2. Click "Instances" in the left menu
3. Find your instance and check the "Status check" column
4. Green checkmarks indicate healthy status

Now answer this question in the same format:

Q: How do I increase my Lambda memory?
A:
```

## Few-Shot for Troubleshooting

```
Examples of troubleshooting responses:

Issue: S3 bucket access denied
Analysis: This usually indicates IAM permission issues.
Steps:
1. Check the bucket policy
2. Verify IAM user permissions
3. Check for explicit deny statements
Resolution: Update IAM policy to include s3:GetObject

Issue: RDS connection timeout
Analysis: Network configuration is likely the cause.
Steps:
1. Verify security group allows inbound traffic
2. Check if RDS is in correct VPC
3. Confirm endpoint and port are correct
Resolution: Update security group rules

Now troubleshoot this issue:

Issue: Lambda function returning 502 error
Analysis:
```

## When to Use Few-Shot

- Specific formatting requirements
- Domain-specific terminology
- Consistent response style needed
- Complex tasks that benefit from examples
