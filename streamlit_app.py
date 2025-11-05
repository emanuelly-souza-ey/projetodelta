# app.py
import logging
import os
import subprocess
import streamlit as st
from dotenv import load_dotenv
import requests
import sys
import os
from app.streamlit.streamlit_models import *

def start_streamlit():
    """Starts the Streamlit application."""
    try:
        logging.info("Starting Streamlit app...")

        # (one of the possible solutions)
        # Setting PYTHONPATH to the current working directory
        os.environ["PYTHONPATH"] = os.getcwd()

        subprocess.run(["streamlit", "run", "ui/streamlit_ui.py"], check=True)
    except subprocess.CalledProcessError as e:
        # Logging the specific error if the Streamlit command fails
        logging.error(f"Streamlit command failed with error: {e}")
    except Exception as e:
        # Logging any other errors that might occur
        logging.error(f"Error starting Streamlit app: {e}")


### WORKING EXAMPLES
def example_display_tasks(epic_id):
    project_id = "e4005fd0-7b95-4391-8486-c4b21c935b2e"
    url = f"http://localhost:8000/devops/projects/{project_id}/daily_tasks"

    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
        response.raise_for_status()
        daily_tasks = response.json()

        result = SlWorkItemQueryResult.from_json_list(daily_tasks)
        result.display_in_streamlit()

        
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados: {e}")

def example_display_projects_selection():
    url = f"http://localhost:8000/epic/projects/"
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
        response.raise_for_status()
        projects = response.json()

        result = SlProjectCollection(projects, EpicProject)
        result.display_in_streamlit(True)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados: {e}")

def example_display_team_members():
    project_id = "e4005fd0-7b95-4391-8486-c4b21c935b2e"
    team_id = "9083e8b0-af44-4f90-9bdd-f54f9bb431f2"
    url = f"http://localhost:8000/devops/projects/{project_id}/members/{team_id}"
    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
        response.raise_for_status()
        team_members = response.json()

        result = SlTeam(team_members.get("value"))
        result.display_in_streamlit()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao obter dados: {e}")

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


    load_dotenv()

    api_base = os.getenv("EYQ_INCUBATOR_ENDPOINT")
    api_key = os.getenv("EYQ_INCUBATOR_KEY")

    if not api_base or not api_key:
        st.error("As variáveis de ambiente devem ser definidas.")
        st.stop()

    if "history" not in st.session_state:
        st.session_state.history = []
    if "selected_project" not in st.session_state:
        st.session_state.selected_project = None
    if "selected_project_id" not in st.session_state:
        st.session_state.selected_project_id = None

    st.markdown("<h1 style='text-align: center;'>Atualiza AI</h1>", unsafe_allow_html=True)
    st.write("<h3>Bem-vindo ao Atualiza AI! Escolha um projeto que deseja obter mais informações e acompanhar o andamento.</h3>", unsafe_allow_html=True)
    st.write("")

    # EXEMPLOS
    #example_display_tasks()
    #example_display_team_members()
    

    if st.session_state.selected_project_id:
        st.write("<h3>Detalhes do Projeto Selecionado</h3>", unsafe_allow_html=True)
        example_display_tasks(st.session_state.selected_project_id)

    else:
        example_display_projects_selection()

#streamlit run streamlit_app.py