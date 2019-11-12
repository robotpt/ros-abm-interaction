from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator


class Common:

    class Messages:
        greeting = Message(
            content="{greeting}",
            options=["{greeting}"]*2,
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
        closing = Message(
            content="{goodbye}",
            options=['{goodbye}']*2,
            message_type=Message.Type.MULTIPLE_CHOICE,
            text_populator=text_populator,
        )
