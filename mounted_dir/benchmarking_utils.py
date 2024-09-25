import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Any, Dict, Type, List
import time
import torch
import utils

def get_average_time_cpu(model, input_vector: torch.Tensor, iterations: int = 1000) -> float:
    total_time = 0
    cpu_input_vector = input_vector.to('cpu')
    # Disable gradient computation for inference
    # with torch.no_grad(): Ends up slower
    # Optional: Warm-up iterations to stabilize timing
    warmup = 10
    for _ in range(warmup):
        _ = model(cpu_input_vector)
    for i in range(iterations):
        start = time.perf_counter()
        _ = model(cpu_input_vector)
        end = time.perf_counter()
        total_time += end - start
    average_time_ms = total_time / iterations * 1000 # (ms)
    return average_time_ms

def get_average_time_gpu(model, device, input_vector: torch.Tensor, iterations: int = 1000) -> float:
    total_time = 0
    gpu_input_vector = input_vector.to(device)
    # Disable gradient computation for inference
    with torch.no_grad():
        warmup = 10
        for _ in range(warmup):
            _ = model(gpu_input_vector)
        for i in range(iterations):
            start = time.perf_counter()
            _ = model(gpu_input_vector)
            torch.cuda.synchronize()
            end = time.perf_counter()
            total_time += end - start
    average_time_ms = total_time / iterations * 1000 # (ms)
    return average_time_ms

def get_average_time_gpu_transfers(model, device, input_vector: torch.Tensor, iterations: int = 1000) -> float:
    total_time = 0
    # Disable gradient computation for inference
    with torch.no_grad():
        warmup = 10
        for _ in range(warmup):
            _ = model(input_vector.to(device))
        for i in range(iterations):
            start = time.perf_counter()
            gpu_input_vector = input_vector.to(device)
            _ = model(gpu_input_vector).to('cpu')
            torch.cuda.synchronize()
            end = time.perf_counter()
            total_time += end - start
    average_time_ms = total_time / iterations * 1000 # (ms)
    return average_time_ms

def get_average_time_alveo(model, input_vector: np.ndarray, iterations: int = 1000) -> float:
    total_time = 0
    # Copy input data to the FPGA buffer and sync it
    model.input_buffer[:] = input_vector
    model.input_buffer.sync_to_device()
    warmup = 10
    for _ in range(warmup):
        _ = model.kernel.call(model.input_buffer, model.output_buffer)
    model.output_buffer.sync_from_device()
    for i in range(iterations):
        start = time.perf_counter()
        _ = model.kernel.call(model.input_buffer, model.output_buffer)
        model.output_buffer.sync_from_device()
        end = time.perf_counter()
        total_time += end - start
    average_time_ms = total_time / iterations * 1000 # (ms)
    return average_time_ms

def get_average_time_alveo_transfers(model, input_vector: np.ndarray, iterations: int = 1000) -> float:
    total_time = 0
    # Copy input data to the FPGA buffer and sync it
    model.input_buffer[:] = input_vector
    model.input_buffer.sync_to_device()
    warmup = 10
    for _ in range(warmup):
        _ = model.kernel.call(model.input_buffer, model.output_buffer)
    model.output_buffer.sync_from_device()
    for i in range(iterations):
        start = time.perf_counter()
        model.input_buffer.sync_to_device()
        _ = model.kernel.call(model.input_buffer, model.output_buffer)
        model.output_buffer.sync_from_device()
        end = time.perf_counter()
        total_time += end - start
    average_time_ms = total_time / iterations * 1000 # (ms)
    return average_time_ms

