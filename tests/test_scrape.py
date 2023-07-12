import sys

sys.path.append("../src")

from data.scrape import (
    get_powerlifting_data,
    row_to_dictionary,
    save_data_to_csv,
    scrape_data,
)
