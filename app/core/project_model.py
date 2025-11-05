#project_model
import requests

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
import pandas as pd

from app.core.devops_models import WorkItem, IdentityRef
    
class Project(BaseModel):
    #Tambien es un WorkItem pero es un epic 
    abbreviation: Optional[str]
    defaultTeamImageUrl: Optional[str]
    description: Optional[str]
    id: Optional[str]
    lastUpdateTime: Optional[datetime]
    name: Optional[str]
    revision: Optional[int]
    state: Optional[str]
    url: Optional[str]
    web: Optional[str]
    visibility: Optional[str]


    def __repr__(self):
        return (
            f"Project(abbreviation={self.abbreviation}, defaultTeamImageUrl={self.defaultTeamImageUrl}, "
            f"description={self.description}, id={self.id}, lastUpdateTime={self.lastUpdateTime}, "
            f"name={self.name}, revision={self.revision}, state={self.state}, url={self.url}, "
            f"visibility={self.visibility})"
        )

    @classmethod
    def from_json(cls, json_data):
        lastUpdateTime = json_data.get("lastUpdateTime")
        try:
            lastUpdateTime = datetime.strptime(lastUpdateTime, "%Y-%m-%dT%H:%M:%S.%fZ") if '.' in lastUpdateTime else datetime.strptime(lastUpdateTime, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            lastUpdateTime = None
        else:
            lastUpdateTime = None

        return cls(
            abbreviation=json_data.get("abbreviation"),
            defaultTeamImageUrl=json_data.get("defaultTeamImageUrl"),
            description=json_data.get("description"),
            id=json_data.get("id"),
            lastUpdateTime=json_data.get("lastUpdateTime"),
            name=json_data.get("name"),
            revision=json_data.get("revision"),
            state=json_data.get("state"),
            url=json_data.get("url"),
            visibility=json_data.get("visibility"),
            web=json_data.get("web"),
        )
    
#The projects in Azure DevOps are respresented as workitems of type Epic
#This class tries to represent this particularity
#also takes care of requests to the Azure DevOps API
class EpicProject(Project):
    # These additional attributes are not needed in the parent because this information can be obtained directly from the api
    root: Optional[WorkItem] = Field(default_factory=WorkItem)#Saves the workitem root of the project
    
    # It heavely relies in python language and allocation of memory
    # if needed in another programming language create the elements and referenciate them trough pointers
    tasks: Optional[List[WorkItem]] = Field(default_factory=list)#All tasks descendants of the root workitem
    teamMembers: Optional[Dict[str,IdentityRef]] = Field(default_factory=list)#All team members of the project

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @classmethod
    def project_from_workitem(cls, json_data):
        fields = json_data.get("fields", {})
        return cls(
            abbreviation=json_data.get("abbreviation",""),
            defaultTeamImageUrl=json_data.get("defaultTeamImageUrl",""),

            id=str(json_data.get("id")) if json_data.get("id") else None,
            name=fields.get("System.Title"),
            description=fields.get("System.Description"),
            lastUpdateTime=datetime.strptime(fields.get("System.ChangedDate"), "%Y-%m-%dT%H:%M:%S.%fZ") if fields.get("System.ChangedDate") and '.' in fields.get("System.ChangedDate") else datetime.strptime(fields.get("System.ChangedDate"), "%Y-%m-%dT%H:%M:%SZ") if fields.get("System.ChangedDate") else None,
            state=fields.get("System.State"),
            revision=json_data.get("rev"),
            url=json_data.get("url"),

            visibility=json_data.get("visibility"),
            web=json_data.get("web"),
            childs=[],
            root=None,
            teamMembers={}
        )
    
    def getTasks(self, headers, azure_path="https://dev.azure.com/FSO-DnA-Devops", azure_project_id="e4005fd0-7b95-4391-8486-c4b21c935b2e"):
        print("Va a obtener las tareas")
        if len(self.tasks) > 0:#si ya se obtuvieron las tareas
            return self.tasks
        
        if not self.root or not len(self.root.childs):#si no fue por los niveles
            self.getRelationships(headers=headers,azure_path=azure_path,azure_project_id=azure_project_id)
        self.tasks = []

        #Recorre el arbol hasta las hojas
        def dfs(node):
            if node.childs:
                for child in node.childs:
                    dfs(child)
            else:
                self.tasks.append(node)#Don,t know if i´ll work
        
        dfs(self.root)
        return self.tasks
    
    def getTeamMembers(self, headers, azure_path="https://dev.azure.com/FSO-DnA-Devops", azure_project_id="e4005fd0-7b95-4391-8486-c4b21c935b2e"):
        if len(self.teamMembers) > 0:
            return self.teamMembers
        
        if not self.root or not len(self.root.childs):#si no fue por los niveles
            self.getRelationships(headers=headers,azure_path=azure_path,azure_project_id=azure_project_id)

        def dfs(node):
            if node.childs:
                for child in node.childs:
                    dfs(child)
            else:
                member = node.assignedTo
                self.teamMember[member.id] = member

        dfs(self.root)
        return List[self.teamMembers]

    def getRelationships(self, headers, azure_path="https://dev.azure.com/FSO-DnA-Devops", azure_project_id="e4005fd0-7b95-4391-8486-c4b21c935b2e"):
        print("viendo relaciones")
        if not self.root:
            print("Esta creando el root")
            url = f"{azure_path}/{azure_project_id}/_apis/wit/workitems/{self.id}"
            response = requests.get(url, headers=headers)
        
            if response.status_code == 200:
                self.root = WorkItem.from_json(response.json())
                self.root.id = self.id

        if not(self.root.childs):
            #Obtiene sus hijos y sus descendientes
            #there are no more than 5 levels but just in case
            print("empezo obteniendo info")
            self.root.getInfo(5,headers=headers,azure_path=azure_path,azure_project_id=azure_project_id)

    @classmethod
    def get_from_request(cls, project_id: str, headers, azure_path="https://dev.azure.com/FSO-DnA-Devops", azure_project_id="e4005fd0-7b95-4391-8486-c4b21c935b2e"):
        print("get from request")
        url = f"{azure_path}/{azure_project_id}/_apis/wit/workitems/{project_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            json_data = response.json()
            project = cls.project_from_workitem(json_data)
            project.root = WorkItem.from_json(json_data)
            print("Ya armo el root")
            return project
        else:
            raise ValueError(f"Error fetching project data: {response.status_code} - {response.text}")