import rospy
import smach
from std_msgs.msg import String
import rosplan_dispatch_msgs.msg as plan_dispatch_msgs

from mdr_monitoring_msgs.msg import ExecutionState
from mas_knowledge_utils.domestic_ontology_interface import DomesticOntologyInterface
from mas_knowledge_base.domestic_kb_interface import DomesticKBInterface

class ScenarioStateBase(smach.State):
    def __init__(self, action_name, outcomes,
                 input_keys=list(), output_keys=list(),
                 save_sm_state=False):
        smach.State.__init__(self, outcomes=outcomes,
                             input_keys=input_keys,
                             output_keys=output_keys)
        self.sm_id = ''
        self.state_name = ''
        self.action_name = action_name
        self.save_sm_state = save_sm_state
        self.retry_count = 0
        self.executing = False
        self.succeeded = False
        self.say_pub = rospy.Publisher('/say', String, latch=True, queue_size=1)
        self.ontology_url = rospy.get_param('/ontology_url', '')
        self.ontology_class_prefix = rospy.get_param('/ontology_class_prefix', '')

        self.action_dispatch_pub = rospy.Publisher('/kcl_rosplan/action_dispatch',
                                                   plan_dispatch_msgs.ActionDispatch,
                                                   queue_size=1)

        rospy.Subscriber('/kcl_rosplan/action_feedback',
                         plan_dispatch_msgs.ActionFeedback,
                         self.get_action_feedback)

        self.kb_interface = DomesticKBInterface()
        self.ontology_interface = DomesticOntologyInterface(self.ontology_url,
                                                            self.ontology_class_prefix)
        self.robot_name = self.kb_interface.robot_name

    def execute(self, userdata):
        pass

    def save_current_state(self):
        execution_state_msg = ExecutionState()
        execution_state_msg.stamp = rospy.Time.now()
        execution_state_msg.state_machine = self.sm_id
        execution_state_msg.state = self.state_name
        self.kb_interface.insert_obj_instance('current_state', execution_state_msg)

    def get_dispatch_msg(self):
        pass

    def get_action_feedback(self, msg):
        if msg.information and msg.information[0].key == 'action_name' and \
        msg.information[0].value == self.action_name:
            self.executing = False
            self.succeeded = msg.status == 'action achieved'

    def say(self, sentence):
        say_msg = String()
        say_msg.data = sentence
        self.say_pub.publish(say_msg)
