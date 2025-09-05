# Testing Metisara in Clean Environments

This document describes how to test Metisara in containerized environments that simulate clean computer installations.

## Container Testing Overview

We provide Docker containers to test Metisara installation and functionality from scratch:

- **Fedora Container**: Primary testing environment matching our main target platform
- **Alpine Container**: Lightweight testing environment for minimal installations
- **Test Container**: Pre-configured environment with sample data for testing

## Quick Start

### Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Build and start Fedora test environment
docker-compose up -d metisara-fedora

# Enter the container
docker-compose exec metisara-fedora /bin/bash

# Inside container - test basic functionality
source venv/bin/activate
./metis --version
./metis --help
./metis --dry-run
```

### Option 2: Direct Docker Build

```bash
# Build Fedora test image
docker build -t metisara-test --build-arg BASE_IMAGE=fedora:latest .

# Run interactive container
docker run -it metisara-test /bin/bash

# Inside container - test functionality
source venv/bin/activate
./metis --version
```

## Available Test Environments

### 1. Fedora Environment (Primary)

```bash
# Start Fedora test environment
docker-compose up -d metisara-fedora
docker-compose exec metisara-fedora /bin/bash

# Test installation
source venv/bin/activate
./metis --version
./metis --help
```

**Purpose**: Test on our primary target platform (Fedora Linux)

### 2. Alpine Environment (Lightweight)

```bash
# Start Alpine test environment  
docker-compose up -d metisara-alpine
docker-compose exec metisara-alpine /bin/bash

# Test installation
source venv/bin/activate
./metis --version
```

**Purpose**: Test on minimal Linux environment, verify dependencies

### 3. Full Test Environment

```bash
# Start test environment with sample data
docker-compose up -d metisara-test
docker-compose exec metisara-test /bin/bash

# Environment comes pre-configured
./metis --dry-run
./metis --generate-config
```

**Purpose**: End-to-end testing with sample configurations

## Testing Scenarios

### 1. Fresh Installation Test

Test the complete installation process from scratch:

```bash
# In any container
source venv/bin/activate

# Verify Python environment
python --version
pip list | grep metisara

# Test basic commands
./metis --version
./metis --help
```

### 2. Configuration Test

Test configuration setup:

```bash
# Verify configuration files exist
ls -la *.conf *.env*

# Test configuration generation
./metis --generate-config --dry-run

# Check workspace creation
./metis --dry-run
ls -la workspace/
```

### 3. Dry Run Test

Test CSV processing without JIRA integration:

```bash
# Copy sample CSV if available
cp test-data/*.csv workspace/input/ 2>/dev/null || echo "No test data available"

# Run dry-run mode
./metis --dry-run

# Check generated files
ls -la workspace/
```

### 4. Development Test

Test development setup:

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests
make test

# Run linting
make lint

# Run type checking
make type-check
```

## Container Maintenance

### Rebuild Containers

```bash
# Rebuild all containers
docker-compose build

# Rebuild specific container
docker-compose build metisara-fedora
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (resets workspaces)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

### View Logs

```bash
# View container logs
docker-compose logs metisara-fedora

# Follow logs
docker-compose logs -f metisara-test
```

## Test Data

### Adding Test CSV Files

```bash
# Copy test files to container
docker cp your-test-file.csv metisara-fedora-test:/home/testuser/metisara/workspace/input/

# Or mount a directory with docker-compose
# (see docker-compose.yml volumes section)
```

### Sample Test Configuration

Create a minimal test configuration:

```bash
# Inside container
cat > metisara.conf << EOF
[jira]
url = https://test-jira-instance.com/
username = test@example.com

[files]
csv_file_input = workspace/input/test-template.csv
csv_file_output = workspace/output/test-processed.csv

[project]
default_project = TEST
EOF

# Set mock API token for dry-run testing
echo "JIRA_API_TOKEN=test-dry-run-token" > .env
```

## Troubleshooting

### Common Issues

1. **Permission Issues**
   ```bash
   # Fix file permissions in container
   sudo chown -R testuser:testuser /home/testuser/metisara/
   ```

2. **Python Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv/
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Missing Dependencies**
   ```bash
   # Install system dependencies (Fedora)
   sudo dnf install python3-devel python3-pip git make

   # Install system dependencies (Alpine)
   sudo apk add python3-dev py3-pip git make bash
   ```

### Debug Mode

```bash
# Run with verbose output
./metis --dry-run --verbose 2>&1 | tee debug.log

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify metisara installation
python -c "import metisara; print(metisara.__version__)"
```

## CI/CD Integration

The same containers can be used in CI/CD pipelines:

```yaml
# Example GitHub Actions usage
- name: Test in Fedora container
  run: |
    docker build -t metisara-ci --build-arg BASE_IMAGE=fedora:latest .
    docker run --rm metisara-ci ./metis --version
```

## Performance Testing

```bash
# Time dry-run operations
time ./metis --dry-run

# Profile memory usage
python -m memory_profiler ./metis --dry-run

# Test with large CSV files
# (copy large test files to workspace/input/)
./metis --dry-run
```

This container-based testing approach ensures Metisara works correctly on clean systems and helps identify installation issues before users encounter them.