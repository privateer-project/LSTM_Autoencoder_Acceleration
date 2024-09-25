#!/bin/bash

# Initialize variables with default values
IMAGE_TAG="aimilefth/pynq_alveo_docker:latest"
DOCKERFILE_OPTION=""


# Current working directory
CURRENT_PATH=$(pwd)
# Docker run mode
DETACHED="-it"

# Function to collect Docker device options
collect_docker_devices() {
    local devices=""

    echo "Collecting Docker device options..." >&2

    # Find xclmgmt devices
    local xclmgmt_drivers
    xclmgmt_drivers=$(find /dev -name "xclmgmt*" 2>/dev/null)
    for device in ${xclmgmt_drivers}; do
        devices+="--device=${device} "
    done

    # Find renderD devices
    local render_drivers
    render_drivers=$(find /dev/dri -name "renderD*" 2>/dev/null)
    for device in ${render_drivers}; do
        devices+="--device=${device} "
    done

    echo "Docker devices collected: ${devices}" >&2
    echo "${devices}"
}

# Collect Docker device options
docker_devices=$(collect_docker_devices)

# Define Docker run parameters with conditional GPU option
docker_run_params=$(cat <<-END
    -v /dev/shm:/dev/shm \
    -v /opt/xilinx/dsa:/opt/xilinx/dsa \
    -v /opt/xilinx/overlaybins:/opt/xilinx/overlaybins \
    -v /etc/xbutler:/etc/xbutler \
    -v /scrape:/scrape \
    --privileged \
    -v ${CURRENT_PATH}/mounted_dir:/setup_dir/Alveo-PYNQ/mounted_dir \
    -p 8888:8888 \
    --pull=always \
    --network=host \
    ${DETACHED} \
    ${IMAGE_TAG}
END
)

echo "Docker run parameters configured."

# Execute the Docker run command
echo "Running Docker container with image: ${IMAGE_TAG}"
docker run \
  ${docker_devices} \
  ${docker_run_params}