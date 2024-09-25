/**
 * @file parameters.h
 * @brief Defines configuration parameters and data types for the LSTM model.
 *
 * This header file includes various parameters for configuring the LSTM layers,
 * dense layers, and data types used in the neural network model. The parameters
 * control aspects such as the number of timesteps, hidden layer sizes, data types,
 * and resource reuse factors for efficient FPGA implementation.
 *
 * @note All defined parameters are crucial for the configuration and performance
 *       of the neural network model on FPGA hardware.
 *
 * @def DEBUG
 * @brief Debug flag to enable or disable debug output.
 *
 * @def ACT_TTL_BIT
 * @brief Total number of bits for the activation data type.
 *
 * @def ACT_INT_BIT
 * @brief Number of integer bits for the activation data type.
 *
 * @def ACC_TTL_BIT
 * @brief Total number of bits for the accumulator data type.
 *
 * @def ACC_INT_BIT
 * @brief Number of integer bits for the accumulator data type.
 *
 * @def N_TS
 * @brief Number of timesteps for the LSTM layers.
 *
 * @def N1_LX
 * @brief Input size for the first LSTM layer.
 *
 * @def N1_LH
 * @brief Hidden size for the first LSTM layer.
 *
 * @def N2_LX
 * @brief Input size for the second LSTM layer, equal to the hidden size of the first layer.
 *
 * @def N2_LH
 * @brief Hidden size for the second LSTM layer.
 *
 * @def DENSE1_OUT
 * @brief Output size for the dense layer, equal to the input size of the first LSTM layer.
 *
 * @def DENSE1_IN
 * @brief Input size for the dense layer, equal to the hidden size of the second LSTM layer.
 *
 * @def MODEL_OUT
 * @brief Total output size of the model, defined as DENSE1_OUT * N_TS.
 *
 * @def R_TS
 * @brief Reuse factor for timesteps, where N_TS means no unroll.
 *
 * @def R1_H
 * @brief Reuse factor for hidden layers in the first LSTM layer.
 *
 * @def R2_H
 * @brief Reuse factor for hidden layers in the second LSTM layer.
 *
 * @def R1_TAIL
 * @brief Reuse factor for the tail computations in the first LSTM layer.
 *
 * @def R2_TAIL
 * @brief Reuse factor for the tail computations in the second LSTM layer.
 *
 * @def R1_X
 * @brief Derived reuse factor for computations involving both hidden and tail layers in the first LSTM layer.
 *
 * @def R2_X
 * @brief Derived reuse factor for computations involving both hidden and tail layers in the second LSTM layer.
 *
 * @def R_DENSE1
 * @brief Reuse factor for the dense layer.
 *
 * @typedef act_default_t
 * @brief Default data type for activations, set to float.
 *
 * @typedef acc_default_t
 * @brief Default data type for accumulators, set to float.
 *
 * @typedef model_default_t
 * @brief Default data type for the model, set to float.
 *
 * @typedef accum_lstm_t
 * @brief Data type for LSTM accumulators, set to float.
 *
 * @typedef input_t
 * @brief Data type for model input, set to float.
 *
 * @typedef result_t
 * @brief Data type for model output, set to float.
 *
 * @typedef model_biases_t
 * @brief Data type for model biases, set to float.
 *
 * @typedef mult_p_t
 * @brief Data type for multipliers, set to float.
 *
 * @struct config1
 * @brief Configuration for the first LSTM layer.
 *
 * @struct config2
 * @brief Configuration for the activation function following the first LSTM layer.
 *
 * @struct config_x
 * @brief Configuration for the dense layer applied to the input of the first LSTM layer.
 *
 * @struct config_h
 * @brief Configuration for the dense layer applied to the hidden state of the first LSTM layer.
 *
 * @struct config1_lstm2
 * @brief Configuration for the second LSTM layer.
 *
 * @struct config2_lstm2
 * @brief Configuration for the activation function following the second LSTM layer.
 *
 * @struct config_x_lstm2
 * @brief Configuration for the dense layer applied to the input of the second LSTM layer.
 *
 * @struct config_h_lstm2
 * @brief Configuration for the dense layer applied to the hidden state of the second LSTM layer.
 *
 * @struct config3
 * @brief Configuration for the final dense layer applied after the second LSTM layer.
 */

#ifndef PARAMETERS_H_
#define PARAMETERS_H_

#include <complex>
#include "ap_int.h"
#include "ap_fixed.h"

#include "../nnet_utils/nnet_lstm.h"
#include "../nnet_utils/nnet_activation.h"
#include "../nnet_utils/nnet_dense.h"

// Debug flag to enable or disable debug output.
#define DEBUG 1

// Total and integer bits for the activation data type. (not used when float)
#define ACT_TTL_BIT 16
#define ACT_INT_BIT 2

// Total and integer bits for the accumulator data type. (not used when float)
#define ACC_TTL_BIT 32
#define ACC_INT_BIT 6

// Number of timesteps for the LSTM layers.
#define N_TS 8 

// Input size for the first LSTM layer.
#define N1_LX 1

// Hidden size for the first LSTM layer.
#define N1_LH 9

// Input size for the second LSTM layer (equal to the hidden size of the first layer).
#define N2_LX N1_LH

// Hidden size for the second LSTM layer.
#define N2_LH 9

// Output size for the dense layer (equal to the input size of the first LSTM layer).
#define DENSE1_OUT N1_LX

// Input size for the dense layer (equal to the hidden size of the second LSTM layer).
#define DENSE1_IN  N2_LH

// Total model output size (DENSE1_OUT * N_TS).
#define MODEL_OUT DENSE1_OUT * N_TS

