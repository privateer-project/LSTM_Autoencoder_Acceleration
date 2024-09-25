#
# Copyright 2019-2021 Xilinx, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# makefile-generator v1.0.3
#

############################## Help Section ##############################
.PHONY: help

help::
	$(ECHO) "Makefile Usage:"
	$(ECHO) "  make all TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> EDGE_COMMON_SW=<rootfs and kernel image path>"
	$(ECHO) "      Command to generate the design for specified Target and Shell."
	$(ECHO) ""
	$(ECHO) "  make clean "
	$(ECHO) "      Command to remove the generated non-hardware files."
	$(ECHO) ""
	$(ECHO) "  make cleanall"
	$(ECHO) "      Command to remove all the generated files."
	$(ECHO) ""
	$(ECHO) "  make test DEVICE=<FPGA platform>"
	$(ECHO) "      Command to run the application. This is same as 'run' target but does not have any makefile dependency."
	$(ECHO) ""
	$(ECHO) "  make sd_card TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> EDGE_COMMON_SW=<rootfs and kernel image path>"
	$(ECHO) "      Command to prepare sd_card files."
	$(ECHO) ""
	$(ECHO) "  make run TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> EDGE_COMMON_SW=<rootfs and kernel image path>"
	$(ECHO) "      Command to run application in emulation."
	$(ECHO) ""
	$(ECHO) "  make build TARGET=<sw_emu/hw_emu/hw> DEVICE=<FPGA platform> HOST_ARCH=<aarch32/aarch64/x86> EDGE_COMMON_SW=<rootfs and kernel image path>"
	$(ECHO) "      Command to build xclbin application."
	$(ECHO) ""
	$(ECHO) "  make host HOST_ARCH=<aarch32/aarch64/x86> EDGE_COMMON_SW=<rootfs and kernel image path>"
	$(ECHO) "      Command to build host application."
	$(ECHO) "  By default, HOST_ARCH=x86. HOST_ARCH and EDGE_COMMON_SW is required for SoC shells"
	$(ECHO) ""
	$(ECHO) "  make large_host HOST_ARCH=<aarch32/aarch64/x86> EDGE_COMMON_SW=<rootfs and kernel image path>"
	$(ECHO) "      Command to build large_host application."
	$(ECHO) "  By default, HOST_ARCH=x86. HOST_ARCH and EDGE_COMMON_SW is required for SoC shells"

############################## Setting up Project Variables ##############################
# Points to top directory of Git repository
FOLDER = $(pwd)
MK_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
#COMMON_REPO ?= $(shell bash -c 'export MK_PATH=$(MK_PATH); echo $${MK_PATH%cpp_kernels/simple_vadd/*}')
COMMON_REPO ?= $(shell bash -c 'export MK_PATH=$(MK_PATH); echo $${MK_PATH%$(FOLDER)/*}')
PWD = $(shell readlink -f .)
XF_PROJ_ROOT = $(shell readlink -f $(COMMON_REPO))


TARGET := hw
HOST_ARCH := x86
SYSROOT := 

include ./utils.mk

XSA := 
ifneq ($(DEVICE), )
XSA := $(call device2xsa, $(DEVICE))
endif
TEMP_DIR := ./_x.$(TARGET).$(XSA)
BUILD_DIR := ./build_dir.$(TARGET).$(XSA)

# SoC variables
RUN_APP_SCRIPT = ./run_app.sh
PACKAGE_OUT = ./package.$(TARGET)

LAUNCH_EMULATOR = $(PACKAGE_OUT)/launch_$(TARGET).sh
RESULT_STRING = TEST PASSED

VPP := v++
VPP_PFLAGS := 
CMD_ARGS = $(BUILD_DIR)/lstm.xclbin
SDCARD := sd_card

include $(XF_PROJ_ROOT)/common/includes/opencl/opencl.mk
CXXFLAGS += $(opencl_CXXFLAGS) -Wall -O0 -g -std=c++1y
LDFLAGS += $(opencl_LDFLAGS)

