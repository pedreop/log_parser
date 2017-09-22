from argparse import Namespace
from distutils import dir_util
import os
from pytest import fixture, mark
from datetime import datetime
from log_parser.log_parser import LogEntry, filter_by_field, load_entries, main

LOG_FILE_NAME = 'example.log'

@fixture
def datadir(tmpdir, request):
    '''
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    '''
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir

@mark.fast
class TestParseLogEntry:
    """Test that the log import procedure works"""

    @fixture
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

    @fixture
    def entries(self, datadir):
        return load_entries(str(datadir.join(LOG_FILE_NAME)))

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


@mark.fast
def test_load_entries(datadir):
    """Verify that each line of the log file is parsed and loaded."""
    assert(len(load_entries(str(datadir.join(LOG_FILE_NAME)))) == 7)


class TestMain:
    """Test main function with and without filters by field."""

    def test_main(self, capsys, datadir):
        main(Namespace(path=[str(datadir.join(LOG_FILE_NAME))]))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_loglevel(self, capsys, datadir):
        main(Namespace(path=[str(datadir.join(LOG_FILE_NAME))], loglevel='DEBUG'))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_business_id(self, capsys, datadir):
        main(Namespace(path=[str(datadir.join(LOG_FILE_NAME))], business_id=319))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_session_id(self, capsys, datadir):
        main(Namespace(path=[str(datadir.join(LOG_FILE_NAME))], session_id='SID:42111'))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_request_id(self, capsys, datadir):
        main(Namespace(path=[str(datadir.join(LOG_FILE_NAME))], request_id='7a323'))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_date_range(self, capsys, datadir):
        main(Namespace(path=[str(datadir.join(LOG_FILE_NAME))],
                       date_range='2012-09-14 2012-09-16'))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)
