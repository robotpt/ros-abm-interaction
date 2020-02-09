#!/usr/bin/env python3.6

from abm_grant_interaction import state_db, param_db
from abm_grant_interaction.abm_interaction import AbmInteraction

import rospy
from cordial_gui.srv import Ask, AskRequest

from interaction_engine.interfaces.interface import Interface
from interaction_engine.messager.message import Message


class AbmCordialClient(Interface):

    def __init__(
            self,
            service_topic,
            pickled_database=None,
            is_create_db_key_if_not_exist=True,
            node_name='cordial_client',
    ):
        super().__init__(
            self.ask,
            pickled_database=pickled_database,
            is_create_db_key_if_not_exist=is_create_db_key_if_not_exist
        )

        rospy.init_node(node_name, anonymous=True)
        self._service_topic = service_topic
        self._client = rospy.ServiceProxy(self._service_topic, Ask)

    def ask(self, message):

        if type(message) is not Message:
            raise ValueError("Must input message class")

        rospy.wait_for_service(self._service_topic)

        try:
            ask_request = AskRequest()
            ask_request.display.type = message.message_type
            ask_request.display.content = message.content
            ask_request.display.buttons = message.options

            response = self._client(ask_request)
            return response.data

        except rospy.ServiceException as e:
            print("Service call failed: {}".format(e))


if __name__ == '__main__':

    interface = AbmCordialClient(
        service_topic='cordial/say_and_ask_on_gui',
        pickled_database=state_db,
    )
    abm_interaction = AbmInteraction(interface=interface)

    while not rospy.is_shutdown():
        abm_interaction.run_scheduler_once()
        rospy.sleep(1.)
        rospy.logdebug("Ran loop")


