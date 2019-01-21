from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

def get_events(number):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json'))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json', SCOPES))
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=number, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
        
    return events
    
if __name__ == '__main__':
    get_events(10)
