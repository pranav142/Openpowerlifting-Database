from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


def get_lifting_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    tables = soup.find_all("table", class_="tabledata")
    rows = tables[0].find_all("tr")[1:]

    return rows


def create_df(rows):
    df = pd.DataFrame(columns=["Name", "Points", "Weight", "Body Weight"])

    data = []

    for row in rows:
        cells = row.find_all("td")
        name = cells[1].a.text
        date = cells[2].text
        points = cells[3].text
        weight = cells[4].text
        body_weight = cells[5].text

        data.append(
            {
                "Name": name,
                "Date": date,
                "points": points,
                "Weight": weight,
                "Body Weight": body_weight,
            }
        )

        df = pd.concat([pd.DataFrame(data)])

    return df


def get_lifting_df(url):
    rows = get_lifting_data(url)
    df = create_df(rows)
    return df


if __name__ == "__main__":
    URL = "https://usapl.liftingdatabase.com/rankings"

    start_time = time.time()

    df = get_lifting_df(URL)

    end_time = time.time()
    execution_time = end_time - start_time

    print(
        f"Execution Time: {execution_time:.03f} seconds, There are {len(df)} examples"
    )
    print(df.head())
    print("Creating CSV File...")

    df.to_csv("powerlifting.csv", index=False)
