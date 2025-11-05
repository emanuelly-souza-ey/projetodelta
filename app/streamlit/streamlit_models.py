
from app.core.devops_models import *
from app.core.project_model import Project, EpicProject
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from app.core.utils import filter_dataframe

#For the interface
import streamlit as st

class SlProject():
    def __init__(self, project, project_class=Project):
        if not issubclass(project_class, (Project, EpicProject)):
            raise ValueError("The project must be an instance of Project or EpicProject.")
        
        self.project_class=project_class
        self.project = project_class(**project)#Just in this class to make it compatible with all kind of projects

    def __str__(self):
        return f"SlProject({self.__dict__})"

    def display_in_streamlit(self, selection = False):
        with st.container(border=True):

            # Título do projeto
            st.subheader(self.project.name or "Nome do Projeto Desconhecido")

            # Mostrar a imagem da equipe, se disponível
            if self.project.defaultTeamImageUrl:
                st.image(self.project.defaultTeamImageUrl, caption="Imagem da Equipe", use_container_width =True)

            # Exibir informações do projeto de forma formatada
            st.write(f"**ID:** {self.project.id}")
            # Mostrar a descrição do projeto, interpretando o HTML
            if self.project.description:
                st.markdown("<b>Descrição:</b>", unsafe_allow_html=True)
                max_length = 300  # Número máximo de caracteres a mostrar inicialmente
                if len(self.project.description) > max_length:
                    k=0
                    words = self.project.description.split()
                    short_description = ""
                    for word in words:
                        k += 1
                        if len(short_description) + len(word) + 1 > max_length:
                            break
                        short_description += word + " "
                    short_description = short_description.strip() + "..."
                    
                    # Mostrar descripción completa o breve según el estado
                    if f"show_full_description_{self.project.id}" not in st.session_state:
                        st.session_state[f"show_full_description_{self.project.id}"] = False

                    if st.session_state[f"show_full_description_{self.project.id}"]:
                        st.markdown(self.project.description, unsafe_allow_html=True)
                        if st.button("Leer menos", key=f"read_less_{self.project.id}"):
                            st.session_state[f"show_full_description_{self.project.id}"] = False
                    else:
                        st.markdown(short_description, unsafe_allow_html=True)
                        if st.button("Leer mais", key=f"read_more_{self.project.id}"):
                            st.session_state[f"show_full_description_{self.project.id}"] = True

                else:
                    st.markdown(self.project.description, unsafe_allow_html=True)
            else:
                st.write("**Descrição:** Não disponível")


            st.write(f"**Estado:** {self.project.state or 'Não disponível'}")
            if self.project.lastUpdateTime:
                formatted_date_time = pd.to_datetime(self.project.lastUpdateTime).strftime("%d/%m/%Y %H:%M:%S")
                st.write(f"**Última Atualização:** {formatted_date_time}")
            else:
                st.write(f"**Última Atualização:** Não disponível")
            #st.write(f"**Visibilidade:** {self.project.visibility or 'Não disponível'}")
            #st.write(f"**Abreviatura:** {self.project.abbreviation or 'Não disponível'}")
            #st.write(f"**URL do Projeto:** [Link]({self.project.url})" if self.project.url else "URL não disponível")
            #st.write(f"**Website:** [Link]({self.project.web})" if self.project.web else "Website não disponível")

            if selection:
                if st.button("Selecionar Projeto", key=self.project.id):
                    st.session_state.selected_project = self.project
                    st.session_state.selected_project_id = self.project.id
                    st.success(f"Você escolheu o projeto: {self.project.name}.")

class SlWebApiTeams(WebApiTeam):
    """A class to represent a Web API team in Streamlit.

    Args:
        WebApiTeam (WebApiTeam): The base class for Web API teams.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"SlWebApiTeams({self.__dict__})"

    def display_in_streamlit(self):
        """
        Display the WebApiTeam details in a Streamlit app with a clean and elegant layout.
        """
        st.markdown(f"### Team ID: {self.id}")
        st.markdown(f"**Name:** {self.name}")
        st.markdown(f"**URL:** [Link to Team]({self.url})")
        st.markdown("---")

class SlIdentityRef(IdentityRef):
    """A class to represent an identity reference in Streamlit.

    Args:
        IdentityRef (IdentityRef): The base class for identity references.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"SlIdentityRef({self.__dict__})"

    def display_in_streamlit(self):
        """
        Display the IdentityRef details in a Streamlit app with a clean and elegant layout.
        """
        cols = st.columns([1, 4, 1])  # Adjust column proportions as needed
        with cols[0]:
            if self.imageUrl:
                st.image(self.imageUrl, use_container_width=True)
        with cols[1]:
            st.markdown(f"{self.displayName} {self.uniqueName or 'Not Available'}")
            
