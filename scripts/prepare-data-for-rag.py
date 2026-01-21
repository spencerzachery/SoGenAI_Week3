#!/usr/bin/env python3
"""
Data Preparation Script for RAG Knowledge Bases

This script demonstrates how to prepare various data sources for ingestion
into Amazon Bedrock Knowledge Bases. It includes examples for:
- Cleaning HTML/Wiki content
- Converting documents to optimal formats
- Adding metadata for filtering
- Pre-chunking special content types

Usage:
    python3 prepare-data-for-rag.py --source wiki --input ./raw-docs --output ./prepared-docs
    python3 prepare-data-for-rag.py --source cases --input ./support-cases.json --output ./prepared-docs
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

# Optional: Install with pip install beautifulsoup4 if processing HTML
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("Note: Install beautifulsoup4 for HTML processing: pip install beautifulsoup4")


def clean_text(text):
    """Clean and normalize text content."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Remove common wiki artifacts
    text = re.sub(r'\[edit\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[citation needed\]', '', text, flags=re.IGNORECASE)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n')
    
    return text.strip()


def html_to_markdown(html_content):
    """Convert HTML content to clean Markdown."""
    if not HAS_BS4:
        # Basic HTML tag removal if BeautifulSoup not available
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)
        return clean_text(text)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()
    
    # Convert to markdown-like format
    markdown_lines = []
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'code', 'blockquote']):
        if element.name.startswith('h'):
            level = int(element.name[1])
            markdown_lines.append(f"\n{'#' * level} {element.get_text(strip=True)}\n")
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text:
                markdown_lines.append(f"\n{text}\n")
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li', recursive=False):
                markdown_lines.append(f"- {li.get_text(strip=True)}")
        elif element.name == 'pre':
            markdown_lines.append(f"\n```\n{element.get_text()}\n```\n")
        elif element.name == 'code' and element.parent.name != 'pre':
            # Inline code - skip, handled in parent
            pass
        elif element.name == 'blockquote':
            text = element.get_text(strip=True)
            markdown_lines.append(f"\n> {text}\n")
    
    return clean_text('\n'.join(markdown_lines))


def process_wiki_document(file_path, output_dir):
    """Process a wiki/HTML document for RAG ingestion."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Determine if HTML or plain text
    if '<html' in content.lower() or '<body' in content.lower():
        processed_content = html_to_markdown(content)
    else:
        processed_content = clean_text(content)
    
    # Extract title from filename or content
    filename = Path(file_path).stem
    title = filename.replace('-', ' ').replace('_', ' ').title()
    
    # Try to extract title from content
    title_match = re.search(r'^#\s+(.+)$', processed_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    
    # Create metadata
    metadata = {
        'title': title,
        'source': 'wiki',
        'source_file': str(file_path),
        'processed_date': datetime.now().isoformat(),
        'document_type': 'documentation'
    }
    
    # Write processed content
    output_filename = f"{filename}.txt"
    output_path = Path(output_dir) / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)
    
    # Write metadata
    metadata_path = Path(output_dir) / f"{output_filename}.metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    return output_path, metadata


def process_support_case(case):
    """Format a support case for optimal RAG retrieval."""
    
    # Build structured document
    content = f"""# Support Case: {case.get('id', 'Unknown')}

## Issue Summary
{case.get('summary', 'No summary provided')}

## Service Affected
{case.get('service', 'Unknown')}

## Severity
{case.get('severity', 'Unknown')}

## Customer Environment
- Account Type: {case.get('account_type', 'Unknown')}
- Region: {case.get('region', 'Unknown')}
- Environment: {case.get('environment', 'Unknown')}

## Problem Description
{case.get('description', 'No description provided')}

## Symptoms Observed
{case.get('symptoms', 'No symptoms documented')}

## Root Cause Analysis
{case.get('root_cause', 'Root cause not determined')}

## Resolution Steps
{case.get('resolution', 'No resolution documented')}

## Time to Resolution
{case.get('time_to_resolution', 'Unknown')}

## Prevention Recommendations
{case.get('prevention', 'No prevention recommendations')}

## Lessons Learned
{case.get('lessons_learned', 'No lessons documented')}

## Related Documentation
{', '.join(case.get('related_docs', ['None']))}

