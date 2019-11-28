from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator


class Common:

    class Messages:
        greeting = Message(
            content="{greeting}",
            options=["{greeting_}"],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        greeting_morning = Message(
            content="{greeting_morning}",
            options=["{greeting_}"],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        greeting_afternoon = Message(
            content="{greeting_afternoon}",
            options=["{greeting_}"],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        greeting_evening = Message(
            content="{greeting_evening}",
            options=["{greeting_}"],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        closing = Message(
            content="{goodbye}",
            options=['{goodbye_}'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        closing_morning = Message(
            content="{goodbye_morning}",
            options=['{goodbye_}'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        closing_afternoon = Message(
            content="{goodbye_afternoon}",
            options=['{goodbye_}'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        closing_night = Message(
            content="{goodbye_night}",
            options=['{goodbye_}'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        missed_checkin = Message(
            content="We missed seeing each other. Let's not miss any more checkins.",
            options=[
                "{apologize_failure}",
                "{neutral_failure}",
                "{okay_button_response}",
            ],
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
