import math
from dataclasses import dataclass
import os


@dataclass
class Configuration:
    number_of_threads: int = 1
    number_of_examples: int = 452785
    step_size: int = 100
    relative_save_path: str = "././data/raw/openpowerlifting.csv"

    @property
    def total_iterations(self) -> int:
        return math.ceil(self.number_of_examples / self.step_size)

    @property
    def steps(self) -> int:
        return math.ceil(self.total_iterations / self.number_of_threads)

    @property
    def absolute_save_path(self) -> str:
        return os.path.abspath(self.relative_save_path)
