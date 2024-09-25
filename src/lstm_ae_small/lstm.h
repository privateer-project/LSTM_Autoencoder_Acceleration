/* lstm.h
 */

#ifndef _CONV_H_
#define _CONV_H_

#include <ap_fixed.h>

#include <complex>
#include "ap_int.h"
#include "ap_fixed.h"

#include "parameters.h"
// Encapsulate the top level function with extern "C" to avoid this problem
// https://support.xilinx.com/s/question/0D54U00005rcJtLSAU/failed-to-add-kernel-c-to-xo-container-because-the-kernel-name-z1cp7apuintili128ees1s1s1-defined-in-kernelxml-does-not-match?language=en_US
extern "C"{ 
	void lstm(
		input_t lstm_in[N_TS*N1_LX],
		//model_default_t weights_x[N_LX*N_LH*4],
		//model_default_t weights_h[N_LH*N_LH*4],
		//model_default_t bias[N_LH*4],
		result_t conv_out[MODEL_OUT]
					);
}
#endif /* _LSTM_H_ */

