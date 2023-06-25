from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import json
import math

number_of_examples = 452786
step_size = 100
total_iterations = math.ceil(number_of_examples / step_size)

for iteration in range(3825, total_iterations):
    start = iteration * step_size
    end = start + step_size - 1

    print(f"Start: {start}, End: {end}")
    url = f"https://www.openpowerlifting.org/api/rankings?start={start}&end={end}&lang=en&units=lbs"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    try:
        json_data = json.loads(soup.body.p.text)
        rows = []
        for row in json_data["rows"]:
            number = row[1]
            name = row[2]
            insta_handle = row[4]
            origin = row[6]
            federation = row[8]
            competition_date = row[9]
            competition_country = row[10]
            competition_city = row[11]
            gender = row[13]
            equipment = row[14]
            age = row[15]
            weight = row[17]
            class_ = row[18]
            squat = row[19]
            bench = row[20]
            deadlift = row[21]
            total = row[22]
            dots = row[23]

            rows.append(
                {
                    "Number": number,
                    "Name": name,
                    "Instagram Handle": insta_handle,
                    "Origin": origin,
                    "Federation": federation,
                    "Competition Date": competition_date,
                    "Competition Country": competition_country,
                    "Competition City": competition_city,
                    "Gender": gender,
                    "Equipment": equipment,
                    "Age": age,
                    "Weight": weight,
                    "Class": class_,
                    "Squat": squat,
                    "Bench": bench,
                    "Deadlift": deadlift,
                    "Total": total,
                    "Dots": dots,
                }
            )

        df = pd.DataFrame(rows)

        df.to_csv("openpowerlifting.csv", mode="a", header=not iteration, index=False)

        print(df.head())

    except Exception as e:
        print(f"An error occurred: {e}")
        continue
