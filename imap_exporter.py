import atexit
import json
import logging
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
import imaplib
from flask import Flask, render_template, make_response

from config import *

app = Flask(__name__)
CACHE_FILE_PATH = "{}.data"
DATETIME_FORMAT = "%d-%b-%Y"


class MailCount():
    def __init__(self, backend, folder):
        self.metric = "imap_mail_count"
        self.backend = backend
        self.folder = folder
        self.mail_count = 0
        self.cache_file_path = "{}.data".format(self.backend)
        self.mail_check_completed = True
        self.last_check = datetime.now().strftime(DATETIME_FORMAT)

    def dump_data_to_file(self):
        # Dump data to file
        self.get_number_email()
        data = {
            'metric': self.metric,
            'backend': self.backend,
            'mail_count': self.mail_count
        }
        with open(CACHE_FILE_PATH.format(self.backend), "w") as cache_file:
            json.dump(data, cache_file)

    def get_number_email(self):
        if not self.mail_check_completed:
            # Do nothing if last check did not complete!
            return
        # Open mail connection
        self.mail_check_completed = False
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(ADDRESS, PASSWORD)
        mail.select(self.folder)
        # Do get number of mail today at this time
        today = datetime.now()
        if self.last_check != today.strftime(DATETIME_FORMAT):
            # Assuming that last check was yesterday
            yesterday = today - timedelta(1)
            _, yesterdayMessageIDs = mail.search(
                None, "(SINCE {0})".format(yesterday.strftime(DATETIME_FORMAT)))
            self.mail_count = len(yesterdayMessageIDs[0].split())
            logging.debug("Yesterday check for {}! Number of mails: {}".format(
                self.backend, self.mail_count))
        else:
            _, messageIDs = mail.search(
                None, "(SINCE {0})".format(today.strftime(DATETIME_FORMAT)))
            self.mail_count = len(messageIDs[0].split())
            logging.debug("Today check for {}! Number of mails: {}".format(
                self.backend, self.mail_count))
        self.last_check = today.strftime(DATETIME_FORMAT)
        mail.close()
        self.mail_check_completed = True


@app.route('/<backend>')
def do_get(backend):
    if backend in LIST_FOLDERS.keys():
        metric = ''
        # Read cache file
        with open(CACHE_FILE_PATH.format(backend), 'r') as cache_file:
            data = json.load(cache_file)
            # Convert cache file to metrics format
            metric = '{}{{folder="{}"}} {}'.format(
                data['metric'], data['backend'], data['mail_count'])

        response = make_response(metric, 200)
        response.mimetype = "text/plain"
        return response
    else:
        return render_template('index.html', enabled_backends=LIST_FOLDERS.keys())


def check_mail_process():
    # Init folder
    list_folders = []
    for backend in LIST_FOLDERS.keys():
        list_folders.append(MailCount(backend, LIST_FOLDERS[backend]))
    for folder in list_folders:
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=folder.dump_data_to_file,
                          trigger="interval", seconds=int(INTERVAL))
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
        folder.dump_data_to_file()


def config_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s   %(levelname)s   %(message)s',
        level=LOG_LEVEL)


if __name__ == '__main__':
    app.debug = LOG_LEVEL
    app.secret_key = os.urandom(30)
    config_logging(LOGFILE)
    check_mail_process()
    app.run(host=HOST, port=PORT, use_reloader=False)
    logging.info("IMAP Exporter is ready now!")
