"""
Configuration management for cloud providers.

Loads and manages cloud provider configurations from clouds.yaml
and environment variables.
"""

import os
import yaml
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CloudConfig:
    """Cloud provider configuration."""

    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize cloud config.

        Args:
            name: Cloud name (e.g., 'ovh', 'mock')
            config: Cloud configuration dictionary
        """
        self.name = name
        self.config = config

    def is_mock(self) -> bool:
        """Check if this is the mock provider."""
        return self.config.get("_provider_type") == "mock" or self.name == "mock"

    def has_auth(self) -> bool:
        """Check if cloud has authentication configured."""
        auth = self.config.get("auth")
        return auth is not None and len(auth) > 0

    def __repr__(self) -> str:
        return f"CloudConfig(name={self.name}, provider={'mock' if self.is_mock() else 'openstack'})"


class CloudsConfig:
    """Manages multiple cloud configurations from clouds.yaml."""

    def __init__(self, clouds: Dict[str, Dict[str, Any]]):
        """Initialize clouds config.

        Args:
            clouds: Dictionary of cloud configurations
        """
        self.clouds: Dict[str, CloudConfig] = {
            name: CloudConfig(name, config) for name, config in clouds.items()
        }

    def get(self, name: str) -> Optional[CloudConfig]:
        """Get cloud config by name.

        Args:
            name: Cloud name

        Returns:
            CloudConfig or None if not found
        """
        return self.clouds.get(name)

    def list(self) -> Dict[str, CloudConfig]:
        """List all cloud configurations.

        Returns:
            Dictionary of all cloud configs
        """
        return self.clouds.copy()

    def get_default(self) -> Optional[CloudConfig]:
        """Get default cloud (first one, or specified by env var).

        Returns:
            Default CloudConfig or None
        """
        default_cloud = os.environ.get("OS_CLOUD")
        if default_cloud:
            return self.get(default_cloud)

        # Return first available
        if self.clouds:
            return next(iter(self.clouds.values()))

        return None

    def __repr__(self) -> str:
        return f"CloudsConfig(clouds={list(self.clouds.keys())})"


def load_clouds_yaml(path: Optional[str] = None) -> CloudsConfig:
    """Load clouds configuration from clouds.yaml file.

    Args:
        path: Path to clouds.yaml (defaults to ~/.config/openstack/clouds.yaml
              or ./clouds.yaml in project root)

    Returns:
        CloudsConfig instance

    Raises:
        FileNotFoundError: If clouds.yaml not found
        yaml.YAMLError: If clouds.yaml is invalid YAML
    """
    if not path:
        # Try common locations
        possible_paths = [
            os.path.expanduser("~/.config/openstack/clouds.yaml"),
            os.path.expanduser("~/.openstack/clouds.yaml"),
            "clouds.yaml",
            "/etc/openstack/clouds.yaml",
        ]

        path = None
        for possible_path in possible_paths:
            if os.path.exists(possible_path):
                path = possible_path
                break

        if not path:
            raise FileNotFoundError(
                "clouds.yaml not found in any of: "
                + ", ".join(possible_paths)
            )

    logger.info(f"Loading clouds.yaml from: {path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    if not config or "clouds" not in config:
        raise ValueError("clouds.yaml must contain 'clouds' section")

    return CloudsConfig(config["clouds"])


def get_clouds_config() -> CloudsConfig:
    """Get global clouds configuration (lazy loaded).

    Returns:
        CloudsConfig instance

    This function caches the loaded configuration in module state.
    """
    # Use module-level cache
    if not hasattr(get_clouds_config, "_config"):
        try:
            get_clouds_config._config = load_clouds_yaml()
        except FileNotFoundError as e:
            logger.warning(f"Could not load clouds.yaml: {e}")
            logger.warning("Using empty cloud configuration")
            get_clouds_config._config = CloudsConfig({})

    return get_clouds_config._config
