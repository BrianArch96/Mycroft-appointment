from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def addEvent():
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store, flags) \
                if flags else tools.run(flow, store)
    CAL = build('calendar', 'v3', http=creds.authorize(Http()))
    GMT_OFF= '-00:00'
    EVENT = {
        'summary': 'Testing this thing',
        'start': {'dateTime': '2019-01-12T19:00:00%s' % GMT_OFF},
        'end':   {'dateTime': '2019-01-12T22:00:00%s' % GMT_OFF},
    }
    e = CAL.events().insert(calendarId='primary',
            sendNotifications=True, body=EVENT).execute()

    print('''*** %r event added:
            Start: %s
            End    %s''' %(e['summary'].encode('utf-8'),
                e['start']['dateTime'], e['end']['dateTime']))

if __name__ == '__main__':
    addEvent()