// Reuse factor for timesteps. N_TS means no unroll.
#define R_TS 1 

// Reuse factors for hidden layers in the first and second LSTM layers.
#define R1_H 1
#define R2_H 1

// Reuse factors for the tail computations in the first and second LSTM layers.
#define R1_TAIL 1
#define R2_TAIL 1

// Derived reuse factors for computations involving both hidden and tail layers in the first and second LSTM layers.
#define R1_X (R1_H + R1_TAIL + 7)
#define R2_X (R2_H + R2_TAIL + 7)

// Reuse factor for the dense layer.
#define R_DENSE1 1

// Default data type for activations, set to float.
typedef float act_default_t;
// typedef ap_fixed<ACT_TTL_BIT, ACT_INT_BIT, AP_RND, AP_SAT> act_default_t;

// Default data type for accumulators, set to float.
typedef float acc_default_t;
// typedef ap_fixed<ACC_TTL_BIT, ACC_INT_BIT, AP_RND, AP_SAT> acc_default_t;

// Default data type for the model, set to float.
typedef float model_default_t;
// typedef ap_fixed<ACT_TTL_BIT, ACT_INT_BIT, AP_RND, AP_SAT> model_default_t;

// Data type for LSTM accumulators, set to float.
typedef float accum_lstm_t;
// typedef ap_fixed<ACC_TTL_BIT, ACC_INT_BIT, AP_RND, AP_SAT> accum_lstm_t;

// Data type for model input, set to float.
typedef model_default_t input_t;

// Data type for model output, set to float.
typedef model_default_t result_t;

// Data type for model biases, set to float.
typedef accum_lstm_t model_biases_t;

// Data type for multipliers, set to float.
typedef accum_lstm_t mult_p_t;

// Configuration for the first LSTM layer.
struct config1 : nnet::lstm_config {
    static const unsigned length_x = N1_LX;
    static const unsigned length_h = N1_LH;
    static const unsigned timestep = N_TS;

    static const unsigned reuse_factor_tail = R1_TAIL;
    static const unsigned reuse_factor_ts = R_TS;
    static const unsigned LSTM_DEBUG = DEBUG;

    typedef accum_lstm_t    bias_t;
    typedef model_default_t weight_t;
    typedef accum_lstm_t    accum_t;
    typedef mult_p_t        mult_t;
};

// Configuration for the activation function following the first LSTM layer.
struct config2 : nnet::activ_config {
    static const unsigned n_in = N1_LH;
    typedef model_default_t table_t;
    typedef act_default_t constant_t;
};

// Configuration for the dense layer applied to the input of the first LSTM layer.
struct config_x : nnet::dense_config {
    typedef model_default_t weight_t;
    typedef accum_lstm_t    bias_t;
    typedef accum_lstm_t    accum_t;
    typedef mult_p_t        mult_t;

    static const unsigned reuse_factor = R1_X;
    static const unsigned n_in = N1_LX;
    static const unsigned n_out = N1_LH * 4;
};

// Configuration for the dense layer applied to the hidden state of the first LSTM layer.
struct config_h : nnet::dense_config {
    typedef model_default_t weight_t;
    typedef accum_lstm_t    bias_t;
    typedef accum_lstm_t    accum_t;
    typedef mult_p_t        mult_t;

    static const unsigned reuse_factor = R1_H;
    static const unsigned n_in = N1_LH;
    static const unsigned n_out = N1_LH * 4;
};

// Configuration for the second LSTM layer.
struct config1_lstm2 : nnet::lstm_config {
    static const unsigned length_x = N2_LX;
    static const unsigned length_h = N2_LH;
    static const unsigned timestep = N_TS;

    static const unsigned reuse_factor_tail = R2_TAIL;
    static const unsigned reuse_factor_ts = R_TS;
    static const unsigned LSTM_DEBUG = DEBUG;

    typedef accum_lstm_t    bias_t;
    typedef model_default_t weight_t;
    typedef accum_lstm_t    accum_t;
    typedef mult_p_t        mult_t;
};

// Configuration for the activation function following the second LSTM layer.
struct config2_lstm2 : nnet::activ_config {
    static const unsigned n_in = N2_LH;
    typedef model_default_t table_t;
    typedef act_default_t constant_t;
};

// Configuration for the dense layer applied to the input of the second LSTM layer.
struct config_x_lstm2 : nnet::dense_config {
    typedef model_default_t weight_t;
    typedef accum_lstm_t    bias_t;
    typedef accum_lstm_t    accum_t;
    typedef mult_p_t        mult_t;

    static const unsigned reuse_factor = R2_X;
    static const unsigned n_in = N2_LX;
    static const unsigned n_out = N2_LH * 4;
};

// Configuration for the dense layer applied to the hidden state of the second LSTM layer.
struct config_h_lstm2 : nnet::dense_config {
    typedef model_default_t weight_t;
    typedef accum_lstm_t    bias_t;
    typedef accum_lstm_t    accum_t;
    typedef mult_p_t        mult_t;

    static const unsigned reuse_factor = R2_H;
    static const unsigned n_in = N2_LH;
    static const unsigned n_out = N2_LH * 4;
};

// Configuration for the final dense layer applied after the second LSTM layer.
struct config3 : nnet::dense_config {
    typedef model_default_t weight_t;
    typedef accum_lstm_t    bias_t;
    typedef accum_lstm_t    accum_t;
    typedef mult_p_t        mult_t;

    static const unsigned reuse_factor = R_DENSE1;
    static const unsigned n_in = DENSE1_IN;
    static const unsigned n_out = DENSE1_OUT;
};

#endif // PARAMETERS_H_
