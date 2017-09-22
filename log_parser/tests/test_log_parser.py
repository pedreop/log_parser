import os
from datetime import datetime
from distutils import dir_util
from pytest import fixture, mark
from log_parser.log_parser import format_log_line, line_relevant_to_filter, \
    load_log_file, parse_log_line, main

LOG_FILE_NAME = 'example.log'


@fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


@fixture
def log_line(datadir):
    """Log line sample data"""
    return parse_log_line("2012-09-13 16:04:22 DEBUG SID:34523 BID:1329 "
                          "RID:65d33 'Starting new session'")


class TestLineRelevantToFilter:
    """Test that a line is relevant to a filter"""

    def test_line_relevant_to_filter_date_range(self, log_line):
        result = line_relevant_to_filter(log_line, {'date_range':
                                                    '2012-09-12 2012-09-14'})
        assert(result)

    def test_line_relevant_to_filter_loglevel(self, log_line):
        result = line_relevant_to_filter(log_line, {'loglevel': 'DEBUG'})
        assert(result)

    def test_line_relevant_to_filter_session_id(self, log_line):
        result = line_relevant_to_filter(log_line, {'session_id': '34523'})
        assert(result)

    def test_line_relevant_to_filter_business_id(self, log_line):
        result = line_relevant_to_filter(log_line, {'business_id': '1329'})
        assert(result)

    def test_line_relevant_to_filter_request_id(self, log_line):
        result = line_relevant_to_filter(log_line, {'request_id': '65d33'})
        assert(result)


@mark.fast
class TestParseLogLine:
    """Test that parse_log_line works"""

    def test_datetime(self, log_line):
        assert(log_line['datetime'] ==
               datetime.strptime('2012-09-13 16:04:22', '%Y-%m-%d %H:%M:%S'))

    def test_log_entry(self, log_line):
        assert(log_line['loglevel'] in
               ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

    def test_session_id(self, log_line):
        assert(log_line['session_id'] == '34523')

    def test_business_id(self, log_line):
        assert(log_line['business_id'] == '1329')

    def test_request_id(self, log_line):
        assert(log_line['request_id'] == '65d33')

    def test_message(self, log_line):
        assert(log_line['message'] == 'Starting new session')


class TestMain:
    """Test main function with and without applying a filter."""

    def test_main(self, capsys, datadir):
        main(str(datadir.join(LOG_FILE_NAME)))
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_loglevel(self, capsys, datadir):
        main(str(datadir.join(LOG_FILE_NAME)), {'loglevel': 'DEBUG'})
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_business_id(self, capsys, datadir):
        main(str(datadir.join(LOG_FILE_NAME)), {'business_id': 319})
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_session_id(self, capsys, datadir):
        main(str(datadir.join(LOG_FILE_NAME)), {'session_id': 'SID:42111'})
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_request_id(self, capsys, datadir):
        main(str(datadir.join(LOG_FILE_NAME)), {'request_id': '7a323'})
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)

    def test_main_date_range(self, capsys, datadir):
        main(str(datadir.join(LOG_FILE_NAME)),
             {'date_range': '2012-09-14 2012-09-16'})
        out, err = capsys.readouterr()
        assert(len(out) > 0 and len(err) == 0)


@mark.fast
def test_format_log_line(log_line):
    """Check that a log line is restructed correctly"""
    assert(format_log_line(log_line) == "2012-09-13 16:04:22 DEBUG SID:34523 "
           "BID:1329 RID:65d33 'Starting new session'")


@mark.fast
def test_load_log_file(datadir):
    """Verify that a line of the log file is loaded."""
    assert(len(load_log_file(str(datadir.join(LOG_FILE_NAME))).__next__())
           == 78)  # 78 characters in the first line
