# PYNQ ALVEO Autoencoder Project

This project provides a Docker-based environment for running and benchmarking LSTM-based autoencoder models on AMD ALVEO devices using the PYNQ framework.\
It includes scripts for building and running the Docker container, downloading necessary data, executing benchmarks, and measuring power consumption on both CPU and FPGA (AMD ALVEO) devices.


## Project Structure

```
.
├── README.md
├── docker
|   ├── Dockerfile                      # Dockerfile for building the Docker image
|   ├── docker_build.sh                 # Script to build and push the Docker image
|   └── setup.sh                        # Script for setting up the environment inside the Docker container
├── docker_run.sh                       # Script to run the Docker container with necessary configurations
├── download_data.sh                    # Script to download required data and models
├── mounted_dir
│   ├── autoencoder_alveo.py            # FPGA-based autoencoder implementation
│   ├── benchmarking_utils.py           # Utility functions for benchmarking
│   ├── cpu_power_scraper.py            # Script to scrape CPU power usage
│   ├── lstm.xclbin                     # Compact autoencoder bitstream file for AMD ALVEO
│   ├── models
│   │   └── rae.py                      # Baseline Autoencoder model definition
│   ├── power_scraper.py                # General power scraping utilities
│   ├── privateer_ae_parameters.json    # Configuration parameters for the baseline autoencoder
│   ├── pynq_alveo_demo_video.ipynb     # Jupyter notebook demonstrating the autoencoder execution
│   ├── rae_model_privateer_2.pth       # Baseline autoencoder model weights
│   ├── timeseries.json                 # Sample timeseries data for benchmarking
│   └── utils.py                        # Utility functions
└── src                                 # FPGA implementation source files
```

## Getting Started

### Prerequisites

- Docker installed on your system.
- Access to an AMD ALVEO U280 device and the necessary drivers installed.

### Installation

1. **Clone the repository:**

   ```shell
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Download the Required Data:**

   Run the `download_data.sh` script to download necessary model and bitstream files (rae_model_privateer_2.pth, lstm.xclbin):

   ```shell
   cd ..
   bash download_data.sh
   ```

3. **(Optional) Build the Docker Image:**

   Navigate to the `src` directory and build the Docker image using the provided script:

   ```shell
   cd src
   bash docker_build.sh
   ```

### Running the Docker Container

To start the Docker container with the appropriate settings, run the `docker_run.sh` script:

```shell
bash docker_run.sh
```

This script sets up the Docker container with the required devices, mounts necessary directories, and starts the Jupyter Notebook server accessible at `http://localhost:8888`.

This script performs the following:

- **Device Configuration**: Mounts necessary devices (e.g., ALVEO FPGA devices) into the container.
- **Volume Mounting**: Mounts the `mounted_dir` to `/setup_dir/Alveo-PYNQ/mounted_dir` inside the container.
- **Port Mapping**: Exposes port `8888` for Jupyter Notebook access.

Upon successful execution, the Jupyter Notebook server will be accessible at `http://localhost:8888`.


### Accessing the Demo notebook

Once the container is running, you can access the Demo notebook by navigating to the mounted directory within the Jupyter Notebook interface:

1. Open your web browser and go to `http://localhost:8888`.
2. Navigate to `mounted_dir/pynq_alveo_demo_video.ipynb` to open and run the Demo notebook.
