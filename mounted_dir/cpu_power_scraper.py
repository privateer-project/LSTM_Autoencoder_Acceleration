from pyJoules.energy_meter import measure_energy
from pyJoules.handler.pandas_handler import PandasHandler
import time
import threading
import numpy as np
import pandas as pd

class power_scraper:
    def __init__(self, model) -> None:
        self.model = model
        self.pandas_handler = PandasHandler()

    def capture_power(self, input_vector: np.ndarray, iterations: int = 100) -> None:
        """
        Wrapper for the capture_power method with the measure_energy decorator applied.
        """
        @measure_energy(handler=self.pandas_handler)
        def wrapped_capture_power(model, input_vector: np.ndarray, iterations: int) -> None:
            for i in range(iterations):
                _ = model(input_vector)
        
        wrapped_capture_power(self.model, input_vector, iterations)

    def get_power_data(self, input_vector: np.ndarray, seconds: float = 10.0) -> pd.DataFrame:
        event = threading.Event()
        waiting = threading.Thread(target=waiting_thread, args=(event, seconds))
        waiting.start()
        while not event.is_set():
            self.capture_power(input_vector)
        waiting.join()
        return self.pandas_handler.get_dataframe()

def waiting_thread(event, seconds):
    time.sleep(seconds)
    event.set()
    return
    