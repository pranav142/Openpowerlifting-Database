import sys

sys.path.append("../src")

from data.config import Configuration
import pytest
import os
import time


def test_total_iterations():
    # Test case where step size is larger than number of examples
    config = Configuration(step_size=500, number_of_examples=100)
    with pytest.raises(AssertionError):
        _ = config.total_iterations

    # Test case where step size evenly divides number of examples
    config = Configuration(step_size=100, number_of_examples=1000)
    assert config.total_iterations == 10

    # Test case where step size does not evenly divide number of examples
    config = Configuration(step_size=150, number_of_examples=1000)
    assert config.total_iterations == 7


def test_steps():
    # Test case where number of threads is larger than total iterations
    config = Configuration(
        number_of_threads=500, step_size=100, number_of_examples=1000
    )
    with pytest.raises(AssertionError):
        _ = config.steps

    # Test case where number of threads evenly divides total iterations
    config = Configuration(number_of_threads=2, step_size=100, number_of_examples=1000)
    assert config.steps == 5

    # Test case where number of threads does not evenly divide total iterations
    config = Configuration(number_of_threads=3, step_size=100, number_of_examples=1000)
    assert config.steps == 4

    # Test case where number of threads is equal to total iterations
    config = Configuration(number_of_threads=10, step_size=100, number_of_examples=1000)
    assert config.steps == 1


def test_save_path():
    config = Configuration(file_name="data.csv", folder_dir="C:\\")
    current_time = time.strftime("[%Y-%m-%d]", time.localtime())
    expected_save_path = f"C:\\{current_time}_data.csv"
    assert config.save_path == expected_save_path

    # Test case where folder is a valid file path
    config = Configuration(
        folder_dir="C:\\Users\\pknad\\OneDrive\\Documents\\Machine_Learning\\PowerLifting\\tests\\test_config.py"
    )
    with pytest.raises(AssertionError):
        _ = config.save_path

    # Test case where folder does not exist
    config = Configuration(folder_dir=" C://hello")
    with pytest.raises(AssertionError):
        _ = config.save_path

    # Test case where a invalid file name is passed
    config = Configuration(file_name="hello.py")
    with pytest.raises(AssertionError):
        _ = config.save_path
