#!/bin/bash

# URLs for the downloads
XCLBIN_URL="https://upatrasgr-my.sharepoint.com/:x:/g/personal/up1053647_upatras_gr/EQ4lTZDX7NNNivoN710RyX8Bsjemckk4ARD-TRt72hDxNg?download=1"
MODEL_URL="https://upatrasgr-my.sharepoint.com/:x:/g/personal/up1053647_upatras_gr/EWPahFXohExKi02JTg8GUdEBgYUY8MRX3Gd5W5LGRqZixQ?download=1"

# Directory to store downloaded and extracted files
DOWNLOAD_DIR="./mounted_dir"

# Function to log progress
log_progress() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Generic function to download and unzip a file
download_model() {
    local url="$1"
    local zip_name="$2"

    log_progress "Ensuring directory ${DOWNLOAD_DIR} exists."
    mkdir -p "${DOWNLOAD_DIR}"

    log_progress "Downloading ${zip_name}."
    if ! wget --content-disposition -O "${DOWNLOAD_DIR}/${zip_name}" "${url}"; then
        log_progress "Error downloading ${zip_name}."
        return 1
    fi

    log_progress "Unzipping ${zip_name} to ${DOWNLOAD_DIR}."
    if ! unzip -o "${DOWNLOAD_DIR}/${zip_name}" -d "${DOWNLOAD_DIR}"; then
        log_progress "Error unzipping ${zip_name}."
        return 1
    fi

    log_progress "Removing ${zip_name}."
    rm "${DOWNLOAD_DIR}/${zip_name}"
}

# Main script execution
main() {
    log_progress "Starting download processes."

    # Download lstm_float_xclbin.zip
    download_model "${XCLBIN_URL}" "lstm_float_xclbin.zip" || log_progress "Xclbin download process failed."

    # Download lstm_float.pth.zip
    download_model "${MODEL_URL}" "lstm_float.pth.zip" || log_progress "Model download process failed."

    log_progress "All tasks completed."
}

# Run the main function
main