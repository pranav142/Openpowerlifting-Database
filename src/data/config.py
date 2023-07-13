import math
from dataclasses import dataclass
import os
import time


@dataclass
class Configuration:
    file_name: str = "powerlifting.csv"
    number_of_threads: int = 1
    number_of_examples: int = 452785
    step_size: int = 100
    folder_dir: str = "C:\\Users\\pknad\\OneDrive\\Documents\\Machine_Learning\\PowerLifting\\data\\raw"

    @property
    def total_iterations(self) -> int:
        assert (
            self.step_size <= self.number_of_examples
        ), "Step size cannot exceed the total number of examples."
        return math.ceil(self.number_of_examples / self.step_size)

    @property
    def steps(self) -> int:
        assert (
            self.number_of_threads <= self.total_iterations
        ), "Number of threads cannot exceed the total number of iterations."
        return math.ceil(self.total_iterations / self.number_of_threads)

    @property
    def save_path(self) -> str:
        assert os.path.exists(self.folder_dir) and os.path.isdir(
            self.folder_dir
        ), "Please enter a valid directory"
        assert self.file_name.endswith(
            ".csv"
        ), "Please enter in filename as csv i.e. filename.csv"
        current_time = time.strftime("%Y-%m-%d", time.localtime())
        filename_with_time = current_time + "_" + self.file_name
        return os.path.join(self.folder_dir, filename_with_time)
