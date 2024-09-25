#!/bin/bash

# Initialize variables with default values
DOCKERFILE="./Dockerfile"
# Change this to the appropriate docker image name, if want to rebuild
TAG="aimilefth/pynq_alveo_docker:latest"

# Display the Dockerfile and tag being used
echo "Using Dockerfile: $DOCKERFILE"
echo "Tagging as: $TAG"

# Execute the Docker build and push command
docker buildx build -f "$DOCKERFILE" \
    --platform linux/amd64 \
    --tag "$TAG" \
    --push .

# Check if the Docker command was successful
if [ $? -eq 0 ]; then
    echo "Docker image built and pushed successfully as $TAG."
else
    echo "An error occurred during the Docker build and push process."
    exit 1
fi