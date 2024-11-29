#!/bin/bash

set -e  # Exit on any error

# Configuration
PYTHON_VERSION=${1:-python3.9}  # Allow passing Python version as an argument
BUILD_DIR="../build"
SOURCE_DIR="../lambda"
ZIP_FILE="lambda.zip"

# Create a build directory (if it doesn't exist)
mkdir -p $BUILD_DIR

# Navigate to the source directory
cd $SOURCE_DIR

# Copy necessary files to the build directory
cp -r . $BUILD_DIR

# Navigate to the build directory
cd $BUILD_DIR

# Create and activate a virtual environment
virtualenv -p $PYTHON_VERSION venv
source venv/bin/activate

# Install dependencies
if [ ! -f requirements.txt ]; then
    echo "Error: requirements.txt not found."
    exit 1
fi
pip install -r requirements.txt

# Copy dependencies
cp -r venv/lib/${PYTHON_VERSION}/site-packages/* .

# Cleanup virtual environment and unnecessary files
rm -rf venv __pycache__

# Create a ZIP package
zip -r $ZIP_FILE .

# Move the ZIP file to the parent directory
rm -f ../$ZIP_FILE
mv $ZIP_FILE ../

# Clean up build directory

rm -rf $BUILD_DIR

echo "Packaging complete: $ZIP_FILE"
