import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_bar_graph(
    *, data: pd.core.series.Series, title: str, xlabel: str, ylabel: str, kind: str
):
    """Plots a bargraph"""
    plt.figure(figsize=(10, 7))
    data.plot(kind=kind, color=plt.cm.Set3(range(10)))
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def plot_pie_chart(
    *,
    data: pd.core.series.Series,
    title: str,
    digit_format: str = "%1.1f%%",
):
    """Plots a pie chart"""
    plt.figure(figsize=(10, 7))
    plt.pie(
        data.values,
        labels=data.index,
        autopct=digit_format,
    )
    plt.axis("equal")
    plt.legend(title="Categories", loc="best")
    plt.title(title)
    plt.show()


def plot_histogram(
    *,
    data: pd.DataFrame,
    title: str,
    bins: int,
    xlabel: str,
    ylabel: str,
    hue: str = None,
    column: str,
):
    """Plots a histogram"""
    assert column in data.columns, "column not found in dataframe"
    ALPHA = 0.4
    plt.figure(figsize=(10, 7))

    if hue is None:
        plt.hist(data[column], bins=bins, alpha=ALPHA)
    else:
        unique_hues = data[hue].unique()
        for hue_value in unique_hues:
            plt.hist(
                data[data[hue] == hue_value][column],
                bins=bins,
                alpha=ALPHA,
                label=hue_value,
            )
        plt.legend()

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def plot_scatterplot(
    *,
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    hue: str = None,
    aspect: int = 2,
    height: int = 7,
    markers: str = "o",
    xlabel: str = "default",
    ylabel: str = "default",
    title: str = "default",
) -> None:
    assert (
        x_column in data.columns and y_column in data.columns
    ), "Column not found in dataframe"

    sns.lmplot(
        x=x_column,
        y=y_column,
        hue=hue,
        data=data,
        aspect=aspect,
        height=height,
        markers=markers,
    )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.show()


def show_column_stats(*, data: pd.DataFrame, column: str, hue: str = None) -> None:
    """Gives a general overview of a column"""
    assert column in data.columns, "column not found in dataframe"
    if hue is None:
        print(f"{column} statistics")
        print(data[column].describe())
    else:
        assert hue in data.columns, "hue could not be found in columns"
        unique_hues = data[hue].unique()
        for hue_value in unique_hues:
            print(f"{column} statistics for {hue_value}")
            print(data.loc[data[hue] == hue_value][column].describe(), end="\n\n")
