Log Parser
=================
Log Parser reads the log entries from a file, stores them in memory, filters the
results if a flag is specified and prints out the result to screen.

Filtering Options:

- LogLevel - *DEBUG, INFO, WARNING, ERROR, CRITICAL*
- Session ID
- Business ID
- Request ID
- Date Range - 'YYYY-MM-DD YYYY-MM-DD' *(from - to)*

Log File Column Format
----------------------

    DATE LOGLEVEL SESSION-ID BUSINESS-ID REQUEST-ID MSG

Usage
-----

    python3 log_parser.py [LOG_FILE_PATH]

Show All Results:

    python3 log_parser.py example.log

Filter by LogLevel (-l):

    python3 log_parser.py example.log -l DEBUG

Filter by Business ID (-b):

    python3 log_parser.py example.log -b  319

Filter by Session ID (-s):

    python3 log_parser.py example.log -s 42111

Filter by Date Range (-d):

    python3 log_parser.py example.log -d  '2012-09-14 2012-09-16'

Testing
-------

    pytest

or

    python3 -m pytest test_log_parser.py
