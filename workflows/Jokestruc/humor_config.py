"""Load humor lever configuration used across the workflow."""

from pathlib import Path
from typing import Dict, List, TypedDict

import yaml  # or json

CONFIG_PATH = Path(__file__).parent / "config" / "humor_levers.yaml"


def load_humor_levers() -> List[Dict[str, str]]:
    """Load humor lever metadata from the configuration file."""
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


class HumorLeverDict(TypedDict):
    name: str
    description: str
    example: str
