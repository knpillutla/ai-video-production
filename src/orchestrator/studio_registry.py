"""Pluggable Studio Agent Registry."""

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger


class StudioAgentDefinition(BaseModel):
    """Metadata and execution interface for a registered studio agent."""
    studio_id: str
    display_name: str
    description: str
    default_fps: int = 24
    supported_aspect_ratios: List[str] = Field(default_factory=lambda: ["16:9", "9:16"])
    genre: str = "general"
    handler_module: str
    handler_func_name: str


class StudioRegistry:
    """Central registry mapping studio identifiers to autonomous studio handlers."""

    def __init__(self):
        self._studios: Dict[str, StudioAgentDefinition] = {}
        self._handlers: Dict[str, Callable] = {}

    def register_studio(
        self,
        studio_id: str,
        display_name: str,
        description: str,
        default_fps: int,
        genre: str,
        handler: Callable,
        supported_aspect_ratios: Optional[List[str]] = None,
    ) -> None:
        """Register an autonomous studio agent."""
        defn = StudioAgentDefinition(
            studio_id=studio_id,
            display_name=display_name,
            description=description,
            default_fps=default_fps,
            genre=genre,
            supported_aspect_ratios=supported_aspect_ratios or ["16:9", "9:16"],
            handler_module=handler.__module__,
            handler_func_name=handler.__name__,
        )
        self._studios[studio_id] = defn
        self._handlers[studio_id] = handler
        logger.info(f"studio_registered: id={studio_id} name='{display_name}'")

    def get_studio(self, studio_id: str) -> Optional[StudioAgentDefinition]:
        """Get studio definition by ID."""
        return self._studios.get(studio_id)

    def get_handler(self, studio_id: str) -> Optional[Callable]:
        """Get the execution handler function for a studio."""
        return self._handlers.get(studio_id)

    def list_studios(self) -> List[StudioAgentDefinition]:
        """List all active registered studio agents."""
        return list(self._studios.values())


studio_registry = StudioRegistry()
