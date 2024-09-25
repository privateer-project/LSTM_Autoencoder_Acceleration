import pynq
import numpy as np
from dataclasses import dataclass
from pprint import pprint
from typing import Any, Dict, Type, List
import time
import inspect
import power_scraper
import threading
import queue
import utils

@dataclass
class AutoencoderParameters:
    """
    Dataclass to hold parameters for configuring the Autoencoder model.
    """
    N_TS: int = 8  # Number of timesteps.
    N_FEATURES: int = 1  # Input size of input features.
    input_t: type = float  # Data type for the input.
    result_t: type = float  # Data type for the output.

class AutoencoderAlveo:
    """
    Class to interface with an autoencoder model implemented on an Alveo FPGA device using PYNQ.
    """
    def __init__(self, bitstream_path: str, parameters: AutoencoderParameters, device: pynq.Device = None) -> None:
        """
        Initializes the Autoencoder model on the FPGA by loading the specified bitstream.

        Args:
            bitstream_path (str): Path to the bitstream file to load onto the FPGA.
            parameters (AutoencoderParameters): Parameters for configuring the Autoencoder model.
            device (pynq.Device, optional): Specific FPGA device to use. If None, the default device is used.
        """
        # Initialize timing dictionary to track performance metrics
        self.timings = {  # Timing data in nanoseconds
            'initialize': None,
            'allocate_buffers': None,
            'runs': []
        }

        # Measure time taken to initialize the FPGA overlay
        initialize_start = time.perf_counter()
        # Load the overlay (bitstream) onto the FPGA
        if device is None:
            self.ae_overlay = pynq.Overlay(bitstream_path)
        else:
            self.ae_overlay = pynq.Overlay(bitstream_path, device=device)
        initialize_end = time.perf_counter()
        self.timings['initialize'] = initialize_end - initialize_start
        print(f"Initialized")
        
        self.kernel = self.ae_overlay.lstm_1  # Reference to the Autoencoder kernel on the FPGA
        # Store parameters and set up the kernel and buffers
        self.parameters = parameters
        self.in_out_size = self.parameters.N_TS * self.parameters.N_FEATURES
        #self.pprint_ip_dict()  # Print information about available IP cores
        #self.print_kernel_signature()  # Print the kernel's function signature
        self.input_buffer = None
        self.output_buffer = None

        # Allocate input and output buffers on the FPGA
        allocate_buffers_start = time.perf_counter()
        self.allocate_buffers()
        allocate_buffers_end = time.perf_counter()
        self.timings['allocate_buffers'] = allocate_buffers_end - allocate_buffers_start
        print(f"Allocated Buffers")

        self.power_scraper = power_scraper.power_scraper('0000:bf:00.1')
        print("Succesfully loaded ALVEO model!")

    def allocate_buffers(self) -> None:
        """
        Allocates memory buffers for input and output on the FPGA.
        """
        # Allocate buffers with specified data types
        self.input_buffer = pynq.allocate(shape=(self.in_out_size,), dtype=utils.convert_types(self.parameters.input_t))
        self.output_buffer = pynq.allocate(shape=(self.in_out_size,), dtype=utils.convert_types(self.parameters.result_t))

    def run(self, input_darray: np.ndarray) -> np.ndarray:
        """
        Runs the Autoencoder model on the FPGA using the provided input data.

        Args:
            input_darray (np.ndarray): Input data array.

        Returns:
            np.ndarray: Output data from the Autoencoder model.
        """
        # Copy input data to the FPGA buffer and sync it
        self.input_buffer[:] = input_darray
        self.input_buffer.sync_to_device()
        # Execute the Autoencoder kernel on the FPGA
        self.kernel.call(self.input_buffer, self.output_buffer)
        # Sync the output buffer from the FPGA
        self.output_buffer.sync_from_device()
        return self.output_buffer

    def timed_run(self, input_darray: np.ndarray, verbose: bool = True) -> np.ndarray:
        """
        Runs the Autoencoder model on the FPGA with timing measurement and optional verbosity.

        Args:
            input_darray (np.ndarray): Input data array that will be passed to the Autoencoder model.
                Must have the same shape and data type as the model's input buffer.
            verbose (bool, optional): If True, prints the runtime of the model execution in milliseconds.
                Defaults to True.

        Returns:
            np.ndarray: Output data from the Autoencoder model as retrieved from the output buffer on the FPGA.
        
        Raises:
            AssertionError: If the shape or dtype of `input_darray` does not match the expected input buffer specifications.
        """
        # Check that the input matches the expected shape and type
        assert self.input_buffer.shape == input_darray.shape, f"Input shape mismatch expected: {self.input_buffer.shape} got: {input_darray.shape}"
        assert self.input_buffer.dtype == input_darray.dtype, f"Input type mismatch expected: {self.input_buffer.dtype} got: {input_darray.dtype}"
        
        # Measure the runtime of the model execution
        run_start = time.perf_counter()
        output_buffer = self.run(input_darray)
        run_end = time.perf_counter()
        
        # Store the timing of the run
        self.timings['runs'].append(run_end - run_start)
        # Print runtime if verbose is enabled
        if verbose:
            print(f"Runtime: {self.timings['runs'][-1] * 1000:.2f} ms")
        
        return output_buffer

    def run_vector(self, input_vector: np.ndarray, timed: bool = False, verbose: bool = False) -> np.ndarray:
        """
        Processes an input vector by dividing it into segments and running the autoencoder model on each segment.

        Args:
            input_vector (np.ndarray): The input data array to be processed. This array should be a multiple of the model's
                input size (`self.in_out_size`).
            timed (bool, optional): If True, measures and stores the execution time for each segment. Defaults to False.
            verbose (bool, optional): If True and `timed` is also True, prints the runtime of each segment's execution.
                Defaults to False.

        Returns:
            np.ndarray: The output vector containing the results of the autoencoder model for each input segment.
        """
        output_vector = np.empty(shape=input_vector.shape, dtype=utils.convert_types(self.parameters.result_t))
        for i in range(0, len(input_vector), self.in_out_size):
            if timed:
                output_vector[i:i+self.in_out_size] = self.timed_run(input_vector[i:i+self.in_out_size], verbose)
            else:
                output_vector[i:i+self.in_out_size] = self.run(input_vector[i:i+self.in_out_size])
        return output_vector

    def print_timings(self, verbose=False) -> None:
        """
        Prints the recorded performance timings for various stages of the autoencoder operation, including initialization,
        buffer allocation, and individual runs.

        Args:
            verbose (bool, optional): If True, prints detailed timing information for each individual run. Defaults to False.
        """
        print(f"Initialize time: {self.timings['initialize']*1000:.2f} ms")
        print(f"Allocate buffers time: {self.timings['allocate_buffers']*1000:.2f} ms")
        if len(self.timings['runs']) != 0:  # Check if there are any recorded runs
            print(f"Average run: {sum(self.timings['runs'])/len(self.timings['runs'])*1000:.2f} ms")
            print(f"Number of runs: {len(self.timings['runs'])}")
            if verbose:
                for i, run in enumerate(self.timings['runs']):
                    print(f"Run {i}: {run*1000:.2f} ms")

    def help(self) -> None:
        """
        Prints information about the Autoencoder overlay, including its type, docstring, attributes, and methods.
        """
        # Get and print the type of the overlay object
        print(f"Type: {type(self.ae_overlay)}\n")

        # Retrieve and print the docstring of the overlay object, if available
        docstring = inspect.getdoc(self.ae_overlay)
        if docstring:
            print(f"Docstring:\n{docstring}\n")
        else:
            print("Docstring: None\n")

        # List and print all attributes and methods of the overlay
        attributes = dir(self.ae_overlay)
        print(f"Attributes and Methods:\n{attributes}\n")

    def get_ip_dict(self) -> Dict[str, Any]:
        """
        Retrieves the dictionary of IP cores available in the overlay.

        Returns:
            Dict[str, Any]: Dictionary containing IP cores information.
        """
        return self.ae_overlay.ip_dict

    def get_mem_dict(self) -> Dict[str, Any]:
        """
        Retrieves the dictionary of memory blocks available in the overlay.

        Returns:
            Dict[str, Any]: Dictionary containing memory blocks information.
        """
        return self.ae_overlay.mem_dict

    def print_kernel_signature(self) -> None:
        """
        Prints the function signature of the Autoencoder kernel.
        """
        print(self.kernel.signature)

    def pprint_ip_dict(self) -> None:
        """
        Pretty prints the dictionary of IP cores available in the overlay.
        """
        pprint(self.ae_overlay.ip_dict, indent=4)

    def print_used_mem_dict(self) -> None:
        """
        Prints information about the used memory blocks in the overlay.
        """
        for key in self.ae_overlay.mem_dict.keys():
            if self.ae_overlay.mem_dict[key]['used'] == 1:
                print(f"Key: {key}, {self.ae_overlay.mem_dict[key]}")

    def clean_class(self) -> None:
        """
        Cleans up resources by deleting buffers and freeing the FPGA overlay.
        """
        del self.input_buffer  # Deletes the input buffer from memory
        del self.output_buffer  # Deletes the output buffer from memory
        self.a_overlay.free()  # Frees the overlay resources

    def collect_power_data_thread(self, event: threading.Event, timeout_seconds: float, power_data_queue: queue.Queue) -> None:
        """
        Collects power data from the FPGA in a separate thread for a specified duration.

        Args:
            event (threading.Event): Event to signal the end of data collection.
            timeout_seconds (float): Duration in seconds for which to collect power data.
            power_data_queue (queue.Queue): Queue to store the collected power data.
        """
        time.sleep(1)  # To get correct power data
        power_data_list = []
        start = time.perf_counter()
        end = start
        while(end - start < timeout_seconds):
            try:
                power_data_list.append(self.power_scraper.get_power())
            except Exception as e:
                print(f'self.power_scraper.get_power() got this error: {e}')
            end = time.perf_counter()
        event.set()
        power_data_queue.put(power_data_list)
        return

    def continuous_runs_thread(self, event: threading.Event) -> None:
        """
        Continuously runs the Autoencoder kernel on the FPGA until the event is set.

        Args:
            event (threading.Event): Event to signal when to stop the continuous runs.
        """
        self.input_buffer[:] = np.random.random((self.in_out_size,)).astype(utils.convert_types(self.parameters.input_t))
        self.input_buffer.sync_to_device()
        while not event.is_set():
            self.kernel.call(self.input_buffer, self.output_buffer)
        self.output_buffer.sync_from_device()
        return

    def continuous_runs_transfers_thread(self, event: threading.Event) -> None:
        """
        Continuously runs the Autoencoder kernel on the FPGA until the event is set.

        Args:
            event (threading.Event): Event to signal when to stop the continuous runs.
        """
        self.input_buffer[:] = np.random.random((self.in_out_size,)).astype(utils.convert_types(self.parameters.input_t))
        while not event.is_set():
            self.input_buffer.sync_to_device()
            self.kernel.call(self.input_buffer, self.output_buffer)
            self.output_buffer.sync_from_device()
        return
        
    def get_power_data(self, seconds: float = 10.0, transfers: bool = False) -> List[Dict[str, Any]]:
        """
        Collects power data from the FPGA during continuous runs for a specified duration.

        Args:
            seconds (float, optional): Duration in seconds to collect power data. Defaults to 10.0 seconds.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing power data collected during the run.
        """
        event = threading.Event()  # Event for signaling
        power_data_queue = queue.Queue()  # Queue for communication
        continuous_power_data = threading.Thread(target=self.collect_power_data_thread, args=(event, seconds, power_data_queue))
        if(transfers):
            continuous_runs = threading.Thread(target=self.continuous_runs_thread, args=(event,))
        else:
            continuous_runs = threading.Thread(target=self.continuous_runs_transfers_thread, args=(event,))
        continuous_runs.start()
        continuous_power_data.start()
        continuous_runs.join()
        power_data = power_data_queue.get()
        continuous_power_data.join()
        
        return power_data
        