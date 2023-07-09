from bs4 import BeautifulSoup
import requests
from requests import Response
import pandas as pd
import json
import math
from multiprocessing import process
import time, os
from threading import Thread, current_thread
from multiprocessing import Process, current_process, cpu_count, Pool, Lock
import concurrent.futures
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any
from enum import Enum

# number_of_examples = 452786
number_of_examples = 10000
step_size = 100
total_iterations = math.ceil(number_of_examples / step_size)

CSV_SAVE_PATH = "..\\..\\data\\raw\\openpowerlifting.csv"
# Indexes of data in json
NUMBER = 1
NAME = 2
INSTAGRAM = 4
ORIGIN = 6
FEDERATION = 8
COMPETITION_DATE = 9
COMPETITON_COUNTRY = 10
COMPETITON_CITY = 11
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

lock = Lock()


class ServerConnectionStatus(Enum):
    SUCCESSFUL = 200
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    INTERNAL_ERROR = 500


@dataclass
class Payload:
    status: int
    raw_response: Dict[str, Any]
    start: int
    end: int
    content: Optional[Dict[str, Any]] = None

    # TODO Fix Issue with post_init
    def __post_init__(self):
        self._generate_content

    def _html_parser(self, html: str) -> str:
        return html.body.p.text

    def _convert_html_to_json(self, html: str) -> Optional[Dict[str, Any]]:
        try:
            raw_data = self._html_parser(html)
            json_data = json.loads(raw_data)
        except Exception as e:
            print(f"Error: {e} for rows {self.start, self.end}")
            json_data = None

        return json_data

    def _generate_content(self):
        if self.status == ServerConnectionStatus.SUCCESSFUL.value:
            html = BeautifulSoup(self.raw_response.text, "lxml")
            self.content = self._convert_html_to_json(html)
        else:
            self.content = None


def get_response(start: int, end: int) -> Payload:
    url = f"https://www.openpowerlifting.org/api/rankings?start={start}&end={end}&lang=en&units=lbs"
    response = requests.get(url)
    data = Payload(
        status=response.status_code, raw_response=response, start=start, end=end
    )
    print(data.content)
    return data


def get_data_from_json(data: Payload):
    rows = []
    json_data = data.content
    for row in json_data["rows"]:
        rows.append(
            {
                "Number": row[NUMBER],
                "Name": row[NAME],
                "Instagram Handle": row[INSTAGRAM],
                "Origin": row[ORIGIN],
                "Federation": row[FEDERATION],
                "Competition Date": row[COMPETITION_DATE],
                "Competition Country": row[COMPETITON_COUNTRY],
                "Competition City": row[COMPETITON_CITY],
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
        )
    df = pd.DataFrame(rows)
    return df


first_iteration = True


def main(start_iteration, end_iteration):
    global first_iteration
    pid = os.getpid()
    threadName = current_thread().name
    processName = current_process().name

    print(
        f"{pid} * {processName} * {threadName} ---> Start getting data from columns {start_iteration * 100} - {end_iteration * 100}"
    )

    for iteration in range(start_iteration, end_iteration):
        start = iteration * step_size
        end = start + step_size - 1
        # print(f"Start: {start}, End: {end}")

        try:
            data = get_response(start, end)
            # json_data = convert_response_to_json(soup)
            df = get_data_from_json(data)
            lock.acquire()
            # print(df.head())
            if first_iteration:
                df.to_csv(CSV_SAVE_PATH, mode="a", header=True, index=False)
                first_iteration = False
            else:
                df.to_csv(CSV_SAVE_PATH, mode="a", header=False, index=False)
            lock.release()
        except Exception as e:
            print(f"error on {start} - {end}: {e}")
            continue

    print(f"{pid} * {processName} * {threadName} ---> Finished getting data...")


if __name__ == "__main__":
    start = time.time()

    number_of_processors = cpu_count()
    start_iteration = 0
    steps = math.ceil(total_iterations / number_of_processors)
    print(steps)
    threads = []

    for _ in range(number_of_processors):
        t = Thread(
            target=main,
            args=(start_iteration, start_iteration + steps),
        )
        threads.append(t)
        t.start()
        start_iteration += steps

    for t in threads:
        t.join()

    end = time.time()
    print(f"Time taken in seconds - {end-start}")
