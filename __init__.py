# TODO: Add an appropriate license to your skill before publishing.  See
# the LICENSE file for more information.

# Below is the list of outside modules you'll be using in your skill.
# They might be built-in to Python, from mycroft-core or from external
# libraries.  If you use an external library, be sure to include it
# in the requirements.txt file so the library is installed properly
# when the skill gets installed later by a user.

from .gcAPI import event
from .gcAPI import quickstart
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from datetime import datetime, timedelta, date
from mycroft.util.parse import extract_datetime

WEEK = 7
MONTH = 30
YEAR = 365

def remove_z(tz_string):
    return tz_string[:-1]

def getEvents(n):
    return quickstart.get_events(n)

def is_today(d):
    return d.date() == datetime.today().date()

def is_tomorrow(d):
    return d.date() == datetime.today().date() + timedelta(days=1)

def is_givenDays(d, n):
    return d.date() == datetime.today().date() + timedelta(days=n)

def time_format(date_t):
    time = date_t.strftime("%H:%M")

    response = ""
    print(time[1])
    if time[0] == '0':
        if time[1] == '0':
            response = " 0 0"
        else:
            response += time[1]
    else:
        response += time[0:2]

    if time[3] == '0':
        if time[4] == '0':
            response += " o clock"
        else:
            response += "0 " + time[4]
    else:
        if time[0] == "0":
            reponse += " " + time[3:5]
        else:
            response += ":" + time[3:5]
    print(response)
    return response

