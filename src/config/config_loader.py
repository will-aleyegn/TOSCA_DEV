# -*- coding: utf-8 -*-
"""
Configuration loader for TOSCA Laser Control System.

Provides singleton pattern for global config access.
"""

import logging
from pathlib import Path
from typing import Optional

import yaml  # type: ignore[import-untyped]

from .models import TOSCAConfig

logger = logging.getLogger(__name__)

_config_instance: Optional[TOSCAConfig] = None


def load_config_from_yaml(config_path: Path) -> TOSCAConfig:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config.yaml file

    Returns:
        Validated TOSCAConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config validation fails
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)

    return TOSCAConfig(**config_dict)


def get_config(config_path: Optional[Path] = None, reload: bool = False) -> TOSCAConfig:
    """
    Get global configuration instance (singleton pattern).

    Args:
        config_path: Path to config file (only used on first call or if reload=True)
        reload: Force reload from file

    Returns:
        TOSCAConfig instance
    """
    global _config_instance

    if _config_instance is None or reload:
        if config_path is None:
            # Default to config.yaml in project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.yaml"

        try:
            _config_instance = load_config_from_yaml(config_path)
            logger.info(f"Configuration loaded from {config_path}")
        except FileNotFoundError:
            # Fall back to default configuration
            logger.warning(f"Config file not found, using defaults: {config_path}")
            _config_instance = TOSCAConfig()

    return _config_instance
