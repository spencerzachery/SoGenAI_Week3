#!/usr/bin/env python3
"""
Compare RAG vs Non-RAG Responses
Side-by-side comparison of responses with and without retrieval augmentation.
"""

import argparse
import boto3
import json
import os
import sys
import textwrap

# Initialize clients
bedrock_agent = boto3.client('bedrock-agent-runtime')
bedrock = boto3.client('bedrock-runtime')

# Configuration
DEFAULT_MODEL_ID = 'anthropic.claude-sonnet-4-5-20250929-v1:0'
REGION = os.environ.get('AWS_REGION', 'us-east-1')


def query_with_rag(query: str, kb_id: str, model_id: str = DEFAULT_MODEL_ID) -> str:
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
        return response['output']['text']
    except Exception as e:
        return f"Error: {str(e)}"


def query_without_rag(query: str, model_id: str = DEFAULT_MODEL_ID) -> str:
    """Query directly without RAG."""
    try:
        prompt = f"""You are a helpful AWS support specialist. Answer the following question clearly and accurately.

Question: {query}

Answer:"""
        
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
        return result['content'][0]['text']
    except Exception as e:
        return f"Error: {str(e)}"


def wrap_text(text: str, width: int = 45) -> list:
    """Wrap text to specified width."""
    lines = []
    for paragraph in text.split('\n'):
        if paragraph.strip():
            wrapped = textwrap.wrap(paragraph, width=width)
            lines.extend(wrapped)
        else:
            lines.append('')
    return lines


def print_side_by_side(left_title: str, left_text: str, 
                       right_title: str, right_text: str):
    """Print two texts side by side."""
    width = 45
    separator = " │ "
    
    left_lines = wrap_text(left_text, width)
    right_lines = wrap_text(right_text, width)
    
    # Pad to equal length
    max_lines = max(len(left_lines), len(right_lines))
    left_lines.extend([''] * (max_lines - len(left_lines)))
    right_lines.extend([''] * (max_lines - len(right_lines)))
    
    # Print header
    print("\n" + "=" * (width * 2 + 3))
    print(f"{left_title:^{width}}{separator}{right_title:^{width}}")
    print("=" * (width * 2 + 3))
    
    # Print content
    for left, right in zip(left_lines, right_lines):
        print(f"{left:<{width}}{separator}{right:<{width}}")
    
    print("=" * (width * 2 + 3))


def analyze_differences(without_rag: str, with_rag: str) -> dict:
    """Analyze key differences between responses."""
    analysis = {
        'without_rag_length': len(without_rag),
        'with_rag_length': len(with_rag),
        'length_difference': len(with_rag) - len(without_rag),
    }
    
    # Check for specific indicators
    specificity_indicators = [
        'console.aws.amazon.com',
        'step 1', 'step 2', 'step 3',
        'first,', 'second,', 'third,',
        'specifically',
        'in your case',
    ]
    
    analysis['without_rag_specificity'] = sum(
        1 for ind in specificity_indicators 
        if ind.lower() in without_rag.lower()
    )
    analysis['with_rag_specificity'] = sum(
        1 for ind in specificity_indicators 
        if ind.lower() in with_rag.lower()
    )
    
    return analysis


def print_analysis(analysis: dict):
    """Print analysis of differences."""
    print("\n📊 Analysis:")
    print("-" * 40)
    print(f"Without RAG: {analysis['without_rag_length']} characters")
    print(f"With RAG: {analysis['with_rag_length']} characters")
    print(f"Difference: {analysis['length_difference']:+d} characters")
    print(f"\nSpecificity Score (higher = more specific):")
    print(f"  Without RAG: {analysis['without_rag_specificity']}")
    print(f"  With RAG: {analysis['with_rag_specificity']}")
    
    if analysis['with_rag_specificity'] > analysis['without_rag_specificity']:
        print("\n✅ RAG response appears more specific and actionable")
    elif analysis['with_rag_specificity'] < analysis['without_rag_specificity']:
        print("\n⚠️ Non-RAG response appears more specific (unusual)")
    else:
        print("\n➡️ Similar specificity levels")


def main():
    parser = argparse.ArgumentParser(
        description='Compare RAG vs Non-RAG responses side by side'
    )
    parser.add_argument('query', help='The question to ask')
    parser.add_argument('--kb-id', default=os.environ.get('KB_ID'),
                        help='Knowledge Base ID (or set KB_ID env var)')
    parser.add_argument('--model-id', default=DEFAULT_MODEL_ID,
                        help='Bedrock model ID')
    parser.add_argument('--no-analysis', action='store_true',
                        help='Skip the analysis section')
    
    args = parser.parse_args()
    
    if not args.kb_id:
        print("❌ Error: Knowledge Base ID required.")
        print("   Set KB_ID environment variable or use --kb-id flag.")
        sys.exit(1)
    
    print(f"\n🔍 Query: {args.query}")
    print("\nFetching responses...")
    
    # Get both responses
    print("  → Querying without RAG...")
    without_rag = query_without_rag(args.query, args.model_id)
    
    print("  → Querying with RAG...")
    with_rag = query_with_rag(args.query, args.kb_id, args.model_id)
    
    # Print side by side
    print_side_by_side(
        "❌ WITHOUT RAG", without_rag,
        "✅ WITH RAG", with_rag
    )
    
    # Print analysis
    if not args.no_analysis:
        analysis = analyze_differences(without_rag, with_rag)
        print_analysis(analysis)


if __name__ == '__main__':
    main()
