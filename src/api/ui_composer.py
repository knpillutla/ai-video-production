"""UI Template Composer for AI Video Producer Studio."""

from functools import lru_cache
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@lru_cache(maxsize=1)
def get_jinja_env() -> Environment:
    """Return cached Jinja2 environment configured for templates directory."""
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=False,
    )


def render_studio_html() -> str:
    """Render the master Studio UI HTML with all modular subcomponents."""
    env = get_jinja_env()
    template = env.get_template("index.html")
    return template.render()
