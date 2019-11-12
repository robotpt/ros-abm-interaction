from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator


class OffCheckin:

    class Messages:
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


