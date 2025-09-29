"""Entry point for the Streamlit based CrewAI Studio application."""

from functools import lru_cache
from typing import Dict, Protocol

from dotenv import load_dotenv
import streamlit as st
from streamlit import session_state as ss

import db_utils
from core.config import load_settings
from llms import load_secrets_fron_env
from pg_agents import PageAgents
from pg_crews import PageCrews
from pg_export_crew import PageExportCrew
from pg_crew_run import PageCrewRun
from pg_knowledge import PageKnowledge
from pg_results import PageResults
from pg_tasks import PageTasks
from pg_tools import PageTools


class Page(Protocol):
    """Protocol describing the expected page interface."""

    def draw(self) -> None:
        """Render the page contents."""


@lru_cache(maxsize=1)
def pages() -> Dict[str, Page]:
    """Build and cache the Streamlit pages used by the application."""

    return {
        "Crews": PageCrews(),
        "Tools": PageTools(),
        "Agents": PageAgents(),
        "Tasks": PageTasks(),
        "Knowledge": PageKnowledge(),
        "Kickoff!": PageCrewRun(),
        "Results": PageResults(),
        "Import/export": PageExportCrew(),
    }


def load_data() -> None:
    """Populate the Streamlit session state with persisted entities."""

    loaded = db_utils.load_all_entities()
    ss.agents = loaded.agents
    ss.tasks = loaded.tasks
    ss.crews = loaded.crews
    ss.tools = loaded.tools
    ss.enabled_tools = db_utils.load_tools_state()
    ss.knowledge_sources = loaded.knowledge_sources


def draw_sidebar() -> None:
    """Render the navigation sidebar and handle page changes."""

    with st.sidebar:
        st.image("img/crewai_logo.png")

        if "page" not in ss:
            ss.page = "Crews"

        labels = list(pages().keys())
        selected_page = st.radio(
            "Page",
            labels,
            index=labels.index(ss.page),
            label_visibility="collapsed",
        )
        if selected_page != ss.page:
            ss.page = selected_page
            st.rerun()


def configure_environment() -> None:
    """Load environment settings and initialise optional integrations."""

    load_dotenv()
    load_secrets_fron_env()
    settings = load_settings()

    if settings.agentops.is_enabled and not ss.get("agentops_failed", False):
        try:
            import agentops

            agentops.init(
                api_key=settings.agentops.api_key,
                auto_start_session=False,
            )
        except ModuleNotFoundError as exc:
            ss.agentops_failed = True
            print(f"Error initializing AgentOps: {exc}")


def main() -> None:
    """Application entry point invoked by Streamlit."""

    st.set_page_config(
        page_title="CrewAI Studio", page_icon="img/favicon.ico", layout="wide"
    )
    configure_environment()
    db_utils.initialize_db()
    load_data()
    draw_sidebar()

    # Persist the session state for the crew run page so crew run can execute in a
    # separate thread.
    PageCrewRun.maintain_session_state()

    pages()[ss.page].draw()


if __name__ == "__main__":
    main()
