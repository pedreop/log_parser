#! /usr/bin/env python3
import argparse
import re
import sys
from collections import OrderedDict
from datetime import datetime
from profiler.profiler import Profile


@Profile
def format_log_line(line):
    """Format log line to its usual structure"""
    return ('{datetime:%Y-%m-%d %H:%M:%S} {loglevel} SID:{session_id} '
            'BID:{business_id} RID:{request_id} \'{message}\''
            .format(**line))


@Profile
def line_relevant_to_query(line, kwargs):
    """Check to see if the specified arguments are relevant to the line"""
    for key, value in kwargs.items():
        if key != 'date_range':
            # If SID:, BID:, RID: is given in the arguments, remove it
            if ':' in str(value):
                value = value.split(':')[1]
            if line[key].lower() != str(value).lower():
                return False
        else:
            from_datetime = datetime.strptime('{from_date} 00:00:00'.format(
                from_date=value.split(' ')[0]), '%Y-%m-%d %H:%M:%S')
            to_datetime = datetime.strptime('{to_date} 23:59:59'.format(
                to_date=value.split(' ')[1]), '%Y-%m-%d %H:%M:%S')
            if line['datetime'] < from_datetime or \
                    line['datetime'] > to_datetime:
                return False
    return True


@Profile
def load_log_file(path):
    """Return the next line of the log file as required"""
    try:
        with open(path) as f:
            yield from f
    except FileNotFoundError:
        print('Loading Log Entries Failed')
        sys.exit(1)


def parse_args():
    """Parse arguments received (terminal). File path is passed separately"""
    kwargs = {}
    parser = argparse.ArgumentParser(
        description='Import log file and return all or a subsection of lines')
    parser.add_argument('path', nargs='+', help='Log File Path')
    parser.add_argument('-l', '--loglevel', nargs='?',
                        help='Filter by Log Level (DEBUG, ERROR, WARN, ..)')
    parser.add_argument('-b', '--business-id', nargs='?',
                        help='Filter by Business ID')
    parser.add_argument('-s', '--session-id', nargs='?',
                        help='Filter by Session ID')
    parser.add_argument('-r', '--request-id', nargs='?',
                        help='Filter by Request ID')
    parser.add_argument('-d', '--date-range', nargs='?',
                        help='Filter by Date Range ("YYYY-MM-DD YYYY-MM-DD")')
    for key, value in parser.parse_args()._get_kwargs():
        if value:
            if key != 'path':
                kwargs[key] = value
            else:
                path = value[0]
    return (path, kwargs)


@Profile
def parse_log_line(line):
    """
    Parse and return a log line.
    Order of Columns: DATE LOGLEVEL SESSION-ID BUSINESS-ID REQUEST-ID MSG
    """
    keys = ['datetime', 'loglevel', 'session_id',
            'business_id', 'request_id', 'message']
    reg = r"(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) " \
        "(?P<loglevel>\w+) SID:(?P<session_id>\d+) " \
        "BID:(?P<business_id>\d+) RID:(?P<request_id>\w+) '(.*)'"
    reg_match = re.match(reg, line)
    if not reg_match:
        return 'Invalid log line'
    values = iter(reg_match.groups())
    log_line = OrderedDict((zip(keys, values)))
    log_line['datetime'] = datetime.strptime(log_line['datetime'],
                                             '%Y-%m-%d %H:%M:%S')
    return log_line


def main(path, kwargs={}):
    """
    Request line from log as required. Show all lines if no argument apart from
    path is given. Check that a line is still relevant if a query argument
    is specified.
    """
    for line in load_log_file(path):
        if kwargs:
            parsed_line = parse_log_line(line)
            if line_relevant_to_query(parsed_line, kwargs):
                print(format_log_line(parsed_line))
        else:
            print(line.strip('\n'))
    # Print Profiling Results
    for key, value in Profile.all_functions().items():
        print(Profile.str(value))


if __name__ == "__main__":
    main(*parse_args())
