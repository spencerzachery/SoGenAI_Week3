# Building Custom Data Connectors for RAG

## Take-Home Exercise: Advanced Data Ingestion

This guide covers how to build custom connectors to ingest data from various sources into your Bedrock Knowledge Base. This is an optional advanced exercise for after the workshop.

---

## Overview

While Bedrock Knowledge Bases support native connectors for S3, Web Crawler, Confluence, Salesforce, and SharePoint, you'll often need to ingest data from custom sources:

- Internal ticketing systems
- Custom wikis or documentation platforms
- CRM systems
- Slack/Teams channels
- Email archives

The pattern is always the same: **Extract → Transform → Load to S3 → Sync KB**

---

## Architecture Pattern

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Source    │     │  Lambda/Script  │     │  S3 Bucket      │
│  (API, DB, etc) │ ──→ │  (ETL Logic)    │ ──→ │  (KB Source)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  RAG Queries    │ ←── │  Bedrock KB     │ ←── │  Sync Job       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Example 1: Support Ticket Connector

This example shows how to sync resolved support tickets to your knowledge base.

### Lambda Function

```python
import boto3
import json
import os
from datetime import datetime, timedelta

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-agent')

# Your ticket system client (replace with actual implementation)
# from your_ticket_system import TicketClient

def handler(event, context):
    """
    Sync resolved tickets from the last 7 days to S3 for KB ingestion.
    Trigger: EventBridge scheduled rule (daily)
    """
    
    bucket = os.environ['KB_BUCKET']
    kb_id = os.environ['KNOWLEDGE_BASE_ID']
    ds_id = os.environ['DATA_SOURCE_ID']
    
    # Fetch resolved tickets (replace with your API)
    tickets = fetch_resolved_tickets(days_back=7)
    
    synced = 0
    for ticket in tickets:
        # Transform ticket to RAG-optimized format
        content = format_ticket_for_rag(ticket)
        metadata = extract_metadata(ticket)
        
        # Upload to S3
        key = f"tickets/{ticket['id']}.txt"
        upload_with_metadata(bucket, key, content, metadata)
        synced += 1
    
    # Trigger KB sync
    if synced > 0:
        bedrock.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id
        )
    
    return {'synced': synced}


def fetch_resolved_tickets(days_back=7):
    """
    Replace this with your actual ticket system API call.
    Example structure for demonstration.
    """
    # ticket_client = TicketClient(api_key=os.environ['TICKET_API_KEY'])
    # return ticket_client.get_tickets(
    #     status='resolved',
    #     since=datetime.now() - timedelta(days=days_back)
    # )
    
    # Placeholder - replace with real implementation
    return []


def format_ticket_for_rag(ticket):
    """
    Format ticket data for optimal RAG retrieval.
    Key principles:
    - Include clear headers for chunking
    - Add context that helps retrieval
    - Structure for readability
    """
    return f"""# Support Ticket Resolution: {ticket['id']}

## Issue Summary
{ticket['summary']}

## Category
{ticket['category']}

## Priority
{ticket['priority']}

## Customer Environment
- Product: {ticket.get('product', 'N/A')}
- Version: {ticket.get('version', 'N/A')}
- Platform: {ticket.get('platform', 'N/A')}

## Problem Description
{ticket['description']}

## Symptoms Reported
{ticket.get('symptoms', 'Not specified')}

## Root Cause
{ticket['root_cause']}

## Resolution Steps
{ticket['resolution']}

## Time to Resolution
{ticket.get('resolution_time', 'N/A')}

## Prevention Recommendations
{ticket.get('prevention', 'N/A')}

## Related Articles
{', '.join(ticket.get('related_articles', []))}

## Tags
{', '.join(ticket.get('tags', []))}

---
Resolved: {ticket['resolved_date']}
Agent: {ticket.get('agent', 'N/A')}
"""


def extract_metadata(ticket):
    """
    Extract metadata for filtering in RAG queries.
    """
    return {
        'ticket_id': ticket['id'],
        'category': ticket['category'],
        'priority': ticket['priority'],
        'product': ticket.get('product', 'unknown'),
        'resolved_date': ticket['resolved_date'],
        'tags': ticket.get('tags', [])
    }


def upload_with_metadata(bucket, key, content, metadata):
    """
    Upload content and metadata sidecar file to S3.
    Bedrock KB reads .metadata.json files automatically.
    """
    # Upload content
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=content.encode('utf-8'),
        ContentType='text/plain'
    )
    
    # Upload metadata sidecar
    s3.put_object(
        Bucket=bucket,
        Key=f"{key}.metadata.json",
        Body=json.dumps(metadata).encode('utf-8'),
        ContentType='application/json'
    )
```

