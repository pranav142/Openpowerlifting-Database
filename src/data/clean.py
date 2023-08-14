import pandas as pd
import numpy as np
import functools
from typing import Callable
import os


CompasableFunction = Callable[[pd.DataFrame], pd.DataFrame]


def compose(*functions: CompasableFunction) -> CompasableFunction:
    """Compose a series of functions into a single function.

    Args:
        *functions (CompasableFunction): Functions to be composed.

    Returns:
        CompasableFunction: A new function representing the composition
        of input functions.
    """
    return functools.reduce(lambda f, g: lambda x: g(f(x)), functions)


def clean_age_column(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the 'Age' column in the DataFrame.

    Args:
        df (DataFrame): Input DataFrame.

    Returns:
        DataFrame: DataFrame with the 'Age' column cleaned.
    """
    assert "Age" in df.columns
    df["Age"] = df["Age"].str.replace("~", "").astype(np.float64)
    return df


def clean_class_column(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the 'Class' column in the DataFrame.

    Args:
        df (DataFrame): Input DataFrame.

    Returns:
        DataFrame: DataFrame with the 'Class' column cleaned.
    """
    assert "Class" in df.columns
    df["Class"] = df["Class"].str.replace("+", "")
    df["Class"] = df["Class"].mask(df["Class"] == "").astype(np.float64)
    return df


def sort_df(df: pd.DataFrame) -> pd.DataFrame:
    """Sort the DataFrame based on the 'Number' column and reset index.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'Number' column.

    Returns:
        pd.DataFrame: Sorted DataFrame with the 'Number' column removed and index reset.
    """
    assert "Number" in df.columns
    df = df.sort_values(by="Number")
    df = df.drop("Number", axis=1).reset_index(drop=True)
    return df


def convert_date(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the 'Competition_Date' column to datetime format.

    Args:
        df (pd.DataFrame): Input DataFrame containing a 'Competition_Date' column.

    Returns:
        pd.DataFrame: DataFrame with the 'Competition_Date' column converted to datetime.
    """
    assert "Competition_Date" in df.columns
    df["Competition_Date"] = pd.to_datetime(df["Competition_Date"])
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Replace spaces in column names with underscores.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with column names replaced by replacing spaces with underscores.
    """
    df.columns = df.columns.str.replace(" ", "_")
    return df


def create_strength_per_bodyweight(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calculate strength per body weight for a specified column.

    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Name of the column for which strength per body weight is calculated.

    Returns:
        pd.DataFrame: DataFrame with an additional column for strength per body weight.
    """
    assert column in df.columns, f"{column} not found in columns"
    df[f"{column}_Per_Body_Weight"] = df[column] / df["Weight"]
    return df


def create_ID_column(df: pd.DataFrame) -> pd.DataFrame:
    """Create an 'ID' column based on factorizing the 'Name' column.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with an additional 'ID' column.
    """
    df["ID"] = pd.factorize(df["Name"])[0] + 1
    return df


def process_data(raw_df_path: str) -> pd.DataFrame:
    """Process raw data from a CSV file.

    Args:
        raw_df_path (str): Path to the raw CSV file.

    Returns:
        DataFrame: Processed DataFrame.
    """
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
    """Clear the save path if conflicting files exist.

    Args:
        save_df_path (str): Path to the save file.
    """
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
    """Process raw data and save the processed DataFrame.

    Args:
        raw_df_path (str): Path to the raw CSV file.
        save_df_path (str): Path to save the processed DataFrame.
    """
    processed_df = process_data(raw_df_path)
    clear_save_path(save_df_path)
    processed_df.to_csv(save_df_path, index=False)
    print(f"{len(processed_df)} records have been loaded successfully")


if __name__ == "__main__":
    RAW_DF_PATH = "..\\..\\data\\raw\\openpowerlifting.csv"
    SAVE_DF_PATH = "..\\..\\data\\processed\\processed_lifting_data.csv"
    main(RAW_DF_PATH, SAVE_DF_PATH)