#ifeq ($(TARGET),hw)
#CXXFLAGS += -D__SYNTHESIS__
#VPP_PFLAGS += -D__SYNTHESIS__
#endif

ifeq ($(findstring nodma, $(DEVICE)), nodma)
$(error [ERROR]: This example is not supported for $(DEVICE).)
endif

############################## Setting up Host Variables ##############################
#Include Required Host Source Files
CXXFLAGS += -I$(XF_PROJ_ROOT)/common/includes/xcl2 -I../nnet_utils/
HOST_SRCS += $(XF_PROJ_ROOT)/common/includes/xcl2/xcl2.cpp ./tb_lstm.cpp ./lstm_fpga.cpp
# Host compiler global settings
CXXFLAGS += -fmessage-length=0
LDFLAGS += -lrt -lstdc++

ifneq ($(HOST_ARCH), x86)
	LDFLAGS += --sysroot=$(SYSROOT)
endif

LARGE_HOST_SRCS = $(XF_PROJ_ROOT)/common/includes/xcl2/xcl2.cpp ./tb_large_lstm.cpp ./lstm_fpga.cpp
LARGE_EXECUTABLE = ./lstm_large_app

############################## Setting up Kernel Variables ##############################
# Kernel compiler global settings
VPP_FLAGS += -t $(TARGET) --platform $(DEVICE) --report_level estimate --hls.clock 200000000:lstm --save-temps  --hls.jobs 8 --config conn_u200.cfg 
ifneq ($(TARGET), hw)
	VPP_FLAGS += -g
endif



EXECUTABLE = ./lstm_app
EMCONFIG_DIR = $(TEMP_DIR)
EMU_DIR = $(SDCARD)/data/emulation

############################## Declaring Binary Containers ##############################
BINARY_CONTAINERS += $(BUILD_DIR)/lstm.xclbin
BINARY_CONTAINER_lstm_OBJS += $(TEMP_DIR)/lstm.xo

############################## Setting Targets ##############################
CP = cp -rf

.PHONY: all clean cleanall docs emconfig
all: check-devices $(EXECUTABLE) $(BINARY_CONTAINERS) emconfig sd_card

.PHONY: host
host: $(EXECUTABLE)

.PHONY: build
build: check-vitis $(BINARY_CONTAINERS)

.PHONY: xclbin
xclbin: build

.PHONY: large_host
large_host: $(LARGE_EXECUTABLE)

############################## Setting Rules for Binary Containers (Building Kernels) ##############################
$(TEMP_DIR)/lstm.xo: lstm.cpp
	mkdir -p $(TEMP_DIR)
	$(VPP) $(VPP_FLAGS) -c -k lstm --temp_dir $(TEMP_DIR)  -I'$(<D)' -o'$@' '$<'
$(BUILD_DIR)/lstm.xclbin: $(BINARY_CONTAINER_lstm_OBJS)
	mkdir -p $(BUILD_DIR)
ifeq ($(HOST_ARCH), x86)
	$(VPP) $(VPP_FLAGS) -l $(VPP_LDFLAGS) --temp_dir $(TEMP_DIR) -o'$(BUILD_DIR)/lstm.link.xclbin' $(+)
	$(VPP) -p $(BUILD_DIR)/lstm.link.xclbin -t $(TARGET) --platform $(DEVICE) --package.out_dir $(PACKAGE_OUT) -o $(BUILD_DIR)/lstm.xclbin
else
	$(VPP) $(VPP_FLAGS) -l $(VPP_LDFLAGS) --temp_dir $(TEMP_DIR) -o'$(BUILD_DIR)/lstm.xclbin' $(+)
endif

############################## Setting Rules for Host (Building Host Executable) ##############################
$(EXECUTABLE): $(HOST_SRCS) | check-xrt
		$(CXX) -o $@ $^ $(CXXFLAGS) $(LDFLAGS)

emconfig:$(EMCONFIG_DIR)/emconfig.json
$(EMCONFIG_DIR)/emconfig.json:
	emconfigutil --platform $(DEVICE) --od $(EMCONFIG_DIR)

