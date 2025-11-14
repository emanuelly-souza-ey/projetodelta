#devops_model
#app/core/devops_models.py
import requests
import pandas as pd


import os
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

from backend.config.azure import get_azure_config
config = get_azure_config()

#Team member
class IdentityRef(BaseModel):
    _links: Optional[Any] = None
    descriptor: Optional[str] = None
    directoryAlias: Optional[str] = None
    displayName: Optional[str] = None
    id: Optional[str] = None
    imageUrl: Optional[str] = None
    inactive: Optional[bool] = None
    isAadIdentity: Optional[bool] = None
    isContainer: Optional[bool] = None
    isDeletedInOrigin: Optional[bool] = None
    profileUrl: Optional[str] = None
    uniqueName: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "displayName": self.displayName,
            "imageUrl": self.imageUrl,
        }

    def __repr__(self):
        return (
            #f"IdentityRef(_links={self._links}, descriptor={self.descriptor}, directoryAlias={self.directoryAlias}, "
            f"displayName={self.displayName}, id={self.id}, imageUrl={self.imageUrl}, inactive={self.inactive}, "
            #f"isAadIdentity={self.isAadIdentity}, isContainer={self.isContainer}, isDeletedInOrigin={self.isDeletedInOrigin}, "
            f"profileUrl={self.profileUrl}, uniqueName={self.uniqueName}, url={self.url})"
        )

    @classmethod
    def from_json(cls, json_data):
        if json_data is None:
            return cls(
                _links=None,
                descriptor="",
                directoryAlias="",
                displayName="",
                id="",
                imageUrl="",
                inactive=False,
                isAadIdentity=False,
                isContainer=False,
                isDeletedInOrigin=False,
                profileUrl="",
                uniqueName="",
                url=""
            )
        return cls(
            _links=json_data.get("_links", None),
            descriptor=json_data.get("descriptor", ""),
            directoryAlias=json_data.get("directoryAlias", ""),
            displayName=json_data.get("displayName", ""),
            id=json_data.get("id", ""),
            imageUrl=json_data.get("imageUrl", ""),
            inactive=json_data.get("inactive", False),
            isAadIdentity=json_data.get("isAadIdentity", False),
            isContainer=json_data.get("isContainer", False),
            isDeletedInOrigin=json_data.get("isDeletedInOrigin", False),
            profileUrl=json_data.get("profileUrl", ""),
            uniqueName=json_data.get("uniqueName", ""),
            url=json_data.get("url", ""),
        )

