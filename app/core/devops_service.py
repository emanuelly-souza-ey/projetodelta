import asyncio
import requests
import os
from datetime import datetime, timedelta
from app.core.devops_models import *
from app.core.project_model import Project


AZURE_DEVOPS_URL = os.getenv("AZURE_DEVOPS_URL")
AZURE_DEVOPS_TOKEN = os.getenv("AZURE_DEVOPS_TOKEN")

#EXAMPLE DATA TO SHOW IN DOCUMENTATION
project_id = "e4005fd0-7b95-4391-8486-c4b21c935b2e",
team_id = "9083e8b0-af44-4f90-9bdd-f54f9bb431f2"

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_DEVOPS_TOKEN}",#Se cambio por bearer
    }


async def get_projects(project_id = "e4005fd0-7b95-4391-8486-c4b21c935b2e"):
    '''
    #OLD
    url = f"{AZURE_DEVOPS_URL}/_apis/projects?api-version=7.1" #OK
    response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        data = response.json()
        projects = [
            Project.from_json(p) for p in data.get("value", [])
        ]
        return projects
    return {"error": "Falha ao obter dados do Azure DevOps"}
    '''
    #NEW
    projects = []

    url = f"{AZURE_DEVOPS_URL}/{project_id}/_apis/wit/wiql?api-version=7.1"
    query = {
        "query": f"""SELECT
            [System.Id],
            [System.rev],
            [System.ChangedDate],
            [System.State],
            [Microsoft.VSTS.Scheduling.TargetDate]
        FROM workitems
        WHERE
            [System.TeamProject] = 'Generative AI'
            AND [System.WorkItemType] = 'Epic'
        ORDER BY [System.Id] asc
        """
    }

    try:
        
        response = requests.post(url, headers=get_headers(), json=query)
        response.raise_for_status()  
        
        data = response.json()

        work_item_ids = [item["id"] for item in data.get("workItems", [])]
        print(f"IDs dos Work Items: {work_item_ids}" if len(work_item_ids)<10 else f"IDs dos Work Items: {len(work_item_ids)} itens")#Tranquilo
        
        fields =  ["System.Title",
                "System.Description",
                "System.ChangedDate",
                "System.State",
                "Microsoft.VSTS.Scheduling.TargetDate"]

        
        work_items_data = await get_workitems_in_batches(project_id, work_item_ids, fields)
        

        projects = [
            Project.project_from_workitem(p) for p in work_items_data
        ]
        

        return projects

    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar a API: {e}")#Tranquilo

    return projects

def select_project(project_id:str):
    url = f"{AZURE_DEVOPS_URL}/_apis/projects/{project_id}?api-version=7.1" #OK
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return Project.from_json(response.json())
    return {"error": "Falha ao obter dados do projeto {project_id}"}

def get_project_status(project_id:str):
    url = f"{AZURE_DEVOPS_URL}/{project_id}/_apis/wit/workitems?api-version=7.1"
    try:
       response = requests.get(url, headers=get_headers())
       response.raise_for_status()
         
       data = response.json()
       if "count" in data and data["count"] > 0:
           work_items = data["value"]
           status_count = {}

           for item in work_items:
               state = item["fields"].get("System.State", "Unknown")
               status_count[state] = status_count.get(state, 0) + 1
           print("Status do Projeto:")#Tranquilo
           for state, count in status_count.items():
               print(f"{state}: {count} itens")#Toma cuidado
       else:
           print("Nenhum work item encontrado.")#Tranquilo
    except requests.exceptions.RequestException as e:
       print(f"Erro ao consultar a API: {e}")#Tranquilo

async def get_workitems_batch(project_id:str, workitem_ids:List[int], fields:List[str]=None):
    if not fields:
        fields = ["System.Title", "System.State", "System.AssignedTo", "Microsoft.VSTS.Scheduling.CompletedWork", "Microsoft.VSTS.Scheduling.TargetDate"]
    ids = ",".join(map(str, workitem_ids))
    field_names = ",".join(fields)
    
    url = f"{AZURE_DEVOPS_URL}/{project_id}/_apis/wit/workitems?ids={ids}&fields={field_names}&api-version=7.1" #OK
    headers = get_headers()
    headers["Content-Type"] = "application/json-patch+json"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
        
    return {"error": "Falha ao obter dados do Azure DevOps"}

