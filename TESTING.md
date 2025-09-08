# Testing Metisara in Clean Environments

This document describes how to test Metisara in containerized environments that simulate clean computer installations.

## Container Testing Overview

We provide Podman containers to test Metisara installation and functionality from scratch:

- **Fedora Container**: Primary testing environment matching our main target platform
- **Alpine Container**: Lightweight testing environment for minimal installations
- **Test Container**: Pre-configured environment with sample data for testing

## Quick Start

### Prerequisites

- Podman installed on your system
- Podman Compose (optional) or use our custom scripts

### Option 1: Podman Scripts (Recommended)

```bash
# Build all test environments
./podman-scripts.sh build

# Start the pod with all containers
./podman-scripts.sh start

# Enter the Fedora container
./podman-scripts.sh exec metisara-fedora

# Inside container - test basic functionality
source venv/bin/activate
./metis --version
./metis --help
./metis --dry-run
```

### Option 2: Direct Podman Build

```bash
# Build Fedora test image
podman build -t metisara-test --build-arg BASE_IMAGE=fedora:latest -f Containerfile .

# Run interactive container
podman run -it metisara-test /bin/bash

# Inside container - test functionality
source venv/bin/activate
./metis --version
```

## Available Test Environments

### 1. Fedora Environment (Primary)

```bash
# Start Fedora test environment
./podman-scripts.sh start
./podman-scripts.sh exec metisara-fedora

# Test installation
source venv/bin/activate
./metis --version
./metis --help
```

**Purpose**: Test on our primary target platform (Fedora Linux)

### 2. Alpine Environment (Lightweight)

```bash
# Start Alpine test environment
./podman-scripts.sh start
./podman-scripts.sh exec metisara-alpine

# Test installation
source venv/bin/activate
./metis --version
```

**Purpose**: Test on minimal Linux environment, verify dependencies

### 3. Full Test Environment

```bash
# Start test environment with sample data
./podman-scripts.sh start
./podman-scripts.sh exec metisara-test

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
./podman-scripts.sh build

# Rebuild specific container (use build script and specify base image)
podman build -t localhost/metisara-fedora:latest --build-arg BASE_IMAGE=fedora:latest -f Containerfile .
```

### Clean Up

```bash
# Stop and remove pod
./podman-scripts.sh stop

# Clean up everything (containers, images, volumes)
./podman-scripts.sh cleanup
```

### View Logs

```bash
# View container logs
./podman-scripts.sh logs metisara-fedora

# Follow logs with podman directly
podman logs -f metisara-pod-metisara-test
```

## Test Data

### Adding Test CSV Files

```bash
# Copy test files to container
podman cp your-test-file.csv metisara-pod-metisara-fedora:/home/testuser/metisara/workspace/input/

# Or mount a directory with the pod configuration
# (see podman-pod.yml volumes section)
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
    podman build -t metisara-ci --build-arg BASE_IMAGE=fedora:latest -f Containerfile .
    podman run --rm metisara-ci ./metis --version
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