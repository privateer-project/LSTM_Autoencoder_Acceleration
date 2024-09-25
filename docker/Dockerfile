FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ARG XRT_URL=https://www.xilinx.com/bin/public/openDownload?filename=xrt_202320.2.16.204_20.04-amd64-xrt.deb
ARG XRT_NAME=xrt_202320.2.16.204_20.04-amd64-xrt.deb

# APT Installs
RUN apt update && \
    apt install curl=7.68.0-1ubuntu2.23 git=1:2.25.1-1ubuntu3.13 python3-pip=20.0.2-5ubuntu1.10 -y

# Install python libraries
RUN pip install --upgrade pip
# Download only cpu torch 
RUN pip install torch==2.3.0+cpu torchvision==0.18.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install pynq==3.0.1 jupyter==1.1.1 matplotlib==3.7.5 pyjoules==0.5.1 pandas==2.0.3

# Workspace setup
ARG SETUP_DIR_ARG=/setup_dir
ARG SETUP_FILE_ARG=setup.sh
ENV SETUP_DIR=${SETUP_DIR_ARG}
ENV SETUP_FILE=${SETUP_FILE_ARG}

# Create working directory and copy setup file
RUN mkdir -p ${SETUP_DIR_ARG}
COPY ${SETUP_FILE} ${SETUP_DIR_ARG}

# Setting the working directory
WORKDIR ${SETUP_DIR_ARG}

# Modify permissions and ownership of setup file and working directory
RUN chmod u+x ${SETUP_FILE_ARG}

# Install XRT
RUN curl -L -o ${XRT_NAME} ${XRT_URL} && \
    apt-get update && \
    apt install ./${XRT_NAME} -y && \
    rm ${XRT_NAME}

EXPOSE 8888

CMD bash -c "source ${SETUP_DIR}/${SETUP_FILE} && jupyter notebook --ip=0.0.0.0 --allow-root --NotebookApp.iopub_data_rate_limit=1.0e10"
