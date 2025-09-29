# CrewAI Studio Architecture Overview

This document summarises the most relevant modules in the Streamlit
application. Use it together with the in-line docstrings for a quick
orientation when making changes.

## High-level layout

```
app/
├── __init__.py        # Package metadata (application version)
├── app.py             # Streamlit entry point
├── core/              # Cross-cutting helpers (configuration, database)
├── db_utils.py        # Persistence helpers
├── llms.py            # Model configuration helpers
├── my_*.py            # Streamlit models (agents, crews, tasks, tools)
└── pg_*.py            # Streamlit pages
```

Supporting scripts (Docker, virtual environment helpers, etc.) live in the
repository root. Static assets such as images are under `img/`.

## Core helpers

- **`app/core/config.py`** – Centralises the loading of environment-based
  settings and exposes a cached `load_settings()` helper. This ensures all
  modules observe the same configuration without duplicating logic.
- **`app/core/database.py`** – Builds the shared SQLAlchemy engine based on
  the configuration. Provides convenience helpers to obtain a connection or
  iterate over result rows in a SQLAlchemy-version agnostic way.

## Persistence utilities

- **`app/db_utils.py`** – Offers a light-weight repository layer for agents,
  tasks, crews, tools, knowledge sources and results. The new
  `load_all_entities()` helper loads related entities in the correct order so
  that Streamlit session state can be populated without redundant queries.

## Streamlit entry point

`app/app.py` wires everything together: configuration loading, optional
AgentOps initialisation, database bootstrap and navigation across Streamlit
pages. The page objects are instantiated once and cached, removing redundant
work in each rerun triggered by Streamlit.

## Adding new components

1. Add the new entity implementation (e.g. `my_newthing.py`) and expose it
   via the relevant page under `pg_*.py`.
2. Extend `db_utils.py` with persistence helpers, ideally following the
   existing patterns for serialisation.
3. Register the page or component in `app/app.py` if it needs to be reachable
   from the navigation sidebar.
4. Update this document when structural changes are introduced.