############################## Adding Rules for Large Host (Building Large Host Executable) ##############################

$(LARGE_EXECUTABLE): $(LARGE_HOST_SRCS)
		$(CXX) -o $@ $^ $(CXXFLAGS) $(LDFLAGS)
############################## Setting Rules for Software Testing (Building Host Executable) ##############################
# Add new source file
SOFTWARE_HOST_SRCS += $(XF_PROJ_ROOT)/common/includes/xcl2/xcl2.cpp ./software_tb_lstm.cpp ./lstm.cpp

# Define new executable name
SOFTWARE_EXECUTABLE = ./software_lstm_app

# Add new target to build the software testbench executable
.PHONY: software_tb
software_tb: $(SOFTWARE_EXECUTABLE)

# Rule to create the software testbench executable
$(SOFTWARE_EXECUTABLE): $(SOFTWARE_HOST_SRCS)
	$(CXX) -o $@ $^ $(CXXFLAGS) $(LDFLAGS)

############################## Setting Essential Checks and Running Rules ##############################
run: all
ifeq ($(TARGET),$(filter $(TARGET),sw_emu hw_emu))
ifeq ($(HOST_ARCH), x86)
	$(CP) $(EMCONFIG_DIR)/emconfig.json .
	XCL_EMULATION_MODE=$(TARGET) $(EXECUTABLE) $(CMD_ARGS)
else
	$(LAUNCH_EMULATOR) -run-app $(RUN_APP_SCRIPT) | tee run_app.log; exit $${PIPESTATUS[0]}
endif
else
ifeq ($(HOST_ARCH), x86)
	$(EXECUTABLE) $(CMD_ARGS)
endif
endif


.PHONY: test
test: $(EXECUTABLE)
ifeq ($(TARGET),$(filter $(TARGET),sw_emu hw_emu))
ifeq ($(HOST_ARCH), x86)
	XCL_EMULATION_MODE=$(TARGET) $(EXECUTABLE) $(CMD_ARGS)
else
	$(LAUNCH_EMULATOR) -run-app $(RUN_APP_SCRIPT) | tee run_app.log; exit $${PIPESTATUS[0]}
endif
else
ifeq ($(HOST_ARCH), x86)
	$(EXECUTABLE) $(CMD_ARGS)
else
	$(ECHO) "Please copy the content of sd_card folder and data to an SD Card and run on the board"
endif
endif


############################## Preparing sdcard ##############################
sd_card: $(BINARY_CONTAINERS) $(EXECUTABLE) gen_run_app
ifneq ($(HOST_ARCH), x86)
	$(VPP) $(VPP_PFLAGS) -p $(BUILD_DIR)/lstm.xclbin -t $(TARGET) --platform $(DEVICE) --package.out_dir $(PACKAGE_OUT) --package.rootfs $(EDGE_COMMON_SW)/rootfs.ext4 --package.sd_file $(SD_IMAGE_FILE) --package.sd_file xrt.ini --package.sd_file $(RUN_APP_SCRIPT) --package.sd_file $(EXECUTABLE) -o lstm.xclbin
endif

############################## Cleaning Rules ##############################
# Cleaning stuff
clean:
	-$(RMDIR) $(EXECUTABLE) $(SOFTWARE_EXECUTABLE) $(LARGE_EXECUTABLE) $(XCLBIN)/{*sw_emu*,*hw_emu*} 
	-$(RMDIR) profile_* TempConfig system_estimate.xtxt *.rpt *.csv 
	-$(RMDIR) src/*.ll *v++* .Xil emconfig.json dltmp* xmltmp* *.log *.jou *.wcfg *.wdb

cleanall: clean
	-$(RMDIR) build_dir* sd_card*
	-$(RMDIR) package.*
	-$(RMDIR) _x* *xclbin.run_summary qemu-memory-_* emulation _vimage pl* start_simulation.sh *.xclbin .run

