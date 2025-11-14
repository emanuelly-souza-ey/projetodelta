"""
Team endpoint for retrieving project team members.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from backend.intents.project_team.service import ProjectTeamService
from backend.intents.project_team.models import ProjectTeamQuery, TeamMember


router = APIRouter()


class TeamMembersResponse(BaseModel):
    """Response model for team members endpoint."""
    members: List[TeamMember] = Field(..., description="List of team members")
    total_count: int = Field(..., description="Total number of team members")
    message: str = Field(..., description="Descriptive message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID used for context")


@router.get("/members", response_model=TeamMembersResponse)
async def get_team_members(
    conversation_id: Optional[str] = Query(None, description="Conversation ID to use project context from session")
):
    """
    Get team members from the project.
    
    This endpoint retrieves team members by querying tasks from Azure DevOps.
    If a conversation_id is provided, it will use the project context from that session.
    
    Args:
        conversation_id: Optional conversation ID to retrieve project context
        
    Returns:
        TeamMembersResponse with list of team members
        
    Raises:
        HTTPException: If the query fails
    """
    try:
        # Use conversation_id as session_id, or default to "anonymous"
        session_id = conversation_id or "anonymous"
        
        # Create service instance
        team_service = ProjectTeamService(session_id=session_id)
        
        # Create query parameters (all optional, will use session context)
        query_params = ProjectTeamQuery()
        
        # Execute query
        result = await team_service.query_data(query_params)
        
        return TeamMembersResponse(
            members=result.members,
            total_count=result.total_count,
            message=result.message or "Team members retrieved successfully",
            conversation_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving team members: {str(e)}"
        )


@router.get("/members/summary")
async def get_team_summary(
    conversation_id: Optional[str] = Query(None, description="Conversation ID to use project context from session")
):
    """
    Get a summary of the team composition.
    
    Returns basic statistics about the team members.
    
    Args:
        conversation_id: Optional conversation ID to retrieve project context
        
    Returns:
        Dict with team summary statistics
    """
    try:
        session_id = conversation_id or "anonymous"
        team_service = ProjectTeamService(session_id=session_id)
        query_params = ProjectTeamQuery()
        result = await team_service.query_data(query_params)
        
        # Calculate summary statistics
        members_with_email = sum(1 for m in result.members if m.email)
        members_with_role = sum(1 for m in result.members if m.role)
        
        return {
            "total_members": result.total_count,
            "members_with_email": members_with_email,
            "members_with_role": members_with_role,
            "member_names": [m.name for m in result.members],
            "message": result.message
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving team summary: {str(e)}"
        )
