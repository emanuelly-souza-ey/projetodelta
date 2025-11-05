# devops_epic.py 
# Quando os projetos são tratados como épicos, a lógica da aplicação muda, e por isso há um arquivo separado para lidar com essa funcionalidade.

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.core.devops_models import *
from app.core.project_model import Project, EpicProject
from app.core.devops_service import get_workitems_in_batches
from app.core.customLRUCache import LRUCache

router = APIRouter()
cache = LRUCache(10)#Maximun of 10 projects in cache

AZURE_DEVOPS_URL = os.getenv("AZURE_DEVOPS_URL")
#AZURE_DEVOPS_TOKEN = os.getenv("AZURE_DEVOPS_TOKEN") #save it is insecure

def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv("AZURE_DEVOPS_TOKEN")}",
    }

global azure_project_id
azure_project_id = "e4005fd0-7b95-4391-8486-c4b21c935b2e" #ID do projeto Generative AI


@router.get("/projects", response_model=List[EpicProject])
async def list_projects():
    global azure_project_id

    #{AZURE_DEVOPS_URL}/_apis/projects?api-version=7.1
    projects = []

    url = f"{AZURE_DEVOPS_URL}/{azure_project_id}/_apis/wit/wiql?api-version=7.1"
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
        ORDER BY [System.ChangedDate] asc
        """
    }

    try:
        response = requests.post(url, headers=get_headers(), json=query)
        response.raise_for_status()  
        
        data = response.json()

        work_item_ids = [item["id"] for item in data.get("workItems", [])]
        #print(f"IDs dos Work Items: {work_item_ids}" if len(work_item_ids)<10 else f"IDs dos Work Items: {len(work_item_ids)} itens")#Tranquilo
        
        fields =  ["System.Title",
                "System.Description",
                "System.ChangedDate",
                "System.State",
                "Microsoft.VSTS.Scheduling.TargetDate"]
        
        work_items_data = await get_workitems_in_batches(azure_project_id, work_item_ids, fields)
        
        projects = [
            EpicProject.project_from_workitem(p) for p in work_items_data
        ]

        return projects

    except requests.exceptions.RequestException as e:
        print(f"Erro ao consultar a API: ")#Tranquilo

    return projects

@router.get("/project/{project_id}/tasks", response_model=List[WorkItem])
async def project_tasks(project_id):
    global azure_project_id

    # Verifica se o projeto já está em cache
    project = cache.get(project_id)
    if project == -1:
        project = EpicProject.get_from_request(project_id, headers=get_headers(), azure_path=AZURE_DEVOPS_URL, azure_project_id=azure_project_id)
    
    print("Va a invocar a obtener tareas")
    tasks = project.getTasks(get_headers(), azure_project_id=azure_project_id)
    cache.put(project_id, project)

    return tasks