### EventBridge Rule (CloudFormation)

```yaml
TicketSyncRule:
  Type: AWS::Events::Rule
  Properties:
    Name: ticket-sync-daily
    Description: Sync resolved tickets to KB daily
    ScheduleExpression: cron(0 6 * * ? *)  # 6 AM UTC daily
    State: ENABLED
    Targets:
      - Id: TicketSyncLambda
        Arn: !GetAtt TicketSyncFunction.Arn
```

---

## Example 2: Confluence Wiki Connector

For teams using Confluence without the native connector (e.g., self-hosted).

```python
import boto3
import requests
from bs4 import BeautifulSoup
import os

def sync_confluence_space(space_key):
    """
    Sync a Confluence space to S3 for KB ingestion.
    """
    
    confluence_url = os.environ['CONFLUENCE_URL']
    api_token = os.environ['CONFLUENCE_TOKEN']
    bucket = os.environ['KB_BUCKET']
    
    s3 = boto3.client('s3')
    
    # Fetch all pages in space
    pages = get_space_pages(confluence_url, space_key, api_token)
    
    for page in pages:
        # Get page content
        content = get_page_content(confluence_url, page['id'], api_token)
        
        # Convert HTML to clean text
        clean_content = html_to_markdown(content, page['title'])
        
        # Upload to S3
        key = f"confluence/{space_key}/{page['id']}.md"
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=clean_content.encode('utf-8'),
            ContentType='text/markdown'
        )
        
        # Upload metadata
        metadata = {
            'source': 'confluence',
            'space': space_key,
            'page_id': page['id'],
            'title': page['title'],
            'last_modified': page['version']['when'],
            'author': page['version']['by']['displayName']
        }
        s3.put_object(
            Bucket=bucket,
            Key=f"{key}.metadata.json",
            Body=json.dumps(metadata).encode('utf-8')
        )


def get_space_pages(base_url, space_key, token):
    """Fetch all pages in a Confluence space."""
    headers = {'Authorization': f'Bearer {token}'}
    
    pages = []
    start = 0
    limit = 50
    
    while True:
        response = requests.get(
            f"{base_url}/rest/api/content",
            params={
                'spaceKey': space_key,
                'type': 'page',
                'start': start,
                'limit': limit,
                'expand': 'version'
            },
            headers=headers
        )
        data = response.json()
        pages.extend(data['results'])
        
        if len(data['results']) < limit:
            break
        start += limit
    
    return pages


def get_page_content(base_url, page_id, token):
    """Fetch page content in storage format."""
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(
        f"{base_url}/rest/api/content/{page_id}",
        params={'expand': 'body.storage'},
        headers=headers
    )
    return response.json()['body']['storage']['value']


def html_to_markdown(html_content, title):
    """Convert Confluence HTML to clean markdown."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove macros and unwanted elements
    for element in soup.find_all(['ac:structured-macro', 'ac:parameter']):
        element.decompose()
    
    lines = [f"# {title}\n"]
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'pre', 'table']):
        if element.name.startswith('h'):
            level = int(element.name[1]) + 1  # Offset since title is h1
            lines.append(f"{'#' * level} {element.get_text(strip=True)}\n")
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text:
                lines.append(f"{text}\n")
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li', recursive=False):
                lines.append(f"- {li.get_text(strip=True)}")
        elif element.name == 'pre':
            lines.append(f"```\n{element.get_text()}\n```\n")
    
    return '\n'.join(lines)
```

---

## Example 3: AWS Documentation Crawler

Crawl specific AWS documentation pages for your KB.

