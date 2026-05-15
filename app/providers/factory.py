"""
Provider factory for creating appropriate cloud provider instances.

Selects and initializes the correct provider (Mock, OpenStack, etc.)
based on cloud configuration.
"""

import logging
from typing import Optional

from app.core.config import CloudConfig, get_clouds_config
from app.providers.base import BaseProvider
from app.providers.mock_provider import MockProvider
from app.core.exceptions import CloudConnectionError

logger = logging.getLogger(__name__)


def create_provider(cloud_name: Optional[str] = None) -> BaseProvider:
    """Create and initialize cloud provider.

    Args:
        cloud_name: Name of cloud from clouds.yaml
                   Defaults to OS_CLOUD env var or first configured cloud

    Returns:
        Initialized provider instance (MockProvider or OpenStackProvider)

    Raises:
        ValueError: If no cloud configured
        CloudConnectionError: If unable to connect to cloud
    """
    clouds_config = get_clouds_config()

    # Determine which cloud to use
    if cloud_name:
        cloud_config = clouds_config.get(cloud_name)
        if not cloud_config:
            raise ValueError(f"Cloud '{cloud_name}' not found in clouds.yaml")
    else:
        cloud_config = clouds_config.get_default()
        if not cloud_config:
            raise ValueError(
                "No cloud configured. "
                "Please configure clouds.yaml or set OS_CLOUD environment variable"
            )

    logger.info(f"Creating provider for cloud: {cloud_config.name}")

    # Create mock provider if configured as mock
    if cloud_config.is_mock():
        logger.info("Initializing Mock provider")
        return MockProvider()

    # Create OpenStack provider
    logger.info("Initializing OpenStack provider")
    try:
        from app.providers.openstack_provider import OpenStackProvider

        return OpenStackProvider(cloud_name=cloud_config.name)
    except ImportError:
        raise CloudConnectionError(
            cloud_config.name, "openstacksdk not installed. Install with: pip install openstacksdk"
        )
    except Exception as e:
        raise CloudConnectionError(cloud_config.name, str(e))


def list_available_clouds() -> dict:
    """List all configured clouds with their types.

    Returns:
        Dictionary with cloud names as keys and provider type as value
    """
    clouds_config = get_clouds_config()
    result = {}

    for name, cloud_config in clouds_config.list().items():
        provider_type = "mock" if cloud_config.is_mock() else "openstack"
        has_auth = cloud_config.has_auth()
        result[name] = {
            "type": provider_type,
            "authenticated": has_auth,
            "default": name == clouds_config.get_default().name
            if clouds_config.get_default()
            else False,
        }

    return result
