"""
Test exact WIQL query provided by user.
This tests the specific query structure from Azure DevOps.
Standalone version - no dependencies on intent system.
"""

import asyncio
import sys
import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure DevOps configuration
AZURE_DEVOPS_URL = os.getenv("AZURE_DEVOPS_URL")
AZURE_DEVOPS_TOKEN = os.getenv("AZURE_DEVOPS_TOKEN")
PROJECT_ID = "b50492f0-02ea-47c0-a987-f5404c7e2f89"

# Encode token properly for Basic Auth
def get_auth_header():
    """Generate properly encoded Basic Auth header."""
    token = f":{AZURE_DEVOPS_TOKEN}"
    encoded = base64.b64encode(token.encode()).decode()
    return f"Basic {encoded}"


async def test_exact_query():
    """Test the exact WIQL query provided by user."""
    
    # The exact query from user
    wiql_query = """SELECT
    [System.Id],
    [System.WorkItemType],
    [System.Title],
    [System.State],
    [System.AssignedTo],
    [Microsoft.VSTS.Scheduling.RemainingWork],
    [System.TeamProject],
    [System.Tags],
    [Microsoft.VSTS.Common.StackRank],
    [System.AreaId],
    [System.IterationPath],
    [System.IterationId],
    [System.AreaPath],
    [Microsoft.VSTS.Common.Activity]
FROM workitemLinks
WHERE
    (
        (
            [Source].[System.WorkItemType] IN ('Task', 'Bug')
            AND [Source].[System.State] IN ('New', 'Active', 'Blocked', 'Closed', 'Resolved')
        )
        OR (
            [Source].[System.WorkItemType] IN ('User Story')
            AND [Source].[System.State] IN ('New', 'Active', 'Resolved', 'Closed')
        )
    )
    AND [Source].[System.IterationPath] UNDER 'HUB GenAI'
    AND [Source].[System.AreaPath] = 'HUB GenAI\\Projeto DELTA'
    AND [System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward'
    AND (
        (
            [Target].[System.WorkItemType] IN ('Task')
            AND [Target].[System.State] IN ('New', 'Active', 'Blocked', 'Closed', 'Resolved')
        )
        OR (
            [Target].[System.WorkItemType] IN ('User Story')
            AND [Target].[System.State] IN ('New', 'Active', 'Resolved', 'Closed')
        )
    )
    AND [Target].[System.IterationPath] UNDER 'HUB GenAI\\Projeto DELTA'
    AND [Target].[System.AreaPath] = 'HUB GenAI\\Projeto DELTA'
ORDER BY [Microsoft.VSTS.Common.StackRank] ASC,
    [System.Id] ASC
MODE (Recursive, ReturnMatchingChildren)"""
    
    print("=== TESTING EXACT USER QUERY ===")
    print(f"Query length: {len(wiql_query)} characters")
    print("\nQuery:")
    print(wiql_query)
    
    # Build URL and headers
    url = f"{AZURE_DEVOPS_URL.rstrip('/')}/{PROJECT_ID}/_apis/wit/wiql?api-version=7.1"
    headers = {
        "Content-Type": "application/json",
        "Authorization": get_auth_header()
    }
    
    print(f"\n=== REQUEST INFO ===")
    print(f"URL: {url}")
    print(f"Project ID: {PROJECT_ID}")
    print(f"Headers: Content-Type and Authorization set")
    
    try:
        print(f"\n=== MAKING REQUEST ===")
        
        # Make the request
        response = requests.post(
            url=url,
            headers=headers,
            json={"query": wiql_query}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text (first 500 chars): {response.text[:500]}")
        
        response.raise_for_status()
        print(f"✅ SUCCESS! Status: {response.status_code}")
        
        # Parse response
        data = response.json()
        
        print(f"\n=== RESPONSE ANALYSIS ===")
        print(f"Response keys: {list(data.keys())}")
        
        # Check for work items
        work_items = data.get("workItems", [])
        print(f"Work items found: {len(work_items)}")
        
        if work_items:
            print(f"\n=== FIRST FEW WORK ITEMS ===")
            for i, item in enumerate(work_items[:5]):
                print(f"  {i+1}. ID: {item.get('id')}, URL: {item.get('url', 'No URL')}")
        
        # Check for work item relations
        relations = data.get("workItemRelations", [])
        print(f"Work item relations found: {len(relations)}")
        
        if relations:
            print(f"\n=== FIRST FEW RELATIONS ===")
            for i, rel in enumerate(relations[:5]):
                source = rel.get("source")
                target = rel.get("target")
                print(f"  {i+1}. Source: {source.get('id') if source else 'None'}, Target: {target.get('id') if target else 'None'}")
            
            # Extract unique work item IDs from relations
            work_item_ids = set()
            for rel in relations:
                source = rel.get("source")
                target = rel.get("target")
                if source and source.get("id"):
                    work_item_ids.add(source.get("id"))
                if target and target.get("id"):
                    work_item_ids.add(target.get("id"))
            
            print(f"\n=== EXTRACTED WORK ITEM IDS ===")
            print(f"Unique work item IDs from relations: {len(work_item_ids)}")
            print(f"First 10 IDs: {list(work_item_ids)[:10]}")
            
            if work_item_ids:
                # Now get the actual work item details
                print(f"\n=== FETCHING WORK ITEM DETAILS ===")
                await fetch_work_item_details(list(work_item_ids)[:10])  # Limit to first 10
        
        else:
            print("No work item relations found - this is why we get 0 work items!")
        
        # Full response for debugging
        print(f"\n=== FULL RESPONSE (first 1000 chars) ===")
        response_text = str(data)
        print(response_text[:1000])
        if len(response_text) > 1000:
            print("... (truncated)")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Print detailed error info
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response headers: {dict(e.response.headers)}")
            print(f"Response text: {e.response.text[:1000]}")
        
        import traceback
        traceback.print_exc()
        
        raise
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        
        import traceback
        traceback.print_exc()
        
        raise


async def fetch_work_item_details(work_item_ids):
    """Fetch detailed information for work items."""
    try:
        # Build work items API URL
        ids_str = ",".join(str(id) for id in work_item_ids)
        url = f"{AZURE_DEVOPS_URL.rstrip('/')}/{PROJECT_ID}/_apis/wit/workitems?ids={ids_str}&api-version=7.1"
        headers = {
            "Content-Type": "application/json",
            "Authorization": get_auth_header()
        }
        
        print(f"Fetching details for IDs: {ids_str}")
        print(f"URL: {url}")
        
        response = requests.get(url=url, headers=headers)
        
        response.raise_for_status()
        data = response.json()
        work_items = data.get("value", [])
        
        print(f"✅ Got details for {len(work_items)} work items")
        
        for item in work_items:
            fields = item.get("fields", {})
            print(f"  - ID: {item.get('id')}")
            print(f"    Type: {fields.get('System.WorkItemType')}")
            print(f"    Title: {fields.get('System.Title', 'No title')}")
            print(f"    State: {fields.get('System.State')}")
            print(f"    Assigned: {fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned') if fields.get('System.AssignedTo') else 'Unassigned'}")
            print(f"    Area: {fields.get('System.AreaPath')}")
            print(f"    Iteration: {fields.get('System.IterationPath')}")
            print()
        
        return work_items
        
    except Exception as e:
        print(f"❌ Error fetching work item details: {e}")
        return []


async def fetch_simple_work_item_details(work_item_ids):
    """Fetch details for simple query comparison."""
    try:
        ids_str = ",".join(str(id) for id in work_item_ids)
        url = f"{AZURE_DEVOPS_URL.rstrip('/')}/{PROJECT_ID}/_apis/wit/workitems?ids={ids_str}&api-version=7.1"
        headers = {
            "Content-Type": "application/json",
            "Authorization": get_auth_header()
        }
        
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        data = response.json()
        work_items = data.get("value", [])
        
        for item in work_items:
            fields = item.get("fields", {})
            assigned_to = fields.get('System.AssignedTo', {})
            assigned_name = assigned_to.get('displayName', 'Unassigned') if assigned_to else 'Unassigned'
            
            print(f"  ✅ ID: {item.get('id')} | {fields.get('System.Title', 'No title')[:50]}... | {assigned_name}")
        
        return work_items
        
    except Exception as e:
        print(f"❌ Error fetching simple work item details: {e}")
        return []



if __name__ == "__main__":
    print("🔬 TESTING BOTH QUERY APPROACHES - COMPLEX vs SIMPLE!")
    print("="*70)
    
    # Test the complex hierarchical query
    print("1️⃣ COMPLEX HIERARCHICAL QUERY (workitemLinks)")
    complex_result = asyncio.run(test_exact_query())
    
    print("\n" + "="*70)
    
    # Test simple direct query for comparison  

    
    print("\n" + "="*70)
    print("🏆 COMPARISON SUMMARY:")
    
    if complex_result:
        # Compare results
        complex_relations = len(complex_result.get("workItemRelations", []))
        complex_items = len(complex_result.get("workItems", []))
        
        print(f"📊 Complex Query: {complex_relations} relations, {complex_items} direct items")
        
    
    print("\n🎭 Moral of the story: Sometimes simple is better! 😄")