def extract_alveo_power_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Extracts specified power data from a list of dictionaries, converts time to timestamps,
    and returns a sorted DataFrame.

    Args:
        data (list): A list of dictionaries containing power data.

    Returns:
        pd.DataFrame: A sorted DataFrame containing 'time', 'Power', '12 Volts Auxillary Power',
                      '12 Volts PCI Express Power', and 'Internal FPGA Vcc Power' for each entry.
    """
    extracted_data = []
    for entry in data:
        # Convert time into a timestamp
        timestamp = datetime.fromtimestamp(entry['time'])
        power = entry['Power']

        # Compute specific powers
        power_12_volts_auxillary = entry['Power Rails']['12 Volts Auxillary']['Voltage'] * entry['Power Rails']['12 Volts Auxillary']['Current']
        power_12_volts_pci_express = entry['Power Rails']['12 Volts PCI Express']['Voltage'] * entry['Power Rails']['12 Volts PCI Express']['Current']
        power_internal_fpga_vcc = entry['Power Rails']['Internal FPGA Vcc']['Voltage'] * entry['Power Rails']['Internal FPGA Vcc']['Current']

        # Append the extracted and calculated values to the list
        extracted_data.append({
            'time': timestamp,
            'Power': power,
            '12 Volts Auxillary Power': power_12_volts_auxillary,
            '12 Volts PCI Express Power': power_12_volts_pci_express,
            'Internal FPGA Vcc Power': power_internal_fpga_vcc
        })

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(extracted_data)
    
    # Sort the DataFrame by ascending timestamp
    df = df.sort_values(by='time').reset_index(drop=True)
    
    return df

def plot_alveo_power_data(df, save_path: str = None) -> None:
    """
    Plots ALVEO power data from the DataFrame without dots, using only lines, ensures the y-axis includes zero,
    and saves the plot as a PNG file.

    Args:
        df (pd.DataFrame): A DataFrame containing the power data with timestamps.
        save_path (str): The file path to save the plot as a PNG file. If None, the plot is not saved. Defaults to None.
    """
    plt.figure(figsize=(12, 6))
    
    # Plotting the power data with lines only
    plt.plot(df['time'], df['Power'], label='ALVEO Total Power')
    plt.plot(df['time'], df['12 Volts Auxillary Power'], label='12 Volts Auxillary Power')
    plt.plot(df['time'], df['12 Volts PCI Express Power'], label='12 Volts PCI Express Power')
    plt.plot(df['time'], df['Internal FPGA Vcc Power'], label='Internal FPGA Vcc Power')
    
    # Ensuring that the y-axis includes zero
    #plt.axhline(0, color='gray', linestyle='--')  # Draws a line at y=0
    plt.ylim(bottom=0)  # Optionally, you can set the bottom limit to zero to make sure the grid starts from zero

    # Formatting the plot
    plt.title('ALVEO Power Data Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Power (W)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)  # Enable grid lines for better visibility
    plt.tight_layout()
    
    # Save the plot as a PNG file
    if(save_path is not None):
        plt.savefig(save_path, format='png', dpi=300)  # Saves the plot with high resolution

    # Show the plot
    plt.show()


def plot_cpu_power_data(df, save_path: str = None) -> None:
    """
    Plots CPU power data from the DataFrame without dots, using only lines, ensures the y-axis includes zero,
    and saves the plot as a PNG file.

    Args:
        df (pd.DataFrame): A DataFrame containing the power data with timestamps.
        save_path (str): The file path to save the plot as a PNG file. If None, the plot is not saved. Defaults to None.
    """
    # Calculate the power in Watts for package_0 and dram_0
    df['package_0_power_w'] = df['package_0'] / (df['duration'] * 1e6)  # Convert microjoules to joules
    df['dram_0_power_w'] = df['dram_0'] / (df['duration'] * 1e6)        # Convert microjoules to joules
    
    # Calculate the total power as the sum of package_0_power_w and dram_0_power_w
    df['total_power_w'] = df['package_0_power_w'] + df['dram_0_power_w']
    
    # Convert the timestamp to a readable datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Plotting the power metrics
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['total_power_w'], label='Total Power (W)')
    plt.plot(df['timestamp'], df['package_0_power_w'], label='Package 0 Power (W)')
    plt.plot(df['timestamp'], df['dram_0_power_w'], label='DRAM 0 Power (W)')
    
    # Adding labels, title, and setting y-axis to start at 0
    plt.xlabel('Timestamp')
    plt.ylabel('Power (W)')
    plt.title('Power Consumption of Package 0, DRAM 0, and Total Power')
    plt.ylim(bottom=0)  # Ensure the y-axis starts at 0
    plt.legend()
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    
    # Display the plot
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    # Save the plot as a PNG file
    if(save_path is not None):
        plt.savefig(save_path, format='png', dpi=300)  # Saves the plot with high resolution
    plt.show()

def extract_gpu_power_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Extracts power data from a list of dictionaries, converts time to timestamps,
    and returns a sorted DataFrame.

    Args:
        data (list): A list of dictionaries containing power data.

    Returns:
        pd.DataFrame: A sorted DataFrame containing 'time' and 'Power' for each entry.
    """
    extracted_data = []
    for entry in data:
        # Convert time into a timestamp
        timestamp = datetime.fromtimestamp(entry['time'])
        power = entry['Power']
        
        # Append the extracted values to the list
        extracted_data.append({
            'time': timestamp,
            'Power': power
        })

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(extracted_data)
    
    # Sort the DataFrame by ascending timestamp
    df = df.sort_values(by='time').reset_index(drop=True)
    
    return df

def plot_gpu_power_data(df: pd.DataFrame, save_path: str = None) -> None:
    """
    Plots GPU power data from the DataFrame using only lines, ensures the y-axis includes zero,
    and saves the plot as a PNG file.

    Args:
        df (pd.DataFrame): A DataFrame containing the power data with timestamps.
        save_path (str): The file path to save the plot as a PNG file. If None, the plot is not saved. Defaults to None.
    """
    plt.figure(figsize=(12, 6))
    
    # Plotting the power data with lines only
    plt.plot(df['time'], df['Power'], label='GPU Power')
    
    # Ensuring that the y-axis includes zero and setting limits closer to the data range
    plt.ylim(bottom=0, top=max(df['Power']) + 5)  # Adding 5 to top to give some space above the data line

    # Formatting the plot
    plt.title('GPU Power Data Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Power (W)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)  # Enable grid lines for better visibility
    plt.tight_layout()
    
    # Save the plot as a PNG file
    if save_path is not None:
        plt.savefig(save_path, format='png', dpi=300)  # Save the plot with high resolution

    # Show the plot
    plt.show()