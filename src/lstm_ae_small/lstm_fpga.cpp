#include "lstm_fpga.h"

int FPGA_LSTM::print_performance_report(){

    double total_fpga_time = TIMER_REPORT_MS(1)+TIMER_REPORT_MS(2)+TIMER_REPORT_MS(3)+TIMER_REPORT_MS(4);
    double total_cpu_time = TIMER_REPORT_MS(5);

    printf("------------------------------------------------------\n");
    printf("  Performance Summary                                 \n");
    printf("------------------------------------------------------\n");
    printf("  Dataset read time          : %12.2f ms\n", TIMER_REPORT_MS(0));
    printf("  Device Initialization      : %12.2f ms\n", TIMER_REPORT_MS(1));
    printf("  Buffer Allocation          : %12.2f ms\n", TIMER_REPORT_MS(2));
    printf("  LSTM Computation            : %12.2f ms\n", TIMER_REPORT_MS(3));
    printf("  Buffer Deallocation        : %12.2f ms\n", TIMER_REPORT_MS(4));
    printf("------------------------------------------------------\n");
    /*
if(run_cpu)
      printf("  Total CPU Time             : %12.2f ms\n", total_cpu_time);
    printf("  Total FPGA Time            : %12.2f ms\n", total_fpga_time);
    if(run_cpu)
      printf("  Speed-up                   : %12.2f x\n", total_cpu_time/total_fpga_time);
    printf("------------------------------------------------------\n");
 */       
    return 0;
}

int FPGA_LSTM::fpga_init(std::string binaryFile) {

  cl_int err;

  // get_xil_devices() is a utility API which will find the xilinx
  // platforms and will return list of devices connected to Xilinx platform
  auto devices = xcl::get_xil_devices();
  // read_binary_file() is a utility API which will load the binaryFile
  // and will return the pointer to file buffer.
  auto fileBuf = xcl::read_binary_file(binaryFile);
  cl::Program::Binaries bins {
    {
      fileBuf.data(), fileBuf.size()
    }
  };
  bool valid_device = false;
  for (unsigned int i = 0; i < devices.size(); i++) {
    auto device = devices[i];
    // Creating Context and Command Queue for selected Device
    OCL_CHECK(err, m_context = cl::Context(device, nullptr, nullptr, nullptr, & err));
    OCL_CHECK(err,
      m_q = cl::CommandQueue(m_context, device,
        CL_QUEUE_PROFILING_ENABLE, & err));

    std::cout << "Trying to program device[" << i << "]: " << device.getInfo < CL_DEVICE_NAME > () << std::endl;
    m_prog = cl::Program(m_context, {
      device
    }, bins, nullptr, & err);
    if (err != CL_SUCCESS) {
      std::cout << "Failed to program device[" << i << "] with xclbin file!\n";
    } else {
      std::cout << "Device[" << i << "]: program successful!\n";
      valid_device = true;
      break; // we break because we found a valid device
    }
  }
  if (!valid_device) {
    std::cout << "Failed to program any device found, exit!\n";
    exit(EXIT_FAILURE);
  }

  for (int i = 0; i < NUM_CU; i++) {
    OCL_CHECK(err, lstm[i] = cl::Kernel(m_prog, "lstm", & err));
  }

  printf("Application compiled with NUM_CU = %d\n", NUM_CU);

  return 0;
}

void FPGA_LSTM::run(input_t * inputs, result_t * results) {

//	std::vector<std::pair<data_t, int>> distances;
  
  cl_int err;
  std::vector < cl::Buffer > in_buf(NUM_CU);
  std::vector < cl::Buffer > out_buf(NUM_CU);
  input_t * host_write_ptr_in[NUM_CU];
  result_t * host_read_ptr_out[NUM_CU];

  //measure fpga buffer allocation
  TIMER_START(2); 
  
std::vector < input_t, aligned_allocator < input_t > > lstm_in(N_TS * N1_LX);
std::vector < result_t, aligned_allocator < result_t > > lstm_out(MODEL_OUT);

  for (int i = 0; i < NUM_CU; i++) {
    OCL_CHECK(err, in_buf[i] = cl::Buffer(m_context, CL_MEM_ALLOC_HOST_PTR | CL_MEM_READ_ONLY, sizeof(input_t) * N_TS * N1_LX, NULL, & err));
    OCL_CHECK(err, out_buf[i] = cl::Buffer(m_context, CL_MEM_ALLOC_HOST_PTR | CL_MEM_WRITE_ONLY, sizeof(result_t) * MODEL_OUT, NULL, & err));
  }

  // Setting kernel arguments. Must be initialized before enqueueMapBuffer
  for (int i = 0; i < NUM_CU; i++) {
    int narg = 0;
    OCL_CHECK(err, err = lstm[i].setArg(narg++, in_buf[i]));
    OCL_CHECK(err, err = lstm[i].setArg(narg++, out_buf[i]));
  }

  for (int i = 0; i < NUM_CU; i++) {
    host_write_ptr_in[i] = (input_t * ) m_q.enqueueMapBuffer(in_buf[i], CL_TRUE, CL_MAP_WRITE, 0, sizeof(input_t) * N_TS * N1_LX);
    host_read_ptr_out[i] = (result_t * ) m_q.enqueueMapBuffer(out_buf[i], CL_TRUE, CL_MAP_READ, 0, sizeof(result_t) * MODEL_OUT);
  }

  TIMER_STOP;
  
  TIMER_START(3);
memcpy(host_write_ptr_in[0], &inputs[0], sizeof(input_t) * N_TS * N1_LX);
     
            //data_t dist = DTWDistance(training_data + i*N_FEATURES, input_data, W);  
            
            OCL_CHECK(err, err = m_q.enqueueMigrateMemObjects({
              in_buf[0]
            }, 0));
            OCL_CHECK(err, err = m_q.enqueueTask(lstm[0]));
            OCL_CHECK(err, err = m_q.enqueueMigrateMemObjects({
              out_buf[0]
            }, CL_MIGRATE_MEM_OBJECT_HOST));
            OCL_CHECK(err, err = m_q.finish());
            //retrieve the lstm_output from the output ptr 
        	memcpy(&results[0], host_read_ptr_out[0], sizeof(result_t) * MODEL_OUT);

  TIMER_STOP;
  
  //measure buffer deallocation time
  TIMER_START(4);
  for (int i = 0; i < NUM_CU; i++) {
    OCL_CHECK(err, err = m_q.enqueueUnmapMemObject(in_buf[i], host_write_ptr_in[i]));
    OCL_CHECK(err, err = m_q.enqueueUnmapMemObject(out_buf[i], host_read_ptr_out[i]));
  }
  OCL_CHECK(err, err = m_q.finish());
  TIMER_STOP;
  
  
  return;
}
