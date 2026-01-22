gre# Data Preparation Guide for Enterprise RAG

## Overview

This guide covers best practices for preparing enterprise data for Retrieval-Augmented Generation (RAG) systems using Amazon Bedrock Knowledge Bases. Learn how to transform internal wikis, support documentation, and case data into high-quality knowledge bases.

## Table of Contents

1. [Data Quality Principles](#data-quality-principles)
2. [Document Formats and Preprocessing](#document-formats-and-preprocessing)
3. [Chunking Strategies](#chunking-strategies)
4. [Metadata and Filtering](#metadata-and-filtering)
5. [Data Connectors](#data-connectors)
6. [Sample Data Pipelines](#sample-data-pipelines)
7. [Quality Assurance](#quality-assurance)

---

## Data Quality Principles

### The RAG Quality Formula

**RAG Output Quality = Retrieval Quality × Generation Quality**

Poor input data leads to poor retrieval, which leads to poor answers. Focus on:

1. **Relevance**: Only include content that answers real questions
2. **Accuracy**: Ensure information is current and correct
3. **Completeness**: Include enough context for standalone understanding
4. **Structure**: Organize content for optimal chunking

### Common Data Quality Issues

| Issue | Impact on RAG | Solution |
|-------|---------------|----------|
| Outdated content | Wrong answers | Regular sync, version dates |
| Duplicate content | Wasted tokens, confusion | Deduplication pipeline |
| Poor formatting | Bad chunking | Preprocessing cleanup |
| Missing context | Incomplete answers | Add headers, metadata |
| Jargon without definition | Misunderstanding | Glossary, expanded terms |

---

## Document Formats and Preprocessing

### Supported Formats in Bedrock KB

| Format | Extension | Best For | Notes |
|--------|-----------|----------|-------|
| Plain Text | .txt | Clean, structured docs | Best chunking results |
| Markdown | .md | Technical docs, wikis | Headers help chunking |
| PDF | .pdf | Official documents | OCR quality varies |
| HTML | .html | Web content | Strip navigation/ads |
| Word | .docx | Business documents | Tables may need cleanup |
| CSV | .csv | Structured data | Good for FAQs |

### Preprocessing Best Practices

#### 1. Clean HTML from Wiki Exports

```python
import re
from bs4 import BeautifulSoup

def clean_wiki_html(html_content):
    """Clean wiki HTML for RAG ingestion."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove navigation, sidebars, footers
    for element in soup.find_all(['nav', 'sidebar', 'footer', 'header']):
        element.decompose()
    
    # Remove scripts and styles
    for element in soup.find_all(['script', 'style']):
        element.decompose()
    
    # Extract main content
    main_content = soup.find('main') or soup.find('article') or soup.find('body')
    
    # Convert to clean text with structure preserved
    text = main_content.get_text(separator='\n', strip=True)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text
```

#### 2. Convert Confluence/Wiki to Markdown

```python
def confluence_to_markdown(confluence_page):
    """Convert Confluence page to clean Markdown."""
    
    # Extract title
    title = confluence_page.get('title', 'Untitled')
    
    # Get body content
    body = confluence_page.get('body', {}).get('storage', {}).get('value', '')
    
    # Convert HTML to Markdown
    soup = BeautifulSoup(body, 'html.parser')
    
    markdown_lines = [f"# {title}\n"]
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'pre']):
        if element.name.startswith('h'):
            level = int(element.name[1])
            markdown_lines.append(f"{'#' * level} {element.get_text(strip=True)}\n")
        elif element.name == 'p':
            markdown_lines.append(f"{element.get_text(strip=True)}\n")
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                markdown_lines.append(f"- {li.get_text(strip=True)}")
        elif element.name == 'pre':
            markdown_lines.append(f"```\n{element.get_text()}\n```\n")
    
    return '\n'.join(markdown_lines)
```

#### 3. Structure Documents for Optimal Chunking

**Before (Poor Structure):**
```
EC2 instances can be launched in multiple ways. You can use the console or CLI. 
The console is easier for beginners. The CLI is better for automation. Instance 
types include t2, t3, m5, c5, and more. T2 instances are burstable. M5 instances 
are general purpose. Pricing varies by region and instance type.
```

**After (Good Structure):**
```markdown
# EC2 Instance Launch Methods

## AWS Console
The console provides a visual interface ideal for beginners and one-off launches.

## AWS CLI
The CLI enables automation and scripting for repeatable deployments.

# EC2 Instance Types

## Burstable Instances (T2, T3)
- Best for: Variable workloads with occasional spikes
- CPU credits accumulate during low usage

## General Purpose (M5, M6i)
- Best for: Balanced compute, memory, and networking
- Common for web servers and small databases

# EC2 Pricing
Pricing varies by:
- Region
- Instance type
- Purchase option (On-Demand, Reserved, Spot)
```

---

## Chunking Strategies

### Understanding Chunk Size Impact

| Chunk Size | Retrieval Precision | Context Completeness | Token Cost |
|------------|---------------------|----------------------|------------|
| Small (100-200 tokens) | High | Low | Low |
| Medium (300-500 tokens) | Balanced | Balanced | Medium |
| Large (500-1000 tokens) | Low | High | High |

### Recommended Chunking Configurations

#### For Technical Documentation
```python
chunking_config = {
    "chunkingStrategy": "FIXED_SIZE",
    "fixedSizeChunkingConfiguration": {
        "maxTokens": 300,
        "overlapPercentage": 15
    }
}
```

#### For FAQ/Q&A Content
```python
# Use semantic chunking to keep Q&A pairs together
chunking_config = {
    "chunkingStrategy": "SEMANTIC",
    "semanticChunkingConfiguration": {
        "maxTokens": 500,
        "bufferSize": 0,
        "breakpointPercentileThreshold": 95
    }
}
```

#### For Long-Form Documents
```python
# Hierarchical chunking for documents with clear structure
chunking_config = {
    "chunkingStrategy": "HIERARCHICAL",
    "hierarchicalChunkingConfiguration": {
        "levelConfigurations": [
            {"maxTokens": 1500},  # Parent chunks
            {"maxTokens": 300}    # Child chunks
        ],
        "overlapTokens": 60
    }
}
```

### Pre-Chunking for Special Content

Sometimes it's better to pre-chunk content before ingestion:

```python
def pre_chunk_support_cases(cases):
    """Pre-chunk support cases for optimal retrieval."""
    chunks = []
    
    for case in cases:
        # Each case becomes its own chunk with full context
        chunk = f"""
# Support Case: {case['case_id']}

## Issue Summary
{case['summary']}

## Customer Environment
- Service: {case['service']}
- Region: {case['region']}
- Account Type: {case['account_type']}

## Problem Description
{case['description']}

## Resolution
{case['resolution']}

## Root Cause
{case['root_cause']}

## Prevention
{case['prevention_steps']}

## Related Documentation
{', '.join(case.get('related_docs', []))}
"""
        chunks.append({
            'content': chunk,
            'metadata': {
                'case_id': case['case_id'],
                'service': case['service'],
                'severity': case['severity'],
                'date': case['created_date']
            }
        })
    
    return chunks
```

---

## Metadata and Filtering

### Why Metadata Matters

Metadata enables:
- **Filtered retrieval**: Only search relevant document subsets
- **Source attribution**: Know where answers came from
- **Freshness control**: Prefer recent content
- **Access control**: Respect document permissions

### Recommended Metadata Schema

```json
{
  "document_id": "DOC-12345",
  "title": "EC2 Instance Troubleshooting Guide",
  "source": "internal-wiki",
  "category": "troubleshooting",
  "service": "ec2",
  "last_updated": "2024-01-15",
  "author": "support-team",
  "audience": ["tam", "support-engineer"],
  "confidence": "verified",
  "version": "2.1"
}
```

### Implementing Metadata Filters

```python
# Query with metadata filtering
response = bedrock_agent.retrieve(
    knowledgeBaseId=kb_id,
    retrievalQuery={'text': query},
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 5,
            'filter': {
                'andAll': [
                    {'equals': {'key': 'service', 'value': 'ec2'}},
                    {'greaterThan': {'key': 'last_updated', 'value': '2023-01-01'}}
                ]
            }
        }
    }
)
```

### Adding Metadata to S3 Objects

```python
import boto3
import json

s3 = boto3.client('s3')

def upload_with_metadata(bucket, key, content, metadata):
    """Upload document with metadata for Bedrock KB."""
    
    # Create metadata file (Bedrock KB reads .metadata.json files)
    metadata_key = f"{key}.metadata.json"
    
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=content.encode('utf-8'),
        ContentType='text/plain'
    )
    
    s3.put_object(
        Bucket=bucket,
        Key=metadata_key,
        Body=json.dumps(metadata).encode('utf-8'),
        ContentType='application/json'
    )
```

---

## Data Connectors

### Bedrock KB Native Connectors

Amazon Bedrock Knowledge Bases supports these data sources:

| Source | Use Case | Setup Complexity |
|--------|----------|------------------|
| Amazon S3 | Files, exports | Low |
| Web Crawler | Public documentation | Medium |
| Confluence | Internal wikis | Medium |
| Salesforce | CRM data | Medium |
| SharePoint | Enterprise docs | Medium |

### S3 Data Source (Most Common)

```python
import boto3

bedrock_agent = boto3.client('bedrock-agent')

# Create S3 data source
response = bedrock_agent.create_data_source(
    knowledgeBaseId='YOUR_KB_ID',
    name='support-documentation',
    dataSourceConfiguration={
        'type': 'S3',
        's3Configuration': {
            'bucketArn': 'arn:aws:s3:::your-kb-bucket',
            'inclusionPrefixes': ['support-cases/', 'runbooks/']
        }
    },
    vectorIngestionConfiguration={
        'chunkingConfiguration': {
            'chunkingStrategy': 'FIXED_SIZE',
            'fixedSizeChunkingConfiguration': {
                'maxTokens': 300,
                'overlapPercentage': 10
            }
        }
    }
)
```

### Web Crawler for AWS Documentation

```python
# Create web crawler data source for AWS docs
response = bedrock_agent.create_data_source(
    knowledgeBaseId='YOUR_KB_ID',
    name='aws-documentation',
    dataSourceConfiguration={
        'type': 'WEB',
        'webConfiguration': {
            'sourceConfiguration': {
                'urlConfiguration': {
                    'seedUrls': [
                        {'url': 'https://docs.aws.amazon.com/ec2/'},
                        {'url': 'https://docs.aws.amazon.com/lambda/'}
                    ]
                }
            },
            'crawlerConfiguration': {
                'crawlerLimits': {
                    'rateLimit': 10  # Pages per second
                },
                'inclusionFilters': ['.*\\.html$'],
                'exclusionFilters': ['.*\\?.*']  # Exclude query strings
            }
        }
    }
)
```

### Confluence Connector

```python
# Create Confluence data source
response = bedrock_agent.create_data_source(
    knowledgeBaseId='YOUR_KB_ID',
    name='internal-wiki',
    dataSourceConfiguration={
        'type': 'CONFLUENCE',
        'confluenceConfiguration': {
            'sourceConfiguration': {
                'hostUrl': 'https://your-company.atlassian.net/wiki',
                'hostType': 'SAAS',
                'authType': 'BASIC',
                'credentialsSecretArn': 'arn:aws:secretsmanager:...'
            },
            'crawlerConfiguration': {
                'filterConfiguration': {
                    'type': 'PATTERN',
                    'patternObjectFilter': {
                        'filters': [
                            {
                                'objectType': 'Space',
                                'inclusionFilters': ['SUPPORT', 'RUNBOOKS']
                            }
                        ]
                    }
                }
            }
        }
    }
)
```

### Custom Connector Pattern (Support Case System)

For systems without native connectors, build a sync pipeline:

```python
import boto3
from datetime import datetime, timedelta

class SupportCaseConnector:
    """Sync support cases to S3 for Bedrock KB ingestion."""
    
    def __init__(self, support_api_client, s3_bucket, kb_id):
        self.support_api = support_api_client
        self.s3 = boto3.client('s3')
        self.bedrock = boto3.client('bedrock-agent')
        self.bucket = s3_bucket
        self.kb_id = kb_id
    
    def sync_cases(self, days_back=30):
        """Sync recent resolved cases to knowledge base."""
        
        # Fetch resolved cases from support system
        cases = self.support_api.get_resolved_cases(
            since=datetime.now() - timedelta(days=days_back)
        )
        
        synced_count = 0
        for case in cases:
            # Skip cases without resolution
            if not case.get('resolution'):
                continue
            
            # Format case for RAG
            content = self._format_case(case)
            metadata = self._extract_metadata(case)
            
            # Upload to S3
            key = f"support-cases/{case['id']}.txt"
            self._upload_with_metadata(key, content, metadata)
            synced_count += 1
        
        # Trigger KB sync
        self._trigger_sync()
        
        return synced_count
    
    def _format_case(self, case):
        """Format support case for optimal RAG retrieval."""
        return f"""
# Support Case Resolution: {case['id']}

## Issue Summary
{case['summary']}

## Service Affected
{case['service']}

## Severity
{case['severity']}

## Customer Impact
{case['impact_description']}

## Symptoms
{case['symptoms']}

## Root Cause Analysis
{case['root_cause']}

## Resolution Steps
{case['resolution']}

## Time to Resolution
{case['time_to_resolution']}

## Prevention Recommendations
{case.get('prevention', 'N/A')}

## Related Cases
{', '.join(case.get('related_cases', []))}

## Tags
{', '.join(case.get('tags', []))}
"""
    
    def _extract_metadata(self, case):
        """Extract metadata for filtering."""
        return {
            'case_id': case['id'],
            'service': case['service'],
            'severity': case['severity'],
            'resolution_date': case['resolved_date'],
            'category': case.get('category', 'general'),
            'tags': case.get('tags', [])
        }
    
    def _upload_with_metadata(self, key, content, metadata):
        """Upload content and metadata to S3."""
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content.encode('utf-8')
        )
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"{key}.metadata.json",
            Body=json.dumps(metadata).encode('utf-8')
        )
    
    def _trigger_sync(self):
        """Trigger knowledge base sync."""
        data_sources = self.bedrock.list_data_sources(
            knowledgeBaseId=self.kb_id
        )
        
        for ds in data_sources['dataSourceSummaries']:
            self.bedrock.start_ingestion_job(
                knowledgeBaseId=self.kb_id,
                dataSourceId=ds['dataSourceId']
            )
```

---

## Sample Data Pipelines

### Pipeline 1: Wiki to Knowledge Base

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Confluence  │ →   │ Export API  │ →   │ Clean &     │ →   │ S3 Bucket   │
│ Wiki        │     │ (Daily)     │     │ Transform   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ RAG Query   │ ←   │ Bedrock KB  │ ←   │ Sync Job    │ ←   │ EventBridge │
│ Interface   │     │             │     │ (Scheduled) │     │ (Trigger)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Pipeline 2: Support Case Ingestion

```python
# Lambda function for automated case ingestion
import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    """Process new resolved support cases for KB ingestion."""
    
    s3 = boto3.client('s3')
    bedrock = boto3.client('bedrock-agent')
    
    KB_BUCKET = 'your-kb-bucket'
    KB_ID = 'your-kb-id'
    DS_ID = 'your-datasource-id'
    
    # Process each case from the event
    for record in event['Records']:
        case = json.loads(record['body'])
        
        # Only process resolved cases
        if case['status'] != 'resolved':
            continue
        
        # Format and upload
        content = format_case_for_rag(case)
        key = f"support-cases/{case['id']}.txt"
        
        s3.put_object(
            Bucket=KB_BUCKET,
            Key=key,
            Body=content.encode('utf-8')
        )
    
    # Trigger incremental sync
    bedrock.start_ingestion_job(
        knowledgeBaseId=KB_ID,
        dataSourceId=DS_ID
    )
    
    return {'statusCode': 200}
```

### Pipeline 3: Multi-Source Aggregation

```
┌─────────────┐
│ AWS Docs    │ ──┐
│ (Crawler)   │   │
└─────────────┘   │
                  │     ┌─────────────┐     ┌─────────────┐
┌─────────────┐   ├──→  │ Bedrock KB  │ →   │ RAG         │
│ Internal    │   │     │ (Multiple   │     │ Playground  │
│ Wiki        │ ──┤     │ Data Sources│     │             │
└─────────────┘   │     └─────────────┘     └─────────────┘
                  │
┌─────────────┐   │
│ Support     │ ──┘
│ Cases (S3)  │
└─────────────┘
```

---

## Quality Assurance

### Testing Your Knowledge Base

#### 1. Retrieval Quality Test

```python
def test_retrieval_quality(kb_id, test_queries):
    """Test retrieval quality with known queries."""
    
    bedrock = boto3.client('bedrock-agent-runtime')
    results = []
    
    for query in test_queries:
        response = bedrock.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={'text': query['question']},
            retrievalConfiguration={
                'vectorSearchConfiguration': {'numberOfResults': 5}
            }
        )
        
        # Check if expected document was retrieved
        retrieved_sources = [
            r['location']['s3Location']['uri'] 
            for r in response['retrievalResults']
        ]
        
        expected_found = any(
            query['expected_source'] in source 
            for source in retrieved_sources
        )
        
        results.append({
            'query': query['question'],
            'expected_found': expected_found,
            'top_score': response['retrievalResults'][0]['score'],
            'sources': retrieved_sources[:3]
        })
    
    return results
```

#### 2. Answer Quality Evaluation

```python
def evaluate_answer_quality(kb_id, test_cases):
    """Evaluate end-to-end answer quality."""
    
    bedrock = boto3.client('bedrock-agent-runtime')
    
    for test in test_cases:
        response = bedrock.retrieve_and_generate(
            input={'text': test['question']},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
                }
            }
        )
        
        answer = response['output']['text']
        
        # Check for expected elements
        test['result'] = {
            'answer': answer,
            'contains_expected': all(
                keyword.lower() in answer.lower() 
                for keyword in test['expected_keywords']
            ),
            'has_citations': len(response.get('citations', [])) > 0
        }
    
    return test_cases
```

### Quality Metrics Dashboard

Track these metrics over time:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Retrieval Precision@5 | >80% | % of queries with relevant doc in top 5 |
| Answer Accuracy | >90% | Human evaluation sample |
| Citation Rate | >95% | % of answers with citations |
| Latency P95 | <3s | CloudWatch metrics |
| User Satisfaction | >4/5 | Feedback collection |

---

## Next Steps

1. **Start Small**: Begin with a focused document set (e.g., top 50 support cases)
2. **Iterate**: Test retrieval quality, adjust chunking, add metadata
3. **Expand**: Add more data sources as quality improves
4. **Monitor**: Set up dashboards for ongoing quality tracking
5. **Feedback Loop**: Collect user feedback to identify gaps

## Additional Resources

- [Amazon Bedrock Knowledge Bases Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Chunking Strategies Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking-parsing.html)
- [Data Source Connectors](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html)
