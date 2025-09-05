# Dockerfile for testing Metisara installation from scratch
# Supports both Fedora and Alpine Linux (lightweight) testing

ARG BASE_IMAGE=fedora:latest
FROM ${BASE_IMAGE}

# Set working directory
WORKDIR /app

# Install system dependencies based on the base image
RUN if [ -f /etc/fedora-release ]; then \
        # Fedora setup
        dnf update -y && \
        dnf install -y python3 python3-pip git make wget curl && \
        dnf clean all; \
    elif [ -f /etc/alpine-release ]; then \
        # Alpine setup (lightweight alternative)
        apk update && \
        apk add --no-cache python3 py3-pip git make wget curl bash; \
    else \
        # Debian/Ubuntu fallback (though we focus on Fedora)
        apt-get update && \
        apt-get install -y python3 python3-pip git make wget curl && \
        apt-get clean && rm -rf /var/lib/apt/lists/*; \
    fi

# Create a non-root user for testing
RUN useradd -m -s /bin/bash testuser || adduser -D testuser
USER testuser
WORKDIR /home/testuser

# Copy the project files
COPY --chown=testuser:testuser . /home/testuser/metisara/

# Set working directory to the project
WORKDIR /home/testuser/metisara

# Create Python virtual environment (simulating clean installation)
RUN python3 -m venv venv

# Activate virtual environment and install dependencies
RUN . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Metisara in development mode
RUN . venv/bin/activate && pip install -e .

# Make metis executable
RUN chmod +x metis

# Create initial setup (simulating first-time user experience)
RUN cp examples/metisara.conf.example metisara.conf && \
    cp .env.example .env

# Set environment variable to indicate container environment
ENV METISARA_CONTAINER=1

# Default command shows help and status
CMD ["/bin/bash", "-c", "source venv/bin/activate && echo '=== Metisara Container Test Environment ===' && echo 'Python version:' && python --version && echo 'Metisara installation:' && ./metis --version && echo 'Available commands:' && ./metis --help && echo 'Configuration files:' && ls -la *.conf *.env* && echo 'Ready for testing! Use: docker run -it <image> /bin/bash'"]