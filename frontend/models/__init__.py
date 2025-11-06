"""
Frontend models module for Streamlit-based UI components.

This module provides Streamlit-adapted wrappers for core business models,
enabling rich display and interaction within the Streamlit interface.
"""

from .streamlit_models import (
    SlProject,
    SlWebApiTeams,
    SlIdentityRef,
    SlWorkItem,
    SlWorkItemQueryResult,
    SlProjectCollection,
    SlTeam,
)

__all__ = [
    "SlProject",
    "SlWebApiTeams",
    "SlIdentityRef",
    "SlWorkItem",
    "SlWorkItemQueryResult",
    "SlProjectCollection",
    "SlTeam",
]
