"""
Models package for the backend application.

This module exports all model classes used across the application.
"""

# DevOps models
from .devops_models import (
    IdentityRef,
    WorkItem,
    WebApiTeam,
    TeamMember,
    WorkItemQueryResult,
)

# Project models
from .project_models import (
    Project,
    EpicProject,
)

__all__ = [
    # DevOps models
    "IdentityRef",
    "WorkItem",
    "WebApiTeam",
    "TeamMember",
    "WorkItemQueryResult",
    # Project models
    "Project",
    "EpicProject",
]
