#!/bin/bash

# Function to show usage
usage() {
    echo "Usage: $0 target_directory"
    exit 1
}

# Check if the target directory is provided
if [ -z "$1" ]; then
    usage
fi

TARGET_DIR=$1

# Create the target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy .log files
find . -type f -name "*.log" -exec rsync -R {} "$TARGET_DIR/" \;

# Copy the prj_cmd directory
rsync -a --progress prj_cmd "$TARGET_DIR/"

# Copy the build_dir.hw.* directories
find . -type d -name "build_dir.hw.*" -exec rsync -a --progress {} "$TARGET_DIR/" \;

# Copy the .Xil directory
rsync -a --progress .Xil "$TARGET_DIR/"

# Copy the package.hw directory
rsync -a --progress package.hw "$TARGET_DIR/"

# Copy the _x directory
rsync -a --progress _x "$TARGET_DIR/"

# Copy the _x.hw.* directories excluding specified subdirectories
find . -type d -name "_x.hw.*" -exec rsync -a --progress --exclude='link/vivado/vpl/prj/prj.gen' --exclude='link/vivado/vpl/prj/prj.runs' --exclude='link/vivado/vpl/.local/hw_platform' {} "$TARGET_DIR/" \;

# Copy the lstm_app file
rsync -a --progress lstm_app "$TARGET_DIR/"


echo "Files and directories have been copied to $TARGET_DIR"
