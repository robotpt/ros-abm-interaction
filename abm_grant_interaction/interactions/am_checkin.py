from interaction_engine.messager import Message, Node, DirectedGraph
from abm_grant_interaction import state_db, param_db, text_populator

import datetime


class Common:

    class Nodes:
        greeting_morning = Node(
            name='greeting',
            content="{greeting_morning}",
            options="{greeting_morning}",
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_type=str,
            text_populator=text_populator,
            transitions='exit'
        )
        greeting = Node(
            name='greeting',
            content="{greeting}",
            options="{greeting}",
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_type=str,
            text_populator=text_populator,
            transitions='exit'
        )

    class Graphs:
        pass


class AmCheckin:

    class Messages:

        greeting = Message(
            content="{greeting}",
            options="{greeting}",
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_type=str,
            text_populator=text_populator,
        )
        closing = Message(
            content="Bye",
            options=['Bye', 'See ya!'],
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_type=str,
            text_populator=text_populator,
        )
        big_5_question = Message(
            content=(
                    "How do you feel about the following statement? " +
                    "'{'var': 'big_5_question', 'index': " +
                    "'{'db': '%s', 'post-op': 'increment'}'}'" % state_db.Keys.PSYCH_QUESTION_INDEX
            ),
            options=[
                'Strongly agree',
                'Agree',
                'Neutral',
                'disagree',
                'Strongly disagree',
            ],
            message_type=Message.Type.MULTIPLE_CHOICE,
            result_db_key=state_db.Keys.PSYCH_QUESTION_ANSWERS,
            is_append_result=True,
            text_populator=text_populator,
        )
        when_question = Message(
            content="When will you walk today?",
            options='is when',
            message_type=Message.Type.DIRECT_INPUT,
            result_db_key=state_db.Keys.WALK_TIME,
            result_type=lambda x: datetime.datetime.strptime(x, '%H:%M').time(),
            tests=[
                lambda x: datetime.datetime.now().time() < x < state_db.get(state_db.Keys.PM_CHECKIN_TIME),
            ],
            error_message="Please pick a time after now and before our evening checkin",
            is_confirm=True,
            text_populator=text_populator,
        )
        where_question = Message(
            content="Where will you walk today?",
            options=state_db.get(state_db.Keys.WALK_PLACES),
            message_type=Message.Type.DIRECT_INPUT,
            result_db_key=state_db.Keys.WALK_PLACES,
            is_append_result=True,
            result_type=lambda x: datetime.datetime.strptime(x, '%H:%M').time(),
            tests=[
                lambda x: datetime.datetime.now().time() < x < state_db.get(state_db.Keys.PM_CHECKIN_TIME),
            ],
            error_message="Please pick a time after now and before our evening checkin",
            is_confirm=True,
            text_populator=text_populator,
        )


if __name__ == '__main__':

    from interaction_engine import InteractionEngine
    from interaction_engine.planner import MessagerPlanner
    from interaction_engine.interfaces import TerminalInterface

    graphs_ = [
        AmCheckin.greeting,
        AmCheckin.basic_questions,
        AmCheckin.big_5_question,
        AmCheckin.closing]

    # Create a plan
    plan_ = MessagerPlanner(graphs_)
    plan_.insert(AmCheckin.greeting)
    plan_.insert(AmCheckin.basic_questions)
    for _ in range(3):
        plan_.insert(AmCheckin.big_5_question)
    plan_.insert(AmCheckin.closing)

    ie = InteractionEngine(TerminalInterface(state_db), plan_, graphs_)
    ie.run()

    print(state_db)
    print(param_db)
