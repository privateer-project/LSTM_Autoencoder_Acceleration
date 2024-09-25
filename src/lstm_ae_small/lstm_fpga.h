#include "parameters.h"

#include "utils.h"

#define NUM_CU 1

class FPGA_LSTM {
  public:
    void run(input_t * inputs, result_t * results);
    int fpga_init(string binaryFile);
    int print_performance_report();
    //int *memberships = new int[N_SERIES];
        
    
  private:

    cl::Context m_context;
    cl::CommandQueue m_q;
    cl::Program m_prog;
    cl::Kernel lstm[NUM_CU];

};
