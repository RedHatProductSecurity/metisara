# Metisara - JIRA Project Management Automation

🏛️ **Wisdom and planning for your project management**

Metisara is an automated JIRA project management workflow tool that streamlines the creation of project tickets through CSV processing and template-based configuration.

## Features

- 📋 **CSV Template Processing**: Convert project templates to JIRA tickets
- 🎯 **Intelligent Placeholder Replacement**: Dynamic configuration with placeholders
- 👥 **Team Management**: Automated resource allocation and conception review tickets
- 🔄 **Epic Linking**: Automatic epic creation and ticket linking
- 🔍 **Dry-Run Mode**: Preview changes before creating actual JIRA tickets
- ⚙️ **Flexible Configuration**: JSON and INI-based configuration management
- 📦 **Issue Reporting**: Built-in diagnostics and issue reporting

## Quick Start

### 1. Installation

**Supported Platforms:** macOS, Fedora Linux

```bash
git clone https://github.com/your-org/metisara.git
cd metisara
```

**Platform-specific setup:**

**macOS:**
```bash
# Install Python 3.7+ if needed (using Homebrew)
brew install python
```

**Fedora:**
```bash
# Install Python 3.7+ if needed
sudo dnf install python3 python3-pip
```

### 2. Configuration

Copy the example configuration file and customize it:

```bash
cp examples/metisara.conf.example metisara.conf
```

Edit `metisara.conf` with your JIRA settings:

```ini
[jira]
url = https://your-jira-instance.com/
username = your.email@company.com

[files]
csv_file_input = workspace/input/Metisara Template - Import.csv
csv_file_output = workspace/output/project-tickets-processed.csv

[project]
default_project = PROJ
```

### 3. Environment Setup

Create a `.env` file with your JIRA API token:

```bash
echo "JIRA_API_TOKEN=your_jira_api_token_here" > .env
```

### 4. Basic Usage

```bash
# Dry run (preview mode) - recommended for first use
./metis --dry-run

# Generate configuration from CSV template
./metis --generate-config

# Create actual JIRA tickets in your JIRA
./metis

# Force refresh CSV from Downloads folder
./metis --force --dry-run
```

## Workflow Overview

Metisara follows a structured 3-phase workflow:

### Phase 1: CSV Processing
1. **Auto-move CSV**: Automatically moves CSV templates from Downloads folder
2. **Configuration Generation**: Extracts configuration from CSV template sections
3. **Placeholder Replacement**: Replaces placeholders with actual values

### Phase 2: JIRA Ticket Creation
1. **Project Issues**: Creates top-level project issues first
2. **Epic Issues**: Creates epic issues with proper naming and linking
3. **Story/Tracker Issues**: Creates detailed work items linked to epics

### Phase 3: Team Integration
- **Resource Allocation**: Auto-generates team assignment tickets
- **Conception Reviews**: Creates review tickets for stakeholders
- **Epic Linking**: Automatically links related tickets

## Command Line Options

```bash
./metis [OPTIONS] [API_TOKEN]

Options:
  --version             Show version information
  --dry-run, --pretend  Simulate ticket creation without creating actual JIRA tickets
  --skip-auto-move      Skip automatic CSV file moving from Downloads folder
  --force               Force move CSV file from Downloads even if destination exists
  --generate-config     Generate placeholder configuration from CSV file
  --report-issue        Create a zip file with workspace contents for issue reporting
  --clean               Clean all project generated files

Arguments:
  API_TOKEN             JIRA API token (optional if using .env file)
```

## Project Structure

```
metisara/
├── metis                           # Main executable script
├── metisara.conf                   # Configuration file
├── .env                           # Environment variables (API tokens)
├── src/metisara/                  # Source code
│   ├── __init__.py               # Package initialization
│   ├── cli.py                    # Command-line interface
│   ├── config/                   # Configuration management
│   │   ├── manager.py           # Config file handling
│   ├── processors/              # CSV processing
│   │   ├── csv_processor.py     # Main CSV processing logic
│   ├── jira/                    # JIRA integration
│   │   ├── ticket_creator.py    # JIRA ticket creation
│   │   ├── field_finder.py      # JIRA field discovery
│   └── utils/                   # Utility functions
│       ├── file_manager.py      # File management utilities
├── workspace/                   # Working directory (auto-created)
│   ├── input/                  # Input CSV templates
│   ├── output/                 # Processed CSV files
│   ├── config/                 # Generated configuration files
│   └── temp/                   # Temporary files and logs
└── examples/                   # Example configuration files
    └── metisara.conf.example   # Example configuration
```

## CSV Template Format

