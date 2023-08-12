import os
import time
from threading import Thread, Lock, current_thread

import pandas as pd
import requests
from multiprocessing import current_process

from data.payload import Payload
from data.scrape_config import Configuration, COLUMN_CONFIG
from data.utils import timeit


def get_powerlifting_data(start: int, end: int, timeout: int = 10) -> Payload:
    """Retrieve powerlifting data from the Open Powerlifting API.

    Args:
        start (int): The starting rank for the data retrieval.
        end (int): The ending rank for the data retrieval.
        timeout (int, optional): The maximum time in seconds to wait for a response. Defaults to 10.

    Returns:
        Payload: An instance of the Payload class containing the API response data.
    """
    url = f"https://www.openpowerlifting.org/api/rankings?start={start}&end={end}&lang=en&units=lbs"
    response = requests.get(url, timeout=timeout)
    data = Payload(
        status=response.status_code, raw_response=response.text, start=start, end=end
    )
    return data


def row_to_dictionary(row: list):
    """_summary_

    Args:
        row (list): _description_

    Returns:
        _type_: _description_
    """
    return {column_name: row[index] for column_name, index in COLUMN_CONFIG.items()}


def save_data_to_csv(data: Payload, save_path: str, header_flag: int) -> None:
    """_summary_

    Args:
        data (Payload): _description_
        save_path (str): _description_
        header_flag (int): _description_
    """
    df = pd.DataFrame([row_to_dictionary(row) for row in data.content["rows"]])
    df.to_csv(save_path, mode="a", header=header_flag, index=False)


def get_process_info() -> tuple[str, str, str]:
    """_summary_

    Returns:
        tuple[str, str, str]: _description_
    """
    process_id = os.getpid()
    thread_name = current_thread().name
    process_name = current_process().name
    return process_id, thread_name, process_name


def scrape_data(
    config: Configuration,
    lock: Lock,
    start_iteration: int,
    end_iteration: int,
) -> None:
    """_summary_

    Args:
        config (Configuration): _description_
        lock (Lock): _description_
        start_iteration (int): _description_
        end_iteration (int): _description_
    """
    assert (
        config.step_size > 0 and config.step_size <= 100
    ), "Configuration for step size must be between 0 and 100"

    assert (
        start_iteration >= 0 and end_iteration >= 0
    ), "Ensure start and end iterations are positive numbers"

    process_id, thread_name, process_name = get_process_info()

    print(
        f"{process_id} * {thread_name} * {process_name}  ---> Start getting data from columns {start_iteration * 100} - {end_iteration * 100}"
    )

    for iteration in range(start_iteration, end_iteration):
        start = iteration * config.step_size
        end = start + config.step_size - 1

        try:
            data = get_powerlifting_data(start, end)
            lock.acquire()
            save_data_to_csv(
                data,
                save_path=config.save_path,
                header_flag=not start,
            )
        except Exception as error:
            print(f"error on {start} - {end}: {error}")
            continue
        finally:
            lock.release()
    print(
        f"{process_id} * {process_name} * {thread_name} ---> Finished getting data..."
    )


@timeit
def main() -> None:
    """_summary_"""
    start_iteration = 0
    config = Configuration(file_name="openpowerlifting.csv", number_of_threads=50)
    config.clear_existing_file()
    lock = Lock()
    print("Config Settings: \n")
    print(f"{config}\n\n")

    print("-----------Starting To Scrape Data------------")

    threads = []
    for _ in range(config.number_of_threads):
        t = Thread(
            target=scrape_data,
            args=(config, lock, start_iteration, start_iteration + config.steps),
        )
        threads.append(t)
        t.start()
        time.sleep(0.1)
        start_iteration += config.steps

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
