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


def process_data(raw_df_path: str) -> pd.DataFrame:
    """Processes the data"""
    raw_data = pd.read_csv(raw_df_path)
    data_processing = compose(
        rename_columns, clean_class_column, clean_age_column, sort_df, convert_date
    )
    processed_df = data_processing(raw_data)
    return processed_df


def clear_save_path(save_df_path: str):
    """Ensures the save path is clear so there are no file conflicts"""
    if os.path.exists(save_df_path):
        print("Conflicting file found")
        os.remove(save_df_path)
        print("File deleted successfully. Loading new data...")
    else:
        print("File does not exist yet. Loading new data...")


def main(raw_df_path: str, save_df_path: str):
    processed_df = process_data(raw_df_path)
    clear_save_path(save_df_path)
    processed_df.to_csv(save_df_path, index=False)
    print(f"{len(processed_df)} records have been loaded successfully")


if __name__ == "__main__":
    RAW_DF_PATH = "../../data/raw/openpowerlifting.csv"
    SAVE_DF_PATH = "../../data/processed/processed_lifting_data.csv"
    main(RAW_DF_PATH, SAVE_DF_PATH)