```python
import boto3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

def crawl_aws_docs(seed_urls, max_pages=50):
    """
    Crawl AWS documentation pages and upload to S3.
    
    Args:
        seed_urls: List of starting URLs
        max_pages: Maximum pages to crawl
    """
    
    bucket = os.environ['KB_BUCKET']
    s3 = boto3.client('s3')
    
    visited = set()
    to_visit = list(seed_urls)
    crawled = 0
    
    while to_visit and crawled < max_pages:
        url = to_visit.pop(0)
        
        if url in visited:
            continue
        
        # Only crawl docs.aws.amazon.com
        if 'docs.aws.amazon.com' not in url:
            continue
        
        visited.add(url)
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content
            main_content = soup.find('div', {'id': 'main-content'}) or soup.find('main')
            if not main_content:
                continue
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else 'Untitled'
            
            # Clean and format content
            content = format_aws_doc(main_content, title_text, url)
            
            # Generate S3 key from URL path
            path = urlparse(url).path.strip('/')
            key = f"aws-docs/{path}.txt"
            
            # Upload
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=content.encode('utf-8')
            )
            
            # Upload metadata
            metadata = {
                'source': 'aws-documentation',
                'url': url,
                'title': title_text,
                'service': extract_service_from_url(url)
            }
            s3.put_object(
                Bucket=bucket,
                Key=f"{key}.metadata.json",
                Body=json.dumps(metadata).encode('utf-8')
            )
            
            crawled += 1
            
            # Find links to other doc pages
            for link in main_content.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if 'docs.aws.amazon.com' in full_url and full_url not in visited:
                    to_visit.append(full_url)
                    
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            continue
    
    return crawled


def format_aws_doc(content, title, url):
    """Format AWS documentation for RAG."""
    
    # Remove navigation, scripts, etc.
    for element in content.find_all(['nav', 'script', 'style', 'aside']):
        element.decompose()
    
    text = content.get_text(separator='\n', strip=True)
    
    # Clean up excessive whitespace
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return f"""# {title}

Source: {url}
Type: AWS Official Documentation

---

{text}
"""


def extract_service_from_url(url):
    """Extract AWS service name from documentation URL."""
    # URLs like: docs.aws.amazon.com/lambda/latest/dg/...
    parts = urlparse(url).path.split('/')
    if len(parts) > 1:
        return parts[1]
    return 'general'
```

---

## Deployment Checklist

### 1. Create IAM Role for Connector

```yaml
ConnectorRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    Policies:
      - PolicyName: ConnectorPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - s3:PutObject
                - s3:GetObject
              Resource: !Sub '${KnowledgeBaseBucket.Arn}/*'
            - Effect: Allow
              Action:
                - bedrock:StartIngestionJob
              Resource: !Sub 'arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:knowledge-base/*'
            - Effect: Allow
              Action:
                - logs:CreateLogGroup
                - logs:CreateLogStream
                - logs:PutLogEvents
              Resource: '*'
```

### 2. Store Credentials Securely

```bash
# Store API credentials in Secrets Manager
aws secretsmanager create-secret \
    --name /rag-pipeline/ticket-api-key \
    --secret-string '{"api_key": "your-api-key"}'
```

### 3. Schedule Sync Jobs

```yaml
# EventBridge rule for daily sync
SyncSchedule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: rate(1 day)
    Targets:
      - Id: SyncLambda
        Arn: !GetAtt SyncFunction.Arn
```

### 4. Monitor Sync Health

Set up CloudWatch alarms for:
- Lambda errors
- Ingestion job failures
- S3 upload failures

---

## Best Practices

### Content Formatting
- Use clear headers (# ## ###) for chunking boundaries
- Include context in each document (don't assume prior knowledge)
- Add metadata for filtering (category, date, source)

### Incremental Sync
- Track last sync timestamp
- Only process new/modified content
- Use S3 object versioning for history

### Error Handling
- Implement retries with exponential backoff
- Log failed items for manual review
- Don't fail entire sync for single item errors

### Testing
- Test with small dataset first
- Verify retrieval quality before full sync
- Compare RAG responses before/after sync

---

## Next Steps

1. Choose a data source to connect
2. Implement the extraction logic
3. Test with a few documents
4. Verify retrieval quality
5. Set up scheduled sync
6. Monitor and iterate

For questions or issues, refer to:
- [Bedrock Knowledge Bases Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Data Source Configuration](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-ds.html)
