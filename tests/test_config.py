import sys

sys.path.append("../src")

from data.config import Configuration
import os


def test_Configuration_iterations() -> None:
    config = Configuration(number_of_threads=10, number_of_examples=1000, step_size=100)
    assert config.total_iterations == 10


def test_Configuration_steps() -> None:
    config = Configuration(number_of_threads=10, number_of_examples=1000, step_size=100)
    assert config.steps == 1
