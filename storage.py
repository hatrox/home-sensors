from apiclient import discovery
from google.oauth2 import service_account
from datetime import datetime
import os, pytz

import common
from common import Sensor
from aqi import aqi

SPREADSHEET_ID = '18SQJSHL2Lg8kgPxiiHce8Yrquyf8Y9i5USvYQyvWWZs'
RANGE_NAME = 'data!A2:I'
CREDS_FILE = common.get_abs_path('credentials.json')
SCOPES = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets",
]
TIMEZONE = 'Europe/Sofia'
TIMESTAMP_FMT = "%Y%m%d_%H%M%S"
TIMESTAMP_FMT_PRETTY = "%Y-%m-%d %H:%M:%S" # parsable by Sheets

def get_sheets():
    credentials = service_account.Credentials \
            .from_service_account_file(CREDS_FILE, scopes=SCOPES)

    return discovery.build(
            'sheets', 'v4', credentials=credentials).spreadsheets()

def put(LOCAL_ENV, readouts):
    localized = datetime.now()
    if not LOCAL_ENV:
        timezone = pytz.timezone(TIMEZONE)
        utc = pytz.utc
        localized = utc.localize(localized).astimezone(timezone)

    timestamp = localized.strftime(TIMESTAMP_FMT)
    timestamp_pretty = localized.strftime(TIMESTAMP_FMT_PRETTY)

    data = {
        'values': [ [timestamp, timestamp_pretty] + readouts ]
    }

    if LOCAL_ENV: data['values'][0].append("test")

    get_sheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            body=data,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED').execute()

def get_response(entry, with_timestamps=True):

    return output

def get_last(LOCAL_ENV):
    # Does this actually get *ALL* lines of the 'data' sheet and return them as
    # an array?! That's horribly inefficient, if we'll only be dealing with the
    # last line there.
    entries = get_sheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME).execute()['values']

    last_entry = entries[-1] # latest reading

    keys = ['timestamp', 'timestamp_pretty'] + [id.name for id in list(Sensor)]
    output = dict(zip(keys, last_entry))

    pm25_aqi, pm25_label = aqi([float(last_entry[7])], Sensor.sds_pm25).get()
    output['pm25_aqi'] = pm25_aqi
    output['pm25_label'] = pm25_label.name

    pm10_aqi, pm10_label = aqi([float(last_entry[8])], Sensor.sds_pm10).get()
    output['pm10_aqi'] = pm10_aqi
    output['pm10_label'] = pm10_label.name

    return output

# TODO: have /get/avg, /get/max, /get/min, etc
