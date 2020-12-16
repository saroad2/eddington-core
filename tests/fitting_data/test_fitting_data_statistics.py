import random

import pytest

from eddington.fitting_data import FittingData
from eddington.statistics import Statistics
from tests.fitting_data import COLUMNS, COLUMNS_NAMES, NUMBER_OF_RECORDS, STATISTICS
from tests.util import assert_statistics

EPSILON = 1e-7


def test_initial_statistics():
    fitting_data = FittingData(COLUMNS)
    for header in COLUMNS_NAMES:
        assert_statistics(
            fitting_data.statistics(header), STATISTICS[header], rel=EPSILON
        )


def test_unselect_record_statistics():
    fitting_data = FittingData(COLUMNS)
    record_index = random.randint(0, NUMBER_OF_RECORDS)
    fitting_data.unselect_record(record_index)
    for header in COLUMNS_NAMES:
        header_statistics = fitting_data.statistics(header)
        assert header_statistics.mean != pytest.approx(STATISTICS[header].mean)
        assert_statistics(
            fitting_data.statistics(header),
            Statistics.from_array(fitting_data.column_data(header)),
            rel=EPSILON,
        )


def test_set_record_indices_statistics():
    fitting_data = FittingData(COLUMNS)
    record_indices = [False, True, False, False, True] + [False] * (
        NUMBER_OF_RECORDS - 5
    )
    fitting_data.records_indices = record_indices
    for header in COLUMNS_NAMES:
        header_statistics = fitting_data.statistics(header)
        assert header_statistics.mean != pytest.approx(STATISTICS[header].mean)
        assert_statistics(
            fitting_data.statistics(header),
            Statistics.from_array(fitting_data.column_data(header)),
            rel=EPSILON,
        )


def test_unselect_all_statistics():
    fitting_data = FittingData(COLUMNS)
    fitting_data.unselect_all_records()
    for header in COLUMNS_NAMES:
        assert fitting_data.statistics(header) is None


def test_reselect_all_statistics():
    fitting_data = FittingData(COLUMNS)
    fitting_data.unselect_all_records()
    fitting_data.select_all_records()
    for header in COLUMNS_NAMES:
        assert_statistics(
            fitting_data.statistics(header), STATISTICS[header], rel=EPSILON
        )
