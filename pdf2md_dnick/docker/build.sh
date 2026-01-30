#!/bin/bash
# =============================================================================
# Build script for PDF2MD Docker images
# =============================================================================
# Usage:
#   ./docker/build.sh           # Build all images
#   ./docker/build.sh base      # Build only base
#   ./docker/build.sh easyocr   # Build base + easyocr
#   ./docker/build.sh full      # Build full image (standalone)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

build_base() {
    log_info "Building pdf2md-base..."
    docker build -f docker/Dockerfile.base -t pdf2md-base:latest .
    log_info "pdf2md-base built successfully"
}

build_easyocr() {
    log_info "Building pdf2md-easyocr..."
    docker build -f docker/Dockerfile.easyocr -t pdf2md-easyocr:latest .
    log_info "pdf2md-easyocr built successfully"
}

build_pytesseract() {
    log_info "Building pdf2md-pytesseract..."
    docker build -f docker/Dockerfile.pytesseract -t pdf2md-pytesseract:latest .
    log_info "pdf2md-pytesseract built successfully"
}

build_marker() {
    log_info "Building pdf2md-marker..."
    docker build -f docker/Dockerfile.marker -t pdf2md-marker:latest .
    log_info "pdf2md-marker built successfully"
}

build_full() {
    log_info "Building pdf2md-full (standalone)..."
    docker build -f docker/Dockerfile.full -t pdf2md-full:latest .
    log_info "pdf2md-full built successfully"
}

build_all() {
    log_info "Building all images..."
    build_base
    build_easyocr
    build_pytesseract
    build_marker
    log_info "All layered images built successfully"
    echo ""
    log_info "To build the full standalone image, run: ./docker/build.sh full"
}

# Parse arguments
case "${1:-all}" in
    base)
        build_base
        ;;
    easyocr)
        build_base
        build_easyocr
        ;;
    pytesseract)
        build_base
        build_pytesseract
        ;;
    marker)
        build_base
        build_marker
        ;;
    full)
        build_full
        ;;
    all)
        build_all
        ;;
    *)
        echo "Usage: $0 {base|easyocr|pytesseract|marker|full|all}"
        exit 1
        ;;
esac

echo ""
log_info "Done! Available images:"
docker images | grep pdf2md || true
