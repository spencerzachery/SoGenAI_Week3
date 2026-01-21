#!/usr/bin/env python3
"""
Query Knowledge Base - RAG Pipeline for Enterprise Support
Supports both RAG and non-RAG queries with various prompt styles.
"""

import argparse
import boto3
import json
import os
import sys

# Initialize clients
bedrock_agent = boto3.client('bedrock-agent-runtime')
bedrock = boto3.client('bedrock-runtime')

# Configuration
DEFAULT_MODEL_ID = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Prompt templates
PROMPT_TEMPLATES = {
    'default': """You are a helpful AWS support specialist. Answer the following question clearly and accurately.

Question: {query}

Answer:""",

    'few-shot': """You are an AWS Enterprise Support specialist. Here are examples of good support responses:

Example 1:
Q: How do I reset my AWS console password?
A: To reset your AWS console password:
1. Go to the AWS sign-in page
2. Click "Forgot password?"
3. Enter your email address
4. Check your email for the reset link
5. Follow the link to create a new password

Example 2:
Q: What should I do if my EC2 instance won't start?
A: If your EC2 instance won't start, follow these steps:
1. Check the instance state in the EC2 console
2. Review the system log for errors
3. Verify your instance type is available in the AZ
4. Check if you've hit any service limits
5. Try stopping and starting (not rebooting) the instance

Now answer this question in the same helpful, step-by-step format:

Q: {query}
A:""",

    'cot': """You are an AWS Enterprise Support specialist helping troubleshoot an issue.

Let's think through this step by step:

Question: {query}

Step 1: First, let's understand what the customer is asking...
Step 2: What are the possible causes?
Step 3: What information do we need to diagnose this?
Step 4: What are the recommended actions?

Analysis and Recommendation:""",

    'role-tam': """You are a Technical Account Manager (TAM) at AWS Enterprise Support with 10 years of experience. You specialize in helping enterprise customers optimize their AWS infrastructure and resolve complex issues.

When responding:
- Be professional but approachable
- Provide specific, actionable guidance
- Reference AWS best practices and Well-Architected Framework
- Suggest proactive measures to prevent future issues
- Offer to schedule a follow-up if needed

Customer Question: {query}

TAM Response:""",

    'role-sa': """You are a Senior AWS Solutions Architect helping a customer design and troubleshoot their AWS architecture.

When responding:
- Focus on architectural best practices
- Consider scalability, reliability, and cost
- Reference relevant AWS services and features
- Provide diagrams or examples when helpful
- Suggest alternatives if applicable

Question: {query}

Solutions Architect Response:"""
}


def query_with_rag(query: str, kb_id: str, model_id: str = DEFAULT_MODEL_ID) -> dict:
    """Query using RAG with Bedrock Knowledge Base."""
    try:
        response = bedrock_agent.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': f'arn:aws:bedrock:{REGION}::foundation-model/{model_id}'
                }
            }
        )
        
        return {
            'response': response['output']['text'],
            'citations': response.get('citations', []),
            'mode': 'RAG'
        }
    except Exception as e:
        return {
            'error': str(e),
            'mode': 'RAG'
        }


def query_without_rag(query: str, prompt_style: str = 'default', 
                      model_id: str = DEFAULT_MODEL_ID) -> dict:
    """Query directly without RAG."""
    try:
        # Get the appropriate prompt template
        template = PROMPT_TEMPLATES.get(prompt_style, PROMPT_TEMPLATES['default'])
        prompt = template.format(query=query)
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1024,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            })
        )
        
        result = json.loads(response['body'].read())
        
        return {
            'response': result['content'][0]['text'],
            'mode': 'Direct',
            'prompt_style': prompt_style
        }
    except Exception as e:
        return {
            'error': str(e),
            'mode': 'Direct'
        }


def print_response(result: dict):
    """Pretty print the response."""
    print("\n" + "=" * 60)
    print(f"Mode: {result.get('mode', 'Unknown')}")
    if 'prompt_style' in result:
        print(f"Prompt Style: {result['prompt_style']}")
    print("=" * 60)
    
    if 'error' in result:
        print(f"\n❌ Error: {result['error']}")
    else:
        print(f"\n{result['response']}")
        
        if result.get('citations'):
            print("\n📚 Citations:")
            for i, citation in enumerate(result['citations'], 1):
                if 'retrievedReferences' in citation:
                    for ref in citation['retrievedReferences']:
                        location = ref.get('location', {})
                        s3_location = location.get('s3Location', {})
                        uri = s3_location.get('uri', 'Unknown source')
                        print(f"  [{i}] {uri}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Query the RAG Knowledge Base for Enterprise Support'
    )
    parser.add_argument('query', help='The question to ask')
    parser.add_argument('--no-rag', action='store_true', 
                        help='Query without RAG (direct model query)')
    parser.add_argument('--kb-id', default=os.environ.get('KB_ID'),
                        help='Knowledge Base ID (or set KB_ID env var)')
    parser.add_argument('--model-id', default=DEFAULT_MODEL_ID,
                        help='Bedrock model ID')
    parser.add_argument('--prompt-style', 
                        choices=['default', 'few-shot', 'cot'],
                        default='default',
                        help='Prompt engineering style (for non-RAG queries)')
    parser.add_argument('--role',
                        choices=['tam', 'sa'],
                        help='Role-based prompting (tam=TAM, sa=Solutions Architect)')
    
    args = parser.parse_args()
    
    # Determine prompt style
    prompt_style = args.prompt_style
    if args.role:
        prompt_style = f'role-{args.role}'
    
    if args.no_rag:
        print(f"\n🔍 Querying without RAG (prompt style: {prompt_style})...")
        result = query_without_rag(args.query, prompt_style, args.model_id)
    else:
        if not args.kb_id:
            print("❌ Error: Knowledge Base ID required for RAG queries.")
            print("   Set KB_ID environment variable or use --kb-id flag.")
            print("   Or use --no-rag for direct model queries.")
            sys.exit(1)
        
        print(f"\n🔍 Querying with RAG (KB: {args.kb_id})...")
        result = query_with_rag(args.query, args.kb_id, args.model_id)
    
    print_response(result)


if __name__ == '__main__':
    main()
