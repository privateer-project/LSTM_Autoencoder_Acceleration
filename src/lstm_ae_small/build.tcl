
open_project -reset prj_vivado

set_top lstm
add_files lstm_fpga.cpp -cflags "-std=c++0x"
add_files /home/dimdano/Desktop/PRIVATEER/RNN_HLS_custom/lstm_ae_small/common/includes/xcl2/xcl2.cpp -cflags "-std=c++0x"
add_files -tb tb_lstm.cpp -cflags "-std=c++0x" 
add_files /home/dimdano/Desktop/PRIVATEER/RNN_HLS_custom/lstm_ae_small/common/includes/xcl2/xcl2.hpp -cflags "-std=c++0x"
add_files ../nnet_utils/ -cflags "-std=c++0x"

open_solution -reset "cmd_z7045_ae_r1"
#  open_solution "cmd_ku115_mnist_r1"

#catch {config_array_partition -maximum_size 4096}


set_part {xcu200-fsgd2104-2-e}
create_clock -period 300MHz -name default

#set_part {xcku115-flvb2104-2-i}
#create_clock -period 5 -name default

#set_part {xcu250-figd2104-2L-e}
#create_clock -period 300MHz -name default

csim_design
csynth_design
add_files -tb tb_lstm.cpp -cflags "-std=c++0x -DRTL_SIM"
cosim_design -trace_level all


exit
