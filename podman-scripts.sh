#!/bin/bash
# Podman scripts for Metisara development environments
# Replaces docker-compose functionality with Podman pods
# Cross-platform support: Linux and macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect platform
IS_MACOS=false
if [[ "$OSTYPE" == "darwin"* ]]; then
    IS_MACOS=true
fi

# Check if Podman machine is running (macOS requirement)
check_podman_machine() {
    if [[ "$IS_MACOS" == "true" ]]; then
        if ! podman machine list 2>/dev/null | grep -q "running"; then
            echo "Starting Podman machine (required on macOS)..."
            podman machine start 2>/dev/null || {
                echo "Podman machine not initialized. Initializing..."
                podman machine init
                podman machine start
            }
        fi
    fi
}

# Build images
build_images() {
    check_podman_machine
    echo "Building Metisara images with Podman..."
    
    # Build Fedora image
    echo "Building Fedora image..."
    podman build -t localhost/metisara-fedora:latest \
        --build-arg BASE_IMAGE=fedora:latest \
        -f Containerfile .
    
    # Build Alpine image  
    echo "Building Alpine image..."
    podman build -t localhost/metisara-alpine:latest \
        --build-arg BASE_IMAGE=alpine:latest \
        -f Containerfile .
    
    # Build test image (same as Fedora for now)
    echo "Building test image..."
    podman build -t localhost/metisara-test:latest \
        --build-arg BASE_IMAGE=fedora:latest \
        -f Containerfile .
    
    echo "All images built successfully!"
}

# Start pod or containers (platform-specific)
start_pod() {
    check_podman_machine
    
    if [[ "$IS_MACOS" == "true" ]]; then
        echo "Starting Metisara containers (macOS mode)..."
        start_containers_macos
    else
        echo "Starting Metisara pod (Linux mode)..."
        podman play kube podman-pod.yml
        echo "Pod started! Use 'podman pod ps' to check status."
    fi
}

# Start containers individually for macOS compatibility
start_containers_macos() {
    # Create volumes if they don't exist
    podman volume create metisara-workspace-fedora 2>/dev/null || true
    podman volume create metisara-workspace-alpine 2>/dev/null || true
    podman volume create metisara-workspace-test 2>/dev/null || true
    
    # SELinux context flag for volume mounting
    local volume_flag=""
    if [[ "$IS_MACOS" == "true" ]]; then
        volume_flag=":Z"
    fi
    
    # Start Fedora container
    echo "Starting Fedora container..."
    podman run -d --name metisara-fedora \
        -v "$SCRIPT_DIR:/home/testuser/metisara-dev:ro${volume_flag}" \
        -v metisara-workspace-fedora:/home/testuser/metisara/workspace${volume_flag} \
        -e METISARA_ENV=development \
        -e PYTHONPATH=/home/testuser/metisara/src \
        -w /home/testuser/metisara \
        --init \
        localhost/metisara-fedora:latest \
        sleep infinity
    
    # Start Alpine container
    echo "Starting Alpine container..."
    podman run -d --name metisara-alpine \
        -v "$SCRIPT_DIR:/home/testuser/metisara-dev:ro${volume_flag}" \
        -v metisara-workspace-alpine:/home/testuser/metisara/workspace${volume_flag} \
        -e METISARA_ENV=development \
        -e PYTHONPATH=/home/testuser/metisara/src \
        -w /home/testuser/metisara \
        --init \
        localhost/metisara-alpine:latest \
        sleep infinity
    
    # Start test container
    echo "Starting test container..."
    podman run -d --name metisara-test \
        -v "$SCRIPT_DIR:/home/testuser/metisara-dev:ro${volume_flag}" \
        -v metisara-workspace-test:/home/testuser/metisara/workspace${volume_flag} \
        -v "$SCRIPT_DIR/tests/fixtures:/home/testuser/metisara/test-data:ro${volume_flag}" \
        -e METISARA_ENV=testing \
        -e PYTHONPATH=/home/testuser/metisara/src \
        -e JIRA_API_TOKEN=test-token-for-dry-run \
        -w /home/testuser/metisara \
        --init \
        localhost/metisara-test:latest \
        sleep infinity
    
    echo "All containers started! Use 'exec' command to enter them."
}

