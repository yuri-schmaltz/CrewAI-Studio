"""Configuration utilities centralising environment management."""

from dataclasses import dataclass
from functools import lru_cache
import os
from typing import Optional

DEFAULT_SQLITE_URL = "sqlite:///crewai.db"


@dataclass(frozen=True)
class AgentOpsSettings:
    """Configuration relevant to the optional AgentOps integration."""

    enabled: bool
    api_key: Optional[str]

    @property
    def is_enabled(self) -> bool:
        """Return ``True`` when AgentOps should be initialised."""

        return self.enabled and bool(self.api_key)


@dataclass(frozen=True)
class DatabaseSettings:
    """Database connection options."""

    url: str
    echo: bool = False


@dataclass(frozen=True)
class AppSettings:
    """Aggregate configuration for the application."""

    database: DatabaseSettings
    agentops: AgentOpsSettings


@lru_cache(maxsize=1)
def load_settings() -> AppSettings:
    """Load application settings from the environment."""

    db_url = os.getenv("DB_URL", DEFAULT_SQLITE_URL)
    db_echo = os.getenv("DATABASE_ECHO", "false").lower() in {"1", "true", "yes"}

    agentops_enabled = os.getenv("AGENTOPS_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    return AppSettings(
        database=DatabaseSettings(url=db_url, echo=db_echo),
        agentops=AgentOpsSettings(
            enabled=agentops_enabled,
            api_key=os.getenv("AGENTOPS_API_KEY"),
        ),
    )
