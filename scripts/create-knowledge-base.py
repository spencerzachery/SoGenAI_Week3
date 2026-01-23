#!/usr/bin/env python3
"""
Knowledge Base Sync Utility
Triggers a re-sync of the Bedrock Knowledge Base data source.

Note: The Knowledge Base is now created automatically by CloudFormation.
This script is useful for manually triggering re-ingestion after adding new documents.
"""

import boto3
import os
import sys
import time

# Configuration
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'rag-pipeline')
REGION = os.environ.get('AWS_REGION', 'us-east-1')

def get_kb_info():
    """Get Knowledge Base ID and Data Source ID from CloudFormation outputs."""
    cf = boto3.client('cloudformation', region_name=REGION)
    
    try:
        response = cf.describe_stacks(StackName=f'{PROJECT_NAME}-stack')
        outputs = response['Stacks'][0]['Outputs']
        
        kb_id = None
        ds_id = None
        
        for output in outputs:
            if output['OutputKey'] == 'KnowledgeBaseId':
                kb_id = output['OutputValue']
            elif output['OutputKey'] == 'DataSourceId':
                ds_id = output['OutputValue']
        
        return kb_id, ds_id
    except Exception as e:
        print(f"Error getting stack outputs: {e}")
        return None, None

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
    print("  Knowledge Base Sync Utility")
    print("=" * 50)
    print()
    
    # Get KB info from CloudFormation
    kb_id, ds_id = get_kb_info()
    
    if not kb_id or not ds_id:
        print("❌ Knowledge Base not found. Deploy CloudFormation stack first:")
        print("   ./cloudformation/deploy.sh")
        sys.exit(1)
    
    print(f"Knowledge Base ID: {kb_id}")
    print(f"Data Source ID: {ds_id}")
    print()
    
    # Sync Data Source
    sync_data_source(kb_id, ds_id)
    
    print()
    print("=" * 50)
    print("  Sync Complete!")
    print("=" * 50)
    print()
    print("To query the knowledge base:")
    print(f"  python3 scripts/query-knowledge-base.py 'Your question here'")
    print()

if __name__ == '__main__':
    main()