Metisara processes CSV templates with the following sections: (no need to create CSV manually, just download CSV from Google Sheets)

### 1. Ticket Definitions
Standard CSV format with columns:
- `Milestone`, `Issue Type`, `Summary`, `Description`, `Priority`
- `Epic Link`, `Epic Name`, `Reporter`, `Assignee`, `Parent Link`
- `Target Start`, `Due Date`, `Component`, `Story Points`

### 2. General Configuration Section
```csv
Milestone,Issue Type,Summary,Description,...
General Configuration,,,,...
<project_key>,PROJ,,,
<project_name>,My Project,,,
<program_manager>,manager@company.com,,,
<project_target_start>,2025-09-05,,,
<project_due_date>,2025-12-31,,,
```

### 3. Resource Allocation Teams
```csv
Milestone,Issue Type,Summary,Description,...
Resource Allocation Tickets,,,,...
Team A,Developer,John Doe,john@company.com,...
Team B,Designer,Jane Smith,jane@company.com,...
```

### 4. Conception Teams
```csv
Milestone,Issue Type,Summary,Description,...
Conception Tickets,,,,...
Architecture,Lead Architect,Bob Wilson,bob@company.com,...
QA,QA Lead,Alice Johnson,alice@company.com,...
```

## Configuration Management

### Automatic Configuration Generation
```bash
# Generate fresh configuration from CSV template
./metis --generate-config
```

This creates `workspace/config/csv_replacements.json` with:
- Extracted placeholder mappings
- Team member information
- JIRA project settings
- File path configurations

### Manual Configuration
Edit `workspace/config/csv_replacements.json` for custom replacements:

```json
{
  "_ai_disclaimer": "AI-Generated file - Review before production use",
  "replacements": {
    "<project_key>": "MYPROJ",
    "<project_name>": "My Amazing Project",
    "<program_manager>": "manager@company.com"
  },
  "jira_settings": {
    "target_project": "MYPROJ"
  }
}
```

## Error Handling & Troubleshooting

### Common Issues

1. **Missing API Token**
   ```bash
   # Solution: Set environment variable or use .env file
   export JIRA_API_TOKEN=your_token
   # Or create .env file with JIRA_API_TOKEN=your_token
   ```

2. **CSV File Not Found**
   ```bash
   # Solution: Use --skip-auto-move if file is already in place
   ./metis --skip-auto-move
   ```

3. **Configuration Errors**
   ```bash
   # Solution: Regenerate configuration
   ./metis --generate-config
   ```

### Issue Reporting
```bash
# Create diagnostic package (WARNING: may contain sensitive data)
./metis --report-issue
```

### Cleaning Up
```bash
# Remove all generated files
./metis --clean
```

## Container Testing

For testing Metisara in clean environments (simulating fresh installations):

```bash
# Quick test in Fedora container
./podman-scripts.sh build
./podman-scripts.sh start
./podman-scripts.sh exec metisara-fedora

# Inside container
source venv/bin/activate
./metis --version
./metis --dry-run
```

See [TESTING.md](TESTING.md) for complete container testing documentation.

## Development

### Project Structure
- **CLI Module** (`cli.py`): Main command-line interface and workflow orchestration
- **CSV Processor** (`csv_processor.py`): Template processing and placeholder replacement
- **JIRA Integration** (`ticket_creator.py`): JIRA API integration and ticket creation
- **Configuration** (`manager.py`): Configuration file management
- **Utilities** (`file_manager.py`): File operations and workspace management

### Key Components

1. **JiraBulkCreator**: Main class for JIRA ticket creation with support for:
   - Hierarchical ticket creation (Project → Epic → Story)
   - Epic placeholder resolution
   - Dry-run simulation
   - Error handling and reporting

2. **CSV Processing**: Advanced CSV processing with:
   - Comment line filtering
   - Configuration section extraction
   - Dynamic team ticket generation
   - Placeholder replacement

3. **Configuration Management**: Flexible configuration with:
   - JSON-based replacement mappings
   - INI-based system configuration
   - Environment variable support

## Dependencies

- **Python 3.7+**
- **jira**: JIRA Python API client
- **python-dotenv**: Environment variable management
- **configparser**: INI file configuration

## Security Considerations

- API tokens are stored in `.env` files (add to `.gitignore`)
- Issue reports may contain sensitive information (names, emails)
- Always review generated configurations before production use
- Use dry-run mode to preview changes

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Use `./metis --report-issue` to create diagnostic information
3. Open an issue on GitHub with the diagnostic information (remove all PII/sensitive information before upload!)

---

🏛️ **Metis** - Named after the Greek goddess of wisdom and planning, Metisara brings methodical wisdom to your project management workflows.
