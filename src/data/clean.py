import pandas as pd
import numpy as np
import functools
from typing import Callable
import os


CompasableFunction = Callable[[pd.DataFrame], pd.DataFrame]


def compose(*functions: CompasableFunction) -> CompasableFunction:
    """Function to chain multiple processing steps"""
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions)


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    """Removes Tildes From Age Column"""
    assert "Age" in df.columns
    df["Age"] = df["Age"].str.replace("~", "").astype(np.float64)
    return df


def clean_class_column(df: pd.DataFrame) -> pd.DataFrame:
    """Converts class values into clean floating point values"""
    assert "Class" in df.columns
    df["Class"] = df["Class"].str.replace("+", "")
    df["Class"] = df["Class"].mask(df["Class"] == "").astype(np.float64)
    return df


def sort_df(df: pd.DataFrame) -> pd.DataFrame:
    """re-orders df into a intutive layout"""
    assert "Number" in df.columns
    df = df.sort_values(by="Number")
    df = df.drop("Number", axis=1).reset_index(drop=True)
    return df


def convert_date(df: pd.DataFrame) -> pd.DataFrame:
    """Converts date column from object to pandas datatime object"""
    assert "Competition_Date" in df.columns
    df["Competition_Date"] = pd.to_datetime(df["Competition_Date"])
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Replaces white space in columns with underscore"""
    df.columns = df.columns.str.replace(" ", "_")
    return df


def create_strength_per_bodyweight(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Creates a column showing relation between bodyweight and strength"""
    assert column in df.columns, f"{column} not found in columns"
    df[f"{column}_Per_Body_Weight"] = df[column] / df["Weight"]
    return df


def create_ID_column(df: pd.DataFrame) -> pd.DataFrame:
    """Creates a unique ID for every person"""
    df["ID"] = pd.factorize(df["Name"])[0] + 1
    return df


def process_data(raw_df_path: str) -> pd.DataFrame:
    """chains preprocessing steps on the data to return final transformed dataframe"""
    raw_data = pd.read_csv(raw_df_path)
    data_processing = compose(
        rename_columns,
        clean_class_column,
        clean_age_column,
        sort_df,
        convert_date,
        functools.partial(create_strength_per_bodyweight, column="Bench"),
        functools.partial(create_strength_per_bodyweight, column="Squat"),
        functools.partial(create_strength_per_bodyweight, column="Deadlift"),
        functools.partial(create_strength_per_bodyweight, column="Total"),
        create_ID_column,
    )
    processed_df = data_processing(raw_data)
    return processed_df


def clear_save_path(save_df_path: str) -> None:
    """Ensures the save path is clear so there are no file conflicts"""
    save_dir = os.path.dirname(save_df_path)

    if not os.path.exists(save_dir):
        print("Folder Doesn't Exist Creating ")
        os.makedirs(save_dir)

    if os.path.exists(save_df_path):
        print("Conflicting file found")
        os.remove(save_df_path)
        print("File deleted successfully. Loading new data...")
    else:
        print("File does not exist yet. Loading new data...")


def main(raw_df_path: str, save_df_path: str) -> None:
    processed_df = process_data(raw_df_path)
    clear_save_path(save_df_path)
    processed_df.to_csv(save_df_path, index=False)
    print(f"{len(processed_df)} records have been loaded successfully")


if __name__ == "__main__":
    RAW_DF_PATH = "..\\..\\data\\raw\\openpowerlifting.csv"
    SAVE_DF_PATH = "..\\..\\data\\processed\\processed_lifting_data.csv"
    main(RAW_DF_PATH, SAVE_DF_PATH)
