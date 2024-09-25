// testbench.cpp
 
#include <iomanip>
#include <fstream>
#include <iostream>
#include "math.h"
#include "lstm.h"
#include "HLS_AE_SMALL/input.h"
#include "utils.h"
#include "lstm_fpga.h"

TIMER_INIT(6); //set number of timers to use

int main(int argc, char * argv[]) {
    std::cout << "# Starting Testbench \n";

    const int BATCH=1;
//std::vector < input_t, aligned_allocator < input_t > > lstm_in(N_TS * N1_LX);
//std::vector < result_t, aligned_allocator < result_t > > lstm_out(MODEL_OUT);
    input_t lstm_in[N_TS*N1_LX];
    result_t lstm_out[MODEL_OUT];
    string xclbinFilename = argv[1];
int REPEAT = atoi(argv[2]);

  printf("------------------------------------------------------\n");
  printf("  Starting FPGA LSTM...                \n");
  printf("------------------------------------------------------\n");
  FPGA_LSTM * fpga = new FPGA_LSTM();

  TIMER_START(1);
  fpga -> fpga_init(xclbinFilename);
  TIMER_STOP;


    for (int k = 0; k < BATCH; k++) {
    	std::cout <<"\n input ";
    	for (int i = 0; i < N_TS*N1_LX; i++) {
    		//conv_out[i] = 0;
    		lstm_in[i] = input[k*N_TS*N1_LX+i];
    		std::cout <<", "<< lstm_in[i];
    	}
    	for (int i = 0; i < MODEL_OUT; i++) {
    		lstm_out[i] =0;
    	}

//    	lstm(lstm_in, lstm_out);
  TIMER_START(5);
for(int r = 0; r < REPEAT; ++r) {
  fpga -> run(lstm_in, lstm_out);
}
TIMER_STOP;
  printf("------------------------------------------------------\n");

    	std::cout <<"\n output ";
    	for(int ff = 0; ff < MODEL_OUT; ff++) {
    		std::cout <<", "<< lstm_out[ff];
    	}
    	std::cout << "\n";
    }

    std::cout << "# End of Testbench \n";

  
  fpga -> print_performance_report();
  
  
  delete fpga;

    //            return 0;
}