# Stop pod or containers (platform-specific)
stop_pod() {
    if [[ "$IS_MACOS" == "true" ]]; then
        echo "Stopping Metisara containers..."
        podman stop metisara-fedora metisara-alpine metisara-test 2>/dev/null || true
        podman rm metisara-fedora metisara-alpine metisara-test 2>/dev/null || true
        echo "Containers stopped and removed."
    else
        echo "Stopping Metisara pod..."
        podman pod stop metisara-pod || true
        podman pod rm metisara-pod || true
        echo "Pod stopped and removed."
    fi
}

# Exec into container
exec_container() {
    check_podman_machine
    local container_name=${1:-metisara-fedora}
    echo "Executing into container: $container_name"
    
    if [[ "$IS_MACOS" == "true" ]]; then
        # Check if container is running
        if ! podman ps --format "{{.Names}}" | grep -q "^$container_name$"; then
            echo "Container $container_name is not running. Starting containers first..."
            start_pod
        fi
        podman exec -it "$container_name" /bin/bash
    else
        podman exec -it "metisara-pod-$container_name" /bin/bash
    fi
}

# Show logs
show_logs() {
    local container_name=${1:-metisara-fedora}
    echo "Showing logs for container: $container_name"
    
    if [[ "$IS_MACOS" == "true" ]]; then
        podman logs "$container_name"
    else
        podman logs "metisara-pod-$container_name"
    fi
}

# Clean up everything
cleanup() {
    echo "Cleaning up Metisara containers and images..."
    stop_pod
    podman image rm localhost/metisara-fedora:latest || true
    podman image rm localhost/metisara-alpine:latest || true
    podman image rm localhost/metisara-test:latest || true
    podman volume rm metisara-workspace-fedora || true
    podman volume rm metisara-workspace-alpine || true
    podman volume rm metisara-workspace-test || true
    echo "Cleanup complete!"
}

# Show status
status() {
    check_podman_machine
    
    if [[ "$IS_MACOS" == "true" ]]; then
        echo "=== Podman Machine Status (macOS) ==="
        podman machine list
        echo ""
        echo "=== Container Status ==="
        podman ps -a --filter name=metisara
    else
        echo "=== Podman Pod Status ==="
        podman pod ps
        echo ""
        echo "=== Container Status ==="
        podman ps -a --filter label=app=metisara
    fi
    echo ""
    echo "=== Volume Status ==="
    podman volume ls | grep metisara || echo "No metisara volumes found"
}

# Show help
show_help() {
    cat << EOF
Metisara Podman Management Script

Usage: $0 [COMMAND]

Commands:
    build           Build all container images
    start           Start the pod with all containers
    stop            Stop and remove the pod
    exec [NAME]     Execute bash in container (default: metisara-fedora)
                    Available: metisara-fedora, metisara-alpine, metisara-test
    logs [NAME]     Show logs for container (default: metisara-fedora)
    status          Show pod, container, and volume status
    cleanup         Stop pod and remove all images and volumes
    help            Show this help message

Examples:
    $0 build                    # Build all images
    $0 start                    # Start the pod
    $0 exec metisara-fedora     # Enter Fedora container
    $0 exec metisara-alpine     # Enter Alpine container
    $0 exec metisara-test       # Enter test container
    $0 stop                     # Stop the pod
    $0 cleanup                  # Clean everything up

Note: This script replaces docker-compose functionality using Podman.
      - Linux: Uses Kubernetes pods for orchestration
      - macOS: Uses individual containers for better compatibility

Platform Detection:
    Automatically detects your operating system and adjusts behavior:
    - macOS: Manages Podman machine and uses individual containers
    - Linux: Uses pod-based orchestration with Kubernetes YAML

macOS Setup:
    If running on macOS, ensure Podman is installed:
    brew install podman
    
    The script will automatically initialize and start the Podman machine as needed.
EOF
}

# Main command handling
case "${1:-help}" in
    build)
        build_images
        ;;
    start)
        start_pod
        ;;
    stop)
        stop_pod
        ;;
    exec)
        exec_container "$2"
        ;;
    logs)
        show_logs "$2"
        ;;
    status)
        status
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information."
        exit 1
        ;;
esac