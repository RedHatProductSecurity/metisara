# Changelog

All notable changes to Metisara will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial open-source release preparation

## [1.0.0] - 2024-09-05

### Added
- 🏛️ Initial release of Metisara - JIRA Project Management Automation
- 📋 CSV template processing with placeholder replacement
- 🎯 Intelligent placeholder replacement system
- 👥 Automated team management (resource allocation and conception reviews)
- 🔄 Epic linking and hierarchical ticket creation
- 🔍 Dry-run mode for safe preview of changes
- ⚙️ Flexible JSON and INI-based configuration management
- 📦 Built-in issue reporting and diagnostics
- 🧹 Workspace cleanup functionality
- 🔧 Command-line interface with comprehensive options
- 📁 Automatic file management (CSV auto-move from Downloads)
- 🛡️ Security considerations (API token management)

### Features
- **CLI Tool**: Main executable script (`metis`) with multiple operation modes
- **CSV Processing**: Advanced CSV processing with comment filtering and section extraction
- **JIRA Integration**: Full JIRA API integration with bulk ticket creation
- **Configuration Management**: Automatic configuration generation from CSV templates
- **Team Integration**: Dynamic generation of team assignment and review tickets
- **Error Handling**: Comprehensive error handling and user-friendly messages
- **Logging**: Automatic logging of all operations to workspace/temp/

### Components
- **JiraBulkCreator**: Main class for JIRA ticket creation with hierarchical support
- **CSV Processor**: Template processing and placeholder replacement engine
- **Configuration Manager**: Flexible configuration file management
- **File Manager**: Workspace and file operation utilities
- **Field Finder**: JIRA field discovery and mapping

### Dependencies
- Python 3.7+
- jira>=3.0.0 (JIRA Python API client)
- python-dotenv>=0.19.0 (Environment variable management)

### Documentation
- Comprehensive README.md with installation and usage instructions
- Example configuration files
- Detailed troubleshooting guide
- Security considerations and best practices

[Unreleased]: https://github.com/your-org/metisara/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/metisara/releases/tag/v1.0.0