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
            'username': self.config.get('jira', 'username', fallback='user@example.com'),
            'google_sheets_url': self.config.get('google_sheets', 'url', fallback='')
        }
        
    def validate_config(self, config: Dict[str, Any], skip_jira_validation: bool = False) -> bool:
        """Validate configuration values.
        
        Args:
            config: Configuration dictionary to validate
            skip_jira_validation: If True, skip JIRA-specific validation (for dry-run mode)
            
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_fields = ['csv_input', 'csv_output', 'jira_url', 'username']
        
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"Required configuration field '{field}' is missing or empty")
        
        # Skip JIRA validation for dry-run mode
        if not skip_jira_validation:
            # Check for example/placeholder values that need to be updated
            example_values = {
                'jira_url': ['https://your-jira-instance.com/', 'https://your-jira-instance.com'],
                'username': ['user@example.com']
            }
            
            for field, examples in example_values.items():
                if config[field] in examples:
                    raise ValueError(f"Please update '{field}' in metisara.conf - it's still set to the example value '{config[field]}'")
            
            # Validate JIRA URL format
            jira_url = config['jira_url']
            if not (jira_url.startswith('http://') or jira_url.startswith('https://')):
                raise ValueError(f"JIRA URL must start with http:// or https:// (current: '{jira_url}')")
            
            if 'example' in jira_url.lower() or 'your-jira' in jira_url.lower():
                raise ValueError(f"Please update the JIRA URL in metisara.conf to your actual JIRA instance (current: '{jira_url}')")
                
        return True