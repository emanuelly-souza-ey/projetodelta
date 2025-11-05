from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.core.devops_service import (
   get_projects, 
   select_project, 
   get_project_status,
   get_overdue_tasks, 
   get_work_hours, 
   get_daily_tasks, 
   get_teams, 
   get_project_info,
   get_team_members,
   get_workitems_batch,
   get_user_daily_tasks
)
from app.core.devops_models import *
from app.core.project_model import Project

router = APIRouter()

"""
|Pronto | Rota                                       | Descrição                                         |
|------ |------------------------------------------- |---------------------------------------------------|
| ✅   | `/projects`                                 | Lista todos os projetos.                          |
| ✅   | `/projects/{project_id}`                    | Obtém os detalhes de um projeto específico.       |
| ❌   | `/projects/{project_id}/status`             | Obtém o status de um projeto específico.          |
| ✅   | `/projects/{project_id}/overdue_tasks`      | Obtém as tarefas vencidas de um projeto.          |
| ❌   | `/projects/{project_id}/work_hours/{repository_id}` | Obtém as horas de trabalho de um projeto. |
| ✅   | `/projects/{project_id}/daily_tasks`        | Obtém as tarefas diárias de um projeto.           |
| ✅   | `/projects/{project_id}/daily_tasks/{user_id}`| Obtém as tarefas diárias de uma pessoa de um projeto. |
| ❌   | `/projects/{project_id}/team`               | Obtém informações sobre todas as equipes em um projeto. |
| ✅   | `/projects/{project_id}/members/{team_id}`  | Obtém todos os membros de uma equipe específica. |
| ❌   | `/project_info/{project_id}/{repository_id}`| Obtém informações do projeto e repositório.    |
"""



@router.get("/projects", response_model=List[Project])
async def list_projects():
   #{AZURE_DEVOPS_URL}/_apis/projects?api-version=7.1
   projects = await get_projects()
   if "error" in projects:
       raise HTTPException(status_code=500, detail=projects["error"])
   return projects

@router.get("/projects/{project_id}", response_model=Project)
async def project_details(project_id: str):
   #{AZURE_DEVOPS_URL}/_apis/projects/{project_id}?api-version=7.1
   project = select_project(project_id)
   if "error" in project:
       raise HTTPException(status_code=404, detail=project["error"])
   return project

@router.get("/projects/{project_id}/status", response_model=Dict[str, Any])
async def project_status(project_id: str):
   status = get_project_status(project_id)
   if "error" in status:
       raise HTTPException(status_code=500, detail=status["error"])
   return status

@router.get("/projects/{project_id}/workitems_batch", response_model=Dict[str, Any])
async def workitems_batch(project_id: str, work_item_ids: List[int]):
   # Returns all work items in a project
   work_items = get_workitems_batch(project_id, work_item_ids)
   if "error" in work_items:
       raise HTTPException(status_code=500, detail=work_items["error"])
   return work_items

@router.post("/projects/{project_id}/overdue_tasks", response_model=Dict[str, Any])#TODO
async def overdue_tasks(project_id: str):
   tasks = get_overdue_tasks(project_id)
   if "error" in tasks:
       raise HTTPException(status_code=500, detail=tasks["error"])
   return tasks

@router.post("/projects/{project_id}/work_hours/{repository_id}", response_model=Dict[str, Any])
async def work_hours(project_id: str, repository_id: str):
   hours = get_work_hours(project_id, repository_id)
   if "error" in hours:
       raise HTTPException(status_code=500, detail=hours["error"])
   return hours

@router.get("/projects/{project_id}/daily_tasks", response_model=List[Dict[str, Any]])
async def daily_tasks(project_id: str):
   tasks = await get_daily_tasks(project_id)
   if "error" in tasks:
       raise HTTPException(status_code=500, detail=tasks["error"])
   return tasks

@router.get("/projects/{project_id}/daily_tasks/{userName}", response_model=List[Dict[str, Any]])
async def daily_tasks(project_id: str, userName:str):
   tasks = await get_user_daily_tasks(project_id, userName)
   if "error" in tasks:
       raise HTTPException(status_code=500, detail=tasks["error"])
   return tasks

@router.get("/projects/{project_id}/team", response_model=Dict[str, Any])
async def project_team(project_id: str):
   # Returns all teams in a project
   team_info = get_teams(project_id)
   if "error" in team_info:
       raise HTTPException(status_code=500, detail=team_info["error"])
   return team_info

@router.get("/projects/{project_id}/members/{team_id}", response_model=Dict[str, Any])
async def team_members(project_id: str, team_id: str):
   # Returns all members of a team
   team_members = get_team_members(project_id, team_id)
   if "error" in team_members:
       raise HTTPException(status_code=500, detail=team_members["error"])
   return team_members

@router.get("/project_info/{project_id}/{repository_id}", response_model=Dict[str, Any])
async def project_info(project_id: str, repository_id: str):
   info = get_project_info(project_id, repository_id)
   if "error" in info:
       raise HTTPException(status_code=500, detail=info["error"])
   return info

## Data to test
'''
project_id = e4005fd0-7b95-4391-8486-c4b21c935b2e
team_id = 9083e8b0-af44-4f90-9bdd-f54f9bb431f2
'''