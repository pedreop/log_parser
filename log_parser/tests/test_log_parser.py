import os
import sys
from datetime import datetime
from distutils import dir_util
from pytest import fixture
from log_parser.log_parser import format_log_line, line_relevant_to_query, \
    load_log_file, parse_args, parse_log_line, main, parse_args_main


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


def test_format_log_line(log_line):
    """Check that a log line is restructed correctly"""
    assert(format_log_line(log_line) == "2012-09-13 16:04:22 DEBUG SID:34523 "
           "BID:1329 RID:65d33 'Starting new session'")
    assert(format_log_line(log_line) != "")


def test_line_relevant_to_query(log_line):
    """
    Test that a log line is relevant to query.
    'line_relevant_to_query' accepts a line of the log parsed as a dictionary
    and a dictionary of query arguments
    Return Value: Boolean (Line relevant to query or not)
    """
    sample_test_args = {'date_range': '2012-09-12 2012-09-14',
                        'loglevel': 'DEBUG',
                        'session_id': '34523',
                        'business_id': '1329',
                        'request_id': '65d33'}
    # Individually
    for key, value in sample_test_args.items():
        assert line_relevant_to_query(log_line, {key: value})
    # All together
    assert line_relevant_to_query(log_line, sample_test_args)
    # Individually (incorrect values switching the last character with a 2)
    for key, value in sample_test_args.items():
        assert not line_relevant_to_query(log_line,
                                          {key: '{}2'.format(value[:-1])})


def test_load_log_file(datadir):
    """
    Verify that a line of the log file is loaded.
    load_log_file requires the path to a log file.
    Return Value: Lazily returns a string (line from log)
    """
    count = 0
    for line in load_log_file(str(datadir.join('example.log'))):
        count += 1
        assert(len(line) > 0)  # Each line should contain characters
    assert(count == 7)  # Lines present in file


def test_parse_args():
    """
    Simulate passing arguments (flags, etc) and expect a path (required) and
    a dictionary of query arguments (optional). Sample Test Values format:
    [['flag', 'Value', { 'Expected Response as a Dictionary' }], ..]
    Return Values: String (Log file path),  Dictionary (All queries)
    """
    # Check with no arguments, except log file path (required)
    sys.argv = ['log_parser/log_parser.py', 'example.log']
    assert(parse_args() == ('example.log', {}))
    # Apply query arguments
    sample_test_values = [['-l', 'DEBUG', {'loglevel': 'DEBUG'}],
                          ['-b', '1329', {'business_id': '1329'}],
                          ['-s', '34523', {'session_id': '34523'}],
                          ['-r', '65d33', {'request_id': '65d33'}],
                          ['-d', '2012-09-13 16:04:22',
                           {'date_range': '2012-09-13 16:04:22'}]]
    for test_value in sample_test_values:
        sys.argv = ['log_parser/log_parser.py', 'example.log',
                    test_value[0], test_value[1]]
        assert(parse_args() == ('example.log', test_value[2]))
    # Check that file path is required
    sys.argv = ['log_parser/log_parser.py', ]
    try:
        parse_args()
        assert False
    except:
        assert True


def test_parse_log_line(log_line):
    """
    Test that parse_log_line takes a string (line) and returns it as a
    dictionary. In the case of this test, the log_line has already been parsed
    by 'parse_log_lines' by the fixture 'log_line'
    Return Value: Dictionary (Log line)
    """
    # Check parsing of datetime
    assert(log_line['datetime'] == datetime.strptime('2012-09-13 16:04:22',
                                                     '%Y-%m-%d %H:%M:%S'))
    # Check if loglevel is in available values
    assert(log_line['loglevel'] in ['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                    'CRITICAL'])
    # Check if other values are parsed from their string form
    sample_test_values = {'session_id': '34523',
                          'business_id': '1329',
                          'request_id': '65d33',
                          'message': 'Starting new session'}
    for key, value in sample_test_values.items():
        assert(log_line[key] == value)
    # Check what happens if a malformed log line is presented
    assert(parse_log_line("13-09-2012 16:04:22 DEBUG SID:34523 BID:1329 "
                          "RID:65d33 'Starting new session'")
           == 'Invalid log line')


def test_main(capsys, datadir):
    """
    Test main function with and without applying a query. The Path is specified
    separately. Sample Test Values format:
    {'Column Name': ['Value', Quantity of results returned], ..}
    """
    sample_test_values = {None: [None, 7],
                          'loglevel': ['DEBUG', 5],
                          'business_id': ['319', 4],
                          'session_id': ['SID:42111', 4],
                          'request_id': ['7a323', 2],
                          'date_range': ['2012-09-14 2012-09-16', 5]}
    for key, value in sample_test_values.items():
        main(str(datadir.join('example.log')), {key: value[0]} if key else {})
        out, err = capsys.readouterr()
        assert(len(out.split('\n\nFunction: ')[0].split('\n'))
               == value[1])  # Check Total Results count
        assert(len(err) == 0)  # Verify that there is no error returned


def test_parse_args_main(capsys):
    """
    Ensure path argument is passed. Usage options should appear if no path
    argument is passed
    """
    # With argument
    sys.argv = ['log_parser/log_parser.py', 'example.log']
    parse_args_main()
    __, err = capsys.readouterr()
    assert(len(err) == 0)
    # Without argument
    try:
        sys.argv = ['log_parser/log_parser.py', ]
        parse_args_main()
    except:
        __, err = capsys.readouterr()
        assert err.startswith('usage')
