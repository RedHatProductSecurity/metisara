"""Configuration management for Metisara."""

import configparser
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Manages configuration loading and validation for Metisara."""
    
    def __init__(self, config_file: str = 'metisara.conf'):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Dictionary containing configuration values
            
        Raises:
            FileNotFoundError: If configuration file is not found
            configparser.Error: If configuration file is invalid
        """
        if not Path(self.config_file).exists():
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
            
        self.config.read(self.config_file)
        
        return {
            'csv_input': self.config.get('files', 'csv_file_input', fallback='Metisara Template - Import.csv'),
            'csv_output': self.config.get('files', 'csv_file_output', fallback='project-tickets-processed.csv'),
            'jira_url': self.config.get('jira', 'url', fallback='https://your-jira-instance.com/'),
            'username': self.config.get('jira', 'username', fallback='user@example.com')
        }
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration values.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_fields = ['csv_input', 'csv_output', 'jira_url', 'username']
        
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"Required configuration field '{field}' is missing or empty")
                
        return True