class SlWorkItem(WorkItem):
    """A class to represent a work item in Streamlit.

    Args:
        WorkItem (WorkItem): The base class for work items.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"SlWorkItem({self.__dict__})"

    def display_in_streamlit(self):
        """
        Display the WorkItem details in a Streamlit app with a clean and elegant layout.
        """
        st.markdown(f"### Work Item ID: {self.id}")
        st.markdown(f"**Title:** {self.title}")
        st.markdown(f"**State:** {self.state}")
        st.markdown(f"**Completed Hours:** {self.completedHours}")
        st.markdown(f"**URL:** [Link to Work Item]({self.url})")
        st.markdown("---")

class SlWorkItemQueryResult(WorkItemQueryResult):
    """A class to represent a work item query result in Streamlit.

    Args:
        WorkItemQueryResult (WorkItemQueryResult): The base class for work item query results.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"SlWorkItemQueryResult({self.__dict__})"
    
    def display_in_streamlit(self):
        """
        Display the WorkItemQueryResult in a Streamlit app with a clean and elegant layout.
        """
        st.markdown(f"### Total Work Items: {len(self.workItems)}")
        df = self.to_dataframe()
        
        if "assignedTo" in df.columns:
            df["assigned_to"] = df["assignedTo"].apply(lambda x: x.get("displayName") if isinstance(x, dict) else None)
            df["assignedTo_email"] = df["assignedTo"].apply(lambda x: x.get("uniqueName") if isinstance(x, dict) else None)

        columns_to_drop = {"commentVersionRef", "fields", "relations", "assignedTo","organization"}

        if "project" in df.columns:
            if df["project"].nunique() <= 1 or df["project"].isnull().all():
                columns_to_drop.add("project")

        df = df.drop(columns=columns_to_drop.intersection(df.columns))


        st.dataframe(filter_dataframe(df))

class SlProjectCollection:
    def __init__(self, projects, project_class):
        """
        Initializes the SlProjectCollection with a list of projects.

        :param projects: List of projects (either dictionaries or SlProject instances).
        :param project_class: The class to use for creating project instances (Project or EpicProject).
        """
        if not issubclass(project_class, (Project, EpicProject)):
            raise ValueError("project_class must be a subclass of Project or EpicProject.")

        if all(isinstance(project, dict) for project in projects):
            self.projects = [SlProject(project, project_class) for project in projects]
        elif all(isinstance(project, SlProject) for project in projects):
            self.projects = projects
        else:
            raise ValueError("Projects must be a list of dictionaries or a list of instances of the specified project class.")

    def display_in_streamlit(self, selection=False):
        """
        Display the list of projects in a Streamlit app with a clean and elegant layout.
        """
        st.markdown("### Lista de Projetos")

        # Add tabs for different views
        tab1, tab2 = st.tabs(["Card view", "Table view"])

        with tab1:
            # Add a search bar for filtering projects
            search_query = st.text_input("Buscar projectos", "")
            filtered_projects = [
                project for project in self.projects
                if search_query.lower() in (project.project.name or "").lower()
            ]

            # Display filtered projects in a responsive grid layout
            cols = st.columns(2)  # Adjust the number of columns as needed
            for idx, project in enumerate(filtered_projects):
                with cols[idx % len(cols)]:
                    project.display_in_streamlit(selection)

        with tab2:
            # Convert projects to a DataFrame for table view
            project_data = [
                {
                    "ID": project.project.id,
                    "Name": project.project.name,
                    "Status": project.project.state,
                    "LastUpdate": project.project.lastUpdateTime,
                }
                for project in self.projects
            ]
            df = pd.DataFrame(project_data)
            st.dataframe(filter_dataframe(df))

class SlTeam():
    def __init__(self, identities):
        if all(isinstance(identity, SlIdentityRef) for identity in identities):
            self.identities = identities
        elif all(isinstance(identity, dict) for identity in identities):
            self.identities = [
                SlIdentityRef.from_json(identity["identity"])
                if "identity" in identity
                else SlIdentityRef.from_json(identity)
                for identity in identities
            ]
        else:
            raise ValueError("Identities must be a list of dictionaries or a list of SlIdentityRef instances.")

    def display_in_streamlit(self):
        """
        Display the list of identities in a Streamlit app with a clean and elegant layout.
        """
        st.markdown("### Team Members")

        # Display identities in a responsive grid layout
        cols = st.columns(2)  # Adjust the number of columns as needed
        for idx, identity in enumerate(self.identities):
            with cols[idx % len(cols)]:
                identity.display_in_streamlit()