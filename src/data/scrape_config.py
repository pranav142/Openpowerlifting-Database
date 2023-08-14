import math
from dataclasses import dataclass
import os


@dataclass
class Configuration:
    """A class for holding configuration settings.

    This class provides attributes and methods related to configuration settings
    for processing data. It includes default values and methods for calculating
    iteration steps and managing file paths.

    Attributes:
        file_name (str): The name of the file to be saved.
        number_of_threads (int): The number of threads for parallel processing.
        number_of_examples (int): The total number of examples in the data.
        step_size (int): The size of each processing step.
        folder_dir (str): The directory where the file will be saved.
    """

    file_name: str = "default.csv"
    number_of_threads: int = 1
    number_of_examples: int = 452785
    step_size: int = 100
    folder_dir: str = "../../data/raw"

    @property
    def total_iterations(self) -> int:
        """Calculate the total number of iterations based on step size.

        Returns:
            int: The total number of iterations.
        """
        assert (
            self.step_size <= self.number_of_examples
        ), "Step size cannot exceed the total number of examples."
        return math.ceil(self.number_of_examples / self.step_size)

    @property
    def steps(self) -> int:
        """Calculate the number of steps based on threads and total iterations.

        Returns:
            int: The number of steps for parallel processing.
        """
        assert (
            self.number_of_threads <= self.total_iterations
        ), "Number of threads cannot exceed the total number of iterations."
        return math.ceil(self.total_iterations / self.number_of_threads)

    def clear_existing_file(self) -> None:
        """Delete the existing file if it exists."""
        save_path = self.save_path
        if os.path.exists(save_path):
            print(f"Conflicting file '{self.file_name}' found")
            os.remove(save_path)
            print("File deleted successfully.")

    @property
    def save_path(self) -> str:
        """Generate the save path for the file.

        Returns:
            str: The full path where the file will be saved.
        """
        assert os.path.exists(self.folder_dir) and os.path.isdir(
            self.folder_dir
        ), "Please enter a valid directory"
        assert self.file_name.endswith(
            ".csv"
        ), "Please enter in filename as csv i.e. filename.csv"

        if not os.path.exists(self.folder_dir):
            os.makedirs(self.folder_dir)

        return os.path.join(self.folder_dir, self.file_name)


# Dictionary Containing Key and Corresponding Index in Response
COLUMN_CONFIG: dict[str, int] = {
    "Number": 1,
    "Name": 2,
    "Instagram Handle": 4,
    "Origin": 6,
    "Federation": 8,
    "Competition Date": 9,
    "Competition Country": 10,
    "Competition City": 11,
    "Gender": 13,
    "Equipment": 14,
    "Age": 15,
    "Weight": 17,
    "Class": 18,
    "Squat": 19,
    "Bench": 20,
    "Deadlift": 21,
    "Total": 22,
    "Dots": 23,
}