async def get_workitems_in_batches(project_id: str, workitem_ids: List[int], fields: List[str] = None):
    if not fields:
        fields = ["System.Title",
                  "System.State",
                  "System.AssignedTo",
                  "Microsoft.VSTS.Scheduling.CompletedWork",
                  "Microsoft.VSTS.Scheduling.TargetDate"]
    
    batch_size = 200
    all_workitems = []

    for i in range(0, len(workitem_ids), batch_size):
        print("Batch", i // batch_size + 1)#Tranquilo
        batch_ids = workitem_ids[i:i + batch_size]
        batch_data = await get_workitems_batch(project_id, batch_ids, fields)
        
        if "error" in batch_data:
            #print(batch_data["error"])#Tranquilo
            continue
        
        all_workitems.extend(batch_data.get("value", []))
    
    return all_workitems

def get_overdue_tasks(project_id:str):
    url = f"{AZURE_DEVOPS_URL}/{project_id}/_apis/wit/workitems?api-version=7.1" #testando, ainda não está pegando as infos necessarias
   
    params = {
       "api-version": "7.1",
       "$filter": "Microsoft.VSTS.Scheduling.TargetDate lt '2025-03-13T00:00:00Z'" 
    }
    try:
        response = requests.get(url, headers=get_headers(), params=params)
        response.raise_for_status() 
        
        data = response.json()

        if "count" in data and data["count"] > 0:
            overdue_tasks = data["value"]
            print(f"Total de cards atrasados: {len(overdue_tasks)}")
            for task in overdue_tasks:
                title = task["fields"].get("System.Title", "Sem título")
                print(f"- {title}")#toma cuidado

            
        else:
            print("Nenhum card atrasado encontrado.")#Tranquilo
    except requests.exceptions.RequestException as e:
       print(f"Erro ao consultar a API: {e}")#Tranquilo

def get_work_hours(project_id, period="weekly"):
    url = f"{AZURE_DEVOPS_URL}/{project_id}/_apis/wit/workitems?api-version=7.1" #testando, ainda não está pegando as infos necessarias
   
    today = datetime.today()
    if period == "weekly":
       start_date = today - timedelta(days=7)
    elif period == "monthly":
       start_date = today.replace(day=1)  
    else:
       raise ValueError("Período inválido. Use 'weekly' ou 'monthly'.")
   
    params = {
       "api-version": "7.1",
       "$filter": f"System.ChangedDate ge '{start_date.strftime('%Y-%m-%d')}T00:00:00Z'"
    }
    try:
       response = requests.get(url, headers=get_headers(), params=params)
       response.raise_for_status()  
       data = response.json()
       if "count" in data and data["count"] > 0:
           work_items = data["value"]
           total_completed = 0
           total_estimated = 0
           total_remaining = 0
        
           for item in work_items:
               fields = item.get("fields", {})
               total_completed += fields.get("Microsoft.VSTS.Scheduling.CompletedWork", 0)
               total_estimated += fields.get("Microsoft.VSTS.Scheduling.OriginalEstimate", 0)
               total_remaining += fields.get("Microsoft.VSTS.Scheduling.RemainingWork", 0)
           print(f"Período: {period.capitalize()}")#Tranquilo
           print(f"- Horas Trabalhadas: {total_completed}h")#Tranquilo
           print(f"- Horas Estimadas: {total_estimated}h")#Tranquilo
           print(f"- Horas Restantes: {total_remaining}h")#Tranquilo
       else:
           print("Nenhuma informação de horas encontrada no período.")#Tranquilo
    except requests.exceptions.RequestException as e:
       print(f"Erro ao consultar a API: {e}")#Tranquilo

async def get_user_daily_tasks(project_id:str, userName:str):
    url = f"{AZURE_DEVOPS_URL}/{project_id}/_apis/wit/wiql?api-version=7.1"
    query = {
        "query": f"""SELECT
        [Microsoft.VSTS.Scheduling.CompletedWork],
        [Microsoft.VSTS.Scheduling.TargetDate]
    FROM workitems
    WHERE
        [System.TeamProject] = 'Generative AI'
        AND [Microsoft.VSTS.Scheduling.TargetDate] = @today
        AND [System.WorkItemType] = 'Task'
        AND [System.AssignedTo] = '{userName}'
    ORDER BY [System.Id] asc
    """
    }

    try:

        response = requests.post(url, headers=get_headers(), json=query)
        response.raise_for_status()  
        
        data = response.json()

        work_item_ids = [item["id"] for item in data.get("workItems", [])]
        print(f"IDs dos Work Items: {work_item_ids}" if len(work_item_ids)<10 else f"IDs dos Work Items: {len(work_item_ids)} itens")#Tranquilo
        work_items_data = await get_workitems_batch(project_id, work_item_ids)
        
        if "error" in work_items_data:
            print(work_items_data["error"])#Tranquilo
            return {}

        return work_items_data
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar a API: {e}")#Tranquilo

    return {}

async def get_daily_tasks(project_id:str):
    url = f"{AZURE_DEVOPS_URL}/{project_id}/_apis/wit/wiql?api-version=7.1"
    query = {
        "query": f"""SELECT
        [Microsoft.VSTS.Scheduling.CompletedWork],
        [Microsoft.VSTS.Scheduling.TargetDate]
    FROM workitems
    WHERE
        [System.TeamProject] = 'Generative AI'
        AND [Microsoft.VSTS.Scheduling.TargetDate] < @today
        AND [Microsoft.VSTS.Scheduling.TargetDate] > @today - 15

        AND [System.WorkItemType] = 'Task'
    ORDER BY [System.Id] asc
    """
    }

    try:

        response = requests.post(url, headers=get_headers(), json=query)
        response.raise_for_status()  
        
        data = response.json()

        work_item_ids = [item["id"] for item in data.get("workItems", [])]
        print(f"IDs dos Work Items: {work_item_ids}" if len(work_item_ids)<10 else f"IDs dos Work Items: muitos ({len(work_item_ids)})")#Tranquilo
        work_items_data = await get_workitems_in_batches(project_id, work_item_ids)
        
        if "error" in work_items_data:
            print(work_items_data["error"])#Tranquilo
            return {}

        return work_items_data
    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar a API: {e}")#Tranquilo

    return {}

def get_teams(project_id:str):
    url: f"{AZURE_DEVOPS_URL}/_apis/projects/{project_id}/teams?api-version=7.1"  #OK
    response = requests.post(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return {"error": f"Falha ao obter informações sobre os times do projeto {project_id}"}

def get_team_members(project_id:str, team_id:str):
    url = f"{AZURE_DEVOPS_URL}/_apis/projects/{project_id}/teams/{team_id}/members?api-version=7.1" #OK
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200 and "value" in response.json():
        return response.json()
    return {"error": f"Falha ao obter informações sobre os membros da equipe {team_id} do projeto {project_id}"}

async def get_project_info(project_id:str, repository_id:str):
    project_status = get_project_status(project_id)
    overdue_tasks = get_overdue_tasks(project_id)
    work_hours = get_work_hours(project_id)
    daily_tasks = await get_daily_tasks(project_id)
    team_info = get_teams(project_id)

    return{
        "project_status": project_status,
        "overdue_tasks": overdue_tasks,
        "work_hours": work_hours,
        "daily_tasks": daily_tasks,
        "team_info": team_info
    }

#in an ideal world we saved the project

global actual_project
actual_project = None
#New for epic Project
async def epic_get_tasks(project_id:str, azure_project_id="e4005fd0-7b95-4391-8486-c4b21c935b2e"):
    global actual_project
    if not actual_project:
        actual_project = Project()
        actual_project.id=project_id
        return actual_project.getTasks(headers=get_headers(), azure_path=AZURE_DEVOPS_URL, azure_project_id=azure_project_id)
    
async def epic_get_team_members(project_id:str, azure_project_id="e4005fd0-7b95-4391-8486-c4b21c935b2e"):
    global actual_project
    if not actual_project:
        actual_project = Project()
        actual_project.id=project_id
        return actual_project.getTeamMembers(headers=get_headers(), azure_path=AZURE_DEVOPS_URL, azure_project_id=azure_project_id)