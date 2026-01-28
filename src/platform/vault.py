"""
Secret management utility for Proxie.
Handles fetching secrets from Google Cloud Secret Manager in production,
falling back to environment variables in development.
"""

import os
import structlog
from typing import Optional

logger = structlog.get_logger(__name__)

class SecretManager:
    """Utility to interface with Google Cloud Secret Manager."""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.client = None
        
        if self.project_id:
            try:
                from google.cloud import secretmanager
                self.client = secretmanager.SecretManagerServiceClient()
            except (ImportError, Exception) as e:
                logger.warning("secret_manager_init_failed", error=str(e), note="Falling back to ENV variables")

    def get_secret(self, secret_id: str, default: Optional[str] = None) -> Optional[str]:
        """
        Fetch a secret value. 
        Tries GCP Secret Manager first if initialized, otherwise falls back to ENV.
        """
        # Try GCP Secret Manager first
        if self.client and self.project_id:
            try:
                from google.api_core import exceptions
                name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
                response = self.client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")
            except Exception as e:
                # We catch all here to be safe
                logger.debug("secret_manager_access_failed", secret_id=secret_id, error=str(e))

        # Fallback to standard environment variables
        return os.getenv(secret_id, default)

# Singleton instance
secrets_utility = SecretManager()

def get_secret(secret_id: str, default: Optional[str] = None) -> Optional[str]:
    """Helper function to get a secret with fallback."""
    return secrets_utility.get_secret(secret_id, default)
