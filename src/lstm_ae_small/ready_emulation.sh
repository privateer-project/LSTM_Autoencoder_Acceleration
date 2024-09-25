# RUN AS SOURCE (https://docs.amd.com/r/en-US/ug1393-vitis-application-acceleration/Running-Emulation-Targets)

# Check if TARGET and DEVICE environment variables are set
if [ $# -ne 2 ]; then
  echo "Error: TARGET and DEVICE parameters must be provided."
  echo "Usage: source sw_emulation_steps.sh <sw_emu/hw_emu> <your_device_platform>"
  return 1
fi

# Set TARGET and DEVICE from parameters
TARGET=$1
DEVICE=$2

# Run emconfig with the specified platform
emconfigutil --platform $DEVICE

# Set the emulation mode
export XCL_EMULATION_MODE=$TARGET
echo "XCL_EMULATION_MODE set to $XCL_EMULATION_MODE"
