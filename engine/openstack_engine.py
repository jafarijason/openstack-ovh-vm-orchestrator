"""
OpenStack Engine

Wrapper around OpenStack SDK for cloud operations and resource management.
"""

import os
from typing import Optional

import openstack


class OpenStackEngine:
    """
    OpenStack Cloud Connection Manager.
    
    Manages connection to OpenStack cloud using openstacksdk.
    Supports multiple clouds via clouds.yaml configuration.
    """

    def __init__(self, cloud_name: Optional[str] = None):
        """
        Initialize OpenStack engine and connect to cloud.
        
        Args:
            cloud_name: Name of the cloud in clouds.yaml. 
                       If None, uses OS_CLOUD env var or first available cloud.
                       
        Raises:
            RuntimeError: If connection to cloud fails.
        """
        try:
            # Determine cloud name
            if cloud_name is None:
                cloud_name = os.environ.get("OS_CLOUD", "ovh")
            
            self.cloud_name = cloud_name
            
            # Connect to cloud
            self.conn = openstack.connect(cloud=cloud_name)
            
            print(f"✅ Connected to OpenStack cloud: {cloud_name}")
            
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to OpenStack cloud '{cloud_name}': {str(e)}"
            ) from e

    def get_connection(self):
        """
        Get the underlying OpenStack connection object.
        
        Returns:
            openstack.connection.Connection: The OpenStack connection.
        """
        return self.conn

    def get_compute(self):
        """
        Get compute service proxy (Nova).
        
        Returns:
            openstack.proxy.Proxy: Nova compute service.
        """
        return self.conn.compute

    def get_volume(self):
        """
        Get volume service proxy (Cinder).
        
        Returns:
            openstack.proxy.Proxy: Cinder volume service.
        """
        return self.conn.block_storage

    def get_network(self):
        """
        Get network service proxy (Neutron).
        
        Returns:
            openstack.proxy.Proxy: Neutron network service.
        """
        return self.conn.network

    def get_image(self):
        """
        Get image service proxy (Glance).
        
        Returns:
            openstack.proxy.Proxy: Glance image service.
        """
        return self.conn.image

    def is_connected(self) -> bool:
        """
        Check if connected to OpenStack cloud.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        try:
            # Try to list projects to verify connection
            _ = list(self.conn.identity.projects())
            return True
        except Exception:
            return False

    def get_cloud_info(self) -> dict:
        """
        Get information about connected cloud.
        
        Returns:
            dict: Cloud information (name, auth_url, project, region).
        """
        try:
            auth = self.conn.auth
            return {
                "cloud_name": self.cloud_name,
                "auth_url": auth.get("auth_url", "N/A"),
                "project_id": auth.get("project_id", "N/A"),
                "region": self.conn.region_name or "N/A",
                "connected": self.is_connected(),
            }
        except Exception as e:
            return {
                "cloud_name": self.cloud_name,
                "error": str(e),
                "connected": False,
            }

    def close(self):
        """Close connection to OpenStack cloud."""
        if self.conn:
            self.conn.close()
            print(f"✅ Closed connection to {self.cloud_name}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        connected = "connected" if self.is_connected() else "disconnected"
        return f"OpenStackEngine(cloud={self.cloud_name}, status={connected})"
