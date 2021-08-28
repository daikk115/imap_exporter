# IMAP Exporter

A tiny exporter to count how many email we receive day by day.

### Quick Start
- Start exporter
```
pip3 install -r requirements.txt
python3 imap_exporter.py
```

- Start Promtheus and Grafana

```
docker-compose up -d
```

### Feature

Only one feature which is expose one metric call `imap_mail_count`.
This is a counter, when you clean the folder, it will reset.

### Architecture

- All metrics will be saved as a json file.
- For now, this just support one metric as above, corresponding with `MailCount` class. In the feature, we can support other metrics by define other function/class to collect and dump metrics to file.
- Each folder need to be monitored in any aspects will present as an instance of a class.
- Each instance will be managed by a `BackgroundScheduler`.
- Each function needs to be run periodically will be managed by a `job` in a `Scheduler`.

### Known Exception

- If last check is yesterday but current check is today, which value should be set for `mail_count`?
> `mail_count` = number of email from yesterday to now. For the next check, metric will be reset and `mail_count` = number of email today
- What happen when `INTERVAL` is set too small and last check did not complete yet?
> Current logic will be skip check until last check is completed.
