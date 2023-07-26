import requests
import pandas as pd
import time, os
from threading import Thread, current_thread, Lock
from multiprocessing import current_process
from payload import Payload
from config import Configuration
from utils import timeit


NUMBER = 1
NAME = 2
INSTAGRAM = 4
ORIGIN = 6
FEDERATION = 8
COMPETITION_DATE = 9
COMPETITION_COUNTRY = 10
COMPETITION_CITY = 11
GENDER = 13
EQUIPMENT = 14
AGE = 15
WEIGHT = 17
CLASS_ = 18
SQUAT = 19
BENCH = 20
DEADLIFT = 21
TOTAL = 22
DOTS = 23


def get_powerlifting_data(start: int, end: int) -> Payload:
    url = f"https://www.openpowerlifting.org/api/rankings?start={start}&end={end}&lang=en&units=lbs"
    response = requests.get(url)
    data = Payload(
        status=response.status_code, raw_response=response.text, start=start, end=end
    )
    return data


def row_to_dictionary(row: list):
    return {
        "Number": row[NUMBER],
        "Name": row[NAME],
        "Instagram Handle": row[INSTAGRAM],
        "Origin": row[ORIGIN],
        "Federation": row[FEDERATION],
        "Competition Date": row[COMPETITION_DATE],
        "Competition Country": row[COMPETITION_COUNTRY],
        "Competition City": row[COMPETITION_CITY],
        "Gender": row[GENDER],
        "Equipment": row[EQUIPMENT],
        "Age": row[AGE],
        "Weight": row[WEIGHT],
        "Class": row[CLASS_],
        "Squat": row[SQUAT],
        "Bench": row[BENCH],
        "Deadlift": row[DEADLIFT],
        "Total": row[TOTAL],
        "Dots": row[DOTS],
    }


def save_data_to_csv(data: Payload, save_path: str, header_flag: int) -> None:
    df = pd.DataFrame([row_to_dictionary(row) for row in data.content["rows"]])
    df.to_csv(save_path, mode="a", header=header_flag, index=False)


def get_process_info() -> tuple[str, str, str]:
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
        except Exception as e:
            print(f"error on {start} - {end}: {e}")
            continue
        finally:
            lock.release()
    print(
        f"{process_id} * {process_name} * {thread_name} ---> Finished getting data..."
    )


@timeit
def main() -> None:
    start_iteration = 0
    config = Configuration(file_name="openpowerlifting.csv", number_of_threads=50)
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
