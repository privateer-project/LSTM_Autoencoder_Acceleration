#include <iomanip>
#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include "math.h"
#include "lstm.h"
#include "HLS_AE_SMALL/input.h"
#include "utils.h"
#include "lstm_fpga.h"

TIMER_INIT(6); //set number of timers to use


void save_outputs_to_file(const std::vector<std::vector<result_t>>& outputs, const std::string& filename) {
    std::ofstream out_file(filename);
    for (size_t i = 0; i < outputs.size(); ++i) {
        out_file << std::setw(5) << std::setfill('0') << i << ":";
        for (size_t j = 0; j < outputs[i].size(); ++j) {
            if (j != 0) {
                out_file << ",";
            }
            out_file << outputs[i][j];
        }
        out_file << std::endl;
    }
    out_file.close();
}

std::vector<input_t> parse_line_to_tensor(const std::string& line, size_t tensor_size) {
    std::vector<input_t> data(tensor_size);
    std::stringstream ss(line);
    std::string index;
    std::getline(ss, index, ':'); // Skip the index part

    for (size_t i = 0; i < tensor_size; ++i) {
        std::string value;
        std::getline(ss, value, ',');
        data[i] = std::stof(value);
    }

    return data;
}

int main(int argc, char * argv[]) {
    std::cout << "# Starting Testbench \n";

    const size_t tensor_size = N_TS * N1_LX; // Adjust this size based on your tensor dimensions
    std::vector<input_t> lstm_in(tensor_size);
    std::vector<result_t> lstm_out(MODEL_OUT);
    std::string xclbinFilename = argv[1];
    std::string input_file = argv[2];
    std::string output_file = argv[3];

    printf("------------------------------------------------------\n");
    printf("  Starting FPGA LSTM...                \n");
    printf("------------------------------------------------------\n");
    FPGA_LSTM * fpga = new FPGA_LSTM();

    TIMER_START(1);
    fpga->fpga_init(xclbinFilename);
    TIMER_STOP;

    std::ifstream in_file(input_file);
    if (!in_file) {
        std::cerr << "Unable to open file: " << input_file << std::endl;
        return 1;
    }

    std::vector<std::vector<result_t>> all_outputs;

    std::string line;
    int idx = 0;
    while (std::getline(in_file, line)) {
        lstm_in = parse_line_to_tensor(line, tensor_size);
        std::cout << idx << std::endl;

        std::fill(lstm_out.begin(), lstm_out.end(), 0);

        TIMER_START(5);
        fpga->run(lstm_in.data(), lstm_out.data());
        TIMER_STOP;

        printf("------------------------------------------------------\n");

        all_outputs.push_back(lstm_out);

        idx++;
    }
    std::cout << "Write to file: " << output_file << std::endl;
    save_outputs_to_file(all_outputs, output_file);

    std::cout << "# End of Testbench \n";

    fpga->print_performance_report();

    delete fpga;
    return 0;
}
