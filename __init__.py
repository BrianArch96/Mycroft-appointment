# TODO: Add an appropriate license to your skill before publishing.  See
# the LICENSE file for more information.

# Below is the list of outside modules you'll be using in your skill.
# They might be built-in to Python, from mycroft-core or from external
# libraries.  If you use an external library, be sure to include it
# in the requirements.txt file so the library is installed properly
# when the skill gets installed later by a user.

from .gcAPI import event
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from datetime import datetime, timedelta, date
from mycroft.util.parse import extract_datetime

# Each skill is contained within its own class, which inherits base methods
# from the MycroftSkill class.  You extend this class as shown below.

# TODO: Change "Template" to a unique name for your skill
class TemplateSkill(MycroftSkill):

    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(TemplateSkill, self).__init__(name="TemplateSkill")
        print("appointment") 
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


    @intent_handler(IntentBuilder("").require("add_event"))
    def handle_add_summary(self, message):
        print("Hello")
    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, there is no need to override it.  If you DO
    # need to implement stop, you should return True to indicate you handled
    # it.
    #
    # def stop(self):
    #    return False

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return TemplateSkill()