class StudentAppointmentSkill(MycroftSkill):


    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(StudentAppointmentSkill, self).__init__(name="StudentAppointmentSkill")
        import logging
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        print("appointment") 
        self._events = quickstart.get_events(10)
        # Initialize working variables used within the skill.
        self.count = 0

    @intent_handler(IntentBuilder("").require("Event"))
    def handle_add_event_intent(self, message):
        GMT_OFF = '-00:00'
        self._summary = self.get_response("summary")
        self._start_time = extract_datetime(self.get_response("start_time"))[0].strftime('%Y-%m-%dT%H:%M:%S')
        self._end_time = extract_datetime(self.get_response("end_time"))[0].strftime('%Y-%m-%dT%H:%M:%S')
        
        self._start_time += GMT_OFF
        self._end_time += GMT_OFF

        EVENT = {
                'summary': self._summary,
                'start': {'dateTime': self._start_time},
                'end': {'dateTime': self._end_time},
        }
        
        event.addEvent(EVENT)
        self.speak_dialog("ok")

    @intent_handler(IntentBuilder("").require("anything_else").require("more"))
    def more_appointments(self, message):
        print("dad")
        events = self.checkForMore(message.data.get("more"))
        print(len(events), "length")
        if len(events) == 0:
            self.speak_dialog("no_more")
            return
        self.speak_dialog("you_have_more", {"context": message.data.get("more")})
        for event in events:
            print(event, "I")
            self.speak_dialog("NextAppDate", event)
    
    @intent_handler(IntentBuilder("").require("remove_appointment").require("appointment"))
    def removeAppointment(self, message):
        for ev in quickstart.get_events(30):
            if ev["summary"] == message.data.get("appointment"):
                try:
                    print(ev["id"])
                    event.removeEvent(ev["id"])
                    self.speak_dialog("I've successfully removed the given appointment from your Google Calendar")
                except Exception as e:
                    print(e)
                    self.speak_dialog("Could not find event, possibly not listed")

    @intent_handler(IntentBuilder("").require("Upcoming_event"))
    def getNextEvent(self, message):
        self._events = quickstart.get_events(10)
        if not self._events:
            self.speak_dialog("NoNextApp")
            return

        event = self._events[0]
        start = event['start'].get('dateTime')
        print(remove_z(start))
        d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
        start_t = time_format(d)
        print(start_t)
        start_d = d.strftime('%-d %B')
        if is_today(d):
            data = {'appointment': event['summary'], 'time': start_t}
            self.speak_dialog("NextAppToday", data)
        elif is_tomorrow(d):
            print('tomorrow')
            data = {'appointment': event['summary'], 'time': start_t}
            self.speak_dialog("NextAppTomorrow", data)
        else:
            data = {'appointment': event['summary'], 'time': start_t, 'date': start_d}
            self.speak_dialog("NextAppDate", data)
            print('another date')

    @intent_handler(IntentBuilder("").require("event_tw"))
    def checkThisWeek(self, message):
        self._events = quickstart.get_events(10)
        if not self._events:
            self.speak_dialog("NoNextAppThisWeek")
            return
        n_events = 0
        for event in self._events:
            start = event['start'].get('dateTime')
            d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
            start_t = time_format(d)
            start_d = d.strftime('%-d %B')
            if is_today(d):
                data = {'appointment':event['summary'], 'time': start_t, 'date': start_d}
                self.speak_dialog('NextAppToday', data)
                self.set_context("more", "week")
                print("re")
                return
            elif is_tomorrow(d):
                data = {'appointment':event['summary'], 'time': start_t, 'date': start_d}
                self.speak_dialog('NextAppDate', data)
                self.set_context("more", "week")
                print("re")
                return
            else:
                for x in range(2, WEEK+1):
                    if is_givenDays(d, x):
                        data = {'appointment':event['summary'], 'time': start_t, 'date': start_d}
                        self.speak_dialog('NextAppDate', data)
                        print("re")
                        self.set_context("more", "week")
                        return
        self.speak_dialog("NoNextAppThisWeek")

    def checkForMore(self, context):
        self._events = quickstart.get_events(10)
        c_events = []
        for event in self._events[1:]:
            start = event['start'].get('dateTime')
            d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
            start_t = time_format(d)
            start_d = d.strftime('%-d %B')
            if context == "week":
                for x in range(0, WEEK+1):
                    if is_givenDays(d,x):
                        c_events.append({'appointment':event['summary'], 'time': start_t, 'date': start_d})
            elif context == "month":
                for x in range(0, MONTH+1):
                    if is_givenDays(d,x):
                        c_events.append({'appointment':event['summary'], 'time': start_t, 'date': start_d})
        if c_events is None:
            self.speak_dialog("no_more_appointments")
            return
        return c_events

    @intent_handler(IntentBuilder("").require("list_appointments"))
    def list_assignments(self, message):
        self._events = quickstart.get_events(10)
        if not self._events:
            self.speak_dialog("no_more")
            return
        self.speak_dialog("Here is a list of upcoming appointments")
        for event in self._events:
            start = event['start'].get('dateTime')
            d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
            start_t = time_format(d)
            start_d = d.strftime('%-d %B')
            self.speak_dialog("appointment_details", { "sum": event["summary"], "start": start_d})


    @intent_handler(IntentBuilder("").require("event_tm"))
    def checkThisMonth(self, message):
        self._events = quickstart.get_events(10)
        if not self._events:
            self.speak_dialog("NoNextAppThisMonth")
            return
        n_events = 0
        for event in self._events:
            start = event['start'].get('dateTime')
            d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
            start_t = time_format(d)
            start_d = d.strftime('%-d %B')
            if is_today(d):
                data = {'appointment':event['summary'], 'time': start_t, 'date': start_d}
                self.speak_dialog('NextAppToday', data)
                self.set_context("more", "month")
                return
            elif is_tomorrow(d):
                data = {'appointment':event['summary'], 'time': start_t, 'date': start_d}
                self.speak_dialog('NextAppDate', data)
                self.set_context("more", "month")
                return
            else:
                for x in range(2, MONTH+1):
                    if is_givenDays(d, x):
                        data = {'appointment':event['summary'], 'time': start_t, 'date': start_d}
                        self.speak_dialog('NextAppDate', data)
                        self.set_context("more", "month")
                        return
        self.speak_dialog("NoNextAppThisMonth")

    @intent_handler(IntentBuilder("").require("event_today"))
    def checkTodaysEvents(self, message):
        self._events = quickstart.get_events(10)
        if not self._events:
            self.speak_dialog("NoNextAppToday")
            return
        
        n_events = 0
        for event in self._events:
            start = event['start'].get('dateTime')
            d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
            start_t = time_format(d)
            print(start_t, " hi")
            start_d = d.strftime('%-d %B')
            if is_today(d):
                n_events + n_events+1
        
        start = self._events[0]['start'].get('dateTime')
        d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
        start_t = time_format(d)

        if n_events == 0:
            self.speak_dialog("NoNextAppToday")
        else:
            data = {'appointment':self._events[0]['summary'], 'time': start_t, 'n_events': n_events}
            self.speak_dialog('AppointmentsToday', data)

    @intent_handler(IntentBuilder("").require("event_tomorrow"))
    def checkTomorrowsEvents(self, message):
        print("Hello")
        self._events = quickstart.get_events(10)
        if not self._events:
            self.speak_dialog("NoNextAppTomorrow")
        
        n_events = 0
        f_event = None

        for event in self._events:
            start = event['start'].get('dateTime')
            d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
            start_t = time_format(d)
            start_d = d.strftime('%-d %B')
            if is_tomorrow(d):
                if n_events == 0:
                    f_event = event          
                n_events = n_events +1
        
        if n_events == 0:
            self.speak_dialog("NoNextAppTomorrow")
            return
        
        start = f_event['start'].get('dateTime')
        d = datetime.strptime(remove_z(start), '%Y-%m-%dT%H:%M:%S')
        start_t = time_format(d)

        data = {'appointment':f_event['summary'], 'time': start_t, 'n_events': n_events}
        self.speak_dialog("AppointmentsTomorrow", data)

def create_skill():
    return StudentAppointmentSkill()
