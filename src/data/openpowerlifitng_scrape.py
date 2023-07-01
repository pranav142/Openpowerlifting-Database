from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import math
from multiprocessing import process
import time, os
from threading import Thread, current_thread
from multiprocessing import Process, current_process, cpu_count, Pool

number_of_examples = 452786
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


def get_response(start, end):
    url = f"https://www.openpowerlifting.org/api/rankings?start={start}&end={end}&lang=en&units=lbs"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    return soup


def convert_response_to_json(soup):
    json_data = json.loads(soup.body.p.text)
    return json_data


def get_data_from_json(json_data):
    rows = []
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


def main(start_iteration, end_iteration):
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
            soup = get_response(start, end)
            json_data = convert_response_to_json(soup)
            df = get_data_from_json(json_data)
            # print(df.head())
            df.to_csv(CSV_SAVE_PATH, mode="a", header=not iteration, index=False)
        except Exception as e:
            print(f"error on {start} - {end}: {e}")
            continue

    print(f"{pid} * {processName} * {threadName} ---> Finished getting data...")


if __name__ == "__main__":
    start = time.time()

    number_of_processors = cpu_count()
    start_iteration = 0
    steps = int(total_iterations / number_of_processors)
    print(steps)
    processes = []

    pool = Pool(processes=number_of_processors)
    for _ in range(number_of_processors):
        pool.apply_async(main, args=(start_iteration, start_iteration + steps))
        start_iteration += steps

    pool.close()
    pool.join()

    end = time.time()
    print(f"Time taken in seconds - {end-start}")
