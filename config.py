import logging

# List of folder we want to monitor
# Key must be contain only character or underscore
LIST_FOLDERS = {
    'my_folder_1': 'INBOX/SubFolder',
    'my_folder_2': 'INBOX/SubFolder/SubSubFolder'
}

# Interval check mail server
INTERVAL = 300

# Mail account
IMAP_HOST = "imap.domain.com"
ADDRESS = "user@domain.com"
PASSWORD = "EasyPass"

# Config metrics server
HOST = '0.0.0.0'
PORT = '8888'

# Logging to file
LOGFILE = 'imap_exporter.log'
LOG_LEVEL = logging.DEBUG
