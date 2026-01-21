#!/usr/bin/env python3
"""
Create Bedrock Knowledge Base
Automates the creation of a Bedrock Knowledge Base with S3 data source.
"""

import boto3
import json
import os
import sys
import time

# Configuration
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'rag-pipeline')
REGION = os.environ.get('AWS_REGION', 'us-east-1')
EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'

def get_account_id():
    """Get AWS account ID."""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Account']

def get_role_arn(account_id):
    """Get the Bedrock KB role ARN from CloudFormation."""
    cf = boto3.client('cloudformation', region_name=REGION)
    try:
        response = cf.describe_stacks(StackName=f'{PROJECT_NAME}-stack')
        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:
            if output['OutputKey'] == 'BedrockKBRoleArn':
                return output['OutputValue']
    except Exception as e:
        print(f"Error getting role ARN: {e}")
    return f"arn:aws:iam::{account_id}:role/{PROJECT_NAME}-bedrock-kb-role"

def get_opensearch_arn(account_id):
    """Get OpenSearch collection ARN from CloudFormation."""
    cf = boto3.client('cloudformation', region_name=REGION)
    try:
        response = cf.describe_stacks(StackName=f'{PROJECT_NAME}-stack')
        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:
            if output['OutputKey'] == 'OpenSearchCollectionArn':
                return output['OutputValue']
    except Exception as e:
        print(f"Error getting OpenSearch ARN: {e}")
    return None

def create_knowledge_base():
    """Create Bedrock Knowledge Base."""
    account_id = get_account_id()
    role_arn = get_role_arn(account_id)
    collection_arn = get_opensearch_arn(account_id)
    
    if not collection_arn:
        print("❌ OpenSearch collection not found. Deploy CloudFormation first.")
        sys.exit(1)
    
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    # Check if KB already exists
    existing = bedrock_agent.list_knowledge_bases()
    for kb in existing.get('knowledgeBaseSummaries', []):
        if kb['name'] == f'{PROJECT_NAME}-kb':
            print(f"Knowledge Base already exists: {kb['knowledgeBaseId']}")
            return kb['knowledgeBaseId']
    
    print("Creating Knowledge Base...")
    
    # Create Knowledge Base
    response = bedrock_agent.create_knowledge_base(
        name=f'{PROJECT_NAME}-kb',
        description='Enterprise Support case resolution knowledge base',
        roleArn=role_arn,
        knowledgeBaseConfiguration={
            'type': 'VECTOR',
            'vectorKnowledgeBaseConfiguration': {
                'embeddingModelArn': f'arn:aws:bedrock:{REGION}::foundation-model/{EMBEDDING_MODEL}'
            }
        },
        storageConfiguration={
            'type': 'OPENSEARCH_SERVERLESS',
            'opensearchServerlessConfiguration': {
                'collectionArn': collection_arn,
                'vectorIndexName': 'bedrock-knowledge-base-index',
                'fieldMapping': {
                    'vectorField': 'vector',
                    'textField': 'text',
                    'metadataField': 'metadata'
                }
            }
        }
    )
    
    kb_id = response['knowledgeBase']['knowledgeBaseId']
    print(f"✓ Knowledge Base created: {kb_id}")
    
    # Wait for KB to be ready
    print("Waiting for Knowledge Base to be ready...")
    while True:
        status = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        state = status['knowledgeBase']['status']
        if state == 'ACTIVE':
            break
        elif state == 'FAILED':
            print(f"❌ Knowledge Base creation failed")
            sys.exit(1)
        time.sleep(5)
    
    return kb_id

def create_data_source(kb_id):
    """Create S3 data source for the Knowledge Base."""
    account_id = get_account_id()
    bucket_name = f'{PROJECT_NAME}-kb-{account_id}-{REGION}'
    
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    # Check if data source exists
    existing = bedrock_agent.list_data_sources(knowledgeBaseId=kb_id)
    for ds in existing.get('dataSourceSummaries', []):
        if ds['name'] == 'support-cases':
            print(f"Data source already exists: {ds['dataSourceId']}")
            return ds['dataSourceId']
    
    print("Creating data source...")
    
    response = bedrock_agent.create_data_source(
        knowledgeBaseId=kb_id,
        name='support-cases',
        description='Enterprise Support case documentation',
        dataSourceConfiguration={
            'type': 'S3',
            's3Configuration': {
                'bucketArn': f'arn:aws:s3:::{bucket_name}',
                'inclusionPrefixes': ['support-cases/']
            }
        },
        vectorIngestionConfiguration={
            'chunkingConfiguration': {
                'chunkingStrategy': 'FIXED_SIZE',
                'fixedSizeChunkingConfiguration': {
                    'maxTokens': 300,
                    'overlapPercentage': 20
                }
            }
        }
    )
    
    ds_id = response['dataSource']['dataSourceId']
    print(f"✓ Data source created: {ds_id}")
    
    return ds_id

def sync_data_source(kb_id, ds_id):
    """Start ingestion job to sync data source."""
    bedrock_agent = boto3.client('bedrock-agent', region_name=REGION)
    
    print("Starting data sync...")
    
    response = bedrock_agent.start_ingestion_job(
        knowledgeBaseId=kb_id,
        dataSourceId=ds_id
    )
    
    job_id = response['ingestionJob']['ingestionJobId']
    print(f"Ingestion job started: {job_id}")
    
    # Wait for sync to complete
    print("Waiting for sync to complete (this may take a few minutes)...")
    while True:
        status = bedrock_agent.get_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id,
            ingestionJobId=job_id
        )
        state = status['ingestionJob']['status']
        if state == 'COMPLETE':
            stats = status['ingestionJob'].get('statistics', {})
            print(f"✓ Sync complete!")
            print(f"  Documents scanned: {stats.get('numberOfDocumentsScanned', 'N/A')}")
            print(f"  Documents indexed: {stats.get('numberOfNewDocumentsIndexed', 'N/A')}")
            break
        elif state == 'FAILED':
            print(f"❌ Sync failed")
            failure = status['ingestionJob'].get('failureReasons', [])
            for reason in failure:
                print(f"  Reason: {reason}")
            sys.exit(1)
        print(f"  Status: {state}...")
        time.sleep(10)
    
    return job_id

def main():
    print("=" * 50)
    print("  Bedrock Knowledge Base Setup")
    print("=" * 50)
    print()
    
    # Create Knowledge Base
    kb_id = create_knowledge_base()
    
    # Create Data Source
    ds_id = create_data_source(kb_id)
    
    # Sync Data Source
    sync_data_source(kb_id, ds_id)
    
    print()
    print("=" * 50)
    print("  Setup Complete!")
    print("=" * 50)
    print()
    print(f"Knowledge Base ID: {kb_id}")
    print()
    print("To query the knowledge base:")
    print(f"  export KB_ID={kb_id}")
    print(f"  python3 query-knowledge-base.py 'Your question here'")
    print()

if __name__ == '__main__':
    main()
