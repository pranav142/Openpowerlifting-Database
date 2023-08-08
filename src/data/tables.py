from enum import Enum

is_weight = True


class Column:
    def __init__(self, _column_name: str, _sql_properties: str, _is_weight: bool):
        self.column_name = _column_name
        self.sql_properties = _sql_properties
        self.is_weight = _is_weight

    def get_full_sql_column_property(self):
        return f"{self.column_name} {self.sql_properties}"


class columnsCollection:
    def __init__(self, _columns: list[Column]):
        self.columns = _columns

    def get_all_sql_columns(self) -> list[str]:
        return [column.get_full_sql_column_property() for column in self.columns]

    def get_all_column_names(self) -> list[str]:
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
    records = ("records", columnsCollection(records_columns))

    @classmethod
    def get_all_tables(cls):
        return [table.value[0] for table in cls]


if __name__ == "__main__":
    for column in Tables.records.value[1].columns:
        print(column.is_weight)