class WorkItem(BaseModel):
    _links: Optional[Any] = None

    title: Optional[str] = None
    id: Optional[int] = None
    state: Optional[str] = None
    assignedTo: Optional[IdentityRef] = None
    target_date: Optional[datetime] = None
    lastUpdateTime: Optional[datetime] = None
    fields: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

    commentVersionRef: Optional[Any] = None
    relations: Optional[List[Any]] = None
    rev: Optional[int] = None
    url: Optional[str] = None
    organization: Optional[str] = None
    project: Optional[str] = None
    completedHours: Optional[float] = None

    childs: Optional[List[Any]] = Field(default_factory=list)
    parentId: Optional[int] = None
    
    # New fields
    value_area: Optional[str] = None
    tags: Optional[str] = None
    estimated_hours: Optional[float] = None
    full_hours: Optional[float] = None
    area_name: Optional[str] = None
    client_face: Optional[str] = None
    product_owner: Optional[str] = None

    @classmethod
    def create_with_defaults(cls, id: int, organization: Optional[str] = None, project: Optional[str] = None):
        """
        Create a WorkItem instance with default values for unspecified fields.
        """
        return cls(
            id=id,
            organization=organization,
            project=project,
            title=None,
            state=None,
            assignedTo=None,
            target_date=None,
            lastUpdateTime=None,
            fields=None,
            description=None,
            commentVersionRef=None,
            relations=None,
            rev=None,
            url=None,
            completedHours=None,
            childs=[],
            parentId=None,
        )

    @classmethod
    def getFieldsForEpicProject(self):
        return ["System.Title",
                "System.Description",
                "System.ChangedDate",
                "System.State",
                "Microsoft.VSTS.Scheduling.TargetDate"]
    
    def getInfo(self, levels:int, headers, azure_path="https://dev.azure.com/FSO-DnA-Devops", azure_project_id=config.devops_project_id):
        #The only thing that needs is id to query all
        print(f"va a obtener info de {self.id}")
        base_url = f"{azure_path}/{azure_project_id}/_apis/wit/workItems/{self.id}?api-version=7.0"
        if levels>0: base_url += f"&$expand=relations"

        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        if response.status_code == 200:
            data = response.json()
            '''
            #lo haremos fuera
            fields = data.get("fields", {})
            print("los items que mandare para parsear",fields)
            if not self.title:
                self.parseFields(fields)
            '''
            if data.get("relations"):
                print("va a ir por las relaciones")
                for relation in data["relations"]:
                    if relation.get("rel") == "System.LinkTypes.Hierarchy-Forward":
                        child_id = relation["url"].split("/")[-1]
                        child_work_item = WorkItem.create_with_defaults(child_id, self.organization, self.project)
                        child_work_item.getInfo(levels-1, headers, azure_path, azure_project_id)
                        self.childs.append(child_work_item)

                    elif relation.get("rel") == "System.LinkTypes.Hierarchy-Reverse":
                        parent_id = relation["url"].split("/")[-1]
                        self.parentId = parent_id

    def __init__(self, **data):
        super().__init__(**data)
        fields = data.get("fields", {})
        if fields!=None and fields != {}:
            self.parseFields(fields)

    def parseFields(self, fields):
        #print("parsing fields", fields)
        self.completedHours = fields.get("Microsoft.VSTS.Scheduling.CompletedWork", None)
        self.title = fields.get("System.Title", None)
        self.state = fields.get("System.State", None)
        self.assignedTo = IdentityRef.from_json(fields.get("System.AssignedTo", {})) if fields.get("System.AssignedTo") else None
        target_date_str = fields.get("Microsoft.VSTS.Scheduling.TargetDate", None)
        if target_date_str:
            try:
                self.target_date = datetime.strptime(target_date_str, "%Y-%m-%dT%H:%M:%S.%fZ") if '.' in target_date_str else datetime.strptime(target_date_str, "%Y-%m-%dT%H:%M:%SZ")
                self.target_date = datetime.strptime(target_date_str, "%Y-%m-%dT%H:%M:%S.%fZ") if '.' in target_date_str else datetime.strptime(target_date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                self.target_date = None
        else:
            self.target_date = None
        
        # New fields mapping
        self.value_area = fields.get("Microsoft.VSTS.Common.ValueArea", None)
        self.tags = fields.get("System.Tags", None)
        self.estimated_hours = fields.get("Custom.EstimatedHours", None)
        self.full_hours = fields.get("Custom.FullHours", None)
        self.area_name = fields.get("Custom.AreaName", None)
        self.client_face = fields.get("Custom.ClientFace", None)
        self.product_owner = fields.get("Custom.ProductOwner", None)

    def getDetails(self, headers):
        #Not using in this field
        response = requests.get(self.url, headers=headers)
        fields = response.json().get("fields")
        self.parseFields(fields)

    def __repr__(self):
        return (
            f"WorkItem(id={self.id}, url={self.url}, title={self.title}, state={self.state}, completedHours={self.completedHours})"
        )

    @classmethod
    def from_json(cls, json_data):
        return cls(
            _links=json_data.get("_links"),
            commentVersionRef=json_data.get("commentVersionRef"),
            fields=json_data.get("fields"),
            id=json_data.get("id"),
            relations=json_data.get("relations"),
            rev=json_data.get("rev"),
            url=json_data.get("url"),
        )
    

        
class WebApiTeam(BaseModel):
    '''
    ALL TEAMS 
    GET https://dev.azure.com/{organization}/_apis/teams?api-version=7.2-preview.3
    MY TEAMS
    GET https://dev.azure.com/{organization}/_apis/teams?api-version=7.2-preview.3

    '''
    description: Optional[str] = None
    id: Optional[str] = None
    identity: Optional[Any] = None
    identityUrl: Optional[str] = None
    name: Optional[str] = None
    projectId: Optional[str] = None
    projectName: Optional[str] = None
    url: Optional[str] = None

    def __repr__(self):
        return (
            f"WebApiTeam(description={self.description}, id={self.id}, identity={self.identity}, "
            f"identityUrl={self.identityUrl}, name={self.name}, projectId={self.projectId}, "
            f"projectName={self.projectName}, url={self.url})"
        )

    @classmethod
    def from_json(cls, json_data):
        return cls(
            description=json_data.get("description"),
            id=json_data.get("id"),
            identity=json_data.get("identity"),
            identityUrl=json_data.get("identityUrl"),
            name=json_data.get("name"),
            projectId=json_data.get("projectId"),
            projectName=json_data.get("projectName"),
            url=json_data.get("url"),
        )
    


class TeamMember(BaseModel):
    identity: Optional[IdentityRef]
    isTeamAdmin: Optional[bool]

    def to_dict(self):
        return {
            "isTeamAdmin": self.isTeamAdmin == True,
            "id": self.identity.id if self.identity else None,
            "displayName": self.identity.displayName if self.identity else None,
            "imageUrl": self.identity.imageUrl if self.identity else None,
        }

    def __repr__(self):
        return f"TeamMember(identity={self.identity}, isTeamAdmin={self.isTeamAdmin})"

    @classmethod
    def from_json(cls, json_data):
        return cls(
            identity=IdentityRef.from_json(json_data.get("identity")),
            isTeamAdmin=json_data.get("isTeamAdmin"),
        )
    
    def to_dict(self):
        return {
            "isTeamAdmin": self.isTeamAdmin == True,
            "id": self.identity.id,
            "displayName": self.identity.displayName,
            "imageUrl": self.identity.imageUrl,
        }


#st.dataframe(filter_dataframe(df))
class WorkItemQueryResult(BaseModel):
    workItems: List[WorkItem]
    def to_dataframe(self, column_order: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Store the work items as a pandas DataFrame with an optional column order.

        Args:
            column_order (Optional[List[str]]): List of column names in the desired order.

        Returns:
            pd.DataFrame: A DataFrame containing the work items.
        """
        if not column_order:
            column_order = [
                "title",#
                "id",#
                "state",#
                "completedHours",#
                "assignedTo",#
                "target_date",#
                "url"#
            ]
            #Falta rev
        df = pd.DataFrame([item.model_dump() for item in self.workItems])
        if column_order:
            df = df[[col for col in column_order if col in df.columns]]
        return df
    
    @classmethod
    def from_json_list(cls, json_list):
        """
        Create a WorkItemQueryResult instance from a list of JSON objects.
        """
        work_items = [WorkItem.from_json(item) for item in json_list]
        return cls(workItems=work_items)

    @classmethod
    def from_json(cls, json_data):
        return cls(
            workItems=[WorkItem.from_json(item) for item in json_data.get("workItems", [])],
        )

    def __repr__(self):
        return f"WorkItemQueryResult(count={len(self.workItems)}, workItems={self.workItems})"
    
