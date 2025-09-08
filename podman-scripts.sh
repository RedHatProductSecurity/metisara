#!/bin/bash
# Podman scripts for Metisara development environments
# Replaces docker-compose functionality with Podman pods

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Build images
build_images() {
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

# Start pod
start_pod() {
    echo "Starting Metisara pod..."
    podman play kube podman-pod.yml
    echo "Pod started! Use 'podman pod ps' to check status."
}

# Stop pod
stop_pod() {
    echo "Stopping Metisara pod..."
    podman pod stop metisara-pod || true
    podman pod rm metisara-pod || true
    echo "Pod stopped and removed."
}

# Exec into container
exec_container() {
    local container_name=${1:-metisara-fedora}
    echo "Executing into container: $container_name"
    podman exec -it "metisara-pod-$container_name" /bin/bash
}

# Show logs
show_logs() {
    local container_name=${1:-metisara-fedora}
    echo "Showing logs for container: $container_name"
    podman logs "metisara-pod-$container_name"
}

# Clean up everything
cleanup() {
    echo "Cleaning up Metisara pod and images..."
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
    echo "=== Podman Pod Status ==="
    podman pod ps
    echo ""
    echo "=== Container Status ==="
    podman ps -a --filter label=app=metisara
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

Note: This script replaces docker-compose functionality using Podman pods.
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