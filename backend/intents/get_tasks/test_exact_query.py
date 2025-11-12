#funcionando
"""
Test exact WIQL query provided by user.
This tests the specific query structure from Azure DevOps.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import get_azure_config
from backend.intents.base_intent import BaseService


class SimpleTestService(BaseService):
    """Simple service just for testing queries."""
    
    def __init__(self):
        super().__init__()
    
    async def query_data(self, params):
        pass  # Not used


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
    AND [Source].[System.AreaPath] = 'HUB GenAI\\Projetos Internos'
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
    AND [Target].[System.IterationPath] UNDER 'HUB GenAI\\Projetos Internos\\Next.IA'
    AND [Target].[System.AreaPath] = 'HUB GenAI\\Projetos Internos'
ORDER BY [Microsoft.VSTS.Common.StackRank] ASC,
    [System.Id] ASC
MODE (Recursive, ReturnMatchingChildren)"""
    
    print("=== TESTING EXACT USER QUERY ===")
    print(f"Query length: {len(wiql_query)} characters")
    print("\nQuery:")
    print(wiql_query)
    
    # Get config and create service
    config = get_azure_config()
    service = SimpleTestService()
    
    # Build URL
    project_id = config.devops_project_id
    url = config.get_devops_url(project_id) + "/_apis/wit/wiql?api-version=7.1"
    headers = config.get_devops_headers()
    
    print(f"\n=== REQUEST INFO ===")
    print(f"URL: {url}")
    print(f"Project ID: {project_id}")
    print(f"Headers: {dict(headers)}")
    
    try:
        print(f"\n=== MAKING REQUEST ===")
        
        # Make the request
        response = service.make_request(
            method="POST",
            url=url,
            headers=headers,
            json={"query": wiql_query}
        )
        
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
                await fetch_work_item_details(service, config, list(work_item_ids)[:10])  # Limit to first 10
        
        else:
            print("No work item relations found - this is why we get 0 work items!")
        
        # Full response for debugging
        print(f"\n=== FULL RESPONSE (first 1000 chars) ===")
        response_text = str(data)
        print(response_text[:1000])
        if len(response_text) > 1000:
            print("... (truncated)")
        
        return data
        
    except Exception as e:
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


async def fetch_work_item_details(service, config, work_item_ids):
    """Fetch detailed information for work items."""
    try:
        # Build work items API URL
        ids_str = ",".join(str(id) for id in work_item_ids)
        project_id = config.devops_project_id
        url = config.get_devops_url(project_id) + f"/_apis/wit/workitems?ids={ids_str}&api-version=7.1"
        headers = config.get_devops_headers()
        
        print(f"Fetching details for IDs: {ids_str}")
        print(f"URL: {url}")
        
        response = service.make_request(
            method="GET",
            url=url,
            headers=headers
        )
        
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


async def test_simple_query():
    """Test a simpler query for comparison."""
    
    simple_query = """SELECT
    [System.Id],
    [System.WorkItemType],
    [System.Title],
    [System.State],
    [System.AssignedTo]
FROM WorkItems
WHERE
    [System.WorkItemType] IN ('Task', 'Bug', 'User Story')
    AND [System.AreaPath] UNDER 'HUB GenAI'
ORDER BY [System.Id] ASC"""
    
    print(f"\n\n=== TESTING SIMPLE QUERY FOR COMPARISON ===")
    print(f"Query: {simple_query}")
    
    # Get config and create service
    config = get_azure_config()
    service = SimpleTestService()
    
    # Build URL
    project_id = config.devops_project_id
    url = config.get_devops_url(project_id) + "/_apis/wit/wiql?api-version=7.1"
    headers = config.get_devops_headers()
    
    try:
        # Make the request
        response = service.make_request(
            method="POST",
            url=url,
            headers=headers,
            json={"query": simple_query}
        )
        
        print(f"✅ Simple query SUCCESS! Status: {response.status_code}")
        
        # Parse response
        data = response.json()
        work_items = data.get("workItems", [])
        print(f"Simple query found: {len(work_items)} work items")
        
        if work_items:
            print("First 3 items:")
            for item in work_items[:3]:
                print(f"  - ID: {item.get('id')}")
        
        return data
        
    except Exception as e:
        print(f"❌ Simple query ERROR: {e}")
        return None


if __name__ == "__main__":
    print("Testing exact WIQL query from user...")
    
    # Test the exact query
    asyncio.run(test_exact_query())
    
    # Test simple query for comparison
    #asyncio.run(test_simple_query())
    
    print("\n🎉 Test completed!")