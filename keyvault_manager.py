"""
Azure Key Vault integration module for GET-SKILLS application.
Securely retrieves configuration values from Azure Key Vault.
"""

import os
import logging
from typing import Optional, Dict, Any
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ChainedTokenCredential, AzureCliCredential, ManagedIdentityCredential

logger = logging.getLogger(__name__)

class KeyVaultManager:
    """Manages secure access to Azure Key Vault secrets."""
    
    def __init__(self, vault_url: Optional[str] = None):
        """
        Initialize Key Vault client.
        
        Args:
            vault_url: Azure Key Vault URL. If not provided, uses environment variable.
        """
        self.vault_url = vault_url or os.environ.get('AZURE_KEY_VAULT_URL', 'https://kv-tedu5upjp2nl6.vault.azure.net/')
        self.client = None
        self._secrets_cache = {}
        
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Key Vault client with appropriate credentials."""
        try:
            # Create a credential chain for different authentication methods
            credential_chain = ChainedTokenCredential(
                ManagedIdentityCredential(),  # For Azure App Service
                AzureCliCredential()         # For local development
            )
            
            self.client = SecretClient(
                vault_url=self.vault_url,
                credential=credential_chain
            )
            
            # Test the connection
            self._test_connection()
            logger.info(f"Successfully connected to Key Vault: {self.vault_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Key Vault client: {e}")
            self.client = None
    
    def _test_connection(self) -> None:
        """Test Key Vault connection by listing secrets."""
        if self.client:
            try:
                # Just list secrets to test connection (doesn't fetch values)
                list(self.client.list_properties_of_secrets())
            except Exception as e:
                logger.warning(f"Key Vault connection test failed: {e}")
                raise
    
    def get_secret(self, secret_name: str, use_cache: bool = True) -> Optional[str]:
        """
        Retrieve a secret from Key Vault.
        
        Args:
            secret_name: Name of the secret to retrieve
            use_cache: Whether to use cached values
            
        Returns:
            Secret value or None if not found/error
        """
        if not self.client:
            logger.warning("Key Vault client not initialized")
            return None
        
        # Check cache first
        if use_cache and secret_name in self._secrets_cache:
            logger.debug(f"Using cached value for secret: {secret_name}")
            return self._secrets_cache[secret_name]
        
        try:
            secret = self.client.get_secret(secret_name)
            value = secret.value
            
            # Cache the value
            if use_cache:
                self._secrets_cache[secret_name] = value
            
            logger.debug(f"Successfully retrieved secret: {secret_name}")
            return value
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
            return None
    
    def get_multiple_secrets(self, secret_names: list, use_cache: bool = True) -> Dict[str, Optional[str]]:
        """
        Retrieve multiple secrets from Key Vault.
        
        Args:
            secret_names: List of secret names to retrieve
            use_cache: Whether to use cached values
            
        Returns:
            Dictionary mapping secret names to their values
        """
        results = {}
        for secret_name in secret_names:
            results[secret_name] = self.get_secret(secret_name, use_cache)
        return results
    
    def is_available(self) -> bool:
        """Check if Key Vault is available and accessible."""
        return self.client is not None

# Global Key Vault manager instance
_kv_manager = None

def get_key_vault_manager() -> KeyVaultManager:
    """Get the global Key Vault manager instance."""
    global _kv_manager
    if _kv_manager is None:
        _kv_manager = KeyVaultManager()
    return _kv_manager

def get_secret(secret_name: str, fallback_env_var: Optional[str] = None) -> Optional[str]:
    """
    Get a secret with fallback to environment variable.
    
    Args:
        secret_name: Name of the secret in Key Vault
        fallback_env_var: Environment variable name to use as fallback
        
    Returns:
        Secret value from Key Vault or environment variable
    """
    kv_manager = get_key_vault_manager()
    
    # Try Key Vault first
    if kv_manager.is_available():
        value = kv_manager.get_secret(secret_name)
        if value:
            logger.debug(f"Retrieved {secret_name} from Key Vault")
            return value
    
    # Fallback to environment variable
    if fallback_env_var:
        value = os.environ.get(fallback_env_var)
        if value:
            logger.debug(f"Retrieved {secret_name} from environment variable {fallback_env_var}")
            return value
    
    logger.warning(f"Could not retrieve secret: {secret_name}")
    return None

def get_application_config() -> Dict[str, Any]:
    """
    Get all application configuration from Key Vault with environment fallbacks.
    
    Returns:
        Dictionary with all configuration values
    """
    config = {
        # Azure OpenAI Configuration
        'azure_openai_endpoint': get_secret('azure-openai-endpoint', 'AZURE_OPENAI_ENDPOINT'),
        'azure_openai_api_key': get_secret('azure-openai-api-key', 'AZURE_OPENAI_API_KEY'),
        'azure_openai_deployment_name': get_secret('azure-openai-deployment-name', 'AZURE_OPENAI_DEPLOYMENT_NAME'),
        
        # Azure Storage Configuration (if needed)
        'azure_storage_connection_string': get_secret('azure-storage-connection-string', 'AZURE_STORAGE_CONNECTION_STRING'),
        
        # Application Insights (if needed)
        'azure_application_insights_connection_string': get_secret('azure-application-insights-connection-string', 'AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING'),
        
        # OpenAI Fallback
        'openai_api_key': get_secret('openai-api-key', 'OPENAI_API_KEY'),
    }
    
    # Log which configurations were found
    found_configs = [k for k, v in config.items() if v is not None]
    missing_configs = [k for k, v in config.items() if v is None]
    
    if found_configs:
        logger.info(f"Found configuration for: {', '.join(found_configs)}")
    if missing_configs:
        logger.warning(f"Missing configuration for: {', '.join(missing_configs)}")
    
    return config