import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_bar_graph(
    *, data: pd.core.series.Series, title: str, xlabel: str, ylabel: str, kind: str
):
    """Plot a bar graph.

    Args:
        data (pd.core.series.Series): Data to be plotted.
        title (str): Title of the plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        kind (str): Type of bar graph (e.g., 'bar', 'barh', etc.).
    """
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
    """Plot a pie chart.

    Args:
        data (pd.core.series.Series): Data to be plotted.
        title (str): Title of the plot.
        digit_format (str, optional): Format for the percentage values. Defaults to "%1.1f%%".
    """
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
    """Plot a histogram.

    Args:
        data (pd.DataFrame): Data to be plotted.
        title (str): Title of the plot.
        bins (int): Number of bins for the histogram.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        hue (str, optional): Column name for hue grouping. Defaults to None.
        column (str): Column to plot the histogram for.
    """
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
    title: str = None,
) -> None:
    """Plot a scatterplot.

    Args:
        data (pd.DataFrame): Data to be plotted.
        x_column (str): Column for the x-axis.
        y_column (str): Column for the y-axis.
        hue (str, optional): Column name for hue grouping. Defaults to None.
        aspect (int, optional): Aspect ratio of the plot. Defaults to 2.
        height (int, optional): Height of the plot. Defaults to 7.
        markers (str, optional): Marker style for the scatter points. Defaults to "o".
        xlabel (str, optional): Label for the x-axis. Defaults to "default".
        ylabel (str, optional): Label for the y-axis. Defaults to "default".
        title (str, optional): Title of the plot. Defaults to None.
    """
    assert (
        x_column in data.columns and y_column in data.columns
    ), "Column not found in dataframe"

    if title is None:
        title = f"Correlation Between {x_column} and {y_column}; Correlation Coeffecient: {data[x_column].corr(data[y_column]) :.3f}"

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
    """Show statistics for a column in the DataFrame.

    Args:
        data (pd.DataFrame): Data for calculating statistics.
        column (str): Column for which to display statistics.
        hue (str, optional): Column name for hue grouping. Defaults to None.
    """
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
