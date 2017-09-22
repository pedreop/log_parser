from argparse import Namespace
import pytest
from datetime import datetime
from log_parser import LogEntry, filter_by_field, load_entries, main

LOG_FILE_PATH = 'example.log'


@pytest.mark.fast
class TestParseLogEntry:
    """Test that the log import procedure works"""

    @pytest.fixture
    def log_entry(self):
        return LogEntry("2012-09-13 16:04:22 DEBUG SID:34523 BID:1329 "
                        "RID:65d33 'Starting new session'")

    def test_datetime(self, log_entry):
        assert(log_entry.datetime ==
               datetime.strptime('2012-09-13 16:04:22', '%Y-%m-%d %H:%M:%S'))

    def test_log_entry(self, log_entry):
        assert(log_entry.loglevel in
               ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    def test_session_id(self, log_entry):
        assert(log_entry.session_id == '34523')

    def test_business_id(self, log_entry):
        assert(log_entry.business_id == '1329')

    def test_request_id(self, log_entry):
        assert(log_entry.request_id == '65d33')

    def test_message(self, log_entry):
        assert(log_entry.message == 'Starting new session')


class TestFilterByField:
    """Test each filter by Field."""

    @pytest.fixture
    def entries(self):
        return load_entries(LOG_FILE_PATH)

    def test_filter_by_field_loglevel(self, entries):
        result = filter_by_field(entries, field='loglevel', value='DEBUG')
        assert(len(result) == 5)

    def test_filter_by_field_business_id(self, entries):
        result = filter_by_field(entries, field='business_id', value='319')
        assert(len(result) == 4)

    def test_filter_by_field_session_id(self, entries):
        result = filter_by_field(entries, field='session_id', value='42111')
        assert(len(result) == 4)

    def test_filter_by_field_request_id(self, entries):
        result = filter_by_field(entries, field='request_id', value='7a323')
        assert(len(result) == 2)

    def test_filter_by_field_date_range(self, entries):
        result = filter_by_field(entries, field='date_range',
                                 value='2012-09-14 2012-09-16')
        assert(len(result) == 5)


@pytest.mark.fast
def test_load_entries():
    """Verify that each line of the log file is parsed and loaded."""
    assert(len(load_entries(LOG_FILE_PATH)) == 7)


class TestMain:
    """Test main function with and without filters by field."""

    def test_main(self, capsys):
        main(Namespace(path=[LOG_FILE_PATH]))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_loglevel(self, capsys):
        main(Namespace(path=[LOG_FILE_PATH], loglevel='DEBUG'))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_business_id(self, capsys):
        main(Namespace(path=[LOG_FILE_PATH], business_id=319))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_session_id(self, capsys):
        main(Namespace(path=[LOG_FILE_PATH], session_id=42111))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_request_id(self, capsys):
        main(Namespace(path=[LOG_FILE_PATH], request_id='7a323'))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_date_range(self, capsys):
        main(Namespace(path=[LOG_FILE_PATH],
                       date_range='2012-09-14 2012-09-16'))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)