## Tags
{', '.join(case.get('tags', ['untagged']))}
"""
    
    # Create metadata for filtering
    metadata = {
        'case_id': case.get('id'),
        'service': case.get('service', 'unknown'),
        'severity': case.get('severity', 'unknown'),
        'category': case.get('category', 'general'),
        'resolution_date': case.get('resolved_date', datetime.now().isoformat()),
        'tags': case.get('tags', []),
        'document_type': 'support_case'
    }
    
    return clean_text(content), metadata


def process_support_cases(input_file, output_dir):
    """Process a JSON file of support cases."""
    with open(input_file, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    # Handle both list and dict with 'cases' key
    if isinstance(cases, dict):
        cases = cases.get('cases', [])
    
    processed = []
    for case in cases:
        content, metadata = process_support_case(case)
        
        # Write content
        case_id = case.get('id', f"case-{len(processed)}")
        output_filename = f"case-{case_id}.txt"
        output_path = Path(output_dir) / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write metadata
        metadata_path = Path(output_dir) / f"{output_filename}.metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        processed.append({
            'case_id': case_id,
            'output_path': str(output_path),
            'metadata': metadata
        })
    
    return processed


def process_faq_document(file_path, output_dir):
    """Process FAQ content, keeping Q&A pairs together."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to identify Q&A patterns
    qa_patterns = [
        r'Q:\s*(.+?)\nA:\s*(.+?)(?=\nQ:|$)',  # Q: ... A: ...
        r'\*\*Q:\*\*\s*(.+?)\n\*\*A:\*\*\s*(.+?)(?=\n\*\*Q:|$)',  # **Q:** ... **A:** ...
        r'###\s*(.+?)\n(.+?)(?=\n###|$)',  # ### Question\nAnswer
    ]
    
    qa_pairs = []
    for pattern in qa_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            qa_pairs = matches
            break
    
    if qa_pairs:
        # Process as individual Q&A chunks
        processed_files = []
        for i, (question, answer) in enumerate(qa_pairs):
            chunk_content = f"""# FAQ: {question.strip()}

## Question
{question.strip()}

## Answer
{answer.strip()}
"""
            filename = f"faq-{i+1:03d}.txt"
            output_path = Path(output_dir) / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(clean_text(chunk_content))
            
            metadata = {
                'document_type': 'faq',
                'question': question.strip()[:100],
                'source_file': str(file_path)
            }
            
            metadata_path = Path(output_dir) / f"{filename}.metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            processed_files.append(output_path)
        
        return processed_files
    else:
        # Fall back to standard processing
        return [process_wiki_document(file_path, output_dir)[0]]


