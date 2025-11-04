"""
Configuration management for GEO Audit Platform
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """Main configuration manager"""

    def __init__(self, config_path: str = "config/platforms.yaml"):
        """
        Initialize settings from configuration file

        Args:
            config_path: Path to platform configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file (supports JSON and YAML)"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        # Determine format based on extension
        if self.config_path.suffix in ['.yaml', '.yml']:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        elif self.config_path.suffix == '.json':
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {self.config_path.suffix}")

    def get_platforms_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Get platform configurations

        Returns:
            Dict mapping platform names to their configs
        """
        return self.config.get('platforms', {})

    def get_storage_config(self) -> Dict[str, Any]:
        """
        Get storage configuration

        Returns:
            Storage config dict
        """
        return self.config.get('storage', {})

    def get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific platform

        Args:
            platform_name: Platform name (Claude, ChatGPT, etc.)

        Returns:
            Platform config dict
        """
        platforms = self.get_platforms_config()
        return platforms.get(platform_name, {})


class ClientConfig:
    """Client/brand-specific configuration"""

    def __init__(self, client_name: str, config_dir: str = "config/clients"):
        """
        Initialize client configuration

        Args:
            client_name: Client/brand name
            config_dir: Directory containing client configs
        """
        self.client_name = client_name
        self.config_dir = Path(config_dir)
        self.config = self._load_client_config()

    def _load_client_config(self) -> Dict[str, Any]:
        """Load client-specific configuration"""
        # Try YAML first, then JSON
        yaml_path = self.config_dir / f"{self.client_name}.yaml"
        json_path = self.config_dir / f"{self.client_name}.json"

        if yaml_path.exists():
            with open(yaml_path, 'r') as f:
                return yaml.safe_load(f)
        elif json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            # Return default config
            print(f"⚠️ No client config found for '{self.client_name}', using defaults")
            return {
                'brand_name': self.client_name,
                'industry': 'general',
                'competitors': []
            }

    def get_brand_name(self) -> str:
        """Get brand name"""
        return self.config.get('brand_name', self.client_name)

    def get_industry(self) -> Optional[str]:
        """Get industry"""
        return self.config.get('industry')

    def get_competitors(self) -> list:
        """Get custom competitor list"""
        return self.config.get('competitors', [])

    def get_keywords(self) -> list:
        """Get custom brand keywords"""
        return self.config.get('keywords', [])


def load_legacy_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load legacy config.json format for backward compatibility

    Args:
        config_path: Path to legacy config file

    Returns:
        Converted configuration dict
    """
    with open(config_path, 'r') as f:
        legacy = json.load(f)

    # Convert to new format
    config = {
        'platforms': {
            'Claude': {
                'api_key': legacy.get('anthropic_api_key'),
                'model': 'claude-sonnet-4-20250514'
            },
            'ChatGPT': {
                'api_key': legacy.get('openai_api_key'),
                'model': 'gpt-4o'
            },
            'Google AI': {
                'api_key': legacy.get('google_api_key'),
                'model': 'gemini-2.0-flash-exp'
            },
            'Perplexity': {
                'api_key': legacy.get('perplexity_api_key'),
                'model': 'sonar-pro'
            }
        },
        'storage': {
            'credentials_path': legacy.get('google_credentials_path'),
            'spreadsheet_id': legacy.get('spreadsheet_id')
        }
    }

    return config
