#! /usr/bin/env python3
import argparse
import re
import sys
from datetime import datetime
from profile import Profile


@Profile
class LogEntry:
    """
    The LogEntry class parses a log entry on creation. A Log Entry has a
    Datetime, LogLevel, Session ID, Business ID, Request ID and a Message.
    """

    def __init__(self, entry):
        self._parse(entry)

    def __str__(self):
        return ('{datetime:%Y-%m-%d %H:%M:%S} {loglevel} SID:{session_id} '
                'BID:{business_id} RID:{request_id} {message}'
                .format(**self.__dict__))

    def _parse(self, entry):
        """
        Parse a Log Entry.
        Order of Columns: DATE LOGLEVEL SESSION-ID BUSINESS-ID REQUEST-ID MSG
        """
        reg = r"(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) " \
            "(?P<loglevel>\w+) SID:(?P<session_id>\d+) " \
            "BID:(?P<business_id>\d+) RID:(?P<request_id>\w+) '(.*)'"
        datetime_string, self.loglevel, self.session_id, self.business_id, \
            self.request_id, self.message = re.match(reg, entry).groups()
        self.datetime = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')


@Profile
def filter_by_field(entries, field, value):
    """Filter by LogLevel, SessionID, Business ID, Request ID and Date Range"""
    if field == 'date_range':
        from_datetime = datetime.strptime('{from_date} 00:00:00'.format(
            from_date=value.split(' ')[0]), '%Y-%m-%d %H:%M:%S')
        to_datetime = datetime.strptime('{to_date} 23:59:59'.format(
            to_date=value.split(' ')[1]), '%Y-%m-%d %H:%M:%S')
        return [entry for entry in entries
                if entry.datetime >= from_datetime
                and entry.datetime <= to_datetime]
    return [entry for entry in entries if entry.__dict__.get(field) == value]


@Profile
def load_entries(file_path):
    """
    Try to log entries from file_path, create log entry objects and add to
    entries list
    """
    try:
        entries = []
        with open(file_path) as f:
            for line in f:
                entries.append(LogEntry(line))
        return entries
    except FileNotFoundError:
        print('Loading Log Entries Failed')
        sys.exit(1)


@Profile
def main(args):
    """
    Intiate loading of entries, apply filters based on specified flags and
    display to screen.
    """
    entries = load_entries(args.path[0])
    for key, value in args._get_kwargs():
        if value and key != 'path':
            # If SID:, BID:, RID: is given in the arguments, remove it
            if ':' in str(value):
                value = value.split(':')[1]
            entries = filter_by_field(entries, key, str(value))

    for entry in entries:
        print(entry)
    # Print Profiling Results
    for key, value in Profile.all_functions().items():
        print(Profile.str(value))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Import log file and return all or a subsection of lines')
    parser.add_argument('path', nargs='+', help='Log File Path')
    parser.add_argument('-l', '--loglevel', nargs='?',
                        help='Filter by Log Level (DEBUG, ERROR, WARN, ..)')
    parser.add_argument('-b', '--business-id', type=int, nargs='?',
                        help='Filter by Business ID')
    parser.add_argument('-s', '--session-id', type=int, nargs='?',
                        help='Filter by Session ID')
    parser.add_argument('-r', '--request-id', nargs='?',
                        help='Filter by Request ID')
    parser.add_argument('-d', '--date-range', nargs='?',
                        help='Filter by Date Range ("YYYY-MM-DD YYYY-MM-DD")')
    args = parser.parse_args()
    main(args)