def create_sample_data(output_dir):
    """Create sample data files for testing."""
    
    # Sample support cases
    sample_cases = [
        {
            "id": "CASE-001",
            "summary": "EC2 instance unreachable after security group change",
            "service": "EC2",
            "severity": "High",
            "account_type": "Enterprise",
            "region": "us-east-1",
            "environment": "Production",
            "description": "Customer reported that their EC2 instance became unreachable immediately after modifying security group rules.",
            "symptoms": "SSH connection timeout, HTTP requests failing, instance status checks passing",
            "root_cause": "Security group rule was modified to restrict inbound traffic on port 22 and 443 to a specific IP range that didn't include the customer's current IP.",
            "resolution": "1. Identified the security group change in CloudTrail\n2. Updated security group to allow traffic from customer's IP range\n3. Verified connectivity restored",
            "time_to_resolution": "45 minutes",
            "prevention": "Implement security group change approval workflow. Use AWS Config rules to detect overly restrictive security groups.",
            "lessons_learned": "Always verify current IP before restricting security group rules. Consider using Session Manager for emergency access.",
            "related_docs": ["EC2 Security Groups", "CloudTrail Analysis"],
            "tags": ["ec2", "security-group", "connectivity", "production-impact"]
        },
        {
            "id": "CASE-002",
            "summary": "Lambda function throttling during peak traffic",
            "service": "Lambda",
            "severity": "Critical",
            "account_type": "Enterprise",
            "region": "us-west-2",
            "environment": "Production",
            "description": "Customer's Lambda functions started returning throttling errors during a marketing campaign launch.",
            "symptoms": "TooManyRequestsException errors, increased latency, failed API requests",
            "root_cause": "Account-level concurrent execution limit of 1000 was reached due to unexpected traffic spike.",
            "resolution": "1. Requested emergency limit increase via support case\n2. Implemented reserved concurrency for critical functions\n3. Added SQS queue to buffer requests",
            "time_to_resolution": "2 hours",
            "prevention": "Set up CloudWatch alarms for concurrent executions at 80% threshold. Pre-scale limits before known traffic events.",
            "lessons_learned": "Proactively review and increase limits before major events. Implement circuit breakers and queuing for traffic spikes.",
            "related_docs": ["Lambda Concurrency", "Service Quotas"],
            "tags": ["lambda", "throttling", "scaling", "production-impact"]
        }
    ]
    
    # Write sample cases
    cases_file = Path(output_dir) / "sample-cases.json"
    with open(cases_file, 'w', encoding='utf-8') as f:
        json.dump({"cases": sample_cases}, f, indent=2)
    
    # Sample wiki document
    sample_wiki = """
<html>
<head><title>EC2 Troubleshooting Guide</title></head>
<body>
<nav>Navigation menu - should be removed</nav>
<main>
<h1>EC2 Instance Troubleshooting Guide</h1>

<h2>Common Issues</h2>
<p>This guide covers the most common EC2 issues encountered by Enterprise Support customers.</p>

<h3>Instance Unreachable</h3>
<p>When an EC2 instance becomes unreachable, follow these steps:</p>
<ul>
<li>Check instance status checks in the EC2 console</li>
<li>Verify security group rules allow inbound traffic</li>
<li>Check Network ACL rules for the subnet</li>
<li>Verify the instance has a public IP or is accessible via VPN</li>
</ul>

<h3>High CPU Usage</h3>
<p>For instances with high CPU usage:</p>
<ul>
<li>Use CloudWatch metrics to identify the spike timing</li>
<li>Connect via Session Manager to run top/htop</li>
<li>Check for runaway processes or memory leaks</li>
<li>Consider upgrading to a larger instance type</li>
</ul>

<h2>Best Practices</h2>
<p>Follow these best practices to prevent common issues:</p>
<ul>
<li>Enable detailed monitoring for production instances</li>
<li>Set up CloudWatch alarms for CPU, memory, and disk</li>
<li>Use Auto Scaling for variable workloads</li>
<li>Implement proper tagging for cost allocation</li>
</ul>
</main>
<footer>Footer content - should be removed</footer>
</body>
</html>
"""
    
    wiki_file = Path(output_dir) / "sample-wiki.html"
    with open(wiki_file, 'w', encoding='utf-8') as f:
        f.write(sample_wiki)
    
    print(f"Created sample data in {output_dir}:")
    print(f"  - {cases_file}")
    print(f"  - {wiki_file}")
    
    return cases_file, wiki_file


def main():
    parser = argparse.ArgumentParser(
        description='Prepare data for RAG Knowledge Base ingestion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create sample data for testing
  python3 prepare-data-for-rag.py --create-samples --output ./sample-data

  # Process wiki/HTML documents
  python3 prepare-data-for-rag.py --source wiki --input ./raw-docs --output ./prepared-docs

  # Process support cases from JSON
  python3 prepare-data-for-rag.py --source cases --input ./cases.json --output ./prepared-docs

  # Process FAQ document
  python3 prepare-data-for-rag.py --source faq --input ./faq.md --output ./prepared-docs
        """
    )
    
    parser.add_argument('--source', choices=['wiki', 'cases', 'faq'],
                        help='Type of source data to process')
    parser.add_argument('--input', help='Input file or directory')
    parser.add_argument('--output', required=True, help='Output directory for processed files')
    parser.add_argument('--create-samples', action='store_true',
                        help='Create sample data files for testing')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.create_samples:
        create_sample_data(output_dir)
        return
    
    if not args.source or not args.input:
        parser.error("--source and --input are required unless using --create-samples")
    
    input_path = Path(args.input)
    
    if args.source == 'wiki':
        if input_path.is_dir():
            # Process all files in directory
            for file_path in input_path.glob('*'):
                if file_path.suffix in ['.html', '.htm', '.txt', '.md']:
                    output_path, metadata = process_wiki_document(file_path, output_dir)
                    print(f"Processed: {file_path} -> {output_path}")
        else:
            output_path, metadata = process_wiki_document(input_path, output_dir)
            print(f"Processed: {input_path} -> {output_path}")
    
    elif args.source == 'cases':
        processed = process_support_cases(input_path, output_dir)
        print(f"Processed {len(processed)} support cases")
        for item in processed:
            print(f"  - {item['case_id']}: {item['output_path']}")
    
    elif args.source == 'faq':
        processed = process_faq_document(input_path, output_dir)
        print(f"Processed FAQ into {len(processed)} chunks")
    
    print(f"\nOutput written to: {output_dir}")
    print("Next steps:")
    print("  1. Upload to S3: aws s3 sync {output_dir} s3://your-kb-bucket/")
    print("  2. Sync Knowledge Base in Bedrock console or via API")


if __name__ == '__main__':
    main()
