from enum import Enum
from typing import List

is_weight = True


class Column:
    """Represents a column in a database table.

    Args:
        _column_name (str): Name of the column.
        _sql_properties (str): SQL properties for the column.
        _is_weight (bool): Indicates if the column represents weight-related data.
    """

    def __init__(self, _column_name: str, _sql_properties: str, _is_weight: bool):
        """Initialize a Column instance.

        Args:
            _column_name (str): Name of the column.
            _sql_properties (str): SQL properties for the column.
            _is_weight (bool): Indicates if the column represents weight-related data.
        """
        self.column_name = _column_name
        self.sql_properties = _sql_properties
        self.is_weight = _is_weight

    def get_full_sql_column_property(self):
        """Get the full SQL property for the column.

        Returns:
            str: Full SQL property of the column.
        """
        return f"{self.column_name} {self.sql_properties}"


class columnsCollection:
    """Collection of columns for a database table."""

    def __init__(self, _columns: list[Column]):
        """Initialize a columnsCollection instance.

        Args:
            _columns (list[Column]): List of Column instances.
        """
        self.columns = _columns

    def get_all_sql_columns(self) -> list[str]:
        """Get a list of all SQL column properties.

        Returns:
            list[str]: List of all SQL column properties.
        """
        return [column.get_full_sql_column_property() for column in self.columns]

    def get_all_column_names(self) -> list[str]:
        """Get a list of all column names.

        Returns:
            list[str]: List of all column names.
        """
        return [column.column_name for column in self.columns]


records_columns = [
    Column("ID", "INT PRIMARY KEY NOT NULL AUTO_INCREMENT", not is_weight),
    Column("Name", "VARCHAR(255)", not is_weight),
    Column("Instagram_Handle", "VARCHAR(255)", not is_weight),
    Column("Origin", "VARCHAR(255)", not is_weight),
    Column("Gender", "CHAR(50)", not is_weight),
    Column("Competition_Date", "DATE", not is_weight),
    Column("Competition_Country", "VARCHAR(255)", not is_weight),
    Column("Competition_City", "VARCHAR(255)", not is_weight),
    Column("Equipment", "VARCHAR(255)", not is_weight),
    Column("Age", "INT", not is_weight),
    Column("Weight", "FLOAT", is_weight),
    Column("Class", "VARCHAR(255)", not is_weight),
    Column("Squat", "FLOAT", is_weight),
    Column("Bench", "FLOAT", is_weight),
    Column("Deadlift", "FLOAT", is_weight),
    Column("Total", "FLOAT", is_weight),
    Column("Dots", "FLOAT", not is_weight),
]


class Tables(Enum):
    """Enumeration of database tables and their column collections."""

    records = ("records", columnsCollection(records_columns))

    @property
    def name(self):
        """Get the name of the table.

        Returns:
            str: Name of the table.
        """
        return self.value[0]

    @property
    def columns_collection(self):
        """Get the columnsCollection instance associated with the table.

        Returns:
            columnsCollection: Collection of columns for the table.
        """
        return self.value[1]

    @classmethod
    def get_all_tables(cls):
        """Get a list of all table names.

        Returns:
            list[str]: List of all table names.
        """
        return [table.value[0] for table in cls]
