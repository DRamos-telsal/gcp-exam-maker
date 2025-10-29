#!/bin/bash

# --- Configuration ---
# !! SET THESE VARIABLES !!
PACKAGE_NAME="gcp-exam-maker"
VERSION="1.1.0"
MAINTAINER_NAME="Diego Ramos"
MAINTAINER_EMAIL="diegoxfer.ramos@gmail.com"
DESCRIPTION="A CLI tool to study for most of the professional certifications for Google Cloud."
# Add any runtime dependencies here, separated by commas
# For a simple Python script, 'python3' is the main one.
# If you use libraries like 'requests', you would add 'python3-requests'.
DEPENDENCIES="python3"
# --- End Configuration ---

# --- Script Logic ---
set -e # Exit immediately if a command exits with a non-zero status.

# Define build directory
BUILD_DIR="build"
PACKAGE_DIR="${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_all"

echo "--- Starting Debian Package Build for ${PACKAGE_NAME} ---"

# 1. Clean up previous build
echo "Cleaning up old build..."
rm -rf "${BUILD_DIR}"

# 2. Create the package directory structure
echo "Creating package structure..."
mkdir -p "${PACKAGE_DIR}/DEBIAN"
mkdir -p "${PACKAGE_DIR}/usr/bin"
mkdir -p "${PACKAGE_DIR}/usr/share/${PACKAGE_NAME}"



# 3. Create the 'control' file
echo "Creating DEBIAN/control file..."
cat << EOF > "${PACKAGE_DIR}/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Architecture: all
Maintainer: ${MAINTAINER_NAME} <${MAINTAINER_EMAIL}>
Depends: ${DEPENDENCIES}
Description: ${DESCRIPTION}

EOF

# 4. Copy application files
echo "Copying application files..."

# Copy the main executable script
# Assumes your modified main.py is in the current directory
cp main.py "${PACKAGE_DIR}/usr/bin/${PACKAGE_NAME}"

# Copy the data directory
# Assumes your 'pickles' directory is in the current directory
cp -r pickles/ "${PACKAGE_DIR}/usr/share/${PACKAGE_NAME}/"

# 5. Set permissions
echo "Setting file permissions..."
chmod 755 "${PACKAGE_DIR}/usr/bin/${PACKAGE_NAME}"

# 6. Build the .deb package
echo "Building .deb package..."
dpkg-deb --build "${PACKAGE_DIR}"

echo "--- Build Complete ---"
echo "Package created at: ${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"
echo "You can inspect its contents with: dpkg -c ${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"
echo "You can install it locally with: sudo apt install ./${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_all.deb"

set +e
