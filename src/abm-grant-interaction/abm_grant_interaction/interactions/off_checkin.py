from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator


class OffCheckin:

    class Messages:

        no_sync = Message(
            content=(
                    "I haven't heard from your Fitbit in a while. " +
                    "Try syncing your phone, and then check back with me again."
            ),
            options=[
                "{affirmative_plus_button_response}",
                "{Ill_try_that_button_response}",
            ],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        give_status = Message(
            content=(
                    "You've done {'db': '%s'} steps so far today. " % state_db.Keys.STEPS_TODAY +
                    "Think you can meet your goal of {'db': '%s'} steps before our checkin at {'db': '%s'}?"
                    % (state_db.Keys.STEPS_GOAL, state_db.Keys.PM_CHECKIN_TIME)
            ),
            options=[
                '{affirmative_plus_button_response}',
                '{affirmative_button_response}',
                "{Ill_try_that_button_response}",
                "I don't think that I can today"
            ],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )

        give_status_met_goal = Message(
            content=(
                    "Your goal was {'db': '%s'} steps today and " % state_db.Keys.STEPS_GOAL +
                    "you've done {'db': '%s'} steps already. " % state_db.Keys.STEPS_TODAY +
                    "Nice job.  We'll review your total progress at our evening checkin at {'db': '%s'}."
                    % state_db.Keys.PM_CHECKIN_TIME
            ),
            options=[
                '{affirmative_button_response}',
            ],